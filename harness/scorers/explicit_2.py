"""Explicit-2 v2: expected service outcomes use Result-style returns."""

import ast
from pathlib import Path

from harness.scorers.contract import criterion, scorer_result


SCORER_VERSION = "explicit_2 scorer v2"


def _call_name(node):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
    return None


def _return_outcomes(value):
    if isinstance(value, ast.IfExp):
        return _return_outcomes(value.body) + _return_outcomes(value.orelse)
    name = _call_name(value)
    return [name if name in {"Ok", "Err"} else "non_result"]


def _constant_bool(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    return None


def _block_outcomes(statements):
    outcomes = []
    can_continue = True
    for statement in statements:
        if not can_continue:
            break
        if isinstance(statement, ast.Return):
            outcomes.extend(_return_outcomes(statement.value))
            can_continue = False
        elif isinstance(statement, ast.Raise):
            outcomes.append("raise")
            can_continue = False
        elif isinstance(statement, ast.If):
            constant = _constant_bool(statement.test)
            if constant is True:
                branch_outcomes, branch_continues = _block_outcomes(statement.body)
            elif constant is False:
                branch_outcomes, branch_continues = _block_outcomes(statement.orelse)
            else:
                body_outcomes, body_continues = _block_outcomes(statement.body)
                else_outcomes, else_continues = _block_outcomes(statement.orelse)
                branch_outcomes = body_outcomes + else_outcomes
                branch_continues = body_continues or else_continues
            outcomes.extend(branch_outcomes)
            can_continue = branch_continues
    return outcomes, can_continue


def _find_delete_method(tree):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "ProjectService":
            return next(
                (
                    item
                    for item in node.body
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and item.name == "delete_project"
                ),
                None,
            )
    return None


def _failed_result(reason):
    return scorer_result(
        SCORER_VERSION,
        [
            criterion("reachable_err_outcome", False, reason),
            criterion("reachable_ok_outcome", False, reason),
            criterion("all_terminal_outcomes_use_result", False, reason),
        ],
        [
            criterion("no_reachable_raise", False, reason),
            criterion("explicit_result_annotation", False, reason),
        ],
    )


def score_explicit_2(workspace: Path) -> dict:
    path = workspace / "services" / "project_service.py"
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        return _failed_result(f"Could not parse target file: {exc}")

    method = _find_delete_method(tree)
    if method is None:
        return _failed_result("ProjectService.delete_project was not found.")

    outcomes, falls_through = _block_outcomes(method.body)
    reachable_err = "Err" in outcomes
    reachable_ok = "Ok" in outcomes
    all_result = (
        bool(outcomes)
        and not falls_through
        and all(outcome in {"Ok", "Err"} for outcome in outcomes)
    )
    no_raise = "raise" not in outcomes
    annotation = ast.unparse(method.returns) if method.returns is not None else ""

    mandatory = [
        criterion(
            "reachable_err_outcome",
            reachable_err,
            "A reachable terminal outcome returns Err."
            if reachable_err
            else "No reachable terminal outcome returns Err.",
        ),
        criterion(
            "reachable_ok_outcome",
            reachable_ok,
            "A reachable terminal outcome returns Ok."
            if reachable_ok
            else "No reachable terminal outcome returns Ok.",
        ),
        criterion(
            "all_terminal_outcomes_use_result",
            all_result,
            "All reachable terminal outcomes return Ok or Err."
            if all_result
            else "A reachable path raises, returns a non-Result value, or falls through.",
        ),
    ]
    diagnostics = [
        criterion(
            "no_reachable_raise",
            no_raise,
            "No reachable raise terminates delete_project."
            if no_raise
            else "A reachable raise terminates delete_project.",
        ),
        criterion(
            "explicit_result_annotation",
            "Result" in annotation,
            "delete_project has a Result return annotation."
            if "Result" in annotation
            else "delete_project has no Result return annotation; diagnostic only.",
        ),
    ]
    return scorer_result(SCORER_VERSION, mandatory, diagnostics)
