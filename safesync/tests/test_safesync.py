import json
import os
import subprocess
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from safesync import (
    ActionType, SyncAction, SyncConfig, SyncPlan, create_plan, execute,
    load_config, preview, run,
)
from safesync.__main__ import main


@pytest.fixture
def config(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    return SyncConfig(source, destination)


def put(root, path, content):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return target


def snapshot(root):
    return tuple((p.relative_to(root).as_posix(), p.stat().st_mtime_ns,
                  p.read_bytes() if p.is_file() else None)
                 for p in sorted(root.rglob("*")))


def make_link(link, target, directory=False):
    try:
        link.symlink_to(target, target_is_directory=directory)
    except OSError as error:
        pytest.skip(f"Host cannot create symbolic links: {error}")


def test_empty(config):
    assert preview(config).actions == ()
    assert run(config).as_dict() == {
        "copied": 0, "updated": 0, "deleted": 0, "skipped": 0,
        "failed": 0, "unattempted": 0, "failures": [],
    }


def test_copy_nested_and_source_unchanged(config):
    put(config.source, "deep/nested/file.txt", b"payload")
    before = snapshot(config.source)
    plan = create_plan(config)
    assert [(a.kind, a.path) for a in plan.actions] == [
        (ActionType.COPY, "deep/nested/file.txt")]
    report = execute(plan)
    assert report.copied == 1 and report.failed == 0
    assert (config.destination / "deep/nested/file.txt").read_bytes() == b"payload"
    assert snapshot(config.source) == before


def test_update_uses_hash_not_timestamp_or_size(config):
    source = put(config.source, "file", b"new")
    destination = put(config.destination, "file", b"old")
    os.utime(source, ns=(1234567890000000000, 1234567890000000000))
    os.utime(destination, ns=(1234567890000000000, 1234567890000000000))
    plan = preview(config)
    action, = plan.actions
    assert action.source.size == action.destination.size
    assert action.source.sha256 != action.destination.sha256
    assert action.kind == ActionType.UPDATE
    assert execute(plan).updated == 1
    assert destination.read_bytes() == b"new"


def test_identical_skip_despite_timestamp(config):
    put(config.source, "file", b"same")
    destination = put(config.destination, "file", b"same")
    os.utime(destination, ns=(1234567890000000000, 1234567890000000000))
    before = snapshot(config.destination)
    assert preview(config).actions[0].kind == ActionType.SKIP
    assert run(config).skipped == 1
    assert snapshot(config.destination) == before


@pytest.mark.parametrize("delete", [False, True])
def test_destination_only(config, delete):
    destination = put(config.destination, "extra", b"keep unless opted in")
    config = replace(config, delete_extra=delete)
    before = snapshot(config.destination)
    assert preview(config).actions[0].kind == (ActionType.DELETE if delete else ActionType.SKIP)
    report = run(config)
    assert report.deleted == int(delete)
    assert report.skipped == int(not delete)
    if delete:
        assert not destination.exists()
    else:
        assert snapshot(config.destination) == before


def test_preview_zero_mutation_and_absent_destination(config):
    put(config.source, "file", b"new")
    put(config.destination, "file", b"old")
    put(config.destination, "extra", b"extra")
    config = replace(config, delete_extra=True)
    before = snapshot(config.source), snapshot(config.destination)
    assert [a.kind for a in preview(config).actions] == [ActionType.DELETE, ActionType.UPDATE]
    assert (snapshot(config.source), snapshot(config.destination)) == before
    absent = config.destination.parent / "not-created"
    assert preview(replace(config, destination=absent)).actions[0].kind == ActionType.COPY
    assert not absent.exists()


def test_missing_destination_created_only_by_run(config):
    put(config.source, "file", b"value")
    config = replace(config, destination=config.destination / "new" / "root")
    report = run(config)
    assert report.copied == 1
    assert (config.destination / "file").read_bytes() == b"value"


def test_ignore_patterns_preserve_both_sides(config):
    for path in ("cache/data", "nested/file.tmp", "visible"):
        put(config.source, path, b"source")
    for path in ("cache/extra", "nested/extra.tmp"):
        put(config.destination, path, b"destination")
    config = replace(config, delete_extra=True, ignore=["cache", "*.tmp"])
    before = snapshot(config.source)
    assert [a.path for a in preview(config).actions] == ["visible"]
    assert run(config).copied == 1
    assert not (config.destination / "cache/data").exists()
    assert (config.destination / "cache/extra").read_bytes() == b"destination"
    assert (config.destination / "nested/extra.tmp").exists()
    assert snapshot(config.source) == before


def test_deterministic_plan(config):
    for name in ("z", "sub/b", "a", "sub/a"):
        put(config.source, name, name.encode())
    plan = preview(config)
    assert plan == preview(config)
    assert [a.path for a in plan.actions] == ["a", "sub/a", "sub/b", "z"]
    # Recreate payloads in a different insertion order, with different timestamps.
    for name in ("a", "sub/a", "sub/b", "z"):
        path = config.source / name
        path.unlink()
        put(config.source, name, name.encode())
    assert plan == preview(config)


@pytest.mark.parametrize("bad", [
    "../outside", "nested/../../outside", "/outside", "C:/outside",
    "C:outside", "\\\\server\\share\\outside", "nested\\..\\outside",
    "", ".", "a//b", "a/./b", "file:stream", "NUL", "trailing.", "trailing ",
])
@pytest.mark.parametrize("kind", [ActionType.COPY, ActionType.UPDATE, ActionType.DELETE])
def test_malicious_paths_cannot_mutate(config, bad, kind):
    outside = put(config.source.parent, "outside", b"untouched")
    put(config.source, "legitimate", b"new")
    before = snapshot(config.source), snapshot(config.destination)
    plan = SyncPlan(config, [SyncAction(kind, bad)])
    report = execute(plan)
    assert report.failed == 1
    assert report.copied == report.updated == report.deleted == 0
    assert outside.read_bytes() == b"untouched"
    assert (snapshot(config.source), snapshot(config.destination)) == before


def test_absolute_source_target_rejected(config):
    source = put(config.source, "protected", b"source")
    report = execute(SyncPlan(config, [SyncAction(ActionType.DELETE, str(source))]))
    assert report.failed == 1
    assert source.read_bytes() == b"source"


@pytest.mark.parametrize("tamper", ["delete", "ignore", "duplicate", "wrong_kind", "wrong_entry", "omit"])
def test_plan_semantics_cannot_be_bypassed(config, tamper):
    put(config.source, "file", b"new")
    put(config.destination, "extra", b"preserved")
    plan = create_plan(config)
    actions = list(plan.actions)
    if tamper == "delete":
        actions[0] = replace(actions[0], kind=ActionType.DELETE)
    elif tamper == "ignore":
        plan = replace(plan, config=replace(config, ignore=["file"]))
    elif tamper == "duplicate":
        actions.append(actions[-1])
    elif tamper == "wrong_kind":
        actions[-1] = replace(actions[-1], kind="COPY")
    elif tamper == "wrong_entry":
        actions[-1] = replace(actions[-1], source=replace(actions[-1].source, sha256="bogus"))
    else:
        actions.pop()
    before = snapshot(config.source), snapshot(config.destination)
    report = execute(replace(plan, actions=actions))
    assert report.failed == 1
    assert (snapshot(config.source), snapshot(config.destination)) == before


def test_invalid_action_after_valid_action_is_preflighted(config):
    put(config.source, "a", b"payload")
    plan = create_plan(config)
    report = execute(replace(plan, actions=plan.actions + (SyncAction(ActionType.DELETE, "../outside"),)))
    assert report.failed == 1 and report.copied == 0
    assert not (config.destination / "a").exists()


def test_stale_plan_is_rejected(config):
    put(config.source, "file", b"old")
    plan = preview(config)
    put(config.source, "file", b"changed")
    report = execute(plan)
    assert report.failed == 1 and report.copied == 0
    assert not (config.destination / "file").exists()


def test_stale_delete_plan_preserves_changed_destination(config):
    put(config.destination, "extra", b"old")
    plan = preview(replace(config, delete_extra=True))
    put(config.destination, "extra", b"changed")
    report = execute(plan)
    assert report.failed == 1 and report.deleted == 0
    assert (config.destination / "extra").read_bytes() == b"changed"


@pytest.mark.parametrize("relationship", ["same", "destination_inside", "source_inside"])
def test_unsafe_roots(config, relationship):
    if relationship == "same":
        config = replace(config, destination=config.source)
    elif relationship == "destination_inside":
        config = replace(config, destination=config.source / "backup")
    else:
        nested = config.destination / "source"
        nested.mkdir()
        config = replace(config, source=nested)
    with pytest.raises(ValueError, match="non-nested"):
        preview(config)
    assert execute(SyncPlan(config, ())).failed == 1


@pytest.mark.parametrize("side", ["source", "destination"])
@pytest.mark.parametrize("directory", [False, True])
def test_symlinks_rejected(config, side, directory):
    outside = config.source.parent / "external"
    if directory:
        outside.mkdir()
        put(outside, "file", b"external")
    else:
        outside.write_bytes(b"external")
    make_link(getattr(config, side) / "link", outside, directory)
    with pytest.raises(ValueError, match="unsupported"):
        preview(config)


def test_dangling_ignored_link_rejected(config):
    make_link(config.source / "ignored", config.source.parent / "absent")
    with pytest.raises(ValueError, match="unsupported"):
        preview(replace(config, ignore=["ignored"]))


def test_symlink_inserted_after_preview(config):
    put(config.source, "folder/file", b"source")
    plan = preview(config)
    outside = config.source.parent / "external"
    outside.mkdir()
    make_link(config.destination / "folder", outside, True)
    assert execute(plan).failed == 1
    assert list(outside.iterdir()) == []


def test_root_and_ancestor_symlink_rejected(config):
    alias = config.source.parent / "alias"
    make_link(alias, config.source, True)
    with pytest.raises(ValueError, match="unsupported"):
        preview(replace(config, source=alias))
    with pytest.raises(ValueError, match="unsupported"):
        preview(replace(config, destination=alias / "new"))


def test_destination_hardlink_update_does_not_change_source(config):
    protected = put(config.source, "protected", b"original")
    put(config.source, "target", b"replacement")
    try:
        os.link(protected, config.destination / "target")
    except OSError as error:
        pytest.skip(f"Host cannot create hard links: {error}")
    before = snapshot(config.source)
    report = run(config)
    assert report.updated == 1 and report.failed == 0
    assert snapshot(config.source) == before
    assert (config.destination / "target").read_bytes() == b"replacement"


def test_real_filesystem_failure_stops_and_reports(config):
    put(config.source, "a/file", b"cannot copy")
    put(config.source, "z", b"not attempted")
    put(config.destination, "a", b"directory blocker")
    # Preflight detects the path conflict before any writes.
    report = run(config)
    assert report.failed == 1
    assert report.copied == report.updated == report.deleted == 0
    assert not (config.destination / "z").exists()
    assert (config.destination / "a").read_bytes() == b"directory blocker"


def test_operation_failure_is_not_success(config, monkeypatch):
    put(config.source, "a", b"first")
    put(config.source, "b", b"second")
    import safesync.filesystem as filesystem
    original_replace = filesystem.os.replace

    def fail_second(source, destination):
        if destination.name == "b":
            raise PermissionError("replacement denied")
        original_replace(source, destination)

    monkeypatch.setattr(filesystem.os, "replace", fail_second)
    report = run(config)
    assert report.copied == 1 and report.failed == 1
    assert report.updated == report.deleted == 0
    assert report.as_dict()["failures"] == [{"path": "b", "error": "replacement denied"}]
    assert (config.destination / "a").read_bytes() == b"first"
    assert not (config.destination / "b").exists()
    assert not list(config.destination.glob(".safesync-*"))


def test_report_counts_all_actions(config):
    put(config.source, "copy", b"new")
    put(config.source, "update", b"new")
    put(config.destination, "update", b"old")
    put(config.source, "skip", b"same")
    put(config.destination, "skip", b"same")
    put(config.destination, "delete", b"extra")
    report = run(replace(config, delete_extra=True))
    assert (report.copied, report.updated, report.deleted, report.skipped, report.failed) == (1, 1, 1, 1, 0)
    assert report.unattempted == 0


def test_public_values_are_immutable_and_defensively_copy_lists(config):
    patterns = ["*.tmp"]
    config = replace(config, ignore=patterns)
    patterns.append("*")
    assert config.ignore == ("*.tmp",)
    put(config.source, "file", b"value")
    plan = preview(config)
    actions = list(plan.actions)
    copied_plan = replace(plan, actions=actions)
    actions.clear()
    assert copied_plan == plan
    for value, field, replacement in (
        (config, "destination", config.source), (plan, "actions", ()),
        (plan.actions[0], "path", "../outside"),
        (plan.actions[0].source, "sha256", "changed"),
    ):
        with pytest.raises(FrozenInstanceError):
            setattr(value, field, replacement)
    report = execute(plan)
    with pytest.raises(FrozenInstanceError):
        report.results = ()


def test_json_config_and_cli_preview_run(config, capsys):
    put(config.source, "file", b"payload")
    path = config.source.parent / "config.json"
    path.write_text(json.dumps({"source": "source", "destination": "destination",
                               "delete_extra": False, "ignore": []}))
    assert load_config(path) == config
    before = snapshot(config.source), snapshot(config.destination)
    assert main(["preview", str(path)]) == 0
    assert json.loads(capsys.readouterr().out) == {"actions": [{"type": "COPY", "path": "file"}]}
    assert (snapshot(config.source), snapshot(config.destination)) == before
    assert main(["run", str(path)]) == 0
    assert json.loads(capsys.readouterr().out)["copied"] == 1
    assert (config.destination / "file").read_bytes() == b"payload"


@pytest.mark.parametrize("data", [
    {}, [], {"source": "source", "destination": "destination"},
    {"source": "source", "destination": "destination", "delete_extra": "false"},
    {"source": "source", "destination": "destination", "delete_extra": False, "ignore": "*"},
    {"source": "source", "destination": "destination", "delete_extra": False, "unknown": 1},
])
def test_invalid_configuration(config, data):
    path = config.source.parent / "config.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_config(path)


def test_cli_error_exit(config, capsys):
    assert main(["preview", str(config.source.parent / "missing.json")]) == 1
    assert "safesync:" in capsys.readouterr().err


def test_module_cli_entrypoint(config):
    path = config.source.parent / "config.json"
    path.write_text(json.dumps({"source": "source", "destination": "destination", "delete_extra": False}))
    result = subprocess.run([sys.executable, "-B", "-m", "safesync", "preview", str(path)],
                            cwd=Path(__file__).resolve().parents[2], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"actions": []}


@pytest.mark.skipif(os.name != "nt", reason="Windows case-insensitive filesystem policy")
def test_windows_case_aliases_rejected(config):
    put(config.source, "File", b"source")
    put(config.destination, "file", b"destination")
    before = snapshot(config.source), snapshot(config.destination)
    with pytest.raises(ValueError, match="Case-aliasing"):
        preview(replace(config, delete_extra=True))
    assert (snapshot(config.source), snapshot(config.destination)) == before


@pytest.mark.skipif(os.name != "nt", reason="Windows junction policy")
@pytest.mark.parametrize("placement", ["source", "destination", "after_preview"])
def test_windows_junctions_rejected(config, placement):
    outside = config.source.parent / "external"
    outside.mkdir()
    protected = put(outside, "file", b"external")
    put(config.source, "folder/file", b"source")
    if placement == "after_preview":
        plan = preview(config)
    root = config.source if placement == "source" else config.destination
    junction = root / "junction"
    result = subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(outside)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    try:
        if placement == "after_preview":
            assert execute(plan).failed == 1
        else:
            with pytest.raises(ValueError, match="unsupported"):
                preview(config)
        assert protected.read_bytes() == b"external"
        assert len(list(outside.iterdir())) == 1
    finally:
        # rmdir removes the junction itself, without traversing its target.
        os.rmdir(junction)


def test_fail_fast_reports_unattempted(config, monkeypatch):
    put(config.source, "a", b"first")
    put(config.source, "b", b"second")
    import safesync.filesystem as filesystem

    def denied(source, destination):
        raise PermissionError("denied")

    monkeypatch.setattr(filesystem.os, "replace", denied)
    report = run(config)
    assert report.failed == 1 and report.unattempted == 1
    assert report.copied == 0
    assert list(config.destination.iterdir()) == []


def test_cli_reports_failed_run(config, capsys):
    put(config.source, "a/file", b"source")
    put(config.destination, "a", b"blocker")
    path = config.source.parent / "config.json"
    path.write_text(json.dumps({"source": "source", "destination": "destination", "delete_extra": False}))
    assert main(["run", str(path)]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["failed"] == 1 and report["copied"] == 0
