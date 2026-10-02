"""No-generation runtime admission and lossless complete-file output protocol."""

from dataclasses import dataclass
import re

from .core import (CONDITIONS, GENERATION, SYSTEM, Diagnostic, canonical_json, digest,
                   fail, normalized_text, raise_diagnostics, require_auth)
from .boundary import path
from .evidence import pack_h

HEADER = re.compile(r"^=== FILE: (.+) ===$")
CONTROL_VALUES = {"decoding": "greedy", "temperature": 0, "top_p": 1, "top_k": "disabled",
                  "repetition_penalty": 1, "frequency_penalty": 0, "presence_penalty": 0,
                  "seed": 0, "text_stops": [], "max_generation": 2048, "completions": 1,
                  "retries": 0, "context_shifting": False, "clipping": False, "truncation": False}


@dataclass(frozen=True)
class TokenizerInterface:
    """Externally verified pure encoding callbacks. No completion transport."""
    model_sha256: str
    tokenizer_sha256: str
    template_sha256: str
    raw_encode: object
    rendered_encode: object


def validate_profile(profile, certificate, auth, tokenizer, *, mode="official"):
    require_auth(auth, profile, certificate, mode)
    diagnostics = []
    required = {"model_sha256", "tokenizer_sha256", "template_sha256", "system_sha256", "capacity", "controls",
                "native_terminal_ids", "terminal_allowance", "reference_encoding", "generation_prompt_sha256",
                "request_isolation", "runtime_identity", "determinism_limitations", "runtime_argument_types"}
    if not isinstance(profile, dict) or set(profile) != required:
        fail("infrastructure_invalid", "run_profile_invalid", 1)
    if (not isinstance(profile["reference_encoding"], dict) or not isinstance(profile["runtime_argument_types"], dict)
            or set(profile["runtime_argument_types"]) != set(CONTROL_VALUES)
            or any(t not in ("integer", "decimal", "boolean", "string", "array", "native", "unsupported") for t in profile["runtime_argument_types"].values())):
        fail("infrastructure_invalid", "run_profile_invalid", 1)
    if (type(profile["capacity"]) is not int or profile["capacity"] <= 0
            or profile["system_sha256"] != digest(SYSTEM.encode())
            or type(profile["terminal_allowance"]) is not int or profile["terminal_allowance"] != 1
            or not isinstance(profile["native_terminal_ids"], list) or not profile["native_terminal_ids"]
            or any(type(t) is not int or t < 0 for t in profile["native_terminal_ids"])
            or profile["request_isolation"] != "fresh_sequence"
            or profile["reference_encoding"].get("bos") is not False
            or profile["reference_encoding"].get("eos") is not False
            or profile["reference_encoding"].get("truncation") is not False
            or not profile["runtime_identity"]):
        diagnostics.append(Diagnostic("infrastructure_invalid", "run_profile_invalid", 1))
    if not isinstance(profile["controls"], dict) or set(profile["controls"]) != set(CONTROL_VALUES):
        diagnostics.append(Diagnostic("infrastructure_invalid", "generation_controls_invalid", 1))
    else:
        for key, requested in CONTROL_VALUES.items():
            setting = profile["controls"][key]
            if (not isinstance(setting, dict) or set(setting) != {"support", "requested", "effective", "verification"}
                    or type(setting["requested"]) is not type(requested) or setting["requested"] != requested or not setting["verification"]
                    or setting["support"] not in ("verified", "unsupported")):
                diagnostics.append(Diagnostic("infrastructure_invalid", "generation_controls_invalid", 1, key))
                continue
            if profile["runtime_argument_types"][key] == "unsupported" and setting["support"] != "unsupported":
                diagnostics.append(Diagnostic("infrastructure_invalid", "generation_controls_invalid", 1, key))
            if key == "seed" and setting["support"] == "unsupported":
                if setting["effective"] != "unsupported":
                    diagnostics.append(Diagnostic("infrastructure_invalid", "generation_controls_invalid", 1, key))
            elif setting["effective"] != requested:
                diagnostics.append(Diagnostic("infrastructure_invalid", "generation_controls_invalid", 1, key))
            elif setting["support"] == "unsupported" and key not in ("top_p", "top_k", "repetition_penalty", "frequency_penalty", "presence_penalty"):
                diagnostics.append(Diagnostic("infrastructure_invalid", "generation_controls_invalid", 1, key))
    for key in ("model_sha256", "tokenizer_sha256", "template_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", str(profile[key])) or getattr(tokenizer, key, None) != profile[key]:
            diagnostics.append(Diagnostic("infrastructure_invalid", "tokenizer_identity_mismatch", 1))
    if not re.fullmatch(r"[0-9a-f]{64}", str(profile["generation_prompt_sha256"])):
        diagnostics.append(Diagnostic("infrastructure_invalid", "run_profile_invalid", 1))
    raise_diagnostics(diagnostics)


def messages(task, k, h):
    if digest(k.serialized) != k.sha256 or digest(h.serialized) != h.sha256:
        fail("infrastructure_invalid", "payload_hash_mismatch", 1)
    user = b"[PUBLIC_TASK]\n" + task.serialized + b"\n[/PUBLIC_TASK]\n" + k.serialized + h.serialized
    return ({"role": "system", "content": SYSTEM}, {"role": "user", "content": user.decode("utf-8")})


