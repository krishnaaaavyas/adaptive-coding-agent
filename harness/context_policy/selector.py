"""Task-only anchors, one-hop nominations and length-based K construction."""

from collections import defaultdict
from dataclasses import dataclass
import re

from .boundary import path
from .core import (INVENTORY_LIMIT, I_CLOSE, I_OMIT, I_OPEN, K_CLOSE, K_LIMIT, K_OPEN,
                   STOPLIST, canonical_json, digest, fail, u)
from .index import ordinary_test, structural


def components(text):
    for identifier in re.finditer(r"[A-Za-z_][A-Za-z0-9_]*", text):
        token = identifier.group()
        starts = {0, len(token)}
        for i, char in enumerate(token):
            if char == "_" or char.isdigit():
                starts.update((i, i + 1))
            if i and token[i - 1].islower() and char.isupper():
                starts.add(i)
            if i and i + 1 < len(token) and token[i - 1].isupper() and char.isupper() and token[i + 1].islower():
                starts.add(i)
        boundaries = sorted(starts)
        for a, b in zip(boundaries, boundaries[1:]):
            component = token[a:b]
            normalized = component.lower()
            if re.fullmatch(r"[A-Za-z]{4,}", component) and normalized not in STOPLIST:
                yield normalized, identifier.start() + a, identifier.start(), a, component


def spans(text):
    i = 0
    while i < len(text):
        char = text[i]
        identifier = lambda c: bool(re.fullmatch(r"[A-Za-z0-9_]", c))
        if (char in "'\"`" and (i == 0 or text[i - 1] != char) and (i + 1 == len(text) or text[i + 1] != char)
                and not (i and i + 1 < len(text) and identifier(text[i - 1]) and identifier(text[i + 1]))):
            end = text.find(char, i + 1)
            newline = text.find("\n", i + 1)
            if end >= 0 and (newline < 0 or end < newline):
                yield text[i + 1:end], i + 1, "quoted", i
                i = end + 1
                continue
        i += 1
    for match in re.finditer(r"[A-Za-z0-9_./\\-]+", text):
        yield match.group(), match.start(), "bare", None


@dataclass(frozen=True)
class Anchor:
    path: str
    key: tuple
    protected: bool
    reason: str
    occurrence: str
    metadata: tuple = ()
    resolution_reasons: tuple = ()


def anchors(task, snapshot, index):
    files = snapshot.files
    directory_files = defaultdict(list)
    basenames = defaultdict(list)
    for p in files:
        directory_files[p.rpartition("/")[0]].append(p)
        basenames[p.rsplit("/", 1)[-1]].append(p)
    found = []
    def match(candidate, location, kind, delimiter=None, structured=False):
        attempts = [candidate]
        if not structured and candidate.endswith("."):
            attempts.append(candidate[:-1])
        for attempt in attempts:
            results, rank, protect = [], None, False
            path_form = structured or "/" in attempt or "\\" in attempt or attempt.startswith("./")
            if path_form:
                try:
                    normalized = attempt if structured else attempt.replace("\\", "/")
                    if not structured and normalized.startswith("./"):
                        normalized = normalized[2:]
                    normalized = path(normalized, normalize=True)
                    if normalized in files:
                        results, rank, protect = [normalized], 0, True
                    elif normalized in snapshot.directories:
                        results, rank = directory_files[normalized], 1
                except (ValueError, UnicodeError):
                    pass
            else:
                if attempt in basenames:
                    results, rank = basenames[attempt], 2
                    protect = len(results) == 1
                elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*", attempt):
                    if attempt in index.modules:
                        results, rank = index.modules[attempt], 3
                    elif attempt in index.declarations:
                        results, rank = index.declarations[attempt], 4
            if results:
                for p in sorted(results, key=u):
                    resolution = ()
                    if rank == 3:
                        resolution = tuple(tuple(sorted({"alias": attempt, "owned_module": r.base,
                                                       "provider": r.provider, "root_prefixed": r.prefixed}.items()))
                                           for r in index.routes[attempt] if r.provider == p)
                    elif rank == 4:
                        resolution = tuple(tuple(sorted(r.items())) for r in index.declaration_reasons[attempt] if r["path"] == p)
                    found.append(Anchor(p, (rank, location, u(p)), protect, kind, candidate,
                                        (("delimiter_offset", delimiter),) if delimiter is not None else (), resolution))
                return
    for candidate, offset, kind, delimiter in spans(task.instructions):
        match(candidate, (0, offset), kind, delimiter)
    for n, target in enumerate(task.targets):
        match(target, (1, n, 0), "target", structured=True)
    if found:
        return tuple(found)
    lexical = defaultdict(list)
    for p in index.files:
        for text, source in [(p, "path")] + [(name, "declaration") for name in index.names[p]]:
            for component, offset, start, relative, original in components(text):
                lexical[component].append((p, source, text, offset))
    for field, text in [(0, task.instructions)] + [(n + 1, target) for n, target in enumerate(task.targets)]:
        for component, offset, start, relative, original in components(text):
            location = (0, offset) if field == 0 else (1, field - 1, offset)
            for p, source, source_text, source_offset in lexical[component]:
                found.append(Anchor(p, (5, location, u(p)), False, "lexical", original,
                                    (("identifier_offset", start), ("component_offset", relative),
                                     ("component", component), ("source", source), ("source_text", source_text),
                                     ("source_offset", source_offset))))
    return tuple(found)


