"""Deterministic immutable provenance for Protocol-v2 experiment runs."""

from datetime import datetime, timezone
import hashlib
import importlib
import inspect
from pathlib import Path
import subprocess
import uuid


MANIFEST_SCHEMA_VERSION = "1"
RUNTIME_DIRECTORIES = {"__pycache__", ".pytest_cache"}


class ProvenanceError(RuntimeError):
    """A failure to establish trustworthy run provenance."""

    def __init__(self, message, manifest=None):
        super().__init__(message)
        self.manifest = manifest


class ProvenanceIntegrityError(ProvenanceError):
    """Previously recorded provenance no longer matches current inputs."""

    def __init__(self, mismatches):
        self.mismatches = mismatches
        fields = ", ".join(item["field"] for item in mismatches)
        super().__init__(f"Run provenance changed after preflight: {fields}")


def new_run_manifest():
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "run_id": str(uuid.uuid4()),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def file_sha256(path):
    path = Path(path)
    if path.is_symlink():
        raise ProvenanceError(f"Provenance file must not be a symlink: {path}")
    if not path.is_file():
        raise ProvenanceError(f"Required provenance file is missing: {path}")
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ProvenanceError(f"Could not hash provenance file {path}: {exc}") from exc


def _excluded_runtime_path(relative):
    return (
        any(part in RUNTIME_DIRECTORIES for part in relative.parts)
        or relative.suffix == ".pyc"
    )


def tree_sha256(root):
    """Hash regular files using the canonical tree-v1 byte encoding."""
    root = Path(root)
    if root.is_symlink():
        raise ProvenanceError(f"Provenance tree must not be a symlink: {root}")
    if not root.is_dir():
        raise ProvenanceError(f"Required provenance tree is missing: {root}")

    entries = []
    try:
        for path in root.rglob("*"):
            relative = path.relative_to(root)
            if path.is_symlink():
                raise ProvenanceError(
                    f"Provenance tree contains a symlink: {relative.as_posix()}"
                )
            if _excluded_runtime_path(relative):
                continue
            if path.is_file():
                entries.append((relative.as_posix(), file_sha256(path)))
    except OSError as exc:
        raise ProvenanceError(f"Could not traverse provenance tree {root}: {exc}") from exc

    if not entries:
        raise ProvenanceError(f"Required provenance tree is empty: {root}")

    digest = hashlib.sha256()
    digest.update(b"provenance-tree-v1\0")
    for relative, file_digest in sorted(entries):
        path_bytes = relative.encode("utf-8")
        digest.update(len(path_bytes).to_bytes(8, "big"))
        digest.update(path_bytes)
        digest.update(bytes.fromhex(file_digest))
    return digest.hexdigest()


