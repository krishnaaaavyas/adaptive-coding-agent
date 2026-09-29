import json
from pathlib import Path

import pytest

from harness.adaptation import (
    adaptation_metadata,
    apply_structured_adaptation,
    validate_adaptation_config,
)


def structured(condition, **components):
    return {
        "adaptation_schema": "1",
        "condition": condition,
        "adaptation": components,
    }


@pytest.mark.parametrize(
    "condition,components,present",
    [
        ("A", {}, set()),
        ("B", {"memory": "A previous correction."}, {"memory"}),
        ("M", {"evidence": "Relevant cases delegate persistence."}, {"evidence"}),
        ("C", {"rule": "Persistence operations must use services."}, {"rule"}),
        (
            "BC",
            {
                "memory": "A previous correction.",
                "rule": "Persistence operations must use services.",
            },
            {"memory", "rule"},
        ),
    ],
)
def test_valid_structured_conditions(condition, components, present):
    state = validate_adaptation_config(structured(condition, **components))

    assert state["mode"] == "structured"
    assert state["schema_version"] == "1"
    assert {
        name for name, value in state["components"].items() if value is not None
    } == present


def test_unknown_structured_condition_rejected():
    with pytest.raises(ValueError, match="one of A, B, M, C, or BC"):
        validate_adaptation_config(structured("D"))


def test_missing_adaptation_object_rejected():
    with pytest.raises(ValueError, match="adaptation object"):
        validate_adaptation_config(
            {"adaptation_schema": "1", "condition": "A"}
        )


def test_extra_adaptation_key_rejected():
    with pytest.raises(ValueError, match="Unsupported adaptation field"):
        validate_adaptation_config(
            structured("A", unexpected="value")
        )


@pytest.mark.parametrize(
    "condition,components",
    [
        ("A", {"memory": "episode"}),
        ("A", {"evidence": "description"}),
        ("A", {"rule": "rule text"}),
        ("B", {}),
        ("B", {"memory": "episode", "evidence": "description"}),
        ("B", {"memory": "episode", "rule": "rule text"}),
        ("M", {}),
        ("M", {"evidence": "description", "memory": "episode"}),
        ("M", {"evidence": "description", "rule": "rule text"}),
        ("C", {}),
        ("C", {"rule": "rule text", "memory": "episode"}),
        ("C", {"rule": "rule text", "evidence": "description"}),
        ("BC", {"rule": "rule text"}),
        ("BC", {"memory": "episode"}),
        (
            "BC",
            {
                "memory": "episode",
                "rule": "rule text",
                "evidence": "description",
            },
        ),
    ],
)
def test_condition_component_mismatches_rejected(condition, components):
    with pytest.raises(ValueError, match="requires adaptation components"):
        validate_adaptation_config(structured(condition, **components))


@pytest.mark.parametrize("value", ["", " ", "\n\t", [], ["valid", " "]])
def test_empty_or_whitespace_adaptation_values_rejected(value):
    with pytest.raises(ValueError, match="must not be|nonempty"):
        validate_adaptation_config(structured("B", memory=value))


@pytest.mark.parametrize(
    "marker",
    [
        "Routers must delegate persistence.",
        "Routers should delegate persistence.",
        "Routers always delegate persistence.",
        "Delegation is required.",
        "This requirement applies to persistence.",
        "The rule concerns persistence.",
        "Repository conventions route persistence.",
        "Follow the service examples.",
        "Ensure that routers use services.",
    ],
)
def test_m_rejects_word_aware_normative_markers(marker):
    with pytest.raises(ValueError, match="prohibited marker"):
        validate_adaptation_config(structured("M", evidence=marker))


def test_m_word_matching_avoids_naive_substring_false_positives():
    evidence = (
        "The mustang example uses a conventional rulebook and follows "
        "the existing routing shape."
    )

    state = validate_adaptation_config(structured("M", evidence=evidence))

    assert state["components"]["evidence"] == evidence


