"""Prepared native serving worker. NEVER run during0R or synthetic tests.

Framework imports are inside main after Linux, explicit separate authorization,
body authentication, immutable image/target/isolation and prior gate checks.
"""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
from .interface import native_byte_table, token_bytes


def main():
    if platform.system() != 'Linux' or os.environ.get('QWEN30_SEPARATE_EXECUTION_AUTHORIZATION') != 'AUTHENTICATED_LATER_STAGE':
        raise RuntimeError('Not authorized:0R never executes this worker')
    request = json.loads(Path('/inputs/request.json').read_text(encoding='utf-8'))
    authority = json.loads(Path('/inputs/execution_authority.json').read_text(encoding='utf-8'))
    if authority.get('stage') != 'LATER_AUTHORIZED_EXECUTION' or not all(authority.get('current_gate_results', {}).get(g) == 'PASS' for g in ['A', 'B', 'C', 'D', 'E', 'L']):
        raise RuntimeError('Missing authenticated current prerequisite evidence')
    if authority['image_digest'] != os.environ.get('QWEN30_IMAGE_DIGEST'):
        raise RuntimeError('Runtime image identity mismatch')
    original = Path('/models/original')
    expected = json.loads(Path('/opt/qwen-bundle/frozen/expected_checkpoint_bodies.json').read_text(encoding='utf-8'))
    for shard in expected['shards']:
        p = original / shard['file']
        if p.is_symlink() or not p.is_file() or p.stat().st_size != shard['bytes']:
            raise RuntimeError('Checkpoint length mismatch')
        h = hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
                h.update(b)
        if h.hexdigest() != shard['upstream_declared_sha256']:
            raise RuntimeError('Original checkpoint hash mismatch')
    for asset in expected['metadata_assets']:
        p=original/asset['file']
        if p.is_symlink() or p.stat().st_size!=asset['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=asset['sha256']:raise RuntimeError('Metadata authentication failed')
    profile = json.loads(Path('/opt/qwen-bundle/frozen/generation_profile.json').read_text(encoding='utf-8'))
    if type(request.get('retry_count')) is not int or request['retry_count']!=0 or request['controls'] != profile['independent_literal_expected_controls'] or len(request['prompt_token_ids']) + 2048 > 32768:
        raise RuntimeError('Control/admission drift')
    if any(type(i) is not int or i<0 for i in request['prompt_token_ids']):raise RuntimeError('Invalid prompt vector')
    table = native_byte_table(json.loads((original / 'tokenizer.json').read_text(encoding='utf-8')))
    from .isolation_probe import measure
    isolation_receipt=measure()
    if not isolation_receipt['all_pass']:raise RuntimeError('Actual execution-container isolation probe failed; do not instantiate model')
    # No model construction occurs until every guard above passes; never imported in currenttests.
    import torch
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    torch.use_deterministic_algorithms(True, warn_only=False)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    # Future authorized native phase counters only; this module is never executed by0R tests.
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    with contextlib.redirect_stdout(sys.stderr):
        llm = LLM(model=str(original), tokenizer=str(original), **profile['requested_runtime_engine'])
        sampling = SamplingParams(**profile['requested_runtime_sampling'])
        effective_sampling={k:getattr(sampling,k,None) for k in profile['requested_runtime_sampling']}
        if effective_sampling!=profile['requested_runtime_sampling']:raise RuntimeError('Effective SamplingParams drift; do not generate')
        result = llm.generate([TokensPrompt(prompt_token_ids=request['prompt_token_ids'])], sampling, use_tqdm=False)
    torch.cuda.synchronize()
    framework_peaks={'max_memory_allocated':torch.cuda.max_memory_allocated(),'max_memory_reserved':torch.cuda.max_memory_reserved(),'phase':'before LLM construction through single completion','synchronized':True}
    if len(result) != 1 or len(result[0].outputs) != 1:
        raise RuntimeError('Exactly one completion required')
    output = result[0].outputs[0]
    ids = list(output.token_ids)
    raw = token_bytes(ids, table)
    reason = {'stop': 'STOP', 'length': 'LENGTH'}.get(output.finish_reason, 'UNKNOWN')
    print(json.dumps({'worker_kind': 'NATIVE_PENDING_CERTIFICATION', 'invocation_count': 1, 'retry_count': 0,
        'prompt_token_ids': list(result[0].prompt_token_ids), 'raw_token_ids': ids, 'raw_bytes_hex': raw.hex(),
        'finish_reason': reason, 'stop_reason': output.stop_reason,
        'terminal_token': ids[-1] if ids and reason == 'STOP' and ids[-1] in [151645, 151643] else None,
        'effective_controls': request['controls'], 'process_id': os.getpid(),
        'effective_sampling_fields': effective_sampling,
        'effective_engine_config': repr(llm.llm_engine.vllm_config),
        'model_instantiated':True,'authenticated_token_byte_table':{str(i):table[str(i)] for i in set(ids)},
        'OS_isolation_receipt':isolation_receipt,
        'framework_phase_peaks':framework_peaks,
        'native_metrics':{k:getattr(result[0].metrics,k,None) for k in ['arrival_time','first_token_time','finished_time']},
        'tools_executed': 0, 'raw_native_stream_certification': 'Requires laterE/I/F; unsupported omission of terminal fails closed'}))


if __name__ == '__main__':
    main()