def _git(repository_root, *arguments):
    try:
        process = subprocess.run(
            ["git", "-C", str(repository_root), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", None) or str(exc)
        raise ProvenanceError(f"Git provenance command failed: {detail.strip()}") from exc
    return process.stdout


def inspect_git_repository(repository_root):
    repository_root = Path(repository_root).resolve()
    discovered = Path(
        _git(repository_root, "rev-parse", "--show-toplevel").strip()
    ).resolve()
    if discovered != repository_root:
        raise ProvenanceError(
            "Experiment repository root does not match the expected Git repository"
        )

    commit = _git(repository_root, "rev-parse", "HEAD").strip()
    status_output = _git(
        repository_root,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
    )
    entries = status_output.split("\0")
    tracked_clean = True
    untracked = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        status = entry[:2]
        path = entry[3:]
        if status == "??":
            untracked.append(path.replace("\\", "/"))
        else:
            tracked_clean = False
            if "R" in status or "C" in status:
                index += 1

    state = {
        "git_commit": commit,
        "tracked_clean": tracked_clean,
        "untracked_files": sorted(untracked),
    }
    return state


def require_clean_git(repository_root, manifest):
    state = inspect_git_repository(repository_root)
    manifest["repository"] = state
    if not state["tracked_clean"]:
        raise ProvenanceError(
            "Official Protocol-v2 runs require a clean tracked working tree",
            manifest,
        )
    if state["untracked_files"]:
        raise ProvenanceError(
            "Official Protocol-v2 runs require no untracked files",
            manifest,
        )
    return state


def _manifest_path(path, repository_root):
    path = Path(path).resolve()
    repository_root = Path(repository_root).resolve()
    try:
        return path.relative_to(repository_root).as_posix()
    except ValueError:
        return path.as_posix()


def record_config(manifest, config_path, repository_root):
    manifest["config"] = {
        "path": _manifest_path(config_path, repository_root),
        "sha256": file_sha256(config_path),
    }
    return manifest["config"]


def declared_scorer_metadata(experiment, scorer):
    try:
        module = importlib.import_module(scorer.__module__)
        version = getattr(module, "SCORER_VERSION")
        source_name = inspect.getsourcefile(scorer)
        if source_name is None:
            raise AttributeError("scorer source file is unavailable")
        source = Path(source_name)
    except (AttributeError, ImportError, TypeError) as exc:
        raise ProvenanceError(
            f"Scorer metadata is unavailable for {experiment}: {exc}"
        ) from exc
    if not isinstance(version, str) or not version:
        raise ProvenanceError(
            f"Scorer {experiment} has no nonempty declared SCORER_VERSION"
        )
    return {
        "name": experiment,
        "version": version,
        "source_sha256": file_sha256(source),
    }


def fixture_tree_sha256(fixtures_root, experiment):
    return tree_sha256(Path(fixtures_root) / experiment)


def manifest_is_complete(manifest):
    return all(
        field in manifest
        for field in (
            "repository",
            "config",
            "base_repository",
            "scorer",
            "scorer_validation",
            "target_tests",
            "regression_tests",
            "protocol",
        )
    )


def verify_run_manifest(
    manifest,
    *,
    repository_root,
    config_path,
    base_repository,
    scorer,
    experiment,
    fixtures_root,
    target_tests,
    protocol_document,
):
    """Compare current provenance inputs with the immutable original manifest."""
    if not manifest_is_complete(manifest):
        raise ProvenanceIntegrityError(
            [{"field": "run_manifest", "expected": "complete", "actual": "partial"}]
        )

    mismatches = []

    def compare(field, expected, current):
        try:
            actual = current()
        except Exception as exc:
            mismatches.append(
                {
                    "field": field,
                    "expected": expected,
                    "actual": None,
                    "error": str(exc),
                }
            )
            return
        if actual != expected:
            mismatches.append(
                {"field": field, "expected": expected, "actual": actual}
            )

    try:
        repository = inspect_git_repository(repository_root)
    except Exception as exc:
        mismatches.append(
            {
                "field": "repository",
                "expected": manifest["repository"],
                "actual": None,
                "error": str(exc),
            }
        )
    else:
        compare(
            "repository.git_commit",
            manifest["repository"]["git_commit"],
            lambda: repository["git_commit"],
        )
        compare(
            "repository.tracked_clean",
            manifest["repository"]["tracked_clean"],
            lambda: repository["tracked_clean"],
        )
        compare(
            "repository.untracked_files",
            manifest["repository"]["untracked_files"],
            lambda: repository["untracked_files"],
        )

    compare(
        "config.sha256",
        manifest["config"]["sha256"],
        lambda: file_sha256(config_path),
    )
    compare(
        "base_repository.tree_sha256",
        manifest["base_repository"]["tree_sha256"],
        lambda: tree_sha256(base_repository),
    )
    compare(
        "scorer.source_sha256",
        manifest["scorer"]["source_sha256"],
        lambda: declared_scorer_metadata(experiment, scorer)["source_sha256"],
    )
    compare(
        "scorer_validation.fixture_tree_sha256",
        manifest["scorer_validation"]["fixture_tree_sha256"],
        lambda: fixture_tree_sha256(fixtures_root, experiment),
    )
    compare(
        "target_tests.tree_sha256",
        manifest["target_tests"]["tree_sha256"],
        lambda: tree_sha256(target_tests),
    )
    compare(
        "regression_tests.tree_sha256",
        manifest["regression_tests"]["tree_sha256"],
        lambda: tree_sha256(Path(base_repository) / "tests"),
    )
    compare(
        "protocol.protocol_document_sha256",
        manifest["protocol"]["protocol_document_sha256"],
        lambda: file_sha256(protocol_document),
    )

    if mismatches:
        raise ProvenanceIntegrityError(mismatches)
    return True


def populate_run_manifest(
    manifest,
    *,
    repository_root,
    config_path,
    base_repository,
    scorer,
    experiment,
    fixtures_root,
    target_tests,
    protocol_document,
):
    """Populate all required provenance, preserving partial data on failure."""
    try:
        if "config" not in manifest:
            record_config(manifest, config_path, repository_root)
        if "repository" not in manifest:
            require_clean_git(repository_root, manifest)
        manifest["base_repository"] = {
            "tree_sha256": tree_sha256(base_repository),
        }
        manifest["scorer"] = declared_scorer_metadata(experiment, scorer)
        manifest["scorer_validation"] = {
            "fixture_tree_sha256": fixture_tree_sha256(
                fixtures_root,
                experiment,
            ),
        }
        manifest["target_tests"] = {
            "tree_sha256": tree_sha256(target_tests),
        }
        manifest["regression_tests"] = {
            "tree_sha256": tree_sha256(Path(base_repository) / "tests"),
        }
        manifest["protocol"] = {
            "evaluation_protocol": "v2",
            "protocol_document_sha256": file_sha256(protocol_document),
        }
    except ProvenanceError as exc:
        if exc.manifest is None:
            exc.manifest = manifest
        raise
    except Exception as exc:
        raise ProvenanceError(
            f"Unexpected provenance failure: {exc}",
            manifest,
        ) from exc
    return manifest
