import ast
from pathlib import Path


def _find_class(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _find_method(class_node, name):
    for node in class_node.body:
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == name
        ):
            return node
    return None


def _called_private_normalizers(method):
    names = set()

    for node in ast.walk(method):
        if not isinstance(node, ast.Call):
            continue

        if isinstance(node.func, ast.Attribute):
            name = node.func.attr
        elif isinstance(node.func, ast.Name):
            name = node.func.id
        else:
            continue

        if name.startswith("_normalize_"):
            names.add(name)

    return names


def _contains_meaningful_normalization(method):
    for node in ast.walk(method):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in {
                    "strip",
                    "lower",
                    "upper",
                    "replace",
                    "join",
                }:
                    return True

    return False


def score_fuzzy_3(workspace: Path) -> dict:
    path = workspace / "services" / "comment_service.py"

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        return {
            "passed": False,
            "score": 0,
            "max_score": 4,
            "criteria": {},
            "reason": f"Could not parse target file: {exc}",
        }

    service = _find_class(tree, "CommentService")

    if service is None:
        return {
            "passed": False,
            "score": 0,
            "max_score": 4,
            "criteria": {},
            "reason": "CommentService was not found.",
        }

    create = _find_method(service, "create_comment")
    edit = _find_method(service, "edit_comment")

    helpers = [
        node
        for node in service.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("_normalize_")
    ]

    meaningful_helpers = {
        helper.name
        for helper in helpers
        if _contains_meaningful_normalization(helper)
    }

    create_calls = (
        _called_private_normalizers(create)
        if create is not None
        else set()
    )

    edit_calls = (
        _called_private_normalizers(edit)
        if edit is not None
        else set()
    )

    shared_helpers = (
        create_calls
        & edit_calls
        & meaningful_helpers
    )

    helper_exists = bool(meaningful_helpers)

    create_uses = bool(
        create_calls & meaningful_helpers
    )

    edit_uses_same = bool(shared_helpers)

    normalization_centralized = bool(shared_helpers)

    criteria = {
        "normalization_helper_exists": helper_exists,
        "create_uses_helper": create_uses,
        "edit_uses_same_helper": edit_uses_same,
        "normalization_centralized": normalization_centralized,
    }

    score = sum(criteria.values())

    return {
        "passed": score >= 3,
        "score": score,
        "max_score": 4,
        "criteria": criteria,
        "reason": (
            f"Fuzzy-3 rubric score: {score}/4 "
            f"(pass threshold: 3/4)."
        ),
    }