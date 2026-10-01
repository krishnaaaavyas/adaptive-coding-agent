"""Configuration, deterministic planning, and guarded execution workflows."""

import json
import os
from pathlib import Path

from . import filesystem
from .models import ActionResult, ActionType, SyncAction, SyncConfig, SyncPlan, SyncReport


def load_config(path: str | Path) -> SyncConfig:
    path = Path(path).absolute()
    with path.open(encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict) or set(data) - {"source", "destination", "delete_extra", "ignore"}:
        raise ValueError("Configuration must be an object with supported fields only")
    if not {"source", "destination", "delete_extra"} <= data.keys():
        raise ValueError("Configuration requires source, destination, and delete_extra")
    if any(not isinstance(data[key], str) or not data[key] for key in ("source", "destination")):
        raise ValueError("Source and destination must be nonempty path strings")
    patterns = data.get("ignore", [])
    if not isinstance(patterns, list):
        raise ValueError("ignore must be an array of glob patterns")
    return filesystem.validate_config(SyncConfig(
        path.parent / data["source"], path.parent / data["destination"],
        data["delete_extra"], patterns,
    ))


def create_plan(config: SyncConfig) -> SyncPlan:
    config = filesystem.validate_config(config)
    source = {entry.path: entry for entry in filesystem.scan(config.source, config.ignore)}
    destination = {entry.path: entry for entry in filesystem.scan(config.destination, config.ignore)}
    paths = source.keys() | destination.keys()
    if os.name == "nt" and len({path.casefold() for path in paths}) != len(paths):
        raise ValueError("Case-aliasing file paths are unsupported on Windows")
    actions = []
    for path in sorted(paths):
        src, dst = source.get(path), destination.get(path)
        if src is None:
            kind = ActionType.DELETE if config.delete_extra else ActionType.SKIP
        elif dst is None:
            kind = ActionType.COPY
        elif (src.size, src.sha256) == (dst.size, dst.sha256):
            kind = ActionType.SKIP
        else:
            kind = ActionType.UPDATE
        actions.append(SyncAction(kind, path, src, dst))
    return SyncPlan(config, actions)


def preview(config: SyncConfig) -> SyncPlan:
    """Read and plan only; this workflow never calls the executor."""
    return create_plan(config)


def execute(plan: SyncPlan) -> SyncReport:
    """Revalidate an approved plan, then stop at the first failure; no rollback."""
    try:
        config = filesystem.validate_config(plan.config)
        for action in plan.actions:
            if not isinstance(action, SyncAction) or not isinstance(action.kind, ActionType):
                raise ValueError("Plan contains an invalid action")
            filesystem.file_path(config.destination, action.path)
            filesystem.file_path(config.source, action.path)
        # Also checks delete opt-in, ignores, snapshots, action semantics, duplicates,
        # and ordering. A supplied plan must describe the actual configured state.
        if plan != create_plan(config):
            raise ValueError("Plan is invalid or filesystem state changed; preview again")
    except (OSError, ValueError, TypeError, AttributeError) as error:
        return SyncReport((ActionResult(None, str(error)),), len(plan.actions))

    results = []
    for index, action in enumerate(plan.actions):
        try:
            filesystem.validate_config(config)
            if (filesystem.read_entry(config.source, action.path) != action.source
                    or filesystem.read_entry(config.destination, action.path) != action.destination):
                raise ValueError("Filesystem state changed; preview again")
            if action.kind in (ActionType.COPY, ActionType.UPDATE):
                filesystem.write_file(config, action.path, action.source)
            elif action.kind == ActionType.DELETE:
                filesystem.delete_file(config, action.path)
            results.append(ActionResult(action))
        except (OSError, ValueError) as error:
            results.append(ActionResult(action, str(error)))
            return SyncReport(results, len(plan.actions) - index - 1)
    return SyncReport(results)


def run(config: SyncConfig) -> SyncReport:
    return execute(create_plan(config))
