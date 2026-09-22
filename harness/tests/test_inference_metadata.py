import hashlib
import json
import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests

from harness import inference


EXPECTED_ID = "Qwen/Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M"
MODEL = {
    "label": "Qwen2.5-Coder-7B-Instruct-Q4_K_M",
    "expected_served_id": EXPECTED_ID,
}
MESSAGES = [
    {"role": "system", "content": "system text\n"},
    {"role": "user", "content": "user text  "},
]


def response(payload=None, json_error=None):
    result = Mock()
    result.raise_for_status.return_value = None
    if json_error is None:
        result.json.return_value = payload
    else:
        result.json.side_effect = json_error
    return result


def models_payload(model_id=EXPECTED_ID, include_metadata=True):
    model = {"id": model_id}
    payload = {"object": "list", "data": [model]}
    if include_metadata:
        payload["models"] = [
            {
                "name": model_id,
                "model": model_id,
                "details": {"format": "gguf"},
            }
        ]
        model["meta"] = {
                "ftype": "Q4_K - Medium",
                "n_params": 7_615_616_512,
                "n_ctx": 4_096,
                "n_ctx_train": 131_072,
            }
    return payload


def runtime_process(output=None):
    return subprocess.CompletedProcess(
        ["llama-server", "--version"],
        0,
        stdout=output or (
            "version: 0.4.1-dev "
            "(build 11026, commit b49650adb)\nbuilt with MSVC\n"
        ),
        stderr="",
    )


