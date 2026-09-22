from unittest.mock import Mock

import pytest

from harness.leakage import LeakageDetectedError, scan_leakage
from harness import run_experiment


MODEL = {"label": "fake", "expected_served_id": "fake-served"}


@pytest.mark.parametrize(
    "text, expected_pattern",
    [
        ("This is eXpLiCiT-2 guidance.", "Explicit-N label"),
        ("Follow explicit_3 here.", "Explicit-N label"),
        ("The FUZZY 1 requirement applies.", "Fuzzy-N label"),
        ("This is a held-out task.", "held-out task"),
        ("This is the HELD_OUT_TARGET.", "held-out target"),
        ("Copied from the Pilot Spec.", "pilot spec"),
        ("Use the expected solution.", "expected solution"),
        ("This file is the benchmark target.", "benchmark target"),
        ("Apply Condition A for this run.", "experimental condition label"),
        ("The fuzzy_3 scorer checks this.", "direct scorer reference"),
    ],
)
def test_high_confidence_patterns_are_case_insensitive(text, expected_pattern):
    findings = scan_leakage([("repository context", text)])

    assert any(
        finding.severity == "error" and finding.pattern == expected_pattern
        for finding in findings
    )


def test_warning_only_language_does_not_abort(monkeypatch, capsys):
    generation = Mock(return_value="generated code")
    monkeypatch.setattr(run_experiment, "generate", generation)
    text = "Follow the project convention for this benchmark."

    result = run_experiment.generate_with_preflight(
        [{"role": "user", "content": text}],
        [("rule", text)],
        MODEL,
    )

    assert result == "generated code"
    generation.assert_called_once()
    assert "Leakage preflight warning" in capsys.readouterr().out


@pytest.mark.parametrize("text", ["benchmark", "convention", "scorer", "pilot"])
def test_ambiguous_terms_are_warnings(text):
    findings = scan_leakage([("task prompt", text)])

    assert len(findings) == 1
    assert findings[0].severity == "warning"


def test_ordinary_production_text_produces_no_findings():
    findings = scan_leakage(
        [
            (
                "repository context",
                "The service validates input and delegates persistence to its repository.",
            )
        ]
    )

    assert findings == []


def test_generic_software_terms_are_not_high_confidence_leakage():
    findings = scan_leakage(
        [
            (
                "task prompt",
                "The test condition stores a rule in memory before execution.",
            )
        ]
    )

    assert not any(finding.severity == "error" for finding in findings)


@pytest.mark.parametrize(
    "source_label,text",
    [
        ("repository context", "# Fuzzy-2"),
        ("memory", "This came from the pilot spec."),
        ("rule", "Use the expected solution exactly."),
    ],
)
def test_leakage_is_attributed_to_model_visible_source(source_label, text):
    findings = scan_leakage([(source_label, text)])

    errors = [finding for finding in findings if finding.severity == "error"]
    assert errors
    assert all(finding.source_label == source_label for finding in errors)


def test_preflight_aborts_before_inference(monkeypatch, capsys):
    generation = Mock()
    monkeypatch.setattr(run_experiment, "generate", generation)

    with pytest.raises(
        LeakageDetectedError,
        match="repository context",
    ) as exc_info:
        run_experiment.generate_with_preflight(
            [{"role": "user", "content": "Fuzzy-3"}],
            [("repository context", "Fuzzy-3")],
            MODEL,
        )

    generation.assert_not_called()
    assert len(exc_info.value.findings) == 1
    assert exc_info.value.findings[0].source_label == "repository context"
    assert "inference aborted" in capsys.readouterr().out


def test_final_message_leakage_aborts_when_sources_are_incomplete(monkeypatch):
    generation = Mock()
    monkeypatch.setattr(run_experiment, "generate", generation)

    with pytest.raises(
        LeakageDetectedError,
        match=r"message\[1\] \(user\)",
    ) as exc_info:
        run_experiment.generate_with_preflight(
            [
                {"role": "system", "content": "Implement the feature."},
                {"role": "user", "content": "Use the expected solution."},
            ],
            [("task prompt", "Implement the feature.")],
            MODEL,
        )

    generation.assert_not_called()
    assert len(exc_info.value.findings) == 1
    assert exc_info.value.findings[0].source_label == "message[1] (user)"
