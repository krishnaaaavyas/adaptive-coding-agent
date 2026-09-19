from pathlib import Path
import shutil
import subprocess
import uuid


def create_workspace(base_repo: Path) -> Path:
    workspace_root = Path("workspaces")
    workspace_root.mkdir(exist_ok=True)

    workspace = workspace_root / str(uuid.uuid4())

    shutil.copytree(
        base_repo,
        workspace,
        ignore=shutil.ignore_patterns(
            "__pycache__",
            "*.pyc",
            ".pytest_cache",
        ),
    )

    return workspace


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