"""Fuzzy-1 v2: comment validation is extracted into a private helper."""

import ast
from pathlib import Path

from harness.scorers.contract import criterion, scorer_result


SCORER_VERSION = "fuzzy_1 scorer v2"


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


class _ReachableFacts(ast.NodeVisitor):
    """Collect narrow reachable facts without descending nested callables."""

    def __init__(self):
        self.calls = []
        self.assignments = []
        self.ifs = []
        self.returns = []
        self.raises = []

    def visit_FunctionDef(self, node):
        return None

    visit_AsyncFunctionDef = visit_FunctionDef
    visit_Lambda = visit_FunctionDef
    visit_ClassDef = visit_FunctionDef

    def visit_Call(self, node):
        self.calls.append(node)
        self.generic_visit(node)

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
        self.ifs.append(node)
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


def _call_tail(node):
    if not isinstance(node, ast.Call):
        return ""
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


def _helper_identity(call):
    if (
        isinstance(call.func, ast.Attribute)
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id in {"self", "cls", "CommentService"}
    ):
        return call.func.attr
    return None


def _is_content_value(node):
    if isinstance(node, ast.Name):
        return node.id == "content"
    if isinstance(node, ast.Attribute):
        return node.attr == "content"
    if isinstance(node, ast.Subscript):
        value = node.slice
        return isinstance(value, ast.Constant) and value.value == "content"
    return False


def _is_stripped_content(node):
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "strip"
        and _is_content_value(node.func.value)
    )


def _contains_nonblank_content_predicate(node):
    for child in ast.walk(node):
        if isinstance(child, ast.UnaryOp) and isinstance(child.op, ast.Not):
            if _is_stripped_content(child.operand):
                return True
        if isinstance(child, ast.Compare):
            values = [child.left, *child.comparators]
            if any(_is_stripped_content(value) for value in values) and any(
                isinstance(value, ast.Constant) and value.value == ""
                for value in values
            ):
                return True
    return False


def _meaningful_content_validation(function):
    facts = _ReachableFacts.from_function(function)
    return any(_contains_nonblank_content_predicate(node.test) for node in facts.ifs) or any(
        return_node.value is not None
        and _contains_nonblank_content_predicate(return_node.value)
        for return_node in facts.returns
    )


def _names_in(node):
    return {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}


def _calls_helper(node, helper_names):
    return any(
        (identity := _helper_identity(child)) is not None and identity in helper_names
        for child in ast.walk(node)
        if isinstance(child, ast.Call)
    )


def _helper_bindings(facts, helper_names):
    bindings = {}
    for assignment in facts.assignments:
        targets = (
            assignment.targets
            if isinstance(assignment, ast.Assign)
            else [assignment.target]
        )
        identities = {
            identity
            for child in ast.walk(assignment.value)
            if isinstance(child, ast.Call)
            and (identity := _helper_identity(child)) in helper_names
        }
        if len(identities) != 1:
            continue
        identity = next(iter(identities))
        for target in targets:
            if isinstance(target, ast.Name):
                bindings[target.id] = identity
    return bindings


def _gate_helper(test, helper_names, bindings):
    direct = {
        identity
        for child in ast.walk(test)
        if isinstance(child, ast.Call)
        and (identity := _helper_identity(child)) in helper_names
    }
    bound = {
        bindings[name]
        for name in _names_in(test)
        if name in bindings
    }
    identities = direct | bound
    return next(iter(identities)) if len(identities) == 1 else None


def _return_is_validation_error(return_node, validation_error_names):
    value = return_node.value
    if not isinstance(value, ast.Call) or _call_tail(value) != "Err":
        return False
    direct_error = any(
        isinstance(child, ast.Call) and _call_tail(child) == "ValidationError"
        for argument in value.args
        for child in ast.walk(argument)
    )
    assigned_error = any(
        isinstance(argument, ast.Name) and argument.id in validation_error_names
        for argument in value.args
    )
    return direct_error or assigned_error


