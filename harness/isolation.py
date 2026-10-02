"""Deterministic researcher-only path policy, independent of Git tracking."""

from pathlib import Path


DESIGN_DIRECTORY = "benchmark_design"


def is_design_path(path) -> bool:
    """Check lexical components and resolved origins (including symlink aliases)."""
    normalized = str(path).replace("\\", "/")
    parts = normalized.split("/")
    if any(part.casefold().rstrip(" .") == DESIGN_DIRECTORY for part in parts):
        return True
    resolved = Path(normalized).resolve()
    return any(part.casefold().rstrip(" .") == DESIGN_DIRECTORY
               for part in resolved.parts)


def is_git_metadata_path(path) -> bool:
    # Git objects/index/history can contain tracked researcher artifacts.
    normalized = Path(str(path).replace("\\", "/"))
    return any(part.casefold() == '.git'
               for candidate in (normalized, normalized.resolve())
               for part in candidate.parts)


def require_model_path(path) -> None:
    if is_design_path(path):
        raise ValueError(f"Researcher-only benchmark_design path is forbidden: {path}")
    if is_git_metadata_path(path):
        raise ValueError(f"Git metadata is forbidden as model material: {path}")