@pytest.mark.parametrize(
    "phrase",
    [
        "The correction said therefore always delegate.",
        "This demonstrates the repository convention.",
        "The rule is to delegate persistence.",
        "The reviewer said you should delegate persistence.",
    ],
)
def test_b_rejects_obvious_generalized_rule_phrases(phrase):
    with pytest.raises(ValueError, match="prohibited marker"):
        validate_adaptation_config(structured("B", memory=phrase))


def test_b_accepts_concrete_episode_without_generalized_rule():
    memory = (
        "Previous task: delete a project. The first implementation used the "
        "session directly. The developer changed it to call the service."
    )

    state = validate_adaptation_config(structured("B", memory=memory))

    assert state["components"]["memory"] == memory


@pytest.mark.parametrize(
    "condition,components,headings",
    [
        ("A", {}, set()),
        ("B", {"memory": "episode"}, {"EPISODIC MEMORY"}),
        ("M", {"evidence": "descriptive evidence"}, {"REPOSITORY EVIDENCE"}),
        ("C", {"rule": "confirmed rule"}, {"CONFIRMED REPOSITORY RULE"}),
        (
            "BC",
            {"memory": "episode", "rule": "confirmed rule"},
            {"EPISODIC MEMORY", "CONFIRMED REPOSITORY RULE"},
        ),
    ],
)
def test_prompt_sections_are_condition_specific(condition, components, headings):
    base = "TASK AND REPOSITORY CONTEXT"
    state = validate_adaptation_config(structured(condition, **components))

    prompt, sources = apply_structured_adaptation(base, state)

    all_headings = {
        "EPISODIC MEMORY",
        "REPOSITORY EVIDENCE",
        "CONFIRMED REPOSITORY RULE",
    }
    for heading in all_headings:
        assert (f"{heading}:" in prompt) is (heading in headings)
    assert prompt.endswith(base)
    assert prompt.count(base) == 1
    assert {label for label, _ in sources} == {
        {
            "EPISODIC MEMORY": "episodic memory",
            "REPOSITORY EVIDENCE": "repository evidence",
            "CONFIRMED REPOSITORY RULE": "confirmed rule",
        }[heading]
        for heading in headings
    }


def test_structured_metadata_records_schema_condition_and_presence():
    state = validate_adaptation_config(
        structured("BC", memory="episode", rule="confirmed rule")
    )

    assert adaptation_metadata(state) == {
        "schema": "structured",
        "schema_version": "1",
        "condition": "BC",
        "components_present": {
            "evidence": False,
            "memory": True,
            "rule": True,
        },
    }


def test_legacy_config_is_explicitly_not_structured():
    state = validate_adaptation_config(
        {"condition": "B", "memory_file": "memory/episode.json"}
    )

    assert state["mode"] == "legacy"
    assert state["schema_version"] is None
    assert state["components"] is None


def test_all_historical_pilot_configs_remain_explicitly_legacy():
    paths = sorted(Path("experiments").glob("*.json"))

    assert len(paths) == 18
    for path in paths:
        config = json.loads(path.read_text(encoding="utf-8"))
        state = validate_adaptation_config(config)
        assert "adaptation_schema" not in config
        assert "adaptation" not in config
        assert state["mode"] == "legacy"


def test_adaptation_without_schema_is_not_silently_structured():
    with pytest.raises(ValueError, match="explicit adaptation_schema"):
        validate_adaptation_config(
            {"condition": "B", "adaptation": {"memory": "episode"}}
        )


@pytest.mark.parametrize("condition", ["M", "BC"])
def test_new_conditions_cannot_fall_back_to_legacy(condition):
    with pytest.raises(ValueError, match="require structured"):
        validate_adaptation_config({"condition": condition})


def test_structured_config_rejects_legacy_adaptation_files():
    config = structured("B", memory="episode")
    config["memory_file"] = "memory/episode.json"

    with pytest.raises(ValueError, match="legacy field"):
        validate_adaptation_config(config)


@pytest.mark.parametrize("field", ["temperature", "max_tokens", "seed"])
def test_structured_config_rejects_run_budget_overrides(field):
    config = structured("A")
    config[field] = 1

    with pytest.raises(ValueError, match="budget/settings"):
        validate_adaptation_config(config)
