"""MODEL-FREE invented worker. No Qwen behavior or OS isolation claim."""
import json
import os
import sys
import time

sys.dont_write_bytecode = True

def denied_broker(operation, payload):
    """Actual application admission attempt; deliberately has no ambient I/O capability."""
    if operation in {'network_request', 'outside_read', 'credentials'}:
        raise PermissionError('DENY_APPLICATION_BROKER')
    if operation == 'callback_text':
        return 'TEXT_ONLY'  # Payload remains inert; no evaluator/subprocess/tool hook.
    raise ValueError('Unknown operation')

def broker_probes():
    results={}
    for op,payload in [('network_request','https://invented.invalid/'),('outside_read','/invented-outside/secret'),('credentials','QWEN_ACQUISITION_CANARY'),('callback_text','raise RuntimeError("must not execute")')]:
        try: results[op]=denied_broker(op,payload)
        except PermissionError as e: results[op]=str(e)
    results['acquisition_sentinel_in_child_env']='QWEN_ACQUISITION_CANARY' in os.environ
    return results


def main():
    request = json.load(sys.stdin)
    time.sleep(0.12)  # Fixed invented test timing to exercise100ms observer; not a model request.
    case = request['case']
    if case == 'injected_failure':
        raise RuntimeError('invented single worker failure')
    ids = [5, 151645]
    raw = '413c7c696d5f656e647c3e'
    finish, terminal, stop = 'STOP', 151645, 151645
    if case == 'length':
        ids, raw, finish, terminal, stop = [0] * 2048, '21' * 2048, 'LENGTH', None, None
    elif case == 'invalid_utf8':
        ids, raw, finish, terminal, stop = [7, 151645], 'ff3c7c696d5f656e647c3e', 'STOP', 151645, 151645
    elif case == 'line_endings':
        ids, raw = [6, 151645], '610d0a620d630a3c7c696d5f656e647c3e'
    elif case == 'internal_special':
        ids, raw = [151645, 5, 151643], '3c7c696d5f656e647c3e413c7c656e646f66746578747c3e'
        terminal, stop = 151643, 151643
    elif case == 'mismatch':
        ids, raw = [8, 151645], '423c7c696d5f656e647c3e'
    elif case == 'at_cap_native':
        ids, raw = [0] * 2047 + [151645], '21' * 2047 + '3c7c696d5f656e647c3e'
    event = {'worker_kind': 'MODEL_FREE_INVENTED', 'invocation_count': 1,
        'retry_count': 1 if case == 'retry_violation' else 0,
        'prompt_token_ids': request['prompt_token_ids'], 'raw_token_ids': ids, 'raw_bytes_hex': raw,
        'finish_reason': finish, 'stop_reason': stop, 'terminal_token': terminal,
        'effective_controls': request['controls'], 'process_id': os.getpid(),
        'model_instantiated': False, 'tools_executed': 0,
        'policy_probe_results': broker_probes(),
        'OS_enforcement_proven': False}
    if case == 'stale_history':
        event['history_present'] = True
    if case == 'controls_violation':
        event['effective_controls'] = dict(request['controls'], temperature=2)
    print(json.dumps(event))


if __name__ == '__main__':
    main()
