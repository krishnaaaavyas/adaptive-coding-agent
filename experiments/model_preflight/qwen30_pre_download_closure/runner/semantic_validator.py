"""Lossless transport validator; no output cleanup and no model/scorer imports."""
from .interface import canonical, digest, token_bytes


def validate_event(event, request, controls):
    if event.get('invocation_count') != 1 or type(event.get('invocation_count')) is not int:
        raise ValueError('single-call rule')
    if event.get('retry_count') != 0 or type(event.get('retry_count')) is not int:
        raise ValueError('retry prohibited')
    if canonical(event.get('effective_controls')) != canonical(controls):
        raise ValueError('effective controls mismatch')
    if event.get('prompt_token_ids') != request['prompt_token_ids']:
        raise ValueError('prompt vector changed')
    ids = event['raw_token_ids']
    if type(ids) is not list or not 0 < len(ids) <= 2048:
        raise ValueError('generated vector/cap')
    if any(type(i) is not int or i<0 for i in ids):raise ValueError('invalid token ID type')
    table = request['byte_table']
    raw = token_bytes(ids, table)
    supplied = bytes.fromhex(event['raw_bytes_hex'])
    if raw != supplied:
        raise ValueError('raw bytes do not match full vector')
    raw.decode('utf-8', errors='strict')
    finish = event['finish_reason']
    if finish not in {'STOP', 'LENGTH'}:
        raise ValueError('unverified finish event')
    terminal = ids[-1] if finish == 'STOP' and ids[-1] in [151645, 151643] else None
    if finish == 'STOP' and terminal is None:
        raise ValueError('native stop has no observed final native terminal')
    if finish == 'LENGTH' and (len(ids) != 2048 or ids[-1] in [151645, 151643]):
        raise ValueError('LENGTH must be2048 and cannot relabel final native stop')
    if event.get('terminal_token') != terminal:
        raise ValueError('terminal claim mismatch')
    if finish=='STOP' and event.get('stop_reason') not in [None,terminal]:raise ValueError('Native stop reason inconsistent with observed final token')
    if finish=='LENGTH' and event.get('stop_reason') is not None:raise ValueError('LENGTH carries unsupported stop reason')
    content = token_bytes(ids[:-1] if terminal is not None else ids, table)
    # Two explicit replacements, no strip/fence/thinking/header projection.
    normalized = content.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    receipt = {'observed_final_native_terminal': terminal is not None,
        'removed_token_ids': [terminal] if terminal is not None else [],
        'removed_count': 1 if terminal is not None else 0,
        'evidence_sha256': digest(canonical({'ids': ids, 'finish': finish, 'stop': event.get('stop_reason')})),
        'justification': 'Observed final native terminal only' if terminal is not None else 'No terminal removed'}
    return raw, normalized, receipt


def validate_receipt(receipt, request, event, controls, raw, normalized):
    payload = receipt['schema_payload']
    if payload['exact_prompt_token_count'] != len(request['prompt_token_ids']):
        raise ValueError('prompt count inconsistency')
    if payload['raw_generated_token_ids'] != event['raw_token_ids']:
        raise ValueError('raw vector inconsistency')
    if payload['generated_token_count'] != len(event['raw_token_ids']):
        raise ValueError('generated count inconsistency')
    if payload['raw_generated_bytes_sha256'] != digest(raw) or payload['raw_byte_length'] != len(raw):
        raise ValueError('raw artifact inconsistency')
    if payload['normalized_completion_sha256'] != digest(normalized):
        raise ValueError('normalized hash inconsistency')
    if canonical(payload['frozen_control_values']) != canonical(controls):
        raise ValueError('control receipt inconsistency')
    if payload['terminal_removal_receipt']['removed_count'] != len(payload['terminal_removal_receipt']['removed_token_ids']):
        raise ValueError('terminal removal count inconsistency')
    if receipt['model_free'] and payload['gate_result'] == 'PASS':
        raise ValueError('synthetic receipt cannot PASS a Qwen gate')
    if payload['retry_count'] != 0 or payload['invocation_count'] != 1:
        raise ValueError('single call/retry receipt')


def compare_receipts(a, b):
    fields = ['exact_prompt_token_ids', 'raw_generated_token_ids', 'generated_token_count',
        'raw_generated_bytes_sha256', 'raw_byte_length', 'normalized_completion_sha256',
        'finish_reason', 'stop_reason', 'terminal_token', 'terminal_removal_receipt', 'invocation_count']
    if any(a['schema_payload'].get(k) is None or b['schema_payload'].get(k) is None for k in fields if k not in ['stop_reason', 'terminal_token']):
        return 'PENDING'
    return 'PASS' if all(a['schema_payload'][k] == b['schema_payload'][k] for k in fields) else 'FAIL'
