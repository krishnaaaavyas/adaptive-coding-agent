"""Explicit-3 v2: public DTOs expose a required UUID, not an internal key."""

import ast
from pathlib import Path

from harness.scorers.contract import criterion, scorer_result


SCORER_VERSION = "explicit_3 scorer v2"
INTERNAL_PRIMARY_KEY_FIELDS = {"id", "internal_id", "db_id", "pk"}


def _find_class(tree, name):
    return next(
        (node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == name),
        None,
    )


def _import_aliases(tree):
    uuid_names = set()
    uuid_modules = set()
    annotated_names = {"Annotated"}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.module == "uuid":
                for alias in node.names:
                    if alias.name == "UUID":
                        uuid_names.add(alias.asname or alias.name)
            elif node.module == "typing":
                for alias in node.names:
                    if alias.name == "Annotated":
                        annotated_names.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "uuid":
                    uuid_modules.add(alias.asname or alias.name)
    return uuid_names, uuid_modules, annotated_names


def _subscript_parts(node):
    if isinstance(node.slice, ast.Tuple):
        return list(node.slice.elts)
    return [node.slice]


def _is_named(node, names):
    return isinstance(node, ast.Name) and node.id in names


def _unwrap_annotated(annotation, annotated_names):
    if not isinstance(annotation, ast.Subscript):
        return annotation
    base = annotation.value
    is_annotated = _is_named(base, annotated_names) or (
        isinstance(base, ast.Attribute)
        and base.attr == "Annotated"
        and isinstance(base.value, ast.Name)
        and base.value.id in {"typing", "t"}
    )
    if not is_annotated:
        return annotation
    parts = _subscript_parts(annotation)
    return parts[0] if parts else annotation


def _is_uuid(annotation, uuid_names, uuid_modules, annotated_names):
    annotation = _unwrap_annotated(annotation, annotated_names)
    if _is_named(annotation, uuid_names):
        return True
    return (
        isinstance(annotation, ast.Attribute)
        and annotation.attr == "UUID"
        and isinstance(annotation.value, ast.Name)
        and annotation.value.id in uuid_modules
    )


def _failed_result(reason):
    return scorer_result(
        SCORER_VERSION,
        [
            criterion("public_id_present", False, reason),
            criterion("public_id_required_uuid", False, reason),
            criterion("internal_primary_key_not_exposed", False, reason),
        ],
        [
            criterion("base_model_subclass", False, reason),
            criterion("from_model_present", False, reason),
        ],
    )


def score_explicit_3(workspace: Path) -> dict:
    path = workspace / "dto" / "comment_dto.py"
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        return _failed_result(f"Could not parse target file: {exc}")

    dto = _find_class(tree, "CommentDTO")
    if dto is None:
        return _failed_result("CommentDTO was not found.")

    uuid_names, uuid_modules, annotated_names = _import_aliases(tree)
    public_id = None
    internal_fields = set()
    for node in dto.body:
        if not isinstance(node, ast.AnnAssign) or not isinstance(node.target, ast.Name):
            continue
        if node.target.id == "public_id":
            public_id = node
        if node.target.id in INTERNAL_PRIMARY_KEY_FIELDS:
            internal_fields.add(node.target.id)

    public_id_present = public_id is not None
    required_uuid = (
        public_id is not None
        and public_id.value is None
        and _is_uuid(
            public_id.annotation,
            uuid_names,
            uuid_modules,
            annotated_names,
        )
    )
    no_internal_key = not internal_fields
    base_model = any(
        (isinstance(base, ast.Name) and base.id == "BaseModel")
        or (isinstance(base, ast.Attribute) and base.attr == "BaseModel")
        for base in dto.bases
    )
    from_model = any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "from_model"
        for node in dto.body
    )

    mandatory = [
        criterion(
            "public_id_present",
            public_id_present,
            "CommentDTO declares public_id."
            if public_id_present
            else "CommentDTO does not declare public_id.",
        ),
        criterion(
            "public_id_required_uuid",
            required_uuid,
            "public_id is a required, non-null UUID field."
            if required_uuid
            else "public_id is absent, optional/defaulted, or not strictly UUID.",
        ),
        criterion(
            "internal_primary_key_not_exposed",
            no_internal_key,
            "CommentDTO exposes no recognized internal primary-key field."
            if no_internal_key
            else f"CommentDTO exposes internal key fields: {sorted(internal_fields)}.",
        ),
    ]
    diagnostics = [
        criterion(
            "base_model_subclass",
            base_model,
            "CommentDTO subclasses BaseModel."
            if base_model
            else "BaseModel inheritance was not found; diagnostic only.",
        ),
        criterion(
            "from_model_present",
            from_model,
            "CommentDTO defines from_model."
            if from_model
            else "CommentDTO has no from_model method; diagnostic only.",
        ),
    ]
    return scorer_result(SCORER_VERSION, mandatory, diagnostics)
