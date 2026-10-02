"""Validation of externally curated evidence; no semantic record generation."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import re
import json

from .core import (EVIDENCE_ID, H_CLOSE, H_LIMIT, H_OPEN, L_CLOSE, L_OPEN,
                   canonical_json, digest, fail, normalized_text, require_auth, u)

KINDS = ("EPISODIC", "DESCRIPTIVE", "CONFIRMED_RULE")
SOURCES = frozenset(("public_task", "developer_request", "product_snapshot", "authorized_attempt",
                     "public_test", "developer_feedback", "accepted_change", "public_documentation"))


@dataclass(frozen=True)
class RegistryArchive:
    """Authenticated immutable registry revision; updates can only append.

    Semantic construction/certification remains external. This interface never
    creates or revises a body; it rejects mutation of an existing record/event.
    """
    serialized: bytes
    sha256: str

    @classmethod
    def capture(cls, registry, certificate, auth, *, mode="official"):
        raw = canonical_json(registry)
        require_auth(auth, json.loads(raw), certificate, mode)
        return cls(raw, digest(raw))

    def extend(self, registry, certificate, auth, *, mode="official"):
        next_archive = self.capture(registry, certificate, auth, mode=mode)
        old, new = json.loads(self.serialized), json.loads(next_archive.serialized)
        try:
            if new["contract"] != old["contract"] or new["events"][:len(old["events"])] != old["events"]:
                raise ValueError("ledger rewrite")
            new_rows = {row["key"]: row for row in new["records"]}
            if len(new_rows) != len(new["records"]) or any(new_rows.get(row["key"]) != row for row in old["records"]):
                raise ValueError("record mutation")
        except (KeyError, TypeError, ValueError):
            fail("infrastructure_invalid", "registry_update_not_append_only", 1)
        return next_archive


@dataclass(frozen=True)
class Record:
    key: str
    kind: str
    body: str
    body_sha256: str
    availability: int
    metadata_sha256: str


@dataclass(frozen=True)
class EligibleRegistry:
    records: tuple[Record, ...]
    identity: str
    ledger_root: str
    cutoff: int
    excluded: tuple


def cutoff_payload(registry, cutoff, task_release_sequence, public_task_sha256):
    return {"registry_sha256": digest(canonical_json(registry)), "cutoff": cutoff,
            "first_public_release_sequence": task_release_sequence, "public_task_sha256": public_task_sha256}


def registry_view(registry, certificate, auth, *, cutoff, task_release_sequence,
                  cutoff_certificate=None, public_task_sha256=None, mode="official"):
    require_auth(auth, registry, certificate, mode)
    binding = cutoff_payload(registry, cutoff, task_release_sequence, public_task_sha256)
    require_auth(auth, binding, cutoff_certificate, mode)
    try:
        if (registry["contract"] != EVIDENCE_ID or type(cutoff) is not int or cutoff < 0
                or type(task_release_sequence) is not int or cutoff > task_release_sequence
                or not isinstance(public_task_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", public_task_sha256)):
            raise ValueError("contract/cutoff")
        events, previous, sequence = {}, "0" * 64, -1
        for event in registry["events"]:
            n = event["sequence"]
            if type(n) is not int or n <= sequence or event["previous_sha256"] != previous:
                raise ValueError("ledger chain")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", event["utc"]):
                raise ValueError("UTC timestamp")
            datetime.strptime(event["utc"], "%Y-%m-%dT%H:%M:%SZ")
            if not event["source_identity"] or event["actor"] not in auth.authorized:
                raise ValueError("actor/source identity")
            payload = {key: value for key, value in event.items() if key != "certificate"}
            require_auth(auth, payload, event["certificate"], mode)
            if event["certificate"]["signer"] != event["actor"]:
                raise ValueError("actor signature")
            events[n], sequence, previous = event, n, digest(canonical_json(event))
        if registry["ledger_root"] != previous:
            raise ValueError("ledger root")
        released_keys = {}
        for n, event in events.items():
            if event["type"] == "registry_available":
                key = event["payload"]["binding"]["key"]
                if key in released_keys:
                    raise ValueError("released record identity reused")
                released_keys[key] = n
        records = {}
        eligibility, excluded = {}, []
        for row in registry["records"]:
            key, kind = row["key"], row["kind"]
            if not isinstance(key, str) or not key or key in records or kind not in KINDS:
                raise ValueError("record identity")
            body = normalized_text(row["body"])
            if body != row["body"] or digest(body.encode()) != row["body_sha256"]:
                raise ValueError("body identity")
            sources = row["sources"]
            if not sources:
                raise ValueError("missing lineage")
            source_sequences = []
            for source in sources:
                event = events[source["event"]]
                if (event["type"] != "source_available" or event["payload"]["kind"] not in SOURCES
                        or event["payload"].get("authorized_public") is not True
                        or not re.fullmatch(r"[0-9a-f]{64}", source["artifact_sha256"])
                        or source["artifact_sha256"] != event["payload"]["artifact_sha256"]
                        or not source["spans"]):
                    raise ValueError("source authorization")
                source_sequences.append(source["event"])
            expected_binding = {"key": key, "kind": kind, "body_sha256": row["body_sha256"],
                                "scope_sha256": digest(canonical_json(row["scope"])),
                                "exceptions_sha256": digest(canonical_json(row["exceptions"])),
                                "lineage_sha256": digest(canonical_json(sources))}
            constructor = events[row["construction"]]
            certifier = events[row["certification"]]
            released = events[row["availability"]]
            for event, event_type in ((constructor, "body_constructed"), (certifier, "eligibility_certified"), (released, "registry_available")):
                if event["type"] != event_type or event["payload"].get("binding") != expected_binding:
                    raise ValueError("required event certification")
            if constructor["actor"] == certifier["actor"]:
                raise ValueError("constructor/certifier independence")
            if not max(source_sequences) < row["construction"] < row["certification"] < row["availability"]:
                raise ValueError("event prerequisite order")
            prerequisite = source_sequences + [row["construction"], row["certification"], row["availability"]]
            if kind == "CONFIRMED_RULE":
                confirmation = events[row["confirmation"]]
                if (confirmation["type"] != "rule_confirmed" or confirmation["payload"].get("binding") != expected_binding
                        or confirmation["payload"].get("route") not in ("developer", "curator_oracle")
                        or not row["construction"] < row["confirmation"] < row["certification"]):
                    raise ValueError("rule confirmation")
                prerequisite.append(row["confirmation"])
            if kind == "EPISODIC" and not row.get("episode"):
                raise ValueError("episode identity")
            records[key] = row
            eligibility[key] = all(n < cutoff for n in prerequisite)
            if not eligibility[key]:
                excluded.append((key, "chronological_ineligible"))
        if released_keys != {key: row["availability"] for key, row in records.items()}:
            raise ValueError("released registry record missing or rewritten")
        # Verify lineage globally, even for records not yet available at cutoff.
        for key, row in records.items():
            seen, current = set(), row
            while current.get("predecessor"):
                predecessor = current["predecessor"]
                if predecessor not in records or predecessor in seen:
                    raise ValueError("revision chain")
                seen.add(predecessor)
                old = records[predecessor]
                if old["kind"] != row["kind"] or old["availability"] >= current["construction"]:
                    raise ValueError("revision chronology")
                if row["kind"] == "EPISODIC" and old.get("episode") != row.get("episode"):
                    raise ValueError("episode revision")
                current = old
        successors = defaultdict(list)
        for key, row in records.items():
            if eligibility[key] and row.get("predecessor"):
                if not eligibility[row["predecessor"]]:
                    raise ValueError("ineligible predecessor")
                successors[row["predecessor"]].append(key)
        if any(len(rows) > 1 for rows in successors.values()):
            raise ValueError("conflicting active revisions")
        withdrawn = set()
        for n, event in events.items():
            if event["type"] == "withdrawn":
                key = event["payload"]["key"]
                if key not in records or n <= records[key]["availability"]:
                    raise ValueError("withdrawal lineage")
                if n < cutoff:
                    withdrawn.add(key)
        active = []
        episode_keys = set()
        for key, row in records.items():
            if not eligibility[key] or key in successors or key in withdrawn:
                continue
            if row["kind"] == "EPISODIC":
                if row["episode"] in episode_keys:
                    raise ValueError("conflicting episode revisions")
                episode_keys.add(row["episode"])
            active.append(Record(key, row["kind"], row["body"], row["body_sha256"], row["availability"], digest(canonical_json(row))))
        active.sort(key=lambda r: (-r.availability, r.body_sha256, u(r.key)))
        view_identity = digest(canonical_json({"registry_sha256": digest(canonical_json(registry)),
                                             "cutoff": cutoff, "active": [r.key for r in active]}))
        return EligibleRegistry(tuple(active), view_identity, previous, cutoff, tuple(excluded))
    except (KeyError, TypeError, ValueError, UnicodeError):
        fail("infrastructure_invalid", "registry_invalid", 1)


def record_block(body):
    return b"[RECORD]\n" + body.encode("utf-8") + b"\n[/RECORD]\n"


@dataclass(frozen=True)
class HPayload:
    serialized: bytes
    sha256: str
    selected: tuple
    skipped: tuple
    duplicates: tuple
    overlaps: tuple
    lane_bytes: tuple


def pack_h(condition, view, snapshot):
    if condition not in ("A", "B", "M", "C", "BC"):
        fail("infrastructure_invalid", "condition_invalid", 1)
    if condition == "A":
        return HPayload(b"", digest(b""), (), (), (), (), ())
    kinds = {"B": ("EPISODIC",), "M": ("DESCRIPTIVE",), "C": ("CONFIRMED_RULE",),
             "BC": ("EPISODIC", "CONFIRMED_RULE")}[condition]
    selected, skipped, duplicates, overlaps, lanes, owned_sizes = [], [], [], [], [], []
    for lane_index, kind in enumerate(kinds):
        if condition == "BC":
            owned_outer = H_OPEN if lane_index == 0 else H_CLOSE
            remaining = 2048 - len(owned_outer + L_OPEN + L_CLOSE)
        else:
            owned_outer = H_OPEN + H_CLOSE
            remaining = H_LIMIT - len(owned_outer + L_OPEN + L_CLOSE)
        records = sorted((r for r in view.records if r.kind == kind), key=lambda r: (-r.availability, r.body_sha256, u(r.key)))
        seen, blocks = {}, []
        for record in records:
            if record.body in seen:
                duplicates.append((record.key, seen[record.body]))
                continue
            seen[record.body] = record.key
            block = record_block(record.body)
            if len(block) > remaining:
                skipped.append((record.key, "record_budget_skip", len(block), remaining))
                continue
            selected.append(record.key)
            blocks.append(block)
            remaining -= len(block)
            overlaps.extend((record.key, p, "exact_body_content") for p, content in snapshot.files.items() if content == record.body)
        lane = L_OPEN + b"".join(blocks) + L_CLOSE
        lanes.append(lane)
        owned_sizes.append((kind, len(owned_outer + lane)))
    serialized = H_OPEN + b"".join(lanes) + H_CLOSE if selected else b""
    assert len(serialized) <= H_LIMIT
    return HPayload(serialized, digest(serialized), tuple(selected), tuple(skipped), tuple(duplicates),
                    tuple(sorted(overlaps)), tuple(owned_sizes) if selected else ())