def reserved_preflight(task, snapshot):
    diagnostics = []
    if len(task.targets) > 1:
        for target in task.targets:
            if target in snapshot.files and any(HEADER.fullmatch(line) for line in snapshot.files[target].split("\n")):
                diagnostics.append(Diagnostic("task_invalid", "reserved_output_header", 4))
    raise_diagnostics(diagnostics)


def reference_artifact(task, snapshot):
    if len(task.targets) == 1:
        return snapshot.files.get(task.targets[0], "").encode()
    parts = []
    for n, target in enumerate(task.targets):
        content = snapshot.files.get(target, "")
        parts.extend((f"=== FILE: {target} ===\n", content))
        if n + 1 < len(task.targets) and content and not content.endswith("\n"):
            parts.append("\n")
    return "".join(parts).encode()


def token_count(callback, text):
    try:
        tokens = callback(text)
        if not isinstance(tokens, (list, tuple)) or any(type(t) is not int or t < 0 for t in tokens):
            raise ValueError("invalid token vector")
        return len(tokens)
    except Exception:
        fail("infrastructure_invalid", "tokenization_unavailable", 1)


def output_preflight(task, snapshot, tokenizer):
    reserved_preflight(task, snapshot)
    artifact = reference_artifact(task, snapshot)
    count = token_count(tokenizer.raw_encode, artifact.decode())
    if count + 1 > GENERATION:
        fail("context_ineligible", "output_reference_overflow", 4)
    return artifact, count


@dataclass(frozen=True)
class PreparedConditions:
    messages: tuple
    adaptation: tuple
    input_tokens: tuple
    reference_bytes: bytes
    reference_tokens: int
    k_sha256: str
    profile_sha256: str


def treatments(task, snapshot, k, view, profile, tokenizer, reference):
    diagnostics, requests, payloads, counts = [], [], [], []
    for condition in CONDITIONS:
        h = pack_h(condition, view, snapshot)
        request = messages(task, k, h)
        count = token_count(tokenizer.rendered_encode, request)
        if count + GENERATION > profile["capacity"]:
            diagnostics.append(Diagnostic("context_ineligible", "runtime_overflow", 5, condition))
        requests.append((condition, request))
        payloads.append((condition, h))
        counts.append((condition, count))
    raise_diagnostics(diagnostics)
    return PreparedConditions(tuple(requests), tuple(payloads), tuple(counts), reference[0], reference[1],
                              k.sha256, digest(canonical_json(profile)))


def common_admission(matrix, model_roster, task_roster):
    diagnostics = []
    for task in task_roster:
        for model in model_roster:
            status = matrix.get((task, model))
            if status is None or status == "infrastructure_invalid":
                diagnostics.append(Diagnostic("infrastructure_invalid", "common_admission_unverified", 5))
            elif status not in ("admitted", "task_invalid", "context_ineligible"):
                diagnostics.append(Diagnostic("infrastructure_invalid", "common_admission_invalid", 5))
    raise_diagnostics(diagnostics)
    common = tuple(task for task in task_roster if all(matrix[(task, model)] == "admitted" for model in model_roster))
    identity = digest(canonical_json({"models": list(model_roster), "tasks": list(task_roster), "common": list(common)}))
    return common, identity


@dataclass(frozen=True)
class OutputResult:
    category: str
    artifacts: tuple
    raw_sha256: str | None
    normalized_sha256: str | None
    diagnostics: tuple
    output_tokens: int | None


def completion(text, task, *, integrity_verified, token_limit, output_tokens):
    diagnostics, artifacts, raw_hash, normalized_hash = [], [], None, None
    if not integrity_verified:
        return OutputResult("infrastructure_invalid", (), None, None, ("runtime_integrity",), output_tokens)
    try:
        raw_hash = digest(text.encode("utf-8"))
        normalized = normalized_text(text, bom=False)
        normalized_hash = digest(normalized.encode())
    except (UnicodeError, ValueError, AttributeError):
        normalized = None
        diagnostics.append("invalid_completion_text")
    if normalized is not None:
        if len(task.targets) == 1:
            artifacts = [(task.targets[0], normalized)]
        else:
            headers, offset = [], 0
            for line in normalized.split("\n"):
                match = HEADER.fullmatch(line)
                if match:
                    candidate = match.group(1)
                    has_lf = offset + len(line) < len(normalized)
                    try:
                        path(candidate)
                    except (ValueError, UnicodeError):
                        diagnostics.append("invalid_output_path")
                    if not has_lf:
                        diagnostics.append("header_missing_lf")
                    headers.append((candidate, offset, offset + len(line) + 1))
                offset += len(line) + 1
            if not headers or headers[0][1] != 0:
                diagnostics.append("first_header_not_zero")
            if tuple(row[0] for row in headers) != task.targets:
                diagnostics.append("header_vector_mismatch")
            if not diagnostics:
                artifacts = [(row[0], normalized[row[2]:headers[n + 1][1] if n + 1 < len(headers) else len(normalized)]) for n, row in enumerate(headers)]
    category = "output_capacity_failure" if token_limit else "output_format_failure" if diagnostics else "artifact_ready"
    return OutputResult(category, tuple(artifacts), raw_hash, normalized_hash, tuple(sorted(set(diagnostics))), output_tokens)
