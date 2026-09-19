import ast
from pathlib import Path


FORBIDDEN_PERSISTENCE_NAMES = {
    "session",
    "db",
    "engine",
}

FORBIDDEN_PERSISTENCE_CALLS = {
    "query",
    "execute",
    "commit",
    "flush",
    "add",
}


def _find_method(tree: ast.AST, class_name: str, method_name: str):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if (
                    isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and item.name == method_name
                ):
                    return item
    return None


def score_explicit_1(workspace: Path) -> dict:
    path = workspace / "services" / "project_service.py"

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError) as exc:
        return {
            "passed": False,
            "repository_call_found": False,
            "direct_persistence_found": False,
            "reason": f"Could not parse target file: {exc}",
        }

    method = _find_method(
        tree,
        "ProjectService",
        "delete_project",
    )

    if method is None:
        return {
            "passed": False,
            "repository_call_found": False,
            "direct_persistence_found": False,
            "reason": "ProjectService.delete_project was not found.",
        }

    repository_call_found = False
    direct_persistence_found = False

    for node in ast.walk(method):
        if not isinstance(node, ast.Call):
            continue

        func = node.func

        if isinstance(func, ast.Attribute):
            # Detect self.<repository-like dependency>.<method>(...)
            if (
                isinstance(func.value, ast.Attribute)
                and isinstance(func.value.value, ast.Name)
                and func.value.value.id == "self"
            ):
                dependency_name = func.value.attr.lower()

                if "repo" in dependency_name or "repository" in dependency_name:
                    repository_call_found = True

                if dependency_name in FORBIDDEN_PERSISTENCE_NAMES:
                    direct_persistence_found = True

            # Detect obvious direct persistence calls such as
            # session.execute(...), db.query(...), etc.
            if isinstance(func.value, ast.Name):
                owner = func.value.id.lower()

                if (
                    owner in FORBIDDEN_PERSISTENCE_NAMES
                    or func.attr.lower() in FORBIDDEN_PERSISTENCE_CALLS
                    and owner in FORBIDDEN_PERSISTENCE_NAMES
                ):
                    direct_persistence_found = True

    passed = repository_call_found and not direct_persistence_found

    if passed:
        reason = (
            "delete_project delegates persistence through a repository "
            "dependency and contains no detected direct persistence access."
        )
    elif not repository_call_found:
        reason = (
            "No repository dependency call was detected inside "
            "ProjectService.delete_project."
        )
    else:
        reason = (
            "Direct persistence access was detected inside "
            "ProjectService.delete_project."
        )

    return {
        "passed": passed,
        "repository_call_found": repository_call_found,
        "direct_persistence_found": direct_persistence_found,
        "reason": reason,
    }