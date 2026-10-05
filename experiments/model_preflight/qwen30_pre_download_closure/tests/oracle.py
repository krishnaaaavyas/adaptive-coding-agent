"""Literal independent oracle; imports no production runner/constants/functions."""
CONTROLS = {'decoding': 'greedy', 'temperature': 0, 'top_p': 1, 'top_k': 'disabled',
    'repetition_penalty': 1, 'frequency_penalty': 0, 'presence_penalty': 0, 'seed': 0,
    'text_stops': [], 'max_generation': 2048, 'completions': 1, 'retries': 0,
    'context_shifting': False, 'clipping': False, 'truncation': False}
TABLE = {'0': '21', '5': '41', '6': '610d0a620d630a', '7': 'ff', '8': '42',
    '151645': '3c7c696d5f656e647c3e', '151643': '3c7c656e646f66746578747c3e'}
NORMAL_RAW_HEX = '413c7c696d5f656e647c3e'
NORMAL_NORMALIZED_HEX = '41'
LINE_NORMALIZED_HEX = '610a620a630a'
INTERNAL_NORMALIZED_HEX = '3c7c696d5f656e647c3e41'
ONE_CALL = 1
RETRIES = 0
LENGTH_COUNT = 2048
REQUIRED_FIELDS = ['schema_version','run_kind','run_id', 'timestamp', 'checkpoint_repo', 'checkpoint_SHA', 'checkpoint_body_hashes',
    'container_digest', 'runtime_identities', 'GPU', 'driver', 'CUDA', 'frozen_control_values',
    'prompt_fixture_id', 'prompt_fixture_sha256', 'exact_prompt_token_count', 'exact_prompt_token_ids',
    'raw_generated_token_ids', 'raw_generated_bytes_sha256', 'generated_token_count', 'finish_reason',
    'stop_reason', 'terminal_token', 'terminal_removal_receipt', 'normalized_completion_sha256',
    'wall_time', 'TTFT', 'throughput', 'peak_VRAM', 'peak_host_RAM', 'isolation_result',
    'gate_result', 'failure_classification', 'provenance_artifact_hashes', 'invocation_count', 'retry_count',
    'effective_control_receipt_sha256','raw_generated_bytes_artifact','raw_byte_length','resource_telemetry_sha256',
    'isolation_receipt_sha256','gate_id','failure_id','prerequisite_run_ids','parent_original_SHA',
    'adapter_identity_sha256','derivative_identity_sha256','freshness_receipt_sha256','notes']
DISPOSITIONS = {'normal': ['PASS', None], 'length': ['PASS', None], 'line_endings': ['PASS', None],
    'internal_special': ['PASS', None], 'invalid_utf8': ['FAIL', 'B'], 'retry_violation': ['FAIL', 'B'],
    'controls_violation': ['FAIL', 'B'], 'stale_history': ['FAIL', 'B'], 'injected_failure': ['FAIL', 'B'],
    'missing_telemetry': ['PENDING', 'C'], 'at_cap_native': ['PASS', None], 'mismatch': ['PASS', None]}
ISOLATION_DECISIONS = {'network_request': 'DENY_APPLICATION_BROKER', 'outside_read': 'DENY_APPLICATION_BROKER',
    'credentials': 'DENY_APPLICATION_BROKER', 'callback_text': 'TEXT_ONLY'}
