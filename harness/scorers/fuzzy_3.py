"""Fuzzy-3 v2: structural centralization of repeated normalization."""

import ast
from pathlib import Path

from harness.scorers.contract import criterion, scorer_result


SCORER_VERSION = "fuzzy_3 scorer v2"
CASE_OPERATIONS = {"lower", "casefold"}
WHITESPACE_OPERATIONS = {"strip", "lstrip", "rstrip"}


class _ExecutableCalls(ast.NodeVisitor):
    """Collect potentially reachable calls without descending nested callables."""

    def __init__(self):
        self.calls = []

    def visit_FunctionDef(self, node):
        return None

    visit_AsyncFunctionDef = visit_FunctionDef
    visit_Lambda = visit_FunctionDef
    visit_ClassDef = visit_FunctionDef

    def visit_Call(self, node):
        self.calls.append(node)
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
            if isinstance(statement, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                break

    @classmethod
    def from_function(cls, function):
        visitor = cls()
        visitor._visit_block(function.body)
        return visitor.calls


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


def _operation_name(call):
    return call.func.attr if isinstance(call.func, ast.Attribute) else None


def _contains_meaningful_normalization(function):
    operations = {
        name
        for call in _ExecutableCalls.from_function(function)
        if (name := _operation_name(call)) is not None
    }
    return bool(operations & CASE_OPERATIONS) and bool(
        operations & WHITESPACE_OPERATIONS
    )


def _defined_normalizers(tree, service):
    definitions = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            definitions[("module", node.name)] = node
    if service is not None:
        for node in service.body:
            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name not in {"create_comment", "edit_comment"}
            ):
                definitions[("method", node.name)] = node
    return {
        identity: function
        for identity, function in definitions.items()
        if _contains_meaningful_normalization(function)
    }


def _resolved_calls(function, definitions):
    if function is None:
        return set()
    identities = set()
    for call in _ExecutableCalls.from_function(function):
        if isinstance(call.func, ast.Name):
            identity = ("module", call.func.id)
        elif (
            isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id in {"self", "cls", "CommentService"}
        ):
            identity = ("method", call.func.attr)
        else:
            continue
        if identity in definitions:
            identities.add(identity)
    return identities


def _inline_normalization(function):
    if function is None:
        return False
    operations = {
        name
        for call in _ExecutableCalls.from_function(function)
        if (name := _operation_name(call)) is not None
    }
    return bool(operations & CASE_OPERATIONS) and bool(
        operations & WHITESPACE_OPERATIONS
    )


def _failed_result(reason):
    return scorer_result(
        SCORER_VERSION,
        [
            criterion("normalization_implementation", False, reason),
            criterion("same_callable_identity", False, reason),
            criterion("centralized_without_reimplementation", False, reason),
        ],
        [
            criterion("relevant_operations_present", False, reason),
            criterion("private_helper", False, reason),
            criterion("single_shared_callable", False, reason),
        ],
    )


def score_fuzzy_3(workspace: Path) -> dict:
    path = workspace / "services" / "comment_service.py"
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        return _failed_result(f"Could not parse target file: {exc}")

    service = _find_class(tree, "CommentService")
    if service is None:
        return _failed_result("CommentService was not found.")

    create = _find_method(service, "create_comment")
    edit = _find_method(service, "edit_comment")
    definitions = _defined_normalizers(tree, service)
    create_calls = _resolved_calls(create, definitions)
    edit_calls = _resolved_calls(edit, definitions)
    shared = create_calls & edit_calls
    separately_used = (create_calls | edit_calls) - shared
    inline = _inline_normalization(create) or _inline_normalization(edit)

    mandatory = [
        criterion(
            "normalization_implementation",
            bool(definitions),
            (
                "A callable containing whitespace and case normalization exists."
                if definitions
                else "No callable contains both whitespace and case normalization."
            ),
        ),
        criterion(
            "same_callable_identity",
            bool(shared),
            (
                "create_comment and edit_comment reference the same normalization "
                f"callable: {sorted(shared)}."
                if shared
                else "The two operations do not reference one shared normalization callable."
            ),
        ),
        criterion(
            "centralized_without_reimplementation",
            bool(shared) and not separately_used and not inline,
            (
                "Normalization is centralized without inline or separate helper copies."
                if shared and not separately_used and not inline
                else "Inline normalization or separately used normalization helpers remain."
            ),
        ),
    ]
    private_shared = any(
        kind == "method" and name.startswith("_") for kind, name in shared
    )
    diagnostics = [
        criterion(
            "relevant_operations_present",
            create is not None and edit is not None,
            "Both relevant operations are present."
            if create is not None and edit is not None
            else "One or both relevant operations are missing.",
        ),
        criterion(
            "private_helper",
            private_shared,
            "The shared callable is a private method."
            if private_shared
            else "The shared callable is not a private method; this is diagnostic only.",
        ),
        criterion(
            "single_shared_callable",
            len(shared) == 1,
            "Exactly one shared normalization callable is used."
            if len(shared) == 1
            else f"Detected {len(shared)} shared normalization callables.",
        ),
    ]
    return scorer_result(SCORER_VERSION, mandatory, diagnostics)
