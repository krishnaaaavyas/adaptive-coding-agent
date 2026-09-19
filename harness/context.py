from pathlib import Path


def build_context(repo_root: Path, files: list[str]) -> str:
    sections = []

    for relative_path in files:
        path = repo_root / relative_path

        if not path.exists():
            raise FileNotFoundError(f"Context file not found: {relative_path}")

        content = path.read_text(encoding="utf-8")

        sections.append(
            f"### FILE: {relative_path}\n"
            f"```python\n{content}\n```"
        )

    return "\n\n".join(sections)