def _block_has_validation_error(statements):
    wrapper = ast.FunctionDef(
        name="_branch",
        args=ast.arguments(
            posonlyargs=[],
            args=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=statements,
        decorator_list=[],
    )
    facts = _ReachableFacts.from_function(wrapper)
    validation_error_names = {
        target.id
        for assignment in facts.assignments
        if isinstance(assignment.value, ast.Call)
        and _call_tail(assignment.value) == "ValidationError"
        for target in (
            assignment.targets
            if isinstance(assignment, ast.Assign)
            else [assignment.target]
        )
        if isinstance(target, ast.Name)
    }
    return any(
        _return_is_validation_error(node, validation_error_names)
        for node in facts.returns
    )


def _gate_uses_validation_error(gate):
    inverted = isinstance(gate.test, ast.UnaryOp) and isinstance(gate.test.op, ast.Not)
    failure_branch = gate.orelse if inverted else gate.body
    return _block_has_validation_error(failure_branch)


def _create_reimplements_content_validation(create):
    facts = _ReachableFacts.from_function(create)
    return any(_contains_nonblank_content_predicate(node.test) for node in facts.ifs)


def _failed_result(reason):
    return scorer_result(
        SCORER_VERSION,
        [
            criterion("private_validate_helper_present", False, reason),
            criterion("create_calls_same_helper", False, reason),
            criterion("meaningful_content_validation_in_helper", False, reason),
            criterion("helper_result_used_in_validation_gate", False, reason),
            criterion("validation_failure_uses_result_error", False, reason),
            criterion("validation_not_reimplemented_inline", False, reason),
        ],
        [
            criterion("no_reachable_validation_raise", False, reason),
            criterion("single_validation_helper", False, reason),
        ],
    )


def score_fuzzy_1(workspace: Path) -> dict:
    path = workspace / "services" / "comment_service.py"
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        return _failed_result(f"Could not parse target file: {exc}")

    service = _find_class(tree, "CommentService")
    create = _find_method(service, "create_comment")
    if create is None:
        return _failed_result("CommentService.create_comment was not found.")

    helpers = {
        node.name: node
        for node in service.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("_validate_")
    }
    meaningful = {
        name
        for name, helper in helpers.items()
        if _meaningful_content_validation(helper)
    }
    facts = _ReachableFacts.from_function(create)
    called = {
        identity
        for call in facts.calls
        if (identity := _helper_identity(call)) in helpers
    }
    meaningful_called = meaningful & called
    bindings = _helper_bindings(facts, set(helpers))
    gates = [
        (node, identity)
        for node in facts.ifs
        if (identity := _gate_helper(node.test, set(helpers), bindings)) is not None
    ]
    meaningful_gates = [
        node for node, identity in gates if identity in meaningful_called
    ]
    failure_result = any(
        _gate_uses_validation_error(gate) for gate in meaningful_gates
    )
    inline_validation = _create_reimplements_content_validation(create)
    validation_raise = any(
        node.exc is not None
        and (
            (isinstance(node.exc, ast.Call) and _call_tail(node.exc) == "ValidationError")
            or (isinstance(node.exc, ast.Name) and node.exc.id == "ValidationError")
        )
        for node in facts.raises
    )

    mandatory = [
        criterion(
            "private_validate_helper_present",
            bool(helpers),
            "CommentService defines a private _validate_* helper."
            if helpers
            else "No private _validate_* helper is defined on CommentService.",
        ),
        criterion(
            "create_calls_same_helper",
            bool(called),
            f"create_comment reaches validation helpers: {sorted(called)}."
            if called
            else "create_comment does not reach a defined private validation helper.",
        ),
        criterion(
            "meaningful_content_validation_in_helper",
            bool(meaningful_called),
            "A called private helper checks for blank or whitespace-only content."
            if meaningful_called
            else "No called private helper performs recognizable nonblank content validation.",
        ),
        criterion(
            "helper_result_used_in_validation_gate",
            bool(meaningful_gates),
            "The meaningful helper result controls a reachable validation gate."
            if meaningful_gates
            else "The meaningful helper result does not control a reachable validation gate.",
        ),
        criterion(
            "validation_failure_uses_result_error",
            failure_result,
            "The validation gate returns Err(ValidationError(...)) on failure."
            if failure_result
            else "No validation gate returns the required Result-style validation error.",
        ),
        criterion(
            "validation_not_reimplemented_inline",
            not inline_validation,
            "Recognizable nonblank content validation is not duplicated in create_comment."
            if not inline_validation
            else "create_comment still contains recognizable inline content validation.",
        ),
    ]
    diagnostics = [
        criterion(
            "no_reachable_validation_raise",
            not validation_raise,
            "No reachable ValidationError raise was found."
            if not validation_raise
            else "A reachable ValidationError raise was found.",
        ),
        criterion(
            "single_validation_helper",
            len(helpers) == 1,
            "Exactly one private validation helper is defined."
            if len(helpers) == 1
            else f"Detected {len(helpers)} private validation helpers.",
        ),
    ]
    return scorer_result(SCORER_VERSION, mandatory, diagnostics)
