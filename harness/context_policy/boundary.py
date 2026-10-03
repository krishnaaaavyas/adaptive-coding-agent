"""Authenticated immutable acquisition and private target-admission boundary."""

from dataclasses import dataclass
from fnmatch import fnmatchcase
import re
from types import MappingProxyType
import unicodedata

from .core import (BASENAMES, EXCLUDED_DIRS, EXTENSIONS, P_LIMIT, SECRET_PATTERNS,
                   SOURCE_LIMIT, Diagnostic, PolicyFailure, ascii_lower, canonical_json,
                   digest, fail, file_text, normalized_text, raise_diagnostics, require_auth, u)


def path(value, *, normalize=False):
    if not isinstance(value, str) or not value:
        raise ValueError("empty/nonstring path")
    value.encode("utf-8", "strict")
    nfc = unicodedata.normalize("NFC", value)
    if normalize:
        value = nfc
    elif value != nfc:
        raise ValueError("non-NFC path")
    for component in value.split("/"):
        if (component in ("", ".", "..") or component.endswith((" ", "."))
                or any(unicodedata.category(c) == "Cc" or c in '\\<>:"|?*' for c in component)):
            raise ValueError("invalid component")
        stem = component.split(".")[0].upper()
        if stem in ("CON", "PRN", "AUX", "NUL") or re.fullmatch(r"(?:COM|LPT)[1-9¹²³]", stem):
            raise ValueError("reserved component")
    return value


def under(name, ancestor):
    return name == ancestor or name.startswith(ancestor + "/")


def prohibited(name):
    parts = name.split("/")
    if any(ascii_lower(p) in EXCLUDED_DIRS or ascii_lower(p).endswith(".egg-info") for p in parts[:-1]):
        return True
    return any(fnmatchcase(ascii_lower(parts[-1]), pattern) for pattern in SECRET_PATTERNS)


def supported(name):
    base = name.rsplit("/", 1)[-1]
    extension = "." + base.rsplit(".", 1)[-1] if "." in base else ""
    return ascii_lower(extension) in EXTENSIONS or base in BASENAMES


def excluded_directory(name):
    return any(ascii_lower(p) in EXCLUDED_DIRS or ascii_lower(p).endswith(".egg-info") for p in name.split("/"))


@dataclass(frozen=True)
class PublicTask:
    instructions: str
    targets: tuple[str, ...]
    serialized: bytes
    sha256: str
    raw_serialized: bytes
    raw_sha256: str


def public_task(envelope, certificate, auth, *, mode="official"):
    diagnostics = []
    if (not isinstance(envelope, dict) or set(envelope) != {"instructions", "targets"}
            or not isinstance(envelope.get("instructions"), str)
            or not isinstance(envelope.get("targets"), list) or not envelope["targets"]):
        fail("task_invalid", "invalid_task_schema", 2)
    try:
        instructions = normalized_text(envelope["instructions"], nul=False)
    except (ValueError, UnicodeError):
        fail("task_invalid", "invalid_task_text", 2)
    targets = []
    for target in envelope["targets"]:
        try:
            targets.append(path(target, normalize=True))
        except (ValueError, UnicodeError):
            diagnostics.append(Diagnostic("task_invalid", "invalid_target_path", 2))
    targets = sorted(set(targets), key=u)
    if len({p.casefold() for p in targets}) != len(targets):
        diagnostics.append(Diagnostic("task_invalid", "target_path_collision", 2))
    if any(a != b and under(b, a) for a in targets for b in targets):
        diagnostics.append(Diagnostic("task_invalid", "conflicting_targets", 2))
    payload = {"instructions": instructions, "targets": targets}
    data = canonical_json(payload)
    if len(data) > P_LIMIT:
        diagnostics.append(Diagnostic("task_invalid", "public_task_overlength", 2))
    raise_diagnostics(diagnostics)
    try:
        require_auth(auth, payload, certificate, mode)
    except PolicyFailure:
        fail("task_invalid", "public_task_uncertified", 2)
    # The interface receives a decoded envelope, not transport bytes. Preserve
    # J of that exact input before normalization; do not claim a wire identity.
    raw = canonical_json(envelope)
    return PublicTask(instructions, tuple(targets), data, digest(data), raw, digest(raw))


