# SafeSync V1

SafeSync is a small one-way local folder synchronization utility for Python
3.10+. It compares relative file paths, sizes, and SHA-256 content hashes to
produce an ordered plan before changing the destination. Runtime dependencies
are entirely from the Python standard library.

From the parent repository directory:

```powershell
python -B -m safesync preview path/to/config.json
python -B -m safesync run path/to/config.json
```

The `-B` option prevents Python's own bytecode-cache writes. Preview only reads
configuration and filesystem contents, prints the proposed actions as JSON,
and exits. It does not create even an absent destination directory. Run builds
and validates a fresh plan, executes it, and prints a JSON report. Invoking run
approves the changes described by the current configuration and filesystem
state; it has no interactive confirmation prompt. Preview and run are separate
invocations, so preview again if files change between them.

Create a JSON configuration (source must already exist):

```json
{
  "source": "../my-files",
  "destination": "../my-backup",
  "delete_extra": false,
  "ignore": ["*.tmp", "cache", "build/*"]
}
```

Paths are relative to the configuration file's directory, or absolute.
`source`, `destination`, and boolean `delete_extra` are required; `ignore` is
optional. Unknown configuration fields are rejected. Keep the configuration
outside the synchronized trees if it should not be synchronized.

## Plan and execution

Source-only files produce COPY, differing files UPDATE, and identical files
SKIP. Destination-only files produce DELETE only with `delete_extra: true`;
otherwise they produce SKIP and remain untouched. Actions are ordered by
case-sensitive relative path. Modification timestamps do not determine equality.
Directories provide structure: parents are created when copying files, while
empty directories are neither copied nor removed. File/directory conflicts
fail safely rather than implicitly deleting a blocking entry.
On Windows, files with different source/destination spelling that would alias
the same case-insensitive path are rejected rather than copied then deleted.

Source and destination must be separate directories: equal roots and nesting
in either direction are rejected. Symbolic links, Windows junctions/reparse
points, and nonordinary files are unsupported. Encountered links are rejected,
including links whose own names match an ignore pattern. Ignored directory
subtrees are not traversed. Roots and path ancestors are checked as well.

Ignore matching uses Python `fnmatchcase` glob semantics against each full
relative path and its directory prefixes, using `/` separators. Matching is
case-sensitive on all platforms; `*` can match `/`, so `*.tmp` also matches
nested temporary files. A matching directory excludes its whole subtree on
both sides. Ignored content never produces execution actions, including deletes.
There are no negation rules or special `**` semantics.

Public planning values are frozen, and sequences are copied to tuples. The
executor independently validates roots and relative paths, rejects absolute,
traversal, alternate-stream, and device paths, and compares the supplied plan
against a fresh plan before making any changes. It rechecks each action's file
state before executing it. Stale or altered plans fail validation, including
plans attempting to bypass ignores or deletion opt-in. The public API supports
`plan = preview(config)` followed by `report = execute(plan)` when the same
filesystem state still holds.

Writes use a temporary file in the destination directory and atomic replacement
of the destination file after checking the copied content hash. Source payloads
are only read; existing destination hard links are replaced rather than written
through. Hard-link relationships and file permissions are not synchronized.

Execution stops at the first failure and does not roll back earlier successes.
Reports count `copied`, `updated`, `deleted`, `skipped`, and `failed`, with error
details and `unattempted` actions. A preflight failure counts as one failed
validation with all actions unattempted. Temporary files are cleaned up on
ordinary operation failures; parent directories created before failure may
remain. CLI exit status is 0 on success and 1 on configuration/planning/execution
failure; argument errors use argparse's status 2.

Use quiescent local directories: simultaneous filesystem writers, hostile
processes changing links during a system call, and abrupt process termination
are outside V1's guarantees. The application checks for stale state and links
but does not provide filesystem locking or transactional synchronization.

SafeSync does not provide network/cloud sync, bidirectional sync, background
monitoring, version history, encryption, or restore management.

## Tests

```powershell
python -B -m pytest safesync/tests
```

Tests use real temporary directories; link creation tests skip if the host
does not permit creating symbolic links. An operation-failure test injects an
OS replacement error to check reporting and temporary-file cleanup.