def seeds(occurrences):
    by_file = defaultdict(list)
    for occurrence in occurrences:
        by_file[occurrence.path].append(occurrence)
    protected = sorted((p for p, rows in by_file.items() if any(a.protected for a in rows)),
                       key=lambda p: min(a.key for a in by_file[p] if a.protected))
    inferred = sorted((p for p in by_file if p not in protected), key=lambda p: min(a.key for a in by_file[p]))[:4]
    return tuple(protected), tuple(inferred)


@dataclass(frozen=True)
class Nomination:
    path: str
    key: tuple
    reason: str
    seed: str
    supporting_test: str = ""


def expand(snapshot, index, protected, inferred):
    original = protected + inferred
    nominations = []
    def add(p, priority, n, reason, subrank=0, supporting_test=""):
        if p in snapshot.files:
            nominations.append(Nomination(p, (priority, n, subrank, u(p)), reason,
                                          original[n] if n < len(original) else "", supporting_test))
    for n, seed in enumerate(original):
        if seed in inferred:
            add(seed, 0, n, "inferred_seed")
        if structural(seed):
            for p in sorted(index.edges.get(seed, ()), key=u):
                add(p, 1, n, "direct_import")
            callers = sorted((p for p in index.reverse.get(seed, ()) if p != seed and not ordinary_test(p)), key=u)[:2]
            for p in callers:
                add(p, 2, n, "reverse_import")
            if not ordinary_test(seed):
                stem = seed.rsplit("/", 1)[-1].rsplit(".", 1)[0]
                paired = {f"test_{stem}.py", f"{stem}_test.py"}
                tests = []
                for p in index.files:
                    if ordinary_test(p):
                        basename = p.rsplit("/", 1)[-1]
                        if basename in paired or seed in index.edges.get(p, ()):
                            tests.append((0 if basename in paired else 1, u(p), p))
                for subrank, _, p in sorted(tests)[:2]:
                    add(p, 3, n, "associated_test", subrank)
        directory = seed.rpartition("/")[0]
        ancestors = ["/".join(directory.split("/")[:i]) for i in range(len(directory.split("/")), -1, -1)] if directory else [""]
        for ancestor in ancestors:
            readmes = sorted((p for p in snapshot.files if p.rpartition("/")[0] == ancestor and p.rsplit("/", 1)[-1].lower() == "readme.md"), key=u)
            if readmes:
                add(readmes[0], 5, n, "nearest_readme")
                break
    # Test nominations are deliberately expanded before global deduplication.
    test_origins = [(p, n, "test_seed") for n, p in enumerate(original) if ordinary_test(p)]
    test_origins += [(nom.path, nom.key[1], nom.reason) for nom in tuple(nominations) if ordinary_test(nom.path)]
    for test, n, reason in test_origins:
        directory = test.rpartition("/")[0]
        parts = directory.split("/") if directory else []
        for depth in range(len(parts), -1, -1):
            p = "/".join(parts[:depth] + ["conftest.py"])
            add(p, 4, n, "fixture:" + reason, supporting_test=test)
    root_readmes = sorted((p for p in snapshot.files if "/" not in p and p.lower() == "readme.md"), key=u)
    if root_readmes:
        add(root_readmes[0], 5, len(original), "root_readme")
    return tuple(nominations)


