from pathlib import Path
import os

from harness.isolation import is_design_path, is_git_metadata_path, require_model_path


def collect_context_files(repo_root: Path) -> list[str]:
    """Collect regular repository files while pruning researcher-only trees."""
    require_model_path(repo_root)
    files = []
    for directory, dirs, names in os.walk(repo_root, followlinks=False):
        dirs[:] = [name for name in dirs
                   if not is_git_metadata_path(Path(directory) / name)
                   and not is_design_path(Path(directory) / name)]
        for name in names:
            path = Path(directory) / name
            if (path.is_file() and not is_git_metadata_path(path)
                    and not is_design_path(path)):
                files.append(path.relative_to(repo_root).as_posix())
    return sorted(files)


def build_context(repo_root: Path, files: list[str]) -> str:
    require_model_path(repo_root)
    sections = []

    for relative_path in files:
        require_model_path(relative_path)
        path = repo_root / relative_path
        require_model_path(path)

        if not path.exists():
            raise FileNotFoundError(f"Context file not found: {relative_path}")

        content = path.read_text(encoding="utf-8")

        sections.append(
            f"### FILE: {relative_path}\n"
            f"```python\n{content}\n```"
        )

    return "\n\n".join(sections)
