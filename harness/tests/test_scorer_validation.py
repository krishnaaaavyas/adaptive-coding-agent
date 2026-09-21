import json
from pathlib import Path

import pytest

from harness.scorers.contract import criterion, scorer_result
from harness.scorers.explicit_2 import SCORER_VERSION as EXPLICIT_2_VERSION
from harness.scorers.explicit_2 import score_explicit_2
from harness.scorers.fuzzy_3 import SCORER_VERSION as FUZZY_3_VERSION
from harness.scorers.fuzzy_3 import score_fuzzy_3


FIXTURES = Path(__file__).parents[1] / "scorers" / "fixtures"


def load_cases(scorer_name):
    directory = FIXTURES / scorer_name
    cases = json.loads((directory / "cases.json").read_text(encoding="utf-8"))
    return [
        pytest.param(directory / case["file"], case, id=case["file"])
        for case in cases
    ]


def assert_contract(result, expected_pass, expected_version):
    assert result["scorer_version"] == expected_version
    assert result["passed"] is expected_pass
    assert result["passed"] is all(
        item["passed"] for item in result["mandatory"]
    )
    assert result["mandatory"]
    assert all(
        set(item) == {"id", "passed", "reason"}
        for item in result["mandatory"]
    )
    assert all(
        set(item) == {"id", "passed", "reason"}
        for item in result["diagnostics"]
    )


@pytest.mark.parametrize("fixture_path,case", load_cases("fuzzy_3"))
def test_fuzzy_3_fixture_matrix(tmp_path, fixture_path, case):
    target = tmp_path / "services" / "comment_service.py"
    target.parent.mkdir(parents=True)
    target.write_text(
        fixture_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    assert_contract(
        score_fuzzy_3(tmp_path),
        case["expected_pass"],
        FUZZY_3_VERSION,
    )


@pytest.mark.parametrize("fixture_path,case", load_cases("explicit_2"))
def test_explicit_2_fixture_matrix(tmp_path, fixture_path, case):
    target = tmp_path / "services" / "project_service.py"
    target.parent.mkdir(parents=True)
    target.write_text(
        fixture_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    result = score_explicit_2(tmp_path)
    assert_contract(result, case["expected_pass"], EXPLICIT_2_VERSION)
    assert [item["id"] for item in result["mandatory"]] == [
        "reachable_err_outcome",
        "reachable_ok_outcome",
        "all_terminal_outcomes_use_result",
    ]


def test_fixture_manifests_cover_every_source_file():
    for scorer_name in ("fuzzy_3", "explicit_2"):
        directory = FIXTURES / scorer_name
        manifest = json.loads(
            (directory / "cases.json").read_text(encoding="utf-8")
        )
        listed = {case["file"] for case in manifest}
        actual = {path.name for path in directory.glob("*.py")}
        assert listed == actual
        assert all(
            case["category"] and case["description"] for case in manifest
        )


def test_diagnostics_cannot_compensate_for_failed_mandatory_requirement():
    result = scorer_result(
        "example scorer v1",
        [criterion("required", False, "Required behavior is absent.")],
        [criterion("nice_to_have", True, "Diagnostic property is present.")],
    )

    assert result["passed"] is False


def test_failed_diagnostics_do_not_block_mandatory_compliance():
    result = scorer_result(
        "example scorer v1",
        [criterion("required", True, "Required behavior is present.")],
        [criterion("nice_to_have", False, "Diagnostic property is absent.")],
    )

    assert result["passed"] is True


def test_hardened_scorer_versions_are_explicit():
    assert FUZZY_3_VERSION == "fuzzy_3 scorer v2"
    assert EXPLICIT_2_VERSION == "explicit_2 scorer v2"
