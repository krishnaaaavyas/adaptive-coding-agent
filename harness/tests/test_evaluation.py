import itertools
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock
import uuid

import pytest

from harness import evaluation as ev
from harness import run_experiment as runner
from harness.inference import InferenceInfrastructureError
from harness.leakage import LeakageDetectedError


MODEL = {"label": "fake", "expected_served_id": "fake-served"}


def generated(content):
    return {
        "content": content,
        "model_identity": {
            "configured_label": "fake",
            "expected_served_id": "fake-served",
            "served_id": "fake-served",
            "verification_status": "verified",
            "server_metadata": {},
        },
        "generation": {
            "temperature": 0.0,
            "max_tokens": 1200,
            "seed": None,
            "finish_reason": "stop",
            "usage": {},
            "timings": None,
        },
        "runtime": {
            "provider": "llama.cpp",
            "version": "test",
            "build": 1,
            "commit": "test",
            "system_fingerprint": "test",
        },
        "prompt_protocol": {
            "system_prompt_sha256": "test",
            "user_prompt_sha256": "test",
            "chat_template": None,
            "chat_template_verification": "unavailable",
        },
    }


@pytest.fixture
def experiment(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    base = tmp_path / "base"
    (base / "tests").mkdir(parents=True)
    (base / "app.py").write_text("VALUE = 1\n")
    (base / "tests" / "test_existing.py").write_text("def test_existing():\n    assert True\n")
    source = tmp_path / "experiments" / "example" / "target_tests"
    source.mkdir(parents=True)
    (source / "test_feature.py").write_text("def test_feature():\n    assert True\n")
    path = source.parent / "A.json"
    config = {"experiment": "example", "condition": "A", "model": MODEL,
              "task": "Implement the feature.", "context_files": ["app.py"],
              "target_file": "app.py", "target_tests": {"source": "target_tests"}}
    path.write_text(json.dumps(config))
    monkeypatch.setattr(runner, "BASE_REPO", base)
    monkeypatch.setattr(runner, "get_scorer", Mock(return_value=Mock()))
    monkeypatch.setattr(
        runner.provenance,
        "require_clean_git",
        lambda repository_root, manifest: manifest.setdefault(
            "repository",
            {
                "git_commit": "test-commit",
                "tracked_clean": True,
                "untracked_files": [],
            },
        ),
    )

    def populate_manifest(manifest, **kwargs):
        manifest.update(
            base_repository={"tree_sha256": "base"},
            scorer={
                "name": "example",
                "version": "example scorer v1",
                "source_sha256": "scorer",
            },
            scorer_validation={"fixture_tree_sha256": "fixtures"},
            target_tests={"tree_sha256": "target"},
            regression_tests={"tree_sha256": "regression"},
            protocol={
                "evaluation_protocol": "v2",
                "protocol_document_sha256": "protocol",
            },
        )
        return manifest

    monkeypatch.setattr(
        runner.provenance,
        "populate_run_manifest",
        populate_manifest,
    )
    monkeypatch.setattr(
        runner.provenance,
        "verify_run_manifest",
        lambda manifest, **kwargs: True,
    )
    monkeypatch.setattr(
        runner,
        "generate",
        Mock(return_value=generated("VALUE = 2\n")),
    )
    monkeypatch.setattr(runner, "score_convention", Mock(return_value={"passed": True}))
    return path, config, base, source


def suite(passed):
    return {**ev.pending_suite(), "passed": passed, "status": "completed",
            "tests_passed": int(passed), "tests_failed": int(not passed),
            "returncode": int(not passed)}


@pytest.mark.parametrize("target,regression,convention", list(itertools.product([True, False], repeat=3)))
def test_independent_gates(experiment, monkeypatch, target, regression, convention):
    path, _, _, _ = experiment
    calls = []

    def execute(workspace, location, generated):
        calls.append(location.name)
        return suite(target if location.name == ev.TARGET_DIRECTORY else regression)

    monkeypatch.setattr(ev, "run_suite", execute)
    runner.score_convention.return_value = {"passed": convention, "score": int(convention)}
    result = runner.run_experiment(path)
    assert calls == [ev.TARGET_DIRECTORY, "tests"]
    assert result["evaluation_protocol"] == "v2"
    assert result["run_status"] == "valid"
    assert result["overall_success"] is (target and regression and convention)
    for gate, expected in [("target", target), ("regression", regression), ("convention", convention)]:
        assert result["evaluation"][gate]["passed"] is expected
    saved = json.loads(next(Path("results").glob("*.json")).read_text())
    assert saved == result


def test_valid_run_keeps_uuid4_and_utc_manifest_identity(experiment, monkeypatch):
    path, _, _, _ = experiment
    monkeypatch.setattr(ev, "run_suite", lambda *args: suite(True))

    result = runner.run_experiment(path)
    manifest = result["run_manifest"]

    assert uuid.UUID(manifest["run_id"]).version == 4
    assert datetime.fromisoformat(manifest["started_at_utc"]).utcoffset() == timedelta(0)
    assert manifest["schema_version"] == "1"
    assert manifest["repository"]["tracked_clean"] is True


def test_dirty_repository_aborts_before_generation_with_partial_manifest(
    experiment,
    monkeypatch,
):
    path, _, _, _ = experiment

    def dirty_repository(_repository_root, manifest):
        manifest["repository"] = {
            "git_commit": "dirty-commit",
            "tracked_clean": False,
            "untracked_files": [],
        }
        raise runner.provenance.ProvenanceError(
            "Official Protocol-v2 runs require a clean tracked working tree",
            manifest,
        )

    monkeypatch.setattr(
        runner.provenance,
        "require_clean_git",
        dirty_repository,
    )

    result = runner.run_experiment(path)
    manifest = result["run_manifest"]

    runner.generate.assert_not_called()
    assert result["run_status"] == "invalid_infrastructure"
    assert result["overall_success"] is None
    assert result["errors"][0]["stage"] == "provenance"
    assert uuid.UUID(manifest["run_id"]).version == 4
    assert manifest["repository"]["tracked_clean"] is False
    assert "config" in manifest


def test_provenance_hash_failure_aborts_before_generation(
    experiment,
    monkeypatch,
):
    path, _, _, _ = experiment

    def fail_manifest(manifest, **_kwargs):
        manifest["base_repository"] = {"tree_sha256": "established"}
        raise runner.provenance.ProvenanceError(
            "Required provenance tree is missing",
            manifest,
        )

    monkeypatch.setattr(
        runner.provenance,
        "populate_run_manifest",
        fail_manifest,
    )

    result = runner.run_experiment(path)

    runner.generate.assert_not_called()
    assert result["run_status"] == "invalid_infrastructure"
    assert result["overall_success"] is None
    assert result["errors"][0]["stage"] == "provenance"
    assert result["run_manifest"]["base_repository"] == {
        "tree_sha256": "established"
    }


def test_final_provenance_mismatch_preserves_evaluation_and_manifest(
    experiment,
    monkeypatch,
):
    path, _, _, _ = experiment
    monkeypatch.setattr(ev, "run_suite", lambda *args: suite(True))
    observed = {}

    def fail_final_verification(manifest, **_kwargs):
        observed["manifest"] = json.loads(json.dumps(manifest))
        raise runner.provenance.ProvenanceIntegrityError(
            [
                {
                    "field": "config.sha256",
                    "expected": manifest["config"]["sha256"],
                    "actual": "changed",
                }
            ]
        )

    monkeypatch.setattr(
        runner.provenance,
        "verify_run_manifest",
        fail_final_verification,
    )

    result = runner.run_experiment(path)

    assert result["run_status"] == "invalid_infrastructure"
    assert result["overall_success"] is None
    assert result["errors"][-1]["stage"] == "provenance_integrity"
    assert result["errors"][-1]["mismatches"][0]["field"] == "config.sha256"
    assert result["run_manifest"] == observed["manifest"]
    assert result["raw_generation"] == "VALUE = 2\n"
    assert result["applied_generation"] == "VALUE = 2"
    assert result["evaluation"]["target"]["status"] == "completed"
    assert result["evaluation"]["regression"]["status"] == "completed"
    assert result["evaluation"]["convention"]["status"] == "completed"


def test_final_provenance_verifier_failure_invalidates_completed_run(
    experiment,
    monkeypatch,
):
    path, _, _, _ = experiment
    monkeypatch.setattr(ev, "run_suite", lambda *args: suite(True))
    monkeypatch.setattr(
        runner.provenance,
        "verify_run_manifest",
        Mock(side_effect=OSError("final verification unavailable")),
    )

    result = runner.run_experiment(path)

    assert result["run_status"] == "invalid_infrastructure"
    assert result["overall_success"] is None
    assert result["errors"][-1]["stage"] == "provenance_integrity"
    assert result["errors"][-1]["message"] == "final verification unavailable"
    assert result["raw_generation"] == "VALUE = 2\n"
    assert result["evaluation"]["target"]["passed"] is True
    assert result["evaluation"]["regression"]["passed"] is True
    assert result["evaluation"]["convention"]["passed"] is True


def test_privacy_lifecycle_and_source_change(experiment, monkeypatch):
    path, _, _, source = experiment
    marker = "EVALUATOR_PRIVATE_SENTINEL"
    (source / "test_feature.py").write_text(f"# {marker}\ndef test_feature():\n    assert True\n")
    events = []

    def generate(messages, model):
        workspace = next(Path("workspaces").iterdir())
        assert not (workspace / ev.TARGET_DIRECTORY).exists()
        assert not list(workspace.rglob("test_feature.py"))
        assert marker not in str(messages)
        events.append("inference")
        assert model == MODEL
        return generated("VALUE = 2\n")

    def execute(workspace, location, generated):
        assert (workspace / "app.py").read_text() == "VALUE = 2\n"
        assert marker in (workspace / ev.TARGET_DIRECTORY / "test_feature.py").read_text()
        events.append(location.name)
        return suite(True)

    monkeypatch.setattr(runner, "generate", generate)
    monkeypatch.setattr(ev, "run_suite", execute)
    assert runner.run_experiment(path)["overall_success"] is True
    assert events == ["inference", ev.TARGET_DIRECTORY, "tests"]


@pytest.mark.parametrize("setting", [None, {}, "target_tests", {"source": "missing"}, {"source": 42}])
def test_bad_target_configuration_invalid(experiment, setting):
    path, config, _, _ = experiment
    if setting is None:
        del config["target_tests"]
    else:
        config["target_tests"] = setting
    path.write_text(json.dumps(config))
    result = runner.run_experiment(path)
    assert result["run_status"] == "invalid_infrastructure"
    assert result["overall_success"] is None
    assert result["errors"]
    runner.generate.assert_not_called()


def test_source_inside_repository_rejected(experiment):
    path, config, base, _ = experiment
    config["target_tests"]["source"] = str(base / "tests")
    path.write_text(json.dumps(config))
    assert runner.run_experiment(path)["overall_success"] is None
    runner.generate.assert_not_called()


def test_old_string_model_config_is_infrastructure_invalid(experiment):
    path, config, _, _ = experiment
    config["model"] = "fake"
    path.write_text(json.dumps(config))

    result = runner.run_experiment(path)

    assert result["run_status"] == "invalid_infrastructure"
    assert result["overall_success"] is None
    assert result["errors"][0]["stage"] == "model_config"
    runner.generate.assert_not_called()


def test_inference_identity_failure_is_recorded_as_infrastructure(experiment):
    path, _, _, _ = experiment
    identity = {
        "configured_label": "fake",
        "expected_served_id": "fake-served",
        "served_id": "wrong-served",
        "verification_status": "mismatch",
        "server_metadata": {},
    }
    runner.generate.side_effect = InferenceInfrastructureError(
        "model_identity",
        "served model mismatch",
        {"model_identity": identity},
    )

    result = runner.run_experiment(path)

    assert result["run_status"] == "invalid_infrastructure"
    assert result["overall_success"] is None
    assert result["model_identity"] == identity
    assert result["errors"][0]["stage"] == "model_identity"
    assert "raw_generation" not in result


@pytest.mark.parametrize("crash", [RuntimeError("scorer crashed"), ValueError("scorer unavailable")])
def test_scorer_errors_are_infrastructure(experiment, monkeypatch, crash):
    path, _, _, _ = experiment
    monkeypatch.setattr(ev, "run_suite", lambda *args: suite(True))
    runner.score_convention.side_effect = crash
    result = runner.run_experiment(path)
    assert result["run_status"] == "invalid_infrastructure"
    assert result["overall_success"] is None
    assert result["evaluation"]["convention"]["passed"] is None
    assert result["evaluation"]["convention"]["errors"][0]["message"] == str(crash)


def test_copy_failure_is_infrastructure(experiment, monkeypatch):
    path, _, _, _ = experiment
    monkeypatch.setattr(ev, "inject_target_tests", Mock(side_effect=OSError("copy failed")))
    result = runner.run_experiment(path)
    assert result["overall_success"] is None
    assert result["evaluation"]["target"]["errors"][0]["message"] == "copy failed"


@pytest.mark.parametrize("mutation", ["modify", "delete", "rename", "replace", "add"])
def test_regression_tampering_detected(experiment, monkeypatch, mutation):
    path, config, _, _ = experiment
    # Mutation represents generated-output application, after the fingerprint.
    apply = runner.apply_multi_file_generation
    config.pop("target_file")
    config["target_files"] = ["app.py"]
    path.write_text(json.dumps(config))
    runner.generate.return_value = generated(
        "=== FILE: app.py ===\nVALUE = 2\n"
    )

    def tamper(workspace, targets, generation):
        result = apply(workspace, targets, generation)
        protected = workspace / "tests" / "test_existing.py"
        if mutation == "modify":
            protected.write_text("def test_existing():\n    assert 1 == 1\n")
        elif mutation == "delete":
            protected.unlink()
        elif mutation == "rename":
            protected.rename(protected.with_name("test_renamed.py"))
        elif mutation == "replace":
            protected.unlink()
            protected.mkdir()
        else:
            (workspace / "tests" / "conftest.py").write_text("# generated fixture override")
        return result

    monkeypatch.setattr(runner, "apply_multi_file_generation", tamper)
    execute = Mock(return_value=suite(True))
    monkeypatch.setattr(ev, "run_suite", execute)
    result = runner.run_experiment(path)
    regression = result["evaluation"]["regression"]
    assert regression["regression_tests_modified"] is True
    assert regression["changed_files"] or regression["missing_files"] or regression["added_files"]
    assert result["run_status"] == "invalid_infrastructure"
    assert regression["passed"] is None
    assert result["overall_success"] is None
    execute.assert_not_called()


def test_direct_generated_regression_edit(experiment, monkeypatch):
    path, config, _, _ = experiment
    config["target_file"] = "tests/test_existing.py"
    path.write_text(json.dumps(config))
    runner.generate.return_value = generated(
        "def test_existing():\n    assert True # changed\n"
    )
    execute = Mock(return_value=suite(True))
    monkeypatch.setattr(ev, "run_suite", execute)
    result = runner.run_experiment(path)
    assert result["evaluation"]["regression"]["changed_files"] == ["tests/test_existing.py"]
    execute.assert_not_called()


def test_leakage_still_aborts_before_inference(experiment):
    path, _, base, _ = experiment
    (base / "app.py").write_text("# Fuzzy-3\n")
    with pytest.raises(LeakageDetectedError):
        runner.run_experiment(path)
    runner.generate.assert_not_called()
    saved = json.loads(next(Path("results").glob("*.json")).read_text())
    assert saved["run_status"] == "invalid_infrastructure"
    assert saved["overall_success"] is None


def test_real_pytest_suites_are_separate(experiment):
    path, _, _, source = experiment
    (source / "test_feature.py").write_text(
        "from app import VALUE\ndef test_feature():\n    assert VALUE == 3\n")
    result = runner.run_experiment(path)
    assert result["run_status"] == "valid", result
    assert result["overall_success"] is False
    assert result["evaluation"]["target"]["tests_failed"] == 1
    assert result["evaluation"]["target"]["tests_passed"] == 0
    assert result["evaluation"]["regression"]["tests_passed"] == 1
    assert result["evaluation"]["regression"]["tests_failed"] == 0


@pytest.mark.parametrize("kind", ["syntax", "import", "setup", "missing_function"])
def test_generated_collection_setup_failure_is_model_failure(experiment, kind):
    path, _, _, source = experiment
    if kind == "syntax":
        runner.generate.return_value = generated("def broken(:\n")
    elif kind == "import":
        runner.generate.return_value = generated(
            "import nonexistent_generated_dependency\n"
        )
    elif kind == "setup":
        runner.generate.return_value = generated(
            "def feature():\n    raise ValueError('broken')\n"
        )
    else:
        runner.generate.return_value = generated("VALUE = 2\n")
    (source / "test_feature.py").write_text(
        "import app\nimport pytest\n"
        "@pytest.fixture\ndef value():\n    return app.feature()\n"
        "def test_feature(value):\n    assert value\n")
    result = runner.run_experiment(path)
    assert result["run_status"] == "valid", result
    assert result["evaluation"]["target"]["passed"] is False


def test_evaluator_syntax_failure_invalid(experiment):
    path, _, _, source = experiment
    (source / "test_feature.py").write_text("def invalid(:\n")
    result = runner.run_experiment(path)
    assert result["run_status"] == "invalid_infrastructure"
    assert result["evaluation"]["target"]["passed"] is None
    assert result["evaluation"]["regression"]["passed"] is True


def test_unavailable_pytest_invalid(tmp_path, monkeypatch):
    monkeypatch.setattr(ev.subprocess, "run", Mock(side_effect=OSError("cannot execute")))
    result = ev.run_suite(tmp_path, tmp_path / "tests", [])
    assert result["status"] == "invalid_infrastructure"
    assert result["passed"] is None


def test_save_result_never_overwrites(tmp_path, monkeypatch):
    from harness.results import save_result
    monkeypatch.chdir(tmp_path)
    result = {"experiment": "example", "condition": "A"}
    first, second = save_result(result), save_result(result)
    assert first != second
    assert first.exists() and second.exists()


def test_malformed_response_is_model_failure(experiment, monkeypatch):
    path, config, _, _ = experiment
    config.pop("target_file")
    config["target_files"] = ["app.py"]
    path.write_text(json.dumps(config))
    runner.generate.return_value = generated(
        "response without required file header"
    )
    monkeypatch.setattr(ev, "run_suite", lambda *args: suite(True))
    result = runner.run_experiment(path)
    assert result["run_status"] == "valid"
    assert result["overall_success"] is False
    assert result["evaluation"]["target"]["passed"] is False
    assert result["model_output_error"]


def test_runtime_regression_tampering_invalid(experiment, monkeypatch):
    path, _, _, _ = experiment

    def execute(workspace, location, generated):
        (workspace / "tests" / "test_existing.py").write_text("# removed by runtime code")
        return suite(True)

    monkeypatch.setattr(ev, "run_suite", execute)
    result = runner.run_experiment(path)
    assert result["overall_success"] is None
    assert result["evaluation"]["regression"]["regression_tests_modified"] is True


def test_evaluator_runtime_crash_invalid(experiment):
    path, _, _, source = experiment
    (source / "test_feature.py").write_text("def test_feature():\n    evaluator_typo()\n")
    result = runner.run_experiment(path)
    assert result["run_status"] == "invalid_infrastructure"
    assert result["evaluation"]["target"]["passed"] is None


def test_pytest_fail_is_model_failure(experiment):
    path, _, _, source = experiment
    (source / "test_feature.py").write_text(
        "import pytest\ndef test_feature():\n    pytest.fail('requirement failed')\n")
    result = runner.run_experiment(path)
    assert result["run_status"] == "valid"
    assert result["overall_success"] is False


def test_no_executed_target_tests_invalid(experiment):
    path, _, _, source = experiment
    (source / "test_feature.py").write_text("# valid Python but no tests\n")
    result = runner.run_experiment(path)
    assert result["run_status"] == "invalid_infrastructure"
    assert result["evaluation"]["target"]["passed"] is None


def test_pytest_timeout_is_infrastructure(tmp_path, monkeypatch):
    import subprocess
    monkeypatch.setattr(ev.subprocess, "run", Mock(side_effect=subprocess.TimeoutExpired(
        "pytest", 120, output=b"partial output", stderr=b"partial error")))
    result = ev.run_suite(tmp_path, tmp_path / "tests", [])
    assert result["passed"] is None
    assert result["stdout"] == "partial output"
    assert result["stderr"] == "partial error"


def test_context_cannot_point_to_private_tests(experiment):
    path, config, _, source = experiment
    config["context_files"] = [str(source / "test_feature.py")]
    path.write_text(json.dumps(config))
    assert runner.run_experiment(path)["run_status"] == "invalid_infrastructure"
    runner.generate.assert_not_called()


def test_generated_application_change_is_artifact_baseline(experiment, monkeypatch):
    path, _, _, _ = experiment
    monkeypatch.setattr(ev, "run_suite", lambda *args: suite(True))

    result = runner.run_experiment(path)

    workspace = Path(result["workspace"])
    assert (workspace / "app.py").read_text() == "VALUE = 2\n"
    assert result["run_status"] == "valid"
    assert result["evaluated_artifact_modified"] is False
    assert "app.py" in result["evaluation"]["artifact"]["fingerprints"]


def test_target_tests_mutating_application_source_invalidates_run(
    experiment,
    monkeypatch,
):
    path, _, _, _ = experiment
    calls = []

    def execute(workspace, location, generated):
        calls.append(location.name)
        (workspace / "app.py").write_text("VALUE = 99\n")
        return suite(True)

    monkeypatch.setattr(ev, "run_suite", execute)
    runner.score_convention.reset_mock()
    result = runner.run_experiment(path)

    assert calls == [ev.TARGET_DIRECTORY]
    runner.score_convention.assert_not_called()
    assert result["run_status"] == "invalid_infrastructure"
    assert result["overall_success"] is None
    assert result["evaluated_artifact_modified"] is True
    assert result["evaluated_artifact_changed_files"] == ["app.py"]
    assert result["evaluation"]["target"]["passed"] is None


def test_regression_tests_mutating_application_source_invalidates_run(
    experiment,
    monkeypatch,
):
    path, _, _, _ = experiment
    calls = []

    def execute(workspace, location, generated):
        calls.append(location.name)
        if location.name == "tests":
            (workspace / "app.py").unlink()
        return suite(True)

    monkeypatch.setattr(ev, "run_suite", execute)
    runner.score_convention.reset_mock()
    result = runner.run_experiment(path)

    assert calls == [ev.TARGET_DIRECTORY, "tests"]
    runner.score_convention.assert_not_called()
    assert result["run_status"] == "invalid_infrastructure"
    assert result["overall_success"] is None
    assert result["evaluated_artifact_modified"] is True
    assert result["evaluated_artifact_missing_files"] == ["app.py"]
    assert result["evaluation"]["regression"]["passed"] is None


def test_scorer_mutating_application_source_invalidates_run(
    experiment,
    monkeypatch,
):
    path, _, _, _ = experiment
    monkeypatch.setattr(ev, "run_suite", lambda *args: suite(True))

    def mutating_scorer(experiment_name, workspace, expected_version):
        (workspace / "app.py").write_text("VALUE = 100\n")
        return {"passed": True}

    monkeypatch.setattr(runner, "score_convention", mutating_scorer)
    result = runner.run_experiment(path)

    assert result["run_status"] == "invalid_infrastructure"
    assert result["overall_success"] is None
    assert result["evaluated_artifact_modified"] is True
    assert result["evaluated_artifact_changed_files"] == ["app.py"]
    assert result["evaluation"]["convention"]["passed"] is None


def test_evaluator_runtime_artifacts_are_excluded(experiment, monkeypatch):
    path, _, _, _ = experiment

    def execute(workspace, location, generated):
        for directory in (
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            ".hypothesis",
        ):
            cache = workspace / directory
            cache.mkdir(exist_ok=True)
            (cache / "runtime.dat").write_text("cache")
        (workspace / "module.pyc").write_bytes(b"cache")
        (workspace / ".coverage").write_text("coverage")
        (workspace / "coverage.xml").write_text("coverage")
        return suite(True)

    monkeypatch.setattr(ev, "run_suite", execute)
    result = runner.run_experiment(path)

    assert result["run_status"] == "valid"
    assert result["evaluated_artifact_modified"] is False
    assert result["overall_success"] is True


def test_normal_evaluation_checks_artifact_after_every_gate(
    experiment,
    monkeypatch,
):
    path, _, _, _ = experiment
    monkeypatch.setattr(ev, "run_suite", lambda *args: suite(True))

    result = runner.run_experiment(path)

    assert result["run_status"] == "valid"
    assert result["overall_success"] is True
    assert [
        check["stage"] for check in result["evaluation"]["artifact"]["checks"]
    ] == ["target", "regression", "convention"]
