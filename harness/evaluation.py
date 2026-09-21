"""Protocol v2 evaluator-private suites and independent evaluation gates."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


TARGET_DIRECTORY = "_evaluation_target_tests"
CONFIG_FILES = ("conftest.py", "pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini")
ARTIFACT_RUNTIME_DIRECTORIES = {
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".hypothesis",
}
ARTIFACT_RUNTIME_FILES = {".coverage", "coverage.xml"}


def pending_suite():
    return {
        "passed": None, "status": "not_run", "tests_passed": 0,
        "tests_failed": 0, "tests_skipped": 0, "returncode": None,
        "stdout": "", "stderr": "", "errors": [],
    }


def new_evaluation():
    return {
        "target": pending_suite(),
        "regression": {**pending_suite(), "regression_tests_modified": False,
                       "changed_files": [], "missing_files": [], "added_files": [],
                       "fingerprints": {}},
        "convention": {"passed": None, "status": "not_run", "errors": []},
        "artifact": {
            "evaluated_artifact_modified": False,
            "changed_files": [], "missing_files": [], "added_files": [],
            "fingerprints": {}, "checks": [], "errors": [],
        },
        "overall_success": None,
    }


def error_info(stage, exc):
    return {"stage": stage, "type": type(exc).__name__, "message": str(exc)}


def target_source(config, config_path, base_repo):
    """A config-relative directory, kept outside the model-visible base checkout."""
    setting = config.get("target_tests")
    if not isinstance(setting, dict) or set(setting) != {"source"}:
        raise ValueError('target_tests must be an object containing only "source"')
    source = setting["source"]
    if not isinstance(source, str) or not source.strip():
        raise ValueError("target_tests.source must be a nonempty directory path")
    source = (config_path.parent / source).resolve()
    base = base_repo.resolve()
    if source.is_relative_to(base) or base.is_relative_to(source):
        raise ValueError("Target tests must be outside the base repository")
    if not source.is_dir():
        raise FileNotFoundError(f"Target-test source directory missing: {source}")
    if any(p.is_symlink() for p in source.rglob("*")):
        raise ValueError("Target-test sources must not contain symbolic links")
    if not any(source.rglob("test_*.py")):
        raise ValueError("Target-test source must contain test_*.py files")
    return source


def _digest(path):
    if path.is_symlink():
        raise ValueError(f"Evaluator file must not be a symbolic link: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprints(workspace):
    """Protect all regression fixtures/data, plus root pytest configuration."""
    suite = workspace / "tests"
    if not suite.is_dir() or suite.is_symlink():
        raise ValueError("Regression suite must be a tests directory")
    paths = [p for p in suite.rglob("*")
             if p.is_file() and not any(part in {"__pycache__", ".pytest_cache"}
                                        for part in p.parts) and p.suffix != ".pyc"]
    paths.extend(workspace / name for name in CONFIG_FILES if (workspace / name).exists())
    return {p.relative_to(workspace).as_posix(): _digest(p) for p in sorted(paths)}


def check_regression(workspace, before):
    try:
        after = fingerprints(workspace)
        changed = sorted(name for name in before.keys() & after.keys()
                         if before[name] != after[name])
        missing = sorted(before.keys() - after.keys())
        added = sorted(after.keys() - before.keys())
    except (OSError, ValueError) as exc:
        return {"regression_tests_modified": True, "changed_files": [],
                "missing_files": [name for name in before if not (workspace / name).is_file()],
                "added_files": [], "integrity_error": str(exc)}
    return {"regression_tests_modified": bool(changed or missing or added),
            "changed_files": changed, "missing_files": missing, "added_files": added}


def artifact_fingerprints(workspace):
    """Fingerprint generated application files, excluding evaluator/runtime material."""
    paths = []
    for path in workspace.rglob("*"):
        relative = path.relative_to(workspace)
        if relative.parts[0] in {"tests", TARGET_DIRECTORY}:
            continue
        if any(part in ARTIFACT_RUNTIME_DIRECTORIES for part in relative.parts):
            continue
        if relative.as_posix() in CONFIG_FILES:
            continue
        if path.name in ARTIFACT_RUNTIME_FILES or path.name.startswith(".coverage."):
            continue
        if path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ValueError(f"Application artifact must not contain a symbolic link: {path}")
        if path.is_file():
            paths.append(path)
    return {path.relative_to(workspace).as_posix(): _digest(path)
            for path in sorted(paths)}


def check_artifact(workspace, before):
    try:
        after = artifact_fingerprints(workspace)
        changed = sorted(name for name in before.keys() & after.keys()
                         if before[name] != after[name])
        missing = sorted(before.keys() - after.keys())
        added = sorted(after.keys() - before.keys())
    except (OSError, ValueError) as exc:
        return {
            "evaluated_artifact_modified": True,
            "changed_files": [],
            "missing_files": [
                name for name in before if not (workspace / name).is_file()
            ],
            "added_files": [],
            "integrity_error": str(exc),
        }
    return {
        "evaluated_artifact_modified": bool(changed or missing or added),
        "changed_files": changed,
        "missing_files": missing,
        "added_files": added,
    }


def inject_target_tests(source, workspace):
    destination = workspace / TARGET_DIRECTORY
    # Refuse collisions instead of trusting or overwriting generated evaluator files.
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(
        "__pycache__", "*.pyc", ".pytest_cache"))
    return destination


def run_suite(workspace, suite, generated_files):
    result = pending_suite()
    try:
        with tempfile.TemporaryDirectory(prefix="evaluation-") as directory:
            report_path = Path(directory) / "report.json"
            env = os.environ.copy()
            env["HARNESS_PYTEST_REPORT"] = str(report_path)
            # Load the trusted plugin from outside the generated checkout.
            env["PYTHONPATH"] = os.pathsep.join(
                [str(Path(__file__).resolve().parent), str(workspace.resolve()),
                 env.get("PYTHONPATH", "")])
            env.pop("PYTEST_ADDOPTS", None)
            process = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "-o", "addopts=",
                 "-p", "pytest_reporter", str(suite), "--tb=long"],
                cwd=workspace, env=env, capture_output=True, text=True, timeout=120)
            result.update(returncode=process.returncode, stdout=process.stdout,
                          stderr=process.stderr)
            if not report_path.exists():
                raise RuntimeError("Pytest did not produce its evaluator report")
            report = json.loads(report_path.read_text(encoding="utf-8"))
        records = report["reports"]
        result["reports"] = records
        failures = [r for r in records if r["outcome"] == "failed"]
        failed_ids = {r["nodeid"] for r in failures}
        result["tests_failed"] = len(failed_ids)
        result["tests_passed"] = len({r["nodeid"] for r in records
            if r["phase"] == "call" and r["outcome"] == "passed"} - failed_ids)
        result["tests_skipped"] = len({r["nodeid"] for r in records if r["outcome"] == "skipped"})
        generated_paths = {str((workspace / name).resolve()) for name in generated_files}
        # Collection/setup errors are model failures only with provenance in a
        # generated source file. Otherwise conservatively exclude the run.
        unattributed = [r for r in failures
                        if not (r["phase"] != "collection" and r["assertion_failure"])
                        and not generated_paths.intersection(r["traceback_paths"])]
        if (not report["finished"] or report["internal_errors"] or unattributed
                or process.returncode not in (0, 1, 2)
                or (process.returncode != 0 and not failures)
                or (not failures and result["tests_passed"] == 0)):
            raise RuntimeError("Pytest infrastructure/collection/setup failure or no executed tests")
        result.update(passed=process.returncode == 0 and not failures, status="completed")
    except Exception as exc:
        result.update(passed=None, status="invalid_infrastructure")
        result["errors"].append(error_info("pytest", exc))
        if isinstance(exc, subprocess.TimeoutExpired):
            result["stdout"] = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            result["stderr"] = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    return result


def evaluate(
    workspace,
    source,
    before,
    generated_files,
    scorer,
    evaluation,
    artifact_before=None,
):
    def integrity():
        if evaluation["regression"]["regression_tests_modified"]:
            return False
        check = check_regression(workspace, before)
        evaluation["regression"].update(check)
        if check["regression_tests_modified"]:
            evaluation["regression"].update(passed=None, status="invalid_infrastructure")
            evaluation["regression"]["errors"].append({
                "stage": "regression_integrity", "type": "RegressionTestsModified",
                "message": "Protected evaluator files changed; regression outcome is untrusted"})
            return False
        return True

    def artifact_integrity(stage, gate):
        artifact = evaluation["artifact"]
        if artifact_before is None:
            return True
        if artifact["evaluated_artifact_modified"]:
            return False

        check = check_artifact(workspace, artifact_before)
        artifact.update(check)
        artifact["checks"].append({"stage": stage, **check})
        if check["evaluated_artifact_modified"]:
            error = {
                "stage": f"artifact_integrity_after_{stage}",
                "type": "EvaluatedArtifactModified",
                "message": (
                    "Evaluator execution changed the generated application artifact; "
                    "subsequent gate outcomes are untrusted"
                ),
            }
            artifact["errors"].append(error)
            evaluation[gate].update(passed=None, status="invalid_infrastructure")
            evaluation[gate]["errors"].append(error)
            return False
        return True

    if not integrity():
        return
    try:
        target = inject_target_tests(source, workspace)
    except Exception as exc:
        evaluation["target"].update(passed=None, status="invalid_infrastructure")
        evaluation["target"]["errors"].append(error_info("target_test_injection", exc))
        return
    evaluation["target"] = run_suite(workspace, target.resolve(), generated_files)
    if not artifact_integrity("target", "target"):
        return
    if integrity():
        regression = run_suite(workspace, (workspace / "tests").resolve(), generated_files)
        evaluation["regression"].update(regression)
        integrity()
        if not artifact_integrity("regression", "regression"):
            return
    try:
        convention = scorer(workspace)
        if not isinstance(convention, dict) or type(convention.get("passed")) is not bool:
            raise ValueError("Scorer must return a dictionary with a boolean passed field")
        evaluation["convention"] = {**convention, "status": "completed", "errors": []}
    except Exception as exc:
        evaluation["convention"] = {
            "passed": None, "status": "invalid_infrastructure",
            "errors": [error_info("convention", exc)]}
    integrity()
    artifact_integrity("convention", "convention")


def finalize(result):
    evaluation = result["evaluation"]
    artifact = evaluation["artifact"]
    valid = (
        not result["errors"]
        and not artifact["evaluated_artifact_modified"]
        and all(
            evaluation[gate]["status"] == "completed"
            for gate in ("target", "regression", "convention")
        )
    )
    result["run_status"] = "valid" if valid else "invalid_infrastructure"
    overall = all(evaluation[gate]["passed"] for gate in ("target", "regression", "convention")) if valid else None
    evaluation["overall_success"] = result["overall_success"] = overall
    result["evaluated_artifact_modified"] = artifact["evaluated_artifact_modified"]
    result["evaluated_artifact_changed_files"] = artifact["changed_files"]
    result["evaluated_artifact_missing_files"] = artifact["missing_files"]
    result["evaluated_artifact_added_files"] = artifact["added_files"]
    # Legacy audit aliases: 'tests' continue to mean repository regression tests.
    regression = evaluation["regression"]
    result.update(tests_passed=regression["passed"], test_returncode=regression["returncode"],
                  test_stdout=regression["stdout"], test_stderr=regression["stderr"],
                  convention_passed=evaluation["convention"]["passed"],
                  convention_result=evaluation["convention"])
