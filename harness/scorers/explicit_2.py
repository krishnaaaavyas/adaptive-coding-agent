import ast
from pathlib import Path


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


def _call_name(node: ast.Call):
    if isinstance(node.func, ast.Name):
        return node.func.id

    if isinstance(node.func, ast.Attribute):
        return node.func.attr

    return None


def score_explicit_2(workspace: Path) -> dict:
    path = workspace / "services" / "project_service.py"

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError) as exc:
        return {
            "passed": False,
            "result_return_found": False,
            "raise_found": False,
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
            "result_return_found": False,
            "raise_found": False,
            "reason": "ProjectService.delete_project was not found.",
        }

    result_return_found = False
    raise_found = False

    for node in ast.walk(method):
        if isinstance(node, ast.Raise):
            raise_found = True

        if isinstance(node, ast.Return):
            value = node.value

            if isinstance(value, ast.Call):
                name = _call_name(value)

                if name in {"Ok", "Err"}:
                    result_return_found = True

    passed = (
        result_return_found
        and not raise_found
    )

    if passed:
        reason = (
            "delete_project represents outcomes using "
            "Result-style Ok/Err returns and contains "
            "no raised exception."
        )
    elif raise_found:
        reason = (
            "delete_project raises an exception instead "
            "of representing the expected failure through Result."
        )
    else:
        reason = (
            "No Result-style Ok/Err return was detected "
            "inside ProjectService.delete_project."
        )

    return {
        "passed": passed,
        "result_return_found": result_return_found,
        "raise_found": raise_found,
        "reason": reason,
    }