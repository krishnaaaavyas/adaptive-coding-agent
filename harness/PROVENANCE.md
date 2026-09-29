# Protocol-v2 run provenance

Every new Protocol-v2 result contains a run_manifest with schema version 1.
The run identifier is a UUID4 generated once when run_experiment starts. The
start time is generated once as a timezone-aware UTC ISO-8601 value. Neither is
derived from the result filename.

Before inference, the harness records the exact configuration bytes, Git HEAD
and cleanliness, the taskflow_base tree, the active scorer source and declared
version, that scorer's validation fixture subtree, evaluator-private target
tests, regression tests, and the Protocol-v2 document. SHA-256 is used for all
file and tree digests.

Structured Step-7 runs additionally record the exact SHA-256 of
ADAPTATION_CONDITIONS.md and verify it again before persistence. Their
adaptation values are inline in the experiment config, so the existing
exact-byte config digest covers the intervention content without duplicating it
in the manifest. Step 7 does not support external structured adaptation files.

## Canonical tree encoding

Runtime directories named __pycache__ or .pytest_cache and files ending in
.pyc are excluded. All other regular files are included. Symlinks are rejected
instead of followed, and a required tree with no included files is invalid.

Each included file is represented by its root-relative UTF-8 path using POSIX
forward slashes and the 32 raw bytes of SHA256(file raw bytes). Entries are
sorted lexicographically by the POSIX path. The tree digest is SHA-256 over:

1. the ASCII bytes provenance-tree-v1 followed by one zero byte;
2. for each entry, the path's unsigned 8-byte big-endian byte length;
3. the UTF-8 path bytes;
4. the 32 raw digest bytes.

This length-prefixed encoding is unambiguous and independent of host path
separators. File hashes always cover raw bytes without text normalization.

## Git and failure policy

The expected repository root must equal Git's reported top-level directory.
HEAD is recorded exactly. Porcelain status includes staged changes, unstaged
changes, and all non-ignored untracked files. Official runs require a clean
tracked tree and no untracked files. Git-ignored files are not reported.

Missing or unreadable inputs, dirty Git state, symlinks, empty required trees,
and unavailable or inconsistent scorer metadata are infrastructure failures.
They abort before model generation, preserve the safely established portion of
the manifest, and leave overall_success null.

After evaluation activity and before finalization or persistence, the harness
recomputes Git state and every recorded source-material digest and compares
them with the original manifest. It never replaces the original hashes. A
mismatch or verification failure makes the run infrastructure-invalid while
retaining completed generation and evaluation outputs for audit.
