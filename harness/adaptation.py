"""Validation and prompt rendering for frozen Step-7 adaptation conditions."""

import re


ADAPTATION_SCHEMA_VERSION = "1"
STRUCTURED_CONDITIONS = {"A", "B", "M", "C", "BC"}
COMPONENTS = {"memory", "evidence", "rule"}
UNSUPPORTED_RUN_OVERRIDES = {
    "context_limit",
    "generation",
    "generation_settings",
    "max_tokens",
    "retry_policy",
    "seed",
    "temperature",
    "tool_availability",
}

M_NORMATIVE_PATTERNS = (
    re.compile(r"\bmust\b", re.IGNORECASE),
    re.compile(r"\bshould\b", re.IGNORECASE),
    re.compile(r"\balways\b", re.IGNORECASE),
    re.compile(r"\brequired\b", re.IGNORECASE),
    re.compile(r"\brequirements?\b", re.IGNORECASE),
    re.compile(r"\brules?\b", re.IGNORECASE),
    re.compile(r"\bconventions?\b", re.IGNORECASE),
    re.compile(r"\bfollow\b", re.IGNORECASE),
    re.compile(r"\bensure\s+that\b", re.IGNORECASE),
)
B_GENERALIZED_RULE_PATTERNS = (
    re.compile(r"\btherefore\s+always\b", re.IGNORECASE),
    re.compile(r"\brepository\s+convention\b", re.IGNORECASE),
    re.compile(r"\bthe\s+rule\s+is\b", re.IGNORECASE),
    re.compile(r"\byou\s+should\b", re.IGNORECASE),
)


def _normalize_component(name, value):
    if value is None:
        return None
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"adaptation.{name} must not be empty or whitespace")
        return normalized
    if isinstance(value, list):
        if not value:
            raise ValueError(f"adaptation.{name} must not be an empty list")
        normalized = []
        for index, item in enumerate(value):
            if not isinstance(item, str) or not item.strip():
                raise ValueError(
                    f"adaptation.{name}[{index}] must be a nonempty string"
                )
            normalized.append(item.strip())
        return normalized
    raise ValueError(
        f"adaptation.{name} must be null, a string, or a list of strings"
    )


def _component_text(value):
    if isinstance(value, list):
        return "\n\n".join(value)
    return value


def _reject_patterns(label, text, patterns):
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            raise ValueError(
                f"{label} contains prohibited marker: {match.group(0)!r}"
            )


def validate_adaptation_config(config):
    """Return explicit legacy or validated structured adaptation state."""
    has_schema = "adaptation_schema" in config
    has_adaptation = "adaptation" in config

    if not has_schema and not has_adaptation:
        if config.get("condition") in {"M", "BC"}:
            raise ValueError(
                "Conditions M and BC require structured adaptation_schema '1'"
            )
        return {
            "mode": "legacy",
            "schema_version": None,
            "condition": config.get("condition"),
            "components": None,
        }

    if not has_schema:
        raise ValueError(
            "Structured adaptation requires explicit adaptation_schema '1'"
        )
    if config["adaptation_schema"] != ADAPTATION_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported adaptation_schema: {config['adaptation_schema']!r}"
        )
    if not has_adaptation or not isinstance(config["adaptation"], dict):
        raise ValueError("Structured adaptation requires an adaptation object")

    condition = config.get("condition")
    if condition not in STRUCTURED_CONDITIONS:
        raise ValueError(
            "Structured adaptation condition must be one of A, B, M, C, or BC"
        )

    extra = set(config["adaptation"]) - COMPONENTS
    if extra:
        raise ValueError(
            "Unsupported adaptation field(s): " + ", ".join(sorted(extra))
        )
    legacy_fields = {"memory_file", "rule_file"} & set(config)
    if legacy_fields:
        raise ValueError(
            "Structured adaptation cannot use legacy field(s): "
            + ", ".join(sorted(legacy_fields))
        )
    overrides = UNSUPPORTED_RUN_OVERRIDES & set(config)
    if overrides:
        raise ValueError(
            "Structured adaptation cannot override run budget/settings: "
            + ", ".join(sorted(overrides))
        )

    components = {
        name: _normalize_component(name, config["adaptation"].get(name))
        for name in sorted(COMPONENTS)
    }
    present = {name for name, value in components.items() if value is not None}
    expected = {
        "A": set(),
        "B": {"memory"},
        "M": {"evidence"},
        "C": {"rule"},
        "BC": {"memory", "rule"},
    }[condition]
    if present != expected:
        raise ValueError(
            f"Condition {condition} requires adaptation components "
            f"{sorted(expected)}; received {sorted(present)}"
        )

    if components["evidence"] is not None:
        _reject_patterns(
            "M evidence",
            _component_text(components["evidence"]),
            M_NORMATIVE_PATTERNS,
        )
    if components["memory"] is not None:
        _reject_patterns(
            "B memory",
            _component_text(components["memory"]),
            B_GENERALIZED_RULE_PATTERNS,
        )

    return {
        "mode": "structured",
        "schema_version": ADAPTATION_SCHEMA_VERSION,
        "condition": condition,
        "components": components,
    }


def adaptation_metadata(state):
    components = state["components"]
    return {
        "schema": state["mode"],
        "schema_version": state["schema_version"],
        "condition": state["condition"],
        "components_present": {
            name: bool(components and components[name] is not None)
            for name in sorted(COMPONENTS)
        },
    }


def apply_structured_adaptation(user_prompt, state):
    """Prepend only the adaptation sections authorized by the condition."""
    if state["mode"] != "structured":
        raise ValueError("Structured prompt rendering requires structured state")

    sections = []
    sources = []
    labels = (
        ("memory", "EPISODIC MEMORY", "episodic memory"),
        ("evidence", "REPOSITORY EVIDENCE", "repository evidence"),
        ("rule", "CONFIRMED REPOSITORY RULE", "confirmed rule"),
    )
    for component, heading, source_label in labels:
        value = state["components"][component]
        if value is None:
            continue
        content = f"{heading}:\n\n{_component_text(value)}"
        sections.append(content)
        sources.append((source_label, content))

    if not sections:
        return user_prompt, sources
    return "\n\n".join([*sections, user_prompt]), sources
