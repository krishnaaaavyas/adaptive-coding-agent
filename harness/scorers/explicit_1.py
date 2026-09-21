"""Explicit-1 v2: services delegate deletion through injected persistence."""

import ast
from pathlib import Path

from harness.scorers.contract import criterion, scorer_result


SCORER_VERSION = "explicit_1 scorer v2"
DIRECT_PERSISTENCE_OWNERS = {"db", "session", "engine"}
DIRECT_PERSISTENCE_CALLS = {
    "add",
    "commit",
    "delete",
    "execute",
    "flush",
    "merge",
    "query",
}
PERSISTENCE_CONSTRUCTORS = {
    "Session",
    "sessionmaker",
    "create_engine",
    "Engine",
}


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


class _ReachableNodes(ast.NodeVisitor):
    """Collect nodes while pruning nested callables and simple dead code."""

    def __init__(self):
        self.nodes = []

    def visit_FunctionDef(self, node):
        return None

    visit_AsyncFunctionDef = visit_FunctionDef
    visit_Lambda = visit_FunctionDef
    visit_ClassDef = visit_FunctionDef

    def generic_visit(self, node):
        self.nodes.append(node)
        super().generic_visit(node)

    def visit_If(self, node):
        self.nodes.append(node)
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
        visitor = cls()
        visitor._visit_block(function.body)
        return visitor.nodes


def _self_attribute(node):
    if (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
    ):
        return node.attr
    return None


def _project_repository_imports(tree):
    names = set()
    modules = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.module == "repositories.project_repository":
                for alias in node.names:
                    if alias.name == "ProjectRepository":
                        names.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "repositories.project_repository":
                    modules.add(alias.asname or alias.name)
    return names, modules


def _annotation_is_project_repository(annotation, names, modules):
    if isinstance(annotation, ast.Name):
        return annotation.id in names
    return (
        isinstance(annotation, ast.Attribute)
        and annotation.attr == "ProjectRepository"
        and isinstance(annotation.value, ast.Name)
        and annotation.value.id in modules
    )


def _constructor_parameters(constructor):
    if constructor is None:
        return []
    return [
        argument
        for argument in [
            *constructor.args.posonlyargs,
            *constructor.args.args,
            *constructor.args.kwonlyargs,
        ]
        if argument.arg not in {"self", "cls"}
    ]


def _annotated_repository_parameters(constructor, tree):
    names, modules = _project_repository_imports(tree)
    return {
        argument.arg
        for argument in _constructor_parameters(constructor)
        if _annotation_is_project_repository(argument.annotation, names, modules)
    }


def _call_uses_imported_name(call, names):
    return isinstance(call, ast.Call) and (
        (isinstance(call.func, ast.Name) and call.func.id in names)
        or (
            isinstance(call.func, ast.Attribute)
            and call.func.attr in names
        )
    )


def _wired_repository_parameters(workspace, constructor):
    router_path = workspace / "routers" / "projects.py"
    try:
        router_tree = ast.parse(router_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return set()

    repository_names, _ = _project_repository_imports(router_tree)
    service_names = set()
    for node in router_tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "services.project_service"
        ):
            for alias in node.names:
                if alias.name == "ProjectService":
                    service_names.add(alias.asname or alias.name)

    parameters = _constructor_parameters(constructor)
    positional = [
        argument
        for argument in [
            *constructor.args.posonlyargs,
            *constructor.args.args,
        ]
        if argument.arg not in {"self", "cls"}
    ]
    parameter_names = {argument.arg for argument in parameters}
    proven = set()
    for node in ast.walk(router_tree):
        if not isinstance(node, ast.Call):
            continue
        if not (
            isinstance(node.func, ast.Name)
            and node.func.id in service_names
        ):
            continue
        for index, argument in enumerate(node.args):
            if (
                index < len(positional)
                and _call_uses_imported_name(argument, repository_names)
            ):
                proven.add(positional[index].arg)
        for keyword in node.keywords:
            if (
                keyword.arg in parameter_names
                and _call_uses_imported_name(keyword.value, repository_names)
            ):
                proven.add(keyword.arg)
    return proven


def _constructor_injections(constructor, repository_parameters):
    if constructor is None:
        return {}
    parameters = {argument.arg for argument in _constructor_parameters(constructor)}
    injected = set()
    for node in _ReachableNodes.from_function(constructor):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value = node.value
        if (
            not isinstance(value, ast.Name)
            or value.id not in parameters
            or value.id not in repository_parameters
        ):
            continue
        for target in targets:
            if (attribute := _self_attribute(target)) is not None:
                injected.add(attribute)
    return injected


def _owner_is_injected(node, injected, aliases):
    attribute = _self_attribute(node)
    if attribute is not None:
        return attribute in injected
    return isinstance(node, ast.Name) and node.id in aliases


