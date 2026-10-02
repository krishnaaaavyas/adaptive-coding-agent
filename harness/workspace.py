from pathlib import Path
import shutil
import subprocess
import uuid

from harness.isolation import is_design_path, is_git_metadata_path, require_model_path


def create_workspace(base_repo: Path) -> Path:
    require_model_path(base_repo)
    workspace_root = Path("workspaces")
    workspace_root.mkdir(exist_ok=True)

    workspace = workspace_root / str(uuid.uuid4())

    shutil.copytree(
        base_repo,
        workspace,
        ignore=lambda directory, names: _workspace_ignore(directory, names) | {
            name for name in names
            if (Path(directory) / name).resolve() == workspace_root.resolve()
        },
    )

    return workspace


def _workspace_ignore(directory, names):
    runtime = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", ".git")
    return set(runtime(directory, names)) | {
        name for name in names if is_design_path(Path(directory) / name)
        or is_git_metadata_path(Path(directory) / name)
    }


def run_tests(workspace: Path) -> dict:
    result = subprocess.run(
        ["python", "-m", "pytest", "-q"],
        cwd=workspace,
        capture_output=True,
        text=True,
        timeout=120,
    )

    return {
        "passed": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
