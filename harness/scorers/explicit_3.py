import ast
from pathlib import Path


def _find_class(tree: ast.AST, class_name: str):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def _annotation_text(annotation):
    if annotation is None:
        return ""

    try:
        return ast.unparse(annotation)
    except Exception:
        return ""


def score_explicit_3(workspace: Path) -> dict:
    path = workspace / "dto" / "comment_dto.py"

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError) as exc:
        return {
            "passed": False,
            "public_id_found": False,
            "public_id_is_uuid": False,
            "internal_id_exposed": False,
            "reason": f"Could not parse target file: {exc}",
        }

    dto_class = _find_class(tree, "CommentDTO")

    if dto_class is None:
        return {
            "passed": False,
            "public_id_found": False,
            "public_id_is_uuid": False,
            "internal_id_exposed": False,
            "reason": "CommentDTO was not found.",
        }

    public_id_found = False
    public_id_is_uuid = False
    internal_id_exposed = False

    for node in dto_class.body:
        if not isinstance(node, ast.AnnAssign):
            continue

        if not isinstance(node.target, ast.Name):
            continue

        field_name = node.target.id
        annotation = _annotation_text(node.annotation)

        if field_name == "public_id":
            public_id_found = True

            if annotation == "UUID" or annotation.endswith(".UUID"):
                public_id_is_uuid = True

        if field_name in {
            "id",
            "internal_id",
            "db_id",
            "pk",
        }:
            internal_id_exposed = True

    passed = (
        public_id_found
        and public_id_is_uuid
        and not internal_id_exposed
    )

    if passed:
        reason = (
            "CommentDTO exposes public_id as UUID and does not "
            "expose an internal database identifier."
        )
    elif internal_id_exposed:
        reason = (
            "CommentDTO exposes an internal database identifier."
        )
    elif not public_id_found:
        reason = (
            "CommentDTO does not expose the required public_id field."
        )
    else:
        reason = (
            "CommentDTO.public_id exists but is not annotated as UUID."
        )

    return {
        "passed": passed,
        "public_id_found": public_id_found,
        "public_id_is_uuid": public_id_is_uuid,
        "internal_id_exposed": internal_id_exposed,
        "reason": reason,
    }