import json
from pathlib import Path

import pytest

from harness.scorers.contract import criterion, scorer_result
from harness.scorers.explicit_1 import SCORER_VERSION as EXPLICIT_1_VERSION
from harness.scorers.explicit_1 import score_explicit_1
from harness.scorers.explicit_2 import SCORER_VERSION as EXPLICIT_2_VERSION
from harness.scorers.explicit_2 import score_explicit_2
from harness.scorers.explicit_3 import SCORER_VERSION as EXPLICIT_3_VERSION
from harness.scorers.explicit_3 import score_explicit_3
from harness.scorers.fuzzy_1 import SCORER_VERSION as FUZZY_1_VERSION
from harness.scorers.fuzzy_1 import score_fuzzy_1
from harness.scorers.fuzzy_2 import SCORER_VERSION as FUZZY_2_VERSION
from harness.scorers.fuzzy_2 import score_fuzzy_2
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


def load_multi_file_cases(scorer_name):
    directory = FIXTURES / scorer_name
    cases = json.loads((directory / "cases.json").read_text(encoding="utf-8"))
    return [pytest.param(directory, case, id=case["name"]) for case in cases]


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


@pytest.mark.parametrize("fixture_path,case", load_cases("explicit_1"))
def test_explicit_1_fixture_matrix(tmp_path, fixture_path, case):
    target = tmp_path / "services" / "project_service.py"
    target.parent.mkdir(parents=True)
    target.write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")
    if wiring := case.get("wiring"):
        router = tmp_path / "routers" / "projects.py"
        router.parent.mkdir(parents=True)
        router.write_text(
            (fixture_path.parent / wiring).read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    result = score_explicit_1(tmp_path)
    assert_contract(result, case["expected_pass"], EXPLICIT_1_VERSION)
    assert [item["id"] for item in result["mandatory"]] == [
        "injected_repository_delete_delegation",
        "no_direct_persistence_access",
        "no_constructed_persistence_dependency",
    ]


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


@pytest.mark.parametrize("fixture_path,case", load_cases("explicit_3"))
def test_explicit_3_fixture_matrix(tmp_path, fixture_path, case):
    target = tmp_path / "dto" / "comment_dto.py"
    target.parent.mkdir(parents=True)
    target.write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")

    result = score_explicit_3(tmp_path)
    assert_contract(result, case["expected_pass"], EXPLICIT_3_VERSION)
    assert [item["id"] for item in result["mandatory"]] == [
        "public_id_present",
        "public_id_required_uuid",
        "internal_primary_key_not_exposed",
    ]


@pytest.mark.parametrize("fixture_path,case", load_cases("fuzzy_1"))
def test_fuzzy_1_fixture_matrix(tmp_path, fixture_path, case):
    target = tmp_path / "services" / "comment_service.py"
    target.parent.mkdir(parents=True)
    target.write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")

    result = score_fuzzy_1(tmp_path)
    assert_contract(result, case["expected_pass"], FUZZY_1_VERSION)
    assert [item["id"] for item in result["mandatory"]] == [
        "private_validate_helper_present",
        "create_calls_same_helper",
        "meaningful_content_validation_in_helper",
        "helper_result_used_in_validation_gate",
        "validation_failure_uses_result_error",
        "validation_not_reimplemented_inline",
    ]


@pytest.mark.parametrize(
    "fixture_directory,case",
    load_multi_file_cases("fuzzy_2"),
)
def test_fuzzy_2_fixture_matrix(tmp_path, fixture_directory, case):
    errors_target = tmp_path / "core" / "errors.py"
    service_target = tmp_path / "services" / "comment_service.py"
    errors_target.parent.mkdir(parents=True)
    service_target.parent.mkdir(parents=True)
    errors_target.write_text(
        (fixture_directory / case["errors"]).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    service_target.write_text(
        (fixture_directory / case["service"]).read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    result = score_fuzzy_2(tmp_path)
    assert_contract(result, case["expected_pass"], FUZZY_2_VERSION)
    assert [item["id"] for item in result["mandatory"]] == [
        "specific_error_defined",
        "specific_error_is_not_found_subtype",
        "reachable_specific_error_result",
        "reachable_ok_result",
        "no_generic_not_found_result",
    ]


def test_fixture_manifests_cover_every_source_file():
    for scorer_name in (
        "explicit_1",
        "explicit_2",
        "explicit_3",
        "fuzzy_1",
        "fuzzy_2",
        "fuzzy_3",
    ):
        directory = FIXTURES / scorer_name
        manifest = json.loads(
            (directory / "cases.json").read_text(encoding="utf-8")
        )
        if scorer_name == "fuzzy_2":
            listed = {
                case[key]
                for case in manifest
                for key in ("errors", "service")
            }
        else:
            listed = {
                case[key]
                for case in manifest
                for key in ("file", "wiring")
                if key in case
            }
        actual = {
            path.relative_to(directory).as_posix()
            for path in directory.rglob("*.py")
        }
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
    assert EXPLICIT_1_VERSION == "explicit_1 scorer v2"
    assert FUZZY_3_VERSION == "fuzzy_3 scorer v2"
    assert EXPLICIT_2_VERSION == "explicit_2 scorer v2"
    assert EXPLICIT_3_VERSION == "explicit_3 scorer v2"
    assert FUZZY_1_VERSION == "fuzzy_1 scorer v2"
    assert FUZZY_2_VERSION == "fuzzy_2 scorer v2"