def _local_aliases(nodes, injected):
    aliases = set()
    changed = True
    while changed:
        changed = False
        for node in nodes:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if not _owner_is_injected(node.value, injected, aliases):
                continue
            for target in targets:
                if isinstance(target, ast.Name) and target.id not in aliases:
                    aliases.add(target.id)
                    changed = True
    return aliases


def _call_tail(call):
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return ""


def _is_direct_persistence_call(call, injected, aliases):
    if not isinstance(call.func, ast.Attribute):
        return False
    owner = call.func.value
    operation = call.func.attr
    if _owner_is_injected(owner, injected, aliases):
        attribute = _self_attribute(owner)
        if attribute is not None and attribute.lower() in DIRECT_PERSISTENCE_OWNERS:
            return True
        if isinstance(owner, ast.Name) and owner.id.lower() in DIRECT_PERSISTENCE_OWNERS:
            return True
        return False
    owner_name = ""
    if isinstance(owner, ast.Name):
        owner_name = owner.id
    elif (attribute := _self_attribute(owner)) is not None:
        owner_name = attribute
    direct_owner = (
        owner_name.lower() in DIRECT_PERSISTENCE_OWNERS
        and operation.lower() in DIRECT_PERSISTENCE_CALLS
    )
    orm_owner = (
        isinstance(owner, ast.Name)
        and owner.id.endswith("Model")
        and operation.lower() in DIRECT_PERSISTENCE_CALLS
    )
    return direct_owner or orm_owner


def _constructs_persistence(call):
    name = _call_tail(call)
    return name in PERSISTENCE_CONSTRUCTORS or name.endswith("Repository")


def _failed_result(reason):
    return scorer_result(
        SCORER_VERSION,
        [
            criterion("injected_repository_delete_delegation", False, reason),
            criterion("no_direct_persistence_access", False, reason),
            criterion("no_constructed_persistence_dependency", False, reason),
        ],
        [
            criterion("constructor_injection_found", False, reason),
            criterion("repository_lookup_present", False, reason),
        ],
    )


def score_explicit_1(workspace: Path) -> dict:
    path = workspace / "services" / "project_service.py"
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        return _failed_result(f"Could not parse target file: {exc}")

    service = _find_class(tree, "ProjectService")
    method = _find_method(service, "delete_project")
    if method is None:
        return _failed_result("ProjectService.delete_project was not found.")

    constructor = _find_method(service, "__init__")
    repository_parameters = (
        _annotated_repository_parameters(constructor, tree)
        | _wired_repository_parameters(workspace, constructor)
    )
    injected = _constructor_injections(constructor, repository_parameters)
    nodes = _ReachableNodes.from_function(method)
    aliases = _local_aliases(nodes, injected)
    calls = [node for node in nodes if isinstance(node, ast.Call)]

    delegated_delete = any(
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "delete"
        and _owner_is_injected(call.func.value, injected, aliases)
        and not _is_direct_persistence_call(call, injected, aliases)
        for call in calls
    )
    direct_persistence = any(
        _is_direct_persistence_call(call, injected, aliases) for call in calls
    )
    constructed_persistence = any(_constructs_persistence(call) for call in calls)
    repository_lookup = any(
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "get"
        and _owner_is_injected(call.func.value, injected, aliases)
        for call in calls
    )

    mandatory = [
        criterion(
            "injected_repository_delete_delegation",
            delegated_delete,
            "A reachable delete call is delegated through a statically proven ProjectRepository dependency."
            if delegated_delete
            else "No reachable delete call through a statically proven ProjectRepository dependency was found.",
        ),
        criterion(
            "no_direct_persistence_access",
            not direct_persistence,
            "No direct database, session, or engine persistence call was found."
            if not direct_persistence
            else "A direct database, session, or engine persistence call was found.",
        ),
        criterion(
            "no_constructed_persistence_dependency",
            not constructed_persistence,
            "No repository or persistence infrastructure is constructed in delete_project."
            if not constructed_persistence
            else "delete_project constructs repository or persistence infrastructure.",
        ),
    ]
    diagnostics = [
        criterion(
            "constructor_injection_found",
            bool(injected),
            (
                "ProjectRepository parameters "
                f"{sorted(repository_parameters)} are received as attributes "
                f"{sorted(injected)}."
            )
            if injected
            else "No constructor-injected ProjectRepository attribute was proven.",
        ),
        criterion(
            "repository_lookup_present",
            repository_lookup,
            "A reachable lookup is delegated through the injected dependency."
            if repository_lookup
            else "No injected-dependency lookup was found; diagnostic only.",
        ),
    ]
    return scorer_result(SCORER_VERSION, mandatory, diagnostics)