@dataclass(frozen=True)
class ProductSnapshot:
    """Selector-safe view. No private existence entries are stored here."""
    files: object
    raw_hashes: object
    raw_sizes: object
    directories: tuple[str, ...]
    identity: str


@dataclass(frozen=True)
class TargetAdmission:
    path: str
    existing: bool
    content_sha256: str | None


@dataclass(frozen=True)
class Acquisition:
    """Restricted boundary object; never pass this to the selector or model."""
    snapshot: ProductSnapshot
    _entries: object
    _denied: tuple[str, ...]
    identity: str
    receipt_bytes: bytes

    @classmethod
    def verify(cls, product_manifest, denied, existence, raw_files, receipt, certificate,
               auth, configuration, *, mode="official"):
        diagnostics = []
        try:
            product = [dict(entry) for entry in product_manifest]
            index = [dict(entry) for entry in existence]
            denied = tuple(sorted((path(p) for p in denied), key=u))
            for entry in product + index:
                if entry["path"]:
                    path(entry["path"])
                if entry["type"] not in ("regular", "directory", "symlink", "reparse", "gitlink", "other"):
                    raise ValueError("entry type")
            for rows in (product, index):
                names = [entry["path"] for entry in rows]
                if len(names) != len(set(names)) or len(names) != len({p.casefold() for p in names}):
                    raise ValueError("namespace collision")
            product.sort(key=lambda e: u(e["path"]))
            index.sort(key=lambda e: u(e["path"]))
            pm = {e["path"]: e for e in product}
            entries = {e["path"]: e for e in index}
            if "" not in entries or entries[""]["type"] != "directory" or not entries[""].get("product"):
                raise ValueError("root enumeration")
            for p, entry in pm.items():
                if any(under(p, d) for d in denied):
                    diagnostics.append(Diagnostic("infrastructure_invalid", "product_evaluator_conflict", 1))
                if p not in entries or not entries[p].get("product") or entries[p]["type"] != entry["type"]:
                    raise ValueError("manifest membership")
            for p, entry in entries.items():
                if any(type(entry.get(field)) is not bool for field in ("product", "denied", "complete")):
                    raise ValueError("index flag types")
                if bool(entry.get("product")) != (p in pm):
                    raise ValueError("index membership")
                if bool(entry.get("denied")) != any(under(p, d) for d in denied):
                    raise ValueError("deny membership")
                if p:
                    parent = p.rpartition("/")[0]
                    if parent not in entries or entries[parent]["type"] != "directory":
                        raise ValueError("orphan entry")
                if entry["type"] == "directory" and entry.get("product") and not entry.get("complete"):
                    diagnostics.append(Diagnostic("infrastructure_invalid", "existence_unverified", 1))
            # Supplied bytes must be only product regular-file bytes, never private material.
            if any(p not in pm or pm[p]["type"] != "regular" for p in raw_files):
                raise ValueError("unmanifested content")
            bundle_rows = []
            texts, hashes, raw_sizes, eligible = {}, {}, {}, {}
            for p, entry in pm.items():
                if entry["type"] != "regular":
                    continue
                size, raw_hash = entry["raw_size"], entry["raw_sha256"]
                if type(size) is not int or size < 0 or not re.fullmatch("[0-9a-f]{64}", raw_hash):
                    raise ValueError("content identity")
                bundle_rows.append({"path": p, "raw_size": size, "raw_sha256": raw_hash})
                # Filtering does not waive integrity for a supplied blob.
                # Filtered files may be metadata-only, but captured bytes must
                # match the signed identity before eligibility is considered.
                if p in raw_files:
                    raw = bytes(raw_files[p])
                    if len(raw) != size or digest(raw) != raw_hash:
                        raise ValueError("acquisition drift")
                code = "eligible"
                if prohibited(p):
                    code = "excluded"
                elif not supported(p):
                    code = "unsupported"
                elif size > SOURCE_LIMIT:
                    code = "oversized"
                else:
                    if p not in raw_files:
                        raise ValueError("missing content")
                    try:
                        texts[p] = file_text(raw)
                        hashes[p] = raw_hash
                        raw_sizes[p] = size
                    except (UnicodeError, ValueError):
                        code = "invalid_text"
                eligible[p] = code
                if entries[p].get("eligibility") != code:
                    raise ValueError("classification conflict")
            expected = {"policy_id": configuration["policy_id"], "configuration_sha256": digest(canonical_json(configuration)),
                        "product_manifest_sha256": digest(canonical_json(product)),
                        "deny_manifest_sha256": digest(canonical_json(list(denied))),
                        "existence_index_sha256": digest(canonical_json(index)),
                        "snapshot_bundle_sha256": digest(canonical_json(bundle_rows)),
                        "acquisition_identity": receipt.get("acquisition_identity")}
            if not expected["acquisition_identity"] or receipt != expected:
                raise ValueError("receipt binding")
            require_auth(auth, receipt, certificate, mode)
        except PolicyFailure as exc:
            diagnostics.extend(exc.diagnostics)
        except (KeyError, TypeError, ValueError, UnicodeError):
            diagnostics.append(Diagnostic("infrastructure_invalid", "snapshot_invalid", 1))
        raise_diagnostics(diagnostics)
        dirs = tuple(sorted((p for p, e in pm.items() if e["type"] == "directory" and not excluded_directory(p)), key=u))
        snapshot = ProductSnapshot(MappingProxyType(texts), MappingProxyType(hashes), MappingProxyType(raw_sizes), dirs,
                                   expected["snapshot_bundle_sha256"])
        frozen_entries = MappingProxyType({p: MappingProxyType(e) for p, e in entries.items()})
        receipt_bytes = canonical_json(receipt)
        return cls(snapshot, frozen_entries, denied, digest(receipt_bytes), receipt_bytes)

    def admit(self, task):
        diagnostics, results = [], []
        folded = {p.casefold(): p for p in self._entries}
        for target in task.targets:
            reason = None
            if prohibited(target) or any(under(target, d) for d in self._denied):
                reason = "prohibited_target_path"
            elif not supported(target):
                reason = "unsupported_target_format"
            parts = target.split("/")
            for n in range(1, len(parts) + 1):
                p = "/".join(parts[:n])
                if p.casefold() in folded and folded[p.casefold()] != p:
                    diagnostics.append(Diagnostic("task_invalid", "target_path_collision", 2))
                entry = self._entries.get(p)
                if entry is None:
                    # Missing entry in a certified complete ordinary hierarchy proves absence.
                    break
                if entry["type"] in ("symlink", "reparse", "gitlink"):
                    diagnostics.append(Diagnostic("task_invalid", "prohibited_target_ancestry", 2))
                    break
                if n < len(parts):
                    if entry["type"] != "directory":
                        diagnostics.append(Diagnostic("task_invalid", "target_parent_not_directory", 2))
                        break
                    if not entry.get("product"):
                        diagnostics.append(Diagnostic("task_invalid", "target_ancestry_not_product", 2))
                    if entry.get("denied") or excluded_directory(p):
                        diagnostics.append(Diagnostic("task_invalid", "prohibited_target_path", 2))
            entry = self._entries.get(target)
            if entry:
                if entry.get("denied"):
                    reason = "prohibited_target_path"
                elif entry["type"] == "directory":
                    reason = "target_not_regular_file"
                elif entry["type"] in ("symlink", "reparse", "gitlink"):
                    reason = "prohibited_target_ancestry"
                elif entry["type"] != "regular":
                    reason = "target_not_regular_file"
                elif not entry.get("product"):
                    reason = "existing_target_not_product"
                elif target not in self.snapshot.files:
                    reason = reason or "prohibited_target_path"
            if reason:
                diagnostics.append(Diagnostic("task_invalid", reason, 2))
            results.append(TargetAdmission(target, entry is not None, digest(self.snapshot.files[target].encode()) if target in self.snapshot.files else None))
        raise_diagnostics(diagnostics)
        return tuple(results)