def file_block(p, content):
    body = content.encode("utf-8")
    return b"[FILE " + canonical_json(p) + b" bytes=" + str(len(body)).encode() + b"]\n" + body + b"\n[/FILE]\n"


@dataclass(frozen=True)
class KContext:
    serialized: bytes
    sha256: str
    protected: tuple[str, ...]
    inferred: tuple[str, ...]
    selected: tuple[str, ...]
    anchors: tuple
    nominations: tuple
    skipped: tuple
    inventory_paths: tuple
    inventory_omitted: bool
    contributions: tuple
    inventory_serialized: bytes
    inventory_allowance: int


def select(task, snapshot, index):
    occurrences = anchors(task, snapshot, index)
    protected, inferred = seeds(occurrences)
    protected_blocks = [file_block(p, snapshot.files[p]) for p in protected]
    remaining = K_LIMIT - len(K_OPEN) - len(K_CLOSE) - sum(map(len, protected_blocks))
    if remaining < 0:
        fail("context_ineligible", "protected_files_overflow", 3)
    inventory_paths = tuple(sorted(snapshot.files, key=u))
    records = [(p, canonical_json(p) + b"\n") for p in inventory_paths]
    allowance = min(INVENTORY_LIMIT, remaining)
    inventory, emitted_inventory, omitted = b"", [], False
    all_bytes = I_OPEN + b"".join(record for _, record in records) + I_CLOSE
    if len(all_bytes) <= allowance:
        inventory, emitted_inventory = all_bytes, list(inventory_paths)
    elif len(I_OPEN + I_OMIT + I_CLOSE) <= allowance:
        residual, prefix = allowance - len(I_OPEN + I_OMIT + I_CLOSE), []
        for p, record in records:
            if len(record) > residual:
                break
            prefix.append(record)
            emitted_inventory.append(p)
            residual -= len(record)
        inventory, omitted = I_OPEN + b"".join(prefix) + I_OMIT + I_CLOSE, True
    remaining -= len(inventory)
    nominations = expand(snapshot, index, protected, inferred)
    by_file = defaultdict(list)
    for nomination in nominations:
        if nomination.path not in protected:
            by_file[nomination.path].append(nomination)
    ordered = sorted(by_file, key=lambda p: min(n.key for n in by_file[p]))
    optional, selected, skipped = [], list(protected), []
    contributions = [(p, len(block), len(snapshot.files[p].encode()), digest(snapshot.files[p].encode())) for p, block in zip(protected, protected_blocks)]
    for p in ordered:
        block = file_block(p, snapshot.files[p])
        if len(block) > remaining:
            skipped.append((p, "optional_budget_skip", len(block), remaining))
            continue
        optional.append(block)
        selected.append(p)
        contributions.append((p, len(block), len(snapshot.files[p].encode()), digest(snapshot.files[p].encode())))
        remaining -= len(block)
    serialized = K_OPEN + b"".join(protected_blocks) + inventory + b"".join(optional) + K_CLOSE
    assert len(serialized) <= K_LIMIT
    return KContext(serialized, digest(serialized), protected, inferred, tuple(selected), occurrences,
                    nominations, tuple(skipped), tuple(emitted_inventory), omitted, tuple(contributions), inventory, allowance)
