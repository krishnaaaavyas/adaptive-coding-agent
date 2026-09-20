from pathlib import Path

import pytest

from harness.run_experiment import (
    apply_multi_file_generation,
    get_target_files,
    parse_multi_file_generation,
)


TARGETS = ["core/errors.py", "services/comment_service.py"]


def test_valid_two_file_response(tmp_path: Path):
    existing = tmp_path / "core/errors.py"
    existing.parent.mkdir(parents=True)
    existing.write_text("original errors\n", encoding="utf-8")
    generation = (
        "=== FILE: core/errors.py ===\n"
        "class CommentError(Exception):\n"
        "    pass\n"
        "=== FILE: services/comment_service.py ===\n"
        "from core.errors import CommentError\n"
    )

    originals, applied = apply_multi_file_generation(
        tmp_path,
        TARGETS,
        generation,
    )

    assert originals == {
        "core/errors.py": "original errors\n",
        "services/comment_service.py": None,
    }
    assert applied == {
        "core/errors.py": "class CommentError(Exception):\n    pass\n",
        "services/comment_service.py": "from core.errors import CommentError\n",
    }
    assert (tmp_path / "core/errors.py").read_text(encoding="utf-8") == applied[
        "core/errors.py"
    ]
    assert (tmp_path / "services/comment_service.py").read_text(
        encoding="utf-8"
    ) == applied["services/comment_service.py"]


def test_missing_requested_file():
    generation = "=== FILE: core/errors.py ===\ncontent\n"

    with pytest.raises(ValueError, match="Missing requested file"):
        parse_multi_file_generation(generation, TARGETS)


def test_unexpected_file():
    generation = (
        "=== FILE: core/errors.py ===\ncontent\n"
        "=== FILE: services/other.py ===\ncontent\n"
    )

    with pytest.raises(ValueError, match="Unexpected file section"):
        parse_multi_file_generation(generation, TARGETS)


def test_duplicate_file():
    generation = (
        "=== FILE: core/errors.py ===\nfirst\n"
        "=== FILE: core/errors.py ===\nsecond\n"
    )

    with pytest.raises(ValueError, match="Duplicate file section"):
        parse_multi_file_generation(generation, TARGETS)


def test_path_traversal_attempt():
    generation = "=== FILE: ../outside.py ===\ncontent\n"

    with pytest.raises(ValueError, match=r"cannot contain '\.\.'"):
        parse_multi_file_generation(generation, TARGETS)


@pytest.mark.parametrize(
    "absolute_path",
    ["/tmp/outside.py", r"C:\temp\outside.py"],
)
def test_absolute_path_attempt(absolute_path: str):
    generation = f"=== FILE: {absolute_path} ===\ncontent\n"

    with pytest.raises(ValueError, match="must be relative"):
        parse_multi_file_generation(generation, TARGETS)


def test_malformed_output_does_not_change_any_target(tmp_path: Path):
    existing = tmp_path / "core/errors.py"
    existing.parent.mkdir(parents=True)
    existing.write_text("original\n", encoding="utf-8")
    generation = "=== FILE: core/errors.py ===\nreplacement\n"

    with pytest.raises(ValueError, match="Missing requested file"):
        apply_multi_file_generation(tmp_path, TARGETS, generation)

    assert existing.read_text(encoding="utf-8") == "original\n"
    assert not (tmp_path / "services/comment_service.py").exists()


def test_config_requires_exactly_one_target_form():
    with pytest.raises(ValueError, match="exactly one"):
        get_target_files({})

    with pytest.raises(ValueError, match="exactly one"):
        get_target_files(
            {
                "target_file": "core/errors.py",
                "target_files": TARGETS,
            }
        )
