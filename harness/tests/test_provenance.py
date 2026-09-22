from datetime import datetime, timedelta
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import uuid

import pytest

from harness import provenance
from harness import run_experiment as runner
from harness.scorers.explicit_1 import (
    SCORER_VERSION,
    score_explicit_1,
)


def write_tree(root):
    root.mkdir(parents=True)
    (root / "a.txt").write_bytes(b"alpha\n")
    nested = root / "nested"
    nested.mkdir()
    (nested / "b.bin").write_bytes(b"beta\x00")


def git(root, *arguments):
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


@pytest.fixture
def git_repository(tmp_path):
    root = tmp_path / "repository"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.email", "tests@example.invalid")
    git(root, "config", "user.name", "Provenance Tests")
    (root / ".gitignore").write_text("*.ignored\n", encoding="utf-8")
    (root / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "fixture")
    return root


@pytest.fixture
def provenance_snapshot(git_repository):
    config = git_repository / "experiments" / "run.json"
    base = git_repository / "taskflow_base"
    regression = base / "tests"
    target = git_repository / "private_target"
    fixtures = git_repository / "fixtures"
    active_fixtures = fixtures / "explicit_1"
    protocol = git_repository / "PROTOCOL_V2.md"
    config.parent.mkdir()
    regression.mkdir(parents=True)
    target.mkdir()
    active_fixtures.mkdir(parents=True)
    config.write_text("{}\n", encoding="utf-8")
    (base / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    (regression / "test_app.py").write_text("assert True\n", encoding="utf-8")
    (target / "test_target.py").write_text("assert True\n", encoding="utf-8")
    (active_fixtures / "cases.json").write_text("{}\n", encoding="utf-8")
    protocol.write_text("protocol\n", encoding="utf-8")
    git(git_repository, "add", ".")
    git(git_repository, "commit", "-q", "-m", "provenance inputs")

    manifest = provenance.new_run_manifest()
    provenance.record_config(manifest, config, git_repository)
    arguments = {
        "repository_root": git_repository,
        "config_path": config,
        "base_repository": base,
        "scorer": score_explicit_1,
        "experiment": "explicit_1",
        "fixtures_root": fixtures,
        "target_tests": target,
        "protocol_document": protocol,
    }
    provenance.populate_run_manifest(manifest, **arguments)
    return {
        "manifest": manifest,
        "arguments": arguments,
        "repository": git_repository,
        "config": config,
        "base": base,
        "regression": regression,
        "target": target,
        "fixtures": active_fixtures,
        "protocol": protocol,
    }


def verify_snapshot(snapshot):
    return provenance.verify_run_manifest(
        snapshot["manifest"],
        **snapshot["arguments"],
    )


def mismatch_fields(exc_info):
    return {item["field"] for item in exc_info.value.mismatches}


def test_same_tree_has_same_hash(tmp_path):
    root = tmp_path / "tree"
    write_tree(root)

    assert provenance.tree_sha256(root) == provenance.tree_sha256(root)


def test_file_content_change_changes_tree_hash(tmp_path):
    root = tmp_path / "tree"
    write_tree(root)
    before = provenance.tree_sha256(root)

    (root / "a.txt").write_bytes(b"changed")

    assert provenance.tree_sha256(root) != before


def test_file_addition_changes_tree_hash(tmp_path):
    root = tmp_path / "tree"
    write_tree(root)
    before = provenance.tree_sha256(root)

    (root / "added.txt").write_bytes(b"added")

    assert provenance.tree_sha256(root) != before


def test_file_deletion_changes_tree_hash(tmp_path):
    root = tmp_path / "tree"
    write_tree(root)
    before = provenance.tree_sha256(root)

    (root / "a.txt").unlink()

    assert provenance.tree_sha256(root) != before


def test_path_rename_changes_tree_hash(tmp_path):
    root = tmp_path / "tree"
    write_tree(root)
    before = provenance.tree_sha256(root)

    (root / "a.txt").rename(root / "renamed.txt")

    assert provenance.tree_sha256(root) != before


def test_runtime_cache_changes_do_not_affect_tree_hash(tmp_path):
    root = tmp_path / "tree"
    write_tree(root)
    before = provenance.tree_sha256(root)

    for directory in ("__pycache__", ".pytest_cache"):
        cache = root / directory
        cache.mkdir()
        (cache / "state").write_bytes(b"one")
    (root / "module.pyc").write_bytes(b"one")
    after_add = provenance.tree_sha256(root)
    (root / "__pycache__" / "state").write_bytes(b"two")
    (root / "module.pyc").write_bytes(b"two")

    assert after_add == before
    assert provenance.tree_sha256(root) == before


def test_tree_encoding_uses_posix_relative_paths(tmp_path):
    root = tmp_path / "tree"
    nested = root / "nested"
    nested.mkdir(parents=True)
    content = b"content"
    (nested / "file.txt").write_bytes(content)

    relative = b"nested/file.txt"
    canonical = (
        b"provenance-tree-v1\0"
        + len(relative).to_bytes(8, "big")
        + relative
        + hashlib.sha256(content).digest()
    )

    assert provenance.tree_sha256(root) == hashlib.sha256(canonical).hexdigest()


def test_symlink_in_tree_is_rejected_where_supported(tmp_path):
    root = tmp_path / "tree"
    write_tree(root)
    link = root / "link.txt"
    try:
        link.symlink_to(root / "a.txt")
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is not available")

    with pytest.raises(provenance.ProvenanceError, match="symlink"):
        provenance.tree_sha256(root)


def test_empty_required_tree_is_rejected(tmp_path):
    root = tmp_path / "empty"
    root.mkdir()

    with pytest.raises(provenance.ProvenanceError, match="empty"):
        provenance.tree_sha256(root)


def test_clean_git_repository_and_exact_head_are_recorded(git_repository):
    state = provenance.inspect_git_repository(git_repository)

    assert state == {
        "git_commit": git(git_repository, "rev-parse", "HEAD"),
        "tracked_clean": True,
        "untracked_files": [],
    }


def test_unstaged_tracked_change_is_rejected(git_repository):
    (git_repository / "tracked.txt").write_text("modified\n", encoding="utf-8")
    manifest = provenance.new_run_manifest()

    with pytest.raises(provenance.ProvenanceError, match="tracked"):
        provenance.require_clean_git(git_repository, manifest)

    assert manifest["repository"]["tracked_clean"] is False


def test_staged_tracked_change_is_rejected(git_repository):
    (git_repository / "tracked.txt").write_text("staged\n", encoding="utf-8")
    git(git_repository, "add", "tracked.txt")

    with pytest.raises(provenance.ProvenanceError, match="tracked"):
        provenance.require_clean_git(
            git_repository,
            provenance.new_run_manifest(),
        )


def test_untracked_file_is_rejected(git_repository):
    (git_repository / "untracked.txt").write_text("new\n", encoding="utf-8")
    manifest = provenance.new_run_manifest()

    with pytest.raises(provenance.ProvenanceError, match="untracked"):
        provenance.require_clean_git(git_repository, manifest)

    assert manifest["repository"]["untracked_files"] == ["untracked.txt"]


def test_ignored_file_does_not_count(git_repository):
    (git_repository / "runtime.ignored").write_text("ignored\n", encoding="utf-8")

    state = provenance.inspect_git_repository(git_repository)

    assert state["tracked_clean"] is True
    assert state["untracked_files"] == []


def test_config_hash_uses_exact_bytes_and_whitespace(tmp_path):
    config = tmp_path / "experiment.json"
    config.write_bytes(b'{"value":1}\n')
    manifest = provenance.new_run_manifest()
    first = provenance.record_config(manifest, config, tmp_path)["sha256"]

    config.write_bytes(b'{ "value": 1 }\n')
    second = provenance.record_config(manifest, config, tmp_path)["sha256"]

    assert first == hashlib.sha256(b'{"value":1}\n').hexdigest()
    assert second == hashlib.sha256(b'{ "value": 1 }\n').hexdigest()
    assert first != second


def test_scorer_name_version_and_source_hash_are_recorded():
    metadata = provenance.declared_scorer_metadata(
        "explicit_1",
        score_explicit_1,
    )
    source = Path(__import__(score_explicit_1.__module__, fromlist=["x"]).__file__)

    assert metadata == {
        "name": "explicit_1",
        "version": SCORER_VERSION,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }


def test_only_active_scorer_fixture_tree_is_hashed(tmp_path):
    fixtures = tmp_path / "fixtures"
    active = fixtures / "explicit_1"
    other = fixtures / "explicit_2"
    active.mkdir(parents=True)
    other.mkdir()
    (active / "cases.json").write_text("{}\n", encoding="utf-8")
    (active / "case.py").write_text("VALUE = 1\n", encoding="utf-8")
    (other / "cases.json").write_text("{}\n", encoding="utf-8")
    before = provenance.fixture_tree_sha256(fixtures, "explicit_1")

    (other / "cases.json").write_text('{"changed": true}\n', encoding="utf-8")

    assert provenance.fixture_tree_sha256(fixtures, "explicit_1") == before


def test_manifest_records_target_regression_fixture_and_protocol_hashes(
    git_repository,
):
    config = git_repository / "experiments" / "run.json"
    base = git_repository / "taskflow_base"
    regression = base / "tests"
    target = git_repository / "private_target"
    fixtures = git_repository / "fixtures"
    active_fixtures = fixtures / "explicit_1"
    protocol = git_repository / "PROTOCOL_V2.md"
    config.parent.mkdir()
    regression.mkdir(parents=True)
    target.mkdir()
    active_fixtures.mkdir(parents=True)
    config.write_text("{}\n", encoding="utf-8")
    (base / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    (regression / "test_app.py").write_text("assert True\n", encoding="utf-8")
    (target / "test_target.py").write_text("assert True\n", encoding="utf-8")
    (active_fixtures / "cases.json").write_text("{}\n", encoding="utf-8")
    protocol.write_text("protocol\n", encoding="utf-8")
    git(git_repository, "add", ".")
    git(git_repository, "commit", "-q", "-m", "provenance inputs")

    manifest = provenance.new_run_manifest()
    provenance.record_config(manifest, config, git_repository)
    provenance.populate_run_manifest(
        manifest,
        repository_root=git_repository,
        config_path=config,
        base_repository=base,
        scorer=score_explicit_1,
        experiment="explicit_1",
        fixtures_root=fixtures,
        target_tests=target,
        protocol_document=protocol,
    )

    assert manifest["base_repository"]["tree_sha256"] == provenance.tree_sha256(base)
    assert manifest["scorer_validation"]["fixture_tree_sha256"] == (
        provenance.tree_sha256(active_fixtures)
    )
    assert manifest["target_tests"]["tree_sha256"] == provenance.tree_sha256(target)
    assert manifest["regression_tests"]["tree_sha256"] == provenance.tree_sha256(
        regression
    )
    assert manifest["protocol"] == {
        "evaluation_protocol": "v2",
        "protocol_document_sha256": provenance.file_sha256(protocol),
    }


def test_scorer_result_version_must_match_manifest(monkeypatch, tmp_path):
    def scorer(_workspace):
        return {"passed": True, "scorer_version": "wrong"}

    monkeypatch.setattr(runner, "get_scorer", lambda _experiment: scorer)

    with pytest.raises(provenance.ProvenanceError, match="version mismatch"):
        runner.score_convention("example", tmp_path, "expected")


def test_scorer_result_matching_manifest_version_passes(monkeypatch, tmp_path):
    expected = {"passed": True, "scorer_version": "expected"}

    def scorer(_workspace):
        return expected

    monkeypatch.setattr(runner, "get_scorer", lambda _experiment: scorer)

    assert runner.score_convention("example", tmp_path, "expected") is expected


def test_manifest_identity_values_are_uuid4_and_utc():
    manifest = provenance.new_run_manifest()
    run_id = uuid.UUID(manifest["run_id"])
    started = datetime.fromisoformat(manifest["started_at_utc"])

    assert run_id.version == 4
    assert started.utcoffset() == timedelta(0)


def test_unchanged_provenance_passes_final_verification(provenance_snapshot):
    assert verify_snapshot(provenance_snapshot) is True


def test_changed_config_fails_final_verification(provenance_snapshot):
    provenance_snapshot["config"].write_text("{ }\n", encoding="utf-8")

    with pytest.raises(provenance.ProvenanceIntegrityError) as exc_info:
        verify_snapshot(provenance_snapshot)

    assert "config.sha256" in mismatch_fields(exc_info)


def test_changed_base_source_fails_final_verification(provenance_snapshot):
    (provenance_snapshot["base"] / "app.py").write_text(
        "VALUE = 2\n",
        encoding="utf-8",
    )

    with pytest.raises(provenance.ProvenanceIntegrityError) as exc_info:
        verify_snapshot(provenance_snapshot)

    assert "base_repository.tree_sha256" in mismatch_fields(exc_info)


def test_changed_target_test_fails_final_verification(provenance_snapshot):
    (provenance_snapshot["target"] / "test_target.py").write_text(
        "assert False\n",
        encoding="utf-8",
    )

    with pytest.raises(provenance.ProvenanceIntegrityError) as exc_info:
        verify_snapshot(provenance_snapshot)

    assert "target_tests.tree_sha256" in mismatch_fields(exc_info)


def test_changed_regression_test_fails_final_verification(provenance_snapshot):
    (provenance_snapshot["regression"] / "test_app.py").write_text(
        "assert False\n",
        encoding="utf-8",
    )

    with pytest.raises(provenance.ProvenanceIntegrityError) as exc_info:
        verify_snapshot(provenance_snapshot)

    assert "regression_tests.tree_sha256" in mismatch_fields(exc_info)


def test_scorer_source_mismatch_without_editing_real_source(
    provenance_snapshot,
    monkeypatch,
):
    original = provenance.declared_scorer_metadata

    def mismatched_metadata(experiment, scorer):
        metadata = original(experiment, scorer)
        return {**metadata, "source_sha256": "0" * 64}

    monkeypatch.setattr(
        provenance,
        "declared_scorer_metadata",
        mismatched_metadata,
    )

    with pytest.raises(provenance.ProvenanceIntegrityError) as exc_info:
        verify_snapshot(provenance_snapshot)

    assert "scorer.source_sha256" in mismatch_fields(exc_info)


def test_changed_fixture_tree_fails_final_verification(provenance_snapshot):
    (provenance_snapshot["fixtures"] / "case.py").write_text(
        "VALUE = 1\n",
        encoding="utf-8",
    )

    with pytest.raises(provenance.ProvenanceIntegrityError) as exc_info:
        verify_snapshot(provenance_snapshot)

    assert "scorer_validation.fixture_tree_sha256" in mismatch_fields(exc_info)


def test_changed_protocol_document_fails_final_verification(provenance_snapshot):
    provenance_snapshot["protocol"].write_text(
        "changed protocol\n",
        encoding="utf-8",
    )

    with pytest.raises(provenance.ProvenanceIntegrityError) as exc_info:
        verify_snapshot(provenance_snapshot)

    assert "protocol.protocol_document_sha256" in mismatch_fields(exc_info)


def test_changed_git_head_fails_final_verification(provenance_snapshot):
    repository = provenance_snapshot["repository"]
    (repository / "tracked.txt").write_text("new commit\n", encoding="utf-8")
    git(repository, "add", "tracked.txt")
    git(repository, "commit", "-q", "-m", "move head")

    with pytest.raises(provenance.ProvenanceIntegrityError) as exc_info:
        verify_snapshot(provenance_snapshot)

    assert "repository.git_commit" in mismatch_fields(exc_info)


@pytest.mark.parametrize("change", ["tracked", "untracked"])
def test_changed_git_state_fails_final_verification(
    provenance_snapshot,
    change,
):
    repository = provenance_snapshot["repository"]
    if change == "tracked":
        (repository / "tracked.txt").write_text("dirty\n", encoding="utf-8")
        expected_field = "repository.tracked_clean"
    else:
        (repository / "new.txt").write_text("untracked\n", encoding="utf-8")
        expected_field = "repository.untracked_files"

    with pytest.raises(provenance.ProvenanceIntegrityError) as exc_info:
        verify_snapshot(provenance_snapshot)

    assert expected_field in mismatch_fields(exc_info)


def test_original_manifest_hashes_are_preserved_after_mismatch(
    provenance_snapshot,
):
    original_manifest = copy.deepcopy(provenance_snapshot["manifest"])
    provenance_snapshot["config"].write_text("{ }\n", encoding="utf-8")

    with pytest.raises(provenance.ProvenanceIntegrityError):
        verify_snapshot(provenance_snapshot)

    assert provenance_snapshot["manifest"] == original_manifest
