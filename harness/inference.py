"""Verified llama.cpp inference and reproducibility metadata."""

import hashlib
import os
import re
import subprocess

import requests


LLAMA_BASE_URL = "http://127.0.0.1:8080"
MODELS_URL = f"{LLAMA_BASE_URL}/v1/models"
COMPLETIONS_URL = f"{LLAMA_BASE_URL}/v1/chat/completions"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 1200
DEFAULT_SEED = None
VERSION_PATTERN = re.compile(
    r"^version:\s*(\S+)\s+\(build\s+(\d+),\s+commit\s+([^)]+)\)",
    re.MULTILINE,
)


class InferenceInfrastructureError(RuntimeError):
    """A failure in model/runtime verification or the inference transport."""

    def __init__(self, stage, message, metadata=None):
        super().__init__(message)
        self.stage = stage
        self.metadata = metadata or {}


def validate_model_config(model):
    if not isinstance(model, dict):
        raise InferenceInfrastructureError(
            "model_config",
            "Experiment model must be an object with label and expected_served_id",
        )
    label = model.get("label")
    expected = model.get("expected_served_id")
    if not isinstance(label, str) or not label.strip():
        raise InferenceInfrastructureError(
            "model_config",
            "model.label must be a nonempty string",
        )
    if not isinstance(expected, str) or not expected.strip():
        raise InferenceInfrastructureError(
            "model_config",
            "model.expected_served_id must be a nonempty string",
            {
                "model_identity": {
                    "configured_label": label,
                    "expected_served_id": expected,
                    "served_id": None,
                    "verification_status": "invalid_config",
                    "server_metadata": _empty_server_metadata(),
                }
            },
        )
    return {"label": label, "expected_served_id": expected}


def _empty_server_metadata():
    return {
        "format": None,
        "quantization": None,
        "parameter_count": None,
        "context_length": None,
        "training_context_length": None,
    }


def initial_model_identity(model):
    validated = validate_model_config(model)
    return {
        "configured_label": validated["label"],
        "expected_served_id": validated["expected_served_id"],
        "served_id": None,
        "verification_status": "not_checked",
        "server_metadata": _empty_server_metadata(),
    }


def _response_json(response, stage):
    try:
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise InferenceInfrastructureError(
            stage,
            f"llama.cpp {stage} response was unavailable or malformed: {exc}",
        ) from exc
    if not isinstance(data, dict):
        raise InferenceInfrastructureError(
            stage,
            f"llama.cpp {stage} response must be a JSON object",
        )
    return data


def inspect_model_identity(model, timeout=30):
    validated = validate_model_config(model)
    identity = initial_model_identity(validated)
    try:
        response = requests.get(MODELS_URL, timeout=timeout)
        data = _response_json(response, "model_identity")
    except requests.RequestException as exc:
        identity["verification_status"] = "unavailable"
        raise InferenceInfrastructureError(
            "model_identity",
            f"Could not inspect llama.cpp served models: {exc}",
            {"model_identity": identity},
        ) from exc
    except InferenceInfrastructureError as exc:
        identity["verification_status"] = "invalid_response"
        exc.metadata["model_identity"] = identity
        raise

    models = data.get("data")
    if not isinstance(models, list):
        identity["verification_status"] = "invalid_response"
        raise InferenceInfrastructureError(
            "model_identity",
            "llama.cpp /v1/models response must contain a data list",
            {"model_identity": identity},
        )
    if not models:
        identity["verification_status"] = "no_model"
        raise InferenceInfrastructureError(
            "model_identity",
            "llama.cpp /v1/models reported no served model",
            {"model_identity": identity},
        )
    if len(models) != 1:
        identity["verification_status"] = "ambiguous"
        raise InferenceInfrastructureError(
            "model_identity",
            "llama.cpp /v1/models must report exactly one served model",
            {"model_identity": identity},
        )

    served = models[0]
    if not isinstance(served, dict) or not isinstance(served.get("id"), str):
        identity["verification_status"] = "invalid_response"
        raise InferenceInfrastructureError(
            "model_identity",
            "llama.cpp served-model entry is malformed or has no string id",
            {"model_identity": identity},
        )

    model_entries = data.get("models")
    matching_model_entries = []
    if isinstance(model_entries, list):
        matching_model_entries = [
            entry
            for entry in model_entries
            if isinstance(entry, dict)
            and (
                entry.get("model") == served["id"]
                or entry.get("name") == served["id"]
            )
        ]
    details = {}
    if len(matching_model_entries) == 1:
        candidate_details = matching_model_entries[0].get("details")
        if isinstance(candidate_details, dict):
            details = candidate_details
    meta = served.get("meta")
    if not isinstance(meta, dict):
        meta = {}
    identity.update(
        served_id=served["id"],
        server_metadata={
            "format": details.get("format"),
            "quantization": meta.get("ftype"),
            "parameter_count": meta.get("n_params"),
            "context_length": meta.get("n_ctx"),
            "training_context_length": meta.get("n_ctx_train"),
        },
    )
    if served["id"] != validated["expected_served_id"]:
        identity["verification_status"] = "mismatch"
        raise InferenceInfrastructureError(
            "model_identity",
            "Configured expected_served_id does not match the served model id",
            {"model_identity": identity},
        )
    identity["verification_status"] = "verified"
    return identity