def completion_payload(model_id=EXPECTED_ID):
    return {
        "model": model_id,
        "system_fingerprint": "b49650adb",
        "choices": [
            {
                "message": {"content": "  value = 1\n\n"},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 11,
            "completion_tokens": 7,
            "total_tokens": 18,
            "prompt_tokens_details": {"cached_tokens": 5},
        },
        "timings": {"prompt_ms": 2.5, "predicted_ms": 4.0},
    }


def test_matching_served_id_and_current_metadata_shape(monkeypatch):
    monkeypatch.setattr(
        inference.requests,
        "get",
        Mock(return_value=response(models_payload())),
    )

    identity = inference.inspect_model_identity(MODEL)

    assert identity == {
        "configured_label": MODEL["label"],
        "expected_served_id": EXPECTED_ID,
        "served_id": EXPECTED_ID,
        "verification_status": "verified",
        "server_metadata": {
            "format": "gguf",
            "quantization": "Q4_K - Medium",
            "parameter_count": 7_615_616_512,
            "context_length": 4_096,
            "training_context_length": 131_072,
        },
    }


def test_top_level_models_absent_keeps_verified_identity(monkeypatch):
    payload = models_payload()
    del payload["models"]
    monkeypatch.setattr(
        inference.requests,
        "get",
        Mock(return_value=response(payload)),
    )

    identity = inference.inspect_model_identity(MODEL)

    assert identity["verification_status"] == "verified"
    assert identity["served_id"] == EXPECTED_ID
    assert identity["server_metadata"]["format"] is None


def test_nonmatching_top_level_model_has_null_format(monkeypatch):
    payload = models_payload()
    payload["models"][0]["model"] = "different-model"
    payload["models"][0]["name"] = "different-model"
    monkeypatch.setattr(
        inference.requests,
        "get",
        Mock(return_value=response(payload)),
    )

    identity = inference.inspect_model_identity(MODEL)

    assert identity["verification_status"] == "verified"
    assert identity["server_metadata"]["format"] is None


def test_multiple_exact_top_level_model_matches_have_null_format(monkeypatch):
    payload = models_payload()
    payload["models"].append(
        {
            "name": EXPECTED_ID,
            "model": EXPECTED_ID,
            "details": {"format": "gguf"},
        }
    )
    monkeypatch.setattr(
        inference.requests,
        "get",
        Mock(return_value=response(payload)),
    )

    identity = inference.inspect_model_identity(MODEL)

    assert identity["verification_status"] == "verified"
    assert identity["server_metadata"]["format"] is None


def test_absent_optional_server_metadata_is_null(monkeypatch):
    monkeypatch.setattr(
        inference.requests,
        "get",
        Mock(return_value=response(models_payload(include_metadata=False))),
    )

    metadata = inference.inspect_model_identity(MODEL)["server_metadata"]

    assert metadata == {
        "format": None,
        "quantization": None,
        "parameter_count": None,
        "context_length": None,
        "training_context_length": None,
    }


@pytest.mark.parametrize(
    "payload,status",
    [
        ({"wrong": []}, "invalid_response"),
        ({"data": []}, "no_model"),
        (
            {
                "data": [
                    {"id": EXPECTED_ID},
                    {"id": "another-model"},
                ]
            },
            "ambiguous",
        ),
    ],
)
def test_invalid_models_responses_fail(payload, status, monkeypatch):
    monkeypatch.setattr(
        inference.requests,
        "get",
        Mock(return_value=response(payload)),
    )

    with pytest.raises(inference.InferenceInfrastructureError) as exc_info:
        inference.inspect_model_identity(MODEL)

    assert exc_info.value.metadata["model_identity"]["verification_status"] == status


def test_malformed_models_json_fails(monkeypatch):
    monkeypatch.setattr(
        inference.requests,
        "get",
        Mock(return_value=response(json_error=ValueError("invalid json"))),
    )

    with pytest.raises(inference.InferenceInfrastructureError) as exc_info:
        inference.inspect_model_identity(MODEL)

    assert exc_info.value.metadata["model_identity"]["verification_status"] == (
        "invalid_response"
    )


def test_unavailable_models_server_fails(monkeypatch):
    monkeypatch.setattr(
        inference.requests,
        "get",
        Mock(side_effect=requests.ConnectionError("refused")),
    )

    with pytest.raises(inference.InferenceInfrastructureError) as exc_info:
        inference.inspect_model_identity(MODEL)

    assert exc_info.value.metadata["model_identity"]["verification_status"] == (
        "unavailable"
    )


def test_identity_mismatch_aborts_before_completion(monkeypatch):
    post = Mock()
    monkeypatch.setattr(
        inference.requests,
        "get",
        Mock(return_value=response(models_payload("wrong-model"))),
    )
    monkeypatch.setattr(inference.requests, "post", post)

    with pytest.raises(inference.InferenceInfrastructureError) as exc_info:
        inference.generate(MESSAGES, MODEL)

    assert exc_info.value.stage == "model_identity"
    assert exc_info.value.metadata["model_identity"]["verification_status"] == (
        "mismatch"
    )
    post.assert_not_called()


def test_missing_expected_served_id_and_old_string_are_rejected():
    with pytest.raises(inference.InferenceInfrastructureError):
        inference.validate_model_config({"label": "Qwen"})
    with pytest.raises(inference.InferenceInfrastructureError):
        inference.validate_model_config("Qwen")


def test_completion_metadata_and_content_are_preserved(monkeypatch):
    post = Mock(return_value=response(completion_payload()))
    monkeypatch.setattr(
        inference.requests,
        "get",
        Mock(return_value=response(models_payload())),
    )
    monkeypatch.setattr(inference.requests, "post", post)
    monkeypatch.setattr(
        inference.subprocess,
        "run",
        Mock(return_value=runtime_process()),
    )

    result = inference.generate(MESSAGES, MODEL)

    assert result["content"] == "  value = 1\n\n"
    assert result["generation"] == {
        "temperature": 0.0,
        "max_tokens": 1200,
        "seed": None,
        "finish_reason": "stop",
        "usage": {
            "prompt_tokens": 11,
            "completion_tokens": 7,
            "total_tokens": 18,
            "cached_tokens": 5,
        },
        "timings": {"prompt_ms": 2.5, "predicted_ms": 4.0},
    }
    assert result["runtime"] == {
        "provider": "llama.cpp",
        "version": "0.4.1-dev",
        "build": 11026,
        "commit": "b49650adb",
        "system_fingerprint": "b49650adb",
    }
    assert post.call_args.kwargs["json"] == {
        "messages": MESSAGES,
        "temperature": 0.0,
        "max_tokens": 1200,
    }


def test_completion_reported_model_mismatch_is_rejected(monkeypatch):
    monkeypatch.setattr(
        inference.requests,
        "get",
        Mock(return_value=response(models_payload())),
    )
    monkeypatch.setattr(
        inference.subprocess,
        "run",
        Mock(return_value=runtime_process()),
    )
    monkeypatch.setattr(
        inference.requests,
        "post",
        Mock(return_value=response(completion_payload("wrong-model"))),
    )

    with pytest.raises(inference.InferenceInfrastructureError) as exc_info:
        inference.generate(MESSAGES, MODEL)

    assert exc_info.value.stage == "completion_model_identity"
    assert exc_info.value.metadata["model_identity"]["verification_status"] == (
        "completion_mismatch"
    )


def test_current_runtime_version_format_parses():
    assert inference.parse_runtime_version(
        "version: 0.4.1-dev (build 11026, commit b49650adb)\nbuilt with MSVC"
    ) == {
        "provider": "llama.cpp",
        "version": "0.4.1-dev",
        "build": 11026,
        "commit": "b49650adb",
        "system_fingerprint": None,
    }


@pytest.mark.parametrize(
    "effect",
    [
        OSError("missing executable"),
        subprocess.TimeoutExpired("llama-server", 30),
    ],
)
def test_unavailable_runtime_version_fails(effect, monkeypatch):
    monkeypatch.setattr(
        inference.subprocess,
        "run",
        Mock(side_effect=effect),
    )

    with pytest.raises(inference.InferenceInfrastructureError) as exc_info:
        inference.inspect_runtime_identity()

    assert exc_info.value.stage == "runtime_identity"


def test_malformed_runtime_version_fails(monkeypatch):
    monkeypatch.setattr(
        inference.subprocess,
        "run",
        Mock(return_value=runtime_process("unparseable output")),
    )

    with pytest.raises(inference.InferenceInfrastructureError):
        inference.inspect_runtime_identity()


def test_runtime_failure_aborts_before_completion(monkeypatch):
    post = Mock()
    monkeypatch.setattr(
        inference.requests,
        "get",
        Mock(return_value=response(models_payload())),
    )
    monkeypatch.setattr(
        inference.subprocess,
        "run",
        Mock(side_effect=OSError("missing executable")),
    )
    monkeypatch.setattr(inference.requests, "post", post)

    with pytest.raises(inference.InferenceInfrastructureError) as exc_info:
        inference.generate(MESSAGES, MODEL)

    assert exc_info.value.stage == "runtime_identity"
    post.assert_not_called()


def test_prompt_hashes_match_exact_sent_strings():
    protocol = inference.build_prompt_protocol(MESSAGES)

    assert protocol["system_prompt_sha256"] == hashlib.sha256(
        MESSAGES[0]["content"].encode("utf-8")
    ).hexdigest()
    assert protocol["user_prompt_sha256"] == hashlib.sha256(
        MESSAGES[1]["content"].encode("utf-8")
    ).hexdigest()
    assert protocol["chat_template"] is None
    assert protocol["chat_template_verification"] == "unavailable"


def test_all_migrated_experiment_configs_validate():
    paths = sorted(Path("experiments").glob("*.json"))

    assert len(paths) == 18
    for path in paths:
        model = json.loads(path.read_text(encoding="utf-8"))["model"]
        assert inference.validate_model_config(model) == MODEL
