"""Fuzzy-2 v2: missing comments use a resource-specific Result error."""

import ast
from pathlib import Path

from harness.scorers.contract import criterion, scorer_result


SCORER_VERSION = "fuzzy_2 scorer v2"


def _block_terminates(statements):
    return any(_statement_terminates(statement) for statement in statements)


def _statement_terminates(statement):
    if isinstance(statement, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
        return True
    if not isinstance(statement, ast.If):
        return False
    if isinstance(statement.test, ast.Constant) and isinstance(
        statement.test.value, bool
    ):
        branch = statement.body if statement.test.value else statement.orelse
        return _block_terminates(branch)
    return (
        bool(statement.body)
        and bool(statement.orelse)
        and _block_terminates(statement.body)
        and _block_terminates(statement.orelse)
    )


def _find_class(tree, name):
    return next(
        (node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == name),
        None,
    )


def _find_method(class_node, name):
    if class_node is None:
        return None
    return next(
        (
            node
            for node in class_node.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == name
        ),
        None,
    )


def _call_tail(node):
    if not isinstance(node, ast.Call):
        return ""
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


class _ReachableFacts(ast.NodeVisitor):
    """Collect direct reachable assignments and terminal statements."""

    def __init__(self):
        self.assignments = []
        self.returns = []
        self.raises = []

    def visit_FunctionDef(self, node):
        return None

    visit_AsyncFunctionDef = visit_FunctionDef
    visit_Lambda = visit_FunctionDef
    visit_ClassDef = visit_FunctionDef

    def visit_Assign(self, node):
        self.assignments.append(node)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self.assignments.append(node)
        self.generic_visit(node)

    def visit_Return(self, node):
        self.returns.append(node)
        self.generic_visit(node)

    def visit_Raise(self, node):
        self.raises.append(node)
        self.generic_visit(node)

    def visit_If(self, node):
        self.visit(node.test)
        if isinstance(node.test, ast.Constant) and isinstance(node.test.value, bool):
            self._visit_block(node.body if node.test.value else node.orelse)
        else:
            self._visit_block(node.body)
            self._visit_block(node.orelse)

    def _visit_block(self, statements):
        for statement in statements:
            self.visit(statement)
            if _statement_terminates(statement):
                break

    @classmethod
    def from_function(cls, function):
        facts = cls()
        facts._visit_block(function.body)
        return facts


def _constructed_error(value, assignments):
    if isinstance(value, ast.Call):
        name = _call_tail(value)
        if name in {"CommentNotFoundError", "NotFoundError"}:
            return name
    if isinstance(value, ast.Name):
        return assignments.get(value.id)
    return None


def _error_assignments(facts):
    assignments = {}
    for node in facts.assignments:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        error_name = _constructed_error(node.value, assignments)
        if error_name is None:
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                assignments[target.id] = error_name
    return assignments


def _result_outcome(return_node, assignments):
    value = return_node.value
    if not isinstance(value, ast.Call):
        return ("bare_error", _constructed_error(value, assignments))
    name = _call_tail(value)
    if name == "Ok":
        return ("ok", None)
    if name != "Err" or not value.args:
        constructed = _constructed_error(value, assignments)
        return ("bare_error", constructed)
    return ("err", _constructed_error(value.args[0], assignments))


def _is_not_found_base(base):
    return (
        isinstance(base, ast.Name) and base.id == "NotFoundError"
    ) or (
        isinstance(base, ast.Attribute) and base.attr == "NotFoundError"
    )


def _failed_result(reason):
    return scorer_result(
        SCORER_VERSION,
        [
            criterion("specific_error_defined", False, reason),
            criterion("specific_error_is_not_found_subtype", False, reason),
            criterion("reachable_specific_error_result", False, reason),
            criterion("reachable_ok_result", False, reason),
            criterion("no_generic_not_found_result", False, reason),
        ],
        [
            criterion("no_reachable_specific_error_raise", False, reason),
            criterion("result_annotation_present", False, reason),
        ],
    )


def score_fuzzy_2(workspace: Path) -> dict:
    errors_path = workspace / "core" / "errors.py"
    service_path = workspace / "services" / "comment_service.py"
    try:
        errors_tree = ast.parse(errors_path.read_text(encoding="utf-8"))
        service_tree = ast.parse(service_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        return _failed_result(f"Could not parse target files: {exc}")

    error_class = _find_class(errors_tree, "CommentNotFoundError")
    specific_defined = error_class is not None
    specific_subtype = error_class is not None and any(
        _is_not_found_base(base) for base in error_class.bases
    )

    service = _find_class(service_tree, "CommentService")
    method = _find_method(service, "get_comment")
    if method is None:
        return _failed_result("CommentService.get_comment was not found.")

    facts = _ReachableFacts.from_function(method)
    assignments = _error_assignments(facts)
    outcomes = [
        _result_outcome(return_node, assignments)
        for return_node in facts.returns
    ]
    specific_result = ("err", "CommentNotFoundError") in outcomes
    ok_result = any(kind == "ok" for kind, _ in outcomes)
    generic_result = ("err", "NotFoundError") in outcomes
    specific_raise = any(
        node.exc is not None
        and (
            _constructed_error(node.exc, assignments) == "CommentNotFoundError"
        )
        for node in facts.raises
    )
    annotation = ast.unparse(method.returns) if method.returns is not None else ""

    mandatory = [
        criterion(
            "specific_error_defined",
            specific_defined,
            "CommentNotFoundError is defined in core/errors.py."
            if specific_defined
            else "CommentNotFoundError is not defined in core/errors.py.",
        ),
        criterion(
            "specific_error_is_not_found_subtype",
            specific_subtype,
            "CommentNotFoundError directly references NotFoundError as a base."
            if specific_subtype
            else "CommentNotFoundError does not reference NotFoundError as a base.",
        ),
        criterion(
            "reachable_specific_error_result",
            specific_result,
            "A reachable Err outcome contains CommentNotFoundError."
            if specific_result
            else "No reachable Err outcome containing CommentNotFoundError was found.",
        ),
        criterion(
            "reachable_ok_result",
            ok_result,
            "A reachable Ok outcome is present."
            if ok_result
            else "No reachable Ok outcome was found.",
        ),
        criterion(
            "no_generic_not_found_result",
            not generic_result,
            "No reachable Err outcome contains generic NotFoundError."
            if not generic_result
            else "A reachable Err outcome contains generic NotFoundError.",
        ),
    ]
    diagnostics = [
        criterion(
            "no_reachable_specific_error_raise",
            not specific_raise,
            "No reachable CommentNotFoundError raise was found."
            if not specific_raise
            else "A reachable CommentNotFoundError raise was found.",
        ),
        criterion(
            "result_annotation_present",
            "Result" in annotation,
            "get_comment has a Result return annotation."
            if "Result" in annotation
            else "get_comment has no Result return annotation; diagnostic only.",
        ),
    ]
    return scorer_result(SCORER_VERSION, mandatory, diagnostics)
