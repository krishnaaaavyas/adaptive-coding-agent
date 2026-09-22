# Model identity and reproducibility

Protocol-v2 experiment configurations distinguish the human-readable model
label from the exact llama.cpp expected_served_id. Before completion, the
harness reads /v1/models and requires the single served model ID to equal the
configured expected ID exactly. Missing, ambiguous, unavailable, malformed, or
mismatched identity information makes the run infrastructure-invalid because
the generating model cannot be proven.

The result records model format, quantization, parameter count, active context
length, and training context length from /v1/models when llama.cpp exposes
them. Completion metadata supplies the finish reason, token usage (including
cached prompt tokens when available), timings, reported model ID validation,
and system fingerprint. The configured temperature, maximum token count, and
seed are recorded alongside that response metadata.

Runtime version, build, and commit are obtained dynamically by executing
llama-server --version; they are never treated as constants. The executable
may be selected with LLAMA_SERVER_EXECUTABLE. An unavailable or unparseable
version is infrastructure-invalid.

SHA-256 hashes are computed from the exact system and user strings sent to
inference. llama.cpp does not currently expose the applied chat template
authoritatively through this harness, so chat_template remains null and
chat_template_verification is unavailable. Other optional metadata also
remains null when the runtime does not provide it; the harness does not infer
or invent values.
