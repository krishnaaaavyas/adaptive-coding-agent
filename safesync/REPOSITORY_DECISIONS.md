# SafeSync V1 repository decisions

ID: SS-01
Decision: JSON configuration, with paths relative to the config file and strict field/type checks.
Product reason: Portable standard-library parsing and predictable paths regardless of working directory.
Status: ACCEPTED
Benchmark relevance considered: NO

ID: SS-02
Decision: Standard-library argparse CLI, invoked with python -B -m safesync.
Product reason: Provides preview/run without installation or changes to parent dependency files; -B suppresses interpreter cache writes.
Status: ACCEPTED
Benchmark relevance considered: NO

ID: SS-03
Decision: Compare ordinary files by relative path, size, and streamed SHA-256 hash.
Product reason: Detects same-size changes regardless of timestamps, without loading entire files into memory.
Status: ACCEPTED
Benchmark relevance considered: NO

ID: SS-04
Decision: Reject encountered symlinks, Windows reparse points, and special files, including root ancestors.
Product reason: Avoids following external content or destination aliases; keeps local behavior understandable.
Status: ACCEPTED
Benchmark relevance considered: NO

ID: SS-05
Decision: Reject equal roots and nesting in either direction.
Product reason: Prevents self-consumption and source mutation with a small explicit policy.
Status: ACCEPTED
Benchmark relevance considered: NO

ID: SS-06
Decision: Stop on first failure, preserve earlier successes, and report remaining actions as unattempted.
Product reason: Limits further mutation when assumptions or filesystem operations fail and gives truthful counts without rollback machinery.
Status: ACCEPTED
Benchmark relevance considered: NO

ID: SS-07
Decision: Case-sensitive fnmatchcase matching on relative paths and their directory prefixes on both sides.
Product reason: Simple documented glob behavior protects ignored destination content and excludes whole matching directories.
Status: ACCEPTED
Benchmark relevance considered: NO

ID: SS-08
Decision: Frozen dataclasses and tuple sequences; execution revalidates a supplied plan against current state before any writes.
Product reason: Preview state cannot change through ordinary public mutation; direct API callers cannot bypass containment, ignores, or delete opt-in through altered actions.
Status: ACCEPTED
Benchmark relevance considered: NO

ID: SS-09
Decision: Temporary destination file plus atomic file replacement, with per-action state checks.
Product reason: Avoids partial payload replacement on copy failure and protects source content when destination files share hard links.
Status: ACCEPTED
Benchmark relevance considered: NO

ID: SS-10
Decision: Direct local filesystem module, standard-library runtime, and pytest temporary-directory tests.
Product reason: Small maintainable filesystem boundary with realistic tests, without provider or dependency frameworks.
Status: ACCEPTED
Benchmark relevance considered: NO

ID: SS-11
Decision: Synchronize file payloads only; leave empty directories and reject blocking file/directory conflicts.
Product reason: Directory structure supports file copying without implicit deletion or extra action types.
Status: ACCEPTED
Benchmark relevance considered: NO

ID: SS-12
Decision: Require quiescent directories; exclude concurrent hostile filesystem mutation and crash recovery guarantees.
Product reason: Local checks and atomic per-file replacement are appropriate for a small utility; locking and transactions require a broader product.
Status: ACCEPTED
Benchmark relevance considered: NO

ID: SS-13
Decision: Reject cross-tree file paths differing only in case on Windows.
Product reason: Case aliases could otherwise cause a copy and deletion to target the same destination file.
Status: ACCEPTED
Benchmark relevance considered: NO