def parse_runtime_version(output):
    if not isinstance(output, str):
        raise InferenceInfrastructureError(
            "runtime_identity",
            "llama-server version output must be text",
        )
    match = VERSION_PATTERN.search(output)
    if not match:
        raise InferenceInfrastructureError(
            "runtime_identity",
            "Could not parse llama-server version, build, and commit",
        )
    return {
        "provider": "llama.cpp",
        "version": match.group(1),
        "build": int(match.group(2)),
        "commit": match.group(3).strip(),
        "system_fingerprint": None,
    }


def inspect_runtime_identity(executable=None, timeout=30):
    executable = executable or os.environ.get(
        "LLAMA_SERVER_EXECUTABLE",
        "llama-server",
    )
    try:
        process = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise InferenceInfrastructureError(
            "runtime_identity",
            f"Could not execute llama-server --version: {exc}",
        ) from exc
    output = "\n".join(part for part in (process.stdout, process.stderr) if part)
    if process.returncode != 0:
        raise InferenceInfrastructureError(
            "runtime_identity",
            f"llama-server --version failed with exit code {process.returncode}",
        )
    return parse_runtime_version(output)


def build_prompt_protocol(messages):
    if not isinstance(messages, list):
        raise InferenceInfrastructureError(
            "prompt_protocol",
            "Inference messages must be a list",
        )
    system_messages = [
        message.get("content")
        for message in messages
        if isinstance(message, dict) and message.get("role") == "system"
    ]
    user_messages = [
        message.get("content")
        for message in messages
        if isinstance(message, dict) and message.get("role") == "user"
    ]
    if (
        len(system_messages) != 1
        or len(user_messages) != 1
        or not isinstance(system_messages[0], str)
        or not isinstance(user_messages[0], str)
    ):
        raise InferenceInfrastructureError(
            "prompt_protocol",
            "Exactly one string system prompt and one string user prompt are required",
        )
    return {
        "system_prompt_sha256": hashlib.sha256(
            system_messages[0].encode("utf-8")
        ).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(
            user_messages[0].encode("utf-8")
        ).hexdigest(),
        "chat_template": None,
        "chat_template_verification": "unavailable",
    }


def _completion_metadata(data, temperature, max_tokens, seed):
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise InferenceInfrastructureError(
            "completion",
            "Completion response must contain choices[0]",
        )
    message = choices[0].get("message")
    if not isinstance(message, dict) or not isinstance(message.get("content"), str):
        raise InferenceInfrastructureError(
            "completion",
            "Completion response must contain string choices[0].message.content",
        )
    usage = data.get("usage")
    if not isinstance(usage, dict):
        usage = {}
    prompt_details = usage.get("prompt_tokens_details")
    if not isinstance(prompt_details, dict):
        prompt_details = {}
    return {
        "content": message["content"],
        "generation": {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "seed": seed,
            "finish_reason": choices[0].get("finish_reason"),
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "cached_tokens": prompt_details.get("cached_tokens"),
            },
            "timings": data.get("timings"),
        },
        "system_fingerprint": data.get("system_fingerprint"),
    }


def generate(
    messages,
    model,
    temperature=DEFAULT_TEMPERATURE,
    max_tokens=DEFAULT_MAX_TOKENS,
    seed=DEFAULT_SEED,
):
    """Verify llama.cpp identity, generate, and return structured metadata."""
    prompt_protocol = build_prompt_protocol(messages)
    identity = initial_model_identity(model)
    try:
        identity = inspect_model_identity(model)
        runtime = inspect_runtime_identity()
    except InferenceInfrastructureError as exc:
        exc.metadata.setdefault("model_identity", identity)
        exc.metadata.setdefault("prompt_protocol", prompt_protocol)
        raise

    payload = {
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if seed is not None:
        payload["seed"] = seed
    try:
        response = requests.post(
            COMPLETIONS_URL,
            json=payload,
            timeout=300,
        )
        data = _response_json(response, "completion")
        completion = _completion_metadata(
            data,
            temperature,
            max_tokens,
            seed,
        )
    except requests.RequestException as exc:
        raise InferenceInfrastructureError(
            "completion",
            f"llama.cpp completion request failed: {exc}",
            {
                "model_identity": identity,
                "runtime": runtime,
                "prompt_protocol": prompt_protocol,
            },
        ) from exc
    except InferenceInfrastructureError as exc:
        exc.metadata.update(
            model_identity=identity,
            runtime=runtime,
            prompt_protocol=prompt_protocol,
        )
        raise

    completion_model = data.get("model")
    if completion_model != identity["expected_served_id"]:
        identity["verification_status"] = "completion_mismatch"
        runtime["system_fingerprint"] = completion["system_fingerprint"]
        raise InferenceInfrastructureError(
            "completion_model_identity",
            "Completion-reported model does not match expected_served_id",
            {
                "model_identity": identity,
                "runtime": runtime,
                "prompt_protocol": prompt_protocol,
            },
        )

    runtime["system_fingerprint"] = completion.pop("system_fingerprint")
    return {
        "content": completion["content"],
        "model_identity": identity,
        "generation": completion["generation"],
        "runtime": runtime,
        "prompt_protocol": prompt_protocol,
    }
