import ast
from pathlib import Path


def _find_class(tree, class_name):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def _find_method(class_node, method_name):
    for node in class_node.body:
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == method_name
        ):
            return node
    return None


def score_fuzzy_2(workspace: Path) -> dict:
    errors_path = workspace / "core" / "errors.py"
    service_path = workspace / "services" / "comment_service.py"

    try:
        errors_tree = ast.parse(
            errors_path.read_text(encoding="utf-8")
        )
        service_tree = ast.parse(
            service_path.read_text(encoding="utf-8")
        )
    except (OSError, SyntaxError) as exc:
        return {
            "passed": False,
            "score": 0,
            "max_score": 4,
            "criteria": {},
            "reason": f"Could not parse target files: {exc}",
        }

    comment_error = _find_class(
        errors_tree,
        "CommentNotFoundError",
    )

    resource_specific_error_defined = (
        comment_error is not None
    )

    inherits_not_found_error = False

    if comment_error is not None:
        for base in comment_error.bases:
            if (
                isinstance(base, ast.Name)
                and base.id == "NotFoundError"
            ):
                inherits_not_found_error = True

    service_class = _find_class(
        service_tree,
        "CommentService",
    )

    if service_class is None:
        return {
            "passed": False,
            "score": 0,
            "max_score": 4,
            "criteria": {
                "resource_specific_error_defined":
                    resource_specific_error_defined,
                "inherits_not_found_error":
                    inherits_not_found_error,
                "get_comment_uses_specific_error": False,
                "no_generic_not_found_return": False,
            },
            "reason": "CommentService was not found.",
        }

    get_comment = _find_method(
        service_class,
        "get_comment",
    )

    if get_comment is None:
        return {
            "passed": False,
            "score": 0,
            "max_score": 4,
            "criteria": {
                "resource_specific_error_defined":
                    resource_specific_error_defined,
                "inherits_not_found_error":
                    inherits_not_found_error,
                "get_comment_uses_specific_error": False,
                "no_generic_not_found_return": False,
            },
            "reason": "CommentService.get_comment was not found.",
        }

    called_names = set()

    for node in ast.walk(get_comment):
        if not isinstance(node, ast.Call):
            continue

        if isinstance(node.func, ast.Name):
            called_names.add(node.func.id)

        elif isinstance(node.func, ast.Attribute):
            called_names.add(node.func.attr)

    get_comment_uses_specific_error = (
        "CommentNotFoundError" in called_names
    )

    no_generic_not_found_return = (
        "NotFoundError" not in called_names
    )

    criteria = {
        "resource_specific_error_defined":
            resource_specific_error_defined,
        "inherits_not_found_error":
            inherits_not_found_error,
        "get_comment_uses_specific_error":
            get_comment_uses_specific_error,
        "no_generic_not_found_return":
            no_generic_not_found_return,
    }

    score = sum(
        1 for value in criteria.values()
        if value
    )

    return {
        "passed": score >= 3,
        "score": score,
        "max_score": 4,
        "criteria": criteria,
        "reason": (
            f"Fuzzy-2 rubric score: {score}/4 "
            f"(pass threshold: 3/4)."
        ),
    }