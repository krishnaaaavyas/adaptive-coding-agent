import ast
from pathlib import Path


def _find_method(class_node, method_name):
    for node in class_node.body:
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == method_name
        ):
            return node

    return None


def _find_class(tree, class_name):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node

    return None


def _called_method_names(node):
    names = set()

    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Attribute):
                names.add(child.func.attr)

            elif isinstance(child.func, ast.Name):
                names.add(child.func.id)

    return names


def score_fuzzy_1(workspace: Path) -> dict:
    path = workspace / "services" / "comment_service.py"

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)

    except (OSError, SyntaxError) as exc:
        return {
            "passed": False,
            "score": 0,
            "max_score": 4,
            "criteria": {},
            "reason": f"Could not parse target file: {exc}",
        }

    service_class = _find_class(
        tree,
        "CommentService",
    )

    if service_class is None:
        return {
            "passed": False,
            "score": 0,
            "max_score": 4,
            "criteria": {},
            "reason": "CommentService was not found.",
        }

    create_method = _find_method(
        service_class,
        "create_comment",
    )

    if create_method is None:
        return {
            "passed": False,
            "score": 0,
            "max_score": 4,
            "criteria": {},
            "reason": "CommentService.create_comment was not found.",
        }

    validation_helpers = [
        node
        for node in service_class.body
        if (
            isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            )
            and node.name.startswith("_validate_")
        )
    ]

    private_validation_helper = (
        len(validation_helpers) > 0
    )

    called_names = _called_method_names(
        create_method
    )

    called_helpers = [
        helper
        for helper in validation_helpers
        if helper.name in called_names
    ]

    create_calls_helper = (
        len(called_helpers) > 0
    )

    helper_contains_validation = False

    for helper in called_helpers:
        has_conditional = any(
            isinstance(
                node,
                (ast.If, ast.IfExp),
            )
            for node in ast.walk(helper)
        )

        if has_conditional:
            helper_contains_validation = True
            break

    result_style_failure = False

    for node in ast.walk(create_method):
        if not isinstance(node, ast.Return):
            continue

        value = node.value

        if isinstance(value, ast.Call):
            if isinstance(value.func, ast.Name):
                if value.func.id == "Err":
                    result_style_failure = True

            elif isinstance(value.func, ast.Attribute):
                if value.func.attr == "Err":
                    result_style_failure = True

    criteria = {
        "private_validation_helper": private_validation_helper,
        "create_calls_helper": create_calls_helper,
        "helper_contains_validation": helper_contains_validation,
        "result_style_failure": result_style_failure,
    }

    score = sum(
        1 for passed in criteria.values()
        if passed
    )

    passed = score >= 3

    return {
        "passed": passed,
        "score": score,
        "max_score": 4,
        "criteria": criteria,
        "reason": (
            f"Fuzzy-1 rubric score: {score}/4 "
            f"(pass threshold: 3/4)."
        ),
    }