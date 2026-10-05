"""One-call fail-closed external transport supervisor; synthetic mode needs no GPU."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import time
from .interface import VERSION, canonical, digest
from .observer import Observer
from .schema_validator import check
from .semantic_validator import validate_event, validate_receipt


def confined(root, relative):
    root = Path(root).resolve()
    if not isinstance(relative, str) or not relative or '\\' in relative:
        raise ValueError('invalid scoped path')
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts or ':' in relative:
        raise ValueError('path traversal/absolute path')
    result = (root / p).resolve()
    if not result.is_relative_to(root):
        raise ValueError('outside scoped root')
    return result


def append_provenance(root, record):
    journal = Path(root) / 'provenance.jsonl'
    previous = '0' * 64
    if journal.exists():
        for line in journal.read_bytes().splitlines():
            entry = json.loads(line)
            assert entry['previous_sha256'] == previous
            assert entry['entry_sha256'] == digest(canonical({k: v for k, v in entry.items() if k != 'entry_sha256'}))
            previous = entry['entry_sha256']
    entry = {'previous_sha256': previous, 'record': record}
    entry['entry_sha256'] = digest(canonical(entry))
    with journal.open('ab') as f:
        f.write(canonical(entry) + b'\n')
        f.flush()
        os.fsync(f.fileno())
    return entry['entry_sha256']


def _run_synthetic(request, output_root, governance):
    """Tests only. Cannot PASS actual A-S because image/target/OS identity is absent."""
    root = Path(output_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    run_id = request['run_id']
    run_dir = confined(root, run_id)
    run_dir.mkdir()  # ExistingrunID fails; nothing overwritten, no retry.
    request_data = canonical(request)
    (run_dir / 'input.json').write_bytes(request_data)
    profile = json.loads((Path(governance) / 'generation_profile.json').read_text(encoding='utf-8'))
    controls = profile['independent_literal_expected_controls']
    if type(request.get('retry_count')) is not int or request['retry_count'] != 0 or canonical(request.get('controls')) != canonical(controls):
        raise ValueError('request drift or retry')
    child_env = {k: os.environ[k] for k in ['SYSTEMROOT', 'WINDIR', 'PATH', 'TEMP', 'TMP'] if k in os.environ}
    child_env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
    start = time.monotonic_ns()
    process = subprocess.Popen([sys.executable, '-B', str(Path(__file__).with_name('synthetic_worker.py'))],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=child_env)
    observer = None if request['case'] == 'missing_telemetry' else Observer(process.pid, run_dir / 'telemetry.json')
    if observer:
        observer.start()
    # Exactly one child launch/communicate. No retry/fallback/callback execution path.
    timed_out=False
    try: stdout, stderr = process.communicate(request_data, timeout=10)
    except subprocess.TimeoutExpired:
        timed_out=True
        process.kill()
        stdout,stderr=process.communicate()  # Collect the same failed process; never another invocation.
    elapsed = (time.monotonic_ns() - start) / 1e9
    telemetry = observer.finish() if observer else None
    (run_dir / 'worker.stdout').write_bytes(stdout)
    (run_dir / 'worker.stderr').write_bytes(stderr)
    isolation = {'status': 'PENDING_TARGET_LINUX_ATTESTATION', 'model_free': True,
        'process_id': process.pid, 'non_model_child_env_allowlist': sorted(child_env),
        'credentials_inherited': False, 'network_namespace_proven': False,
        'OS_mount_capability_seccomp_proven': False, 'tool_callbacks': 0}
    (run_dir / 'isolation.json').write_text(json.dumps(isolation, indent=2) + '\n', encoding='utf-8')
    receipt = {'record_kind': 'MODEL_FREE_SYNTHETIC_RECEIPT_NOT_QWEN_RUN', 'model_free': True,
        'runner_version': VERSION, 'process_id': process.pid, 'invocation_count': 1, 'retry_count': 0,
        'mechanics_result': 'PASS', 'mechanics_failure_class': None, 'schema_payload': None}
    event, raw, normalized, terminal_receipt = None, None, None, None
    try:
        if process.returncode != 0 or timed_out:
            raise ValueError('worker failure; quarantined without retry')
        event = json.loads(stdout)
        if event.get('history_present') or event.get('tools_executed') != 0 or event['policy_probe_results']['acquisition_sentinel_in_child_env']:
            raise ValueError('stale history/tool/credential state')
        raw, normalized, terminal_receipt = validate_event(event, request, controls)
        (run_dir / 'raw_generated.bytes').write_bytes(raw)
        (run_dir / 'normalized.bytes').write_bytes(normalized)
        if telemetry is None:
            receipt['mechanics_result'], receipt['mechanics_failure_class'] = 'PENDING', 'C'
    except (ValueError, UnicodeDecodeError, KeyError) as exc:
        receipt['mechanics_result'], receipt['mechanics_failure_class'] = 'FAIL', 'B'
        receipt['symptom'] = str(exc)
        # Preserve untrusted raw transport too; never replacement-decode or discard a failed stream.
        if event is not None and 'raw_bytes_hex' in event:
            (run_dir / 'untrusted_raw.bytes').write_bytes(bytes.fromhex(event['raw_bytes_hex']))
    schema = json.loads((Path(governance) / 'run_manifest_schema.json').read_text(encoding='utf-8'))
    payload = {k: None for k in schema['required']}
    raw_artifact = None if raw is None else {'path': 'raw_generated.bytes', 'bytes': len(raw), 'sha256': digest(raw)}
    payload.update(schema_version='qwen30-external-run-v1', run_id='qwen30-' + run_id,
        timestamp=datetime.now(timezone.utc).isoformat(), run_kind='generation',
        checkpoint_repo='Qwen/Qwen3-Coder-30B-A3B-Instruct', checkpoint_SHA='b2cff646eb4bb1d68355c01b18ae02e7cf42d120',
        frozen_control_values=controls, exact_prompt_token_ids=request['prompt_token_ids'], exact_prompt_token_count=len(request['prompt_token_ids']),
        effective_control_receipt_sha256=digest(canonical(event['effective_controls'])) if event else None,
        prompt_fixture_id='synthetic.' + request['case'], prompt_fixture_sha256=digest(request_data),
        raw_generated_token_ids=event['raw_token_ids'] if event else None,
        raw_generated_bytes_sha256=digest(raw) if raw is not None else None, raw_generated_bytes_artifact=raw_artifact,
        raw_byte_length=len(raw) if raw is not None else None, generated_token_count=len(event['raw_token_ids']) if event else None,
        finish_reason=event['finish_reason'] if event else 'ERROR', stop_reason=event.get('stop_reason') if event else None,
        terminal_token=event.get('terminal_token') if event else None, terminal_removal_receipt=terminal_receipt,
        normalized_completion_sha256=digest(normalized) if normalized is not None else None,
        wall_time=elapsed, peak_host_RAM=telemetry['peak_host_RAM'] if telemetry else None,
        peak_VRAM=None, resource_telemetry_sha256=digest((run_dir / 'telemetry.json').read_bytes()) if telemetry else None,
        isolation_result='PENDING', isolation_receipt_sha256=digest((run_dir / 'isolation.json').read_bytes()),
        gate_id='I', gate_result='PENDING', failure_classification='C', failure_id='synthetic-not-Qwen-evidence-' + run_id,
        prerequisite_run_ids=[], provenance_artifact_hashes=[{'path': 'input.json', 'bytes': len(request_data), 'sha256': digest(request_data)}],
        invocation_count=1, retry_count=0, parent_original_SHA='b2cff646eb4bb1d68355c01b18ae02e7cf42d120',
        notes=['MODEL_FREE INVENTED TRANSPORT ONLY; checkpoint fields are requested target labels, not verified bodies or observed Qwen behavior',
               'No actual Qwen gate executed or passed; mechanics_result is a separate synthetic-test disposition'])
    receipt['schema_payload'] = payload
    receipt['transport_artifact_hashes'] = [
        {'path': p.name, 'bytes': p.stat().st_size, 'sha256': digest(p.read_bytes())}
        for p in sorted(run_dir.iterdir()) if p.is_file()]
    frozen_schema = Path(governance) / 'run_manifest_schema.json'
    check(payload, frozen_schema, digest(frozen_schema.read_bytes()))
    if raw is not None and receipt['mechanics_result'] in {'PASS', 'PENDING'}:
        validate_receipt(receipt, request, event, controls, raw, normalized)
    receipt_data = canonical(receipt)
    (run_dir / 'synthetic_receipt.json').write_bytes(receipt_data + b'\n')
    append_provenance(root, {'run_id': run_id, 'receipt_sha256': digest(receipt_data + b'\n'), 'model_free': True,
        'mechanics_result': receipt['mechanics_result'], 'single_launch': 1, 'worker_returncode': process.returncode})
    return receipt

def run_synthetic(request, output_root, governance):
    root=Path(output_root).resolve();root.mkdir(parents=True,exist_ok=True)
    lock=root/'.supervisor.lock'
    # O_EXCL serializes append provenance and prevents concurrent launches/races; no wait/retry.
    with lock.open('x',encoding='utf-8') as f:f.write(str(os.getpid()))
    try:return _run_synthetic(request,root,governance)
    except Exception as exc:
        append_provenance(root,{'kind':'MODEL_FREE_ADMISSION_OR_TRANSPORT_FAILURE','run_id':request.get('run_id'),'exception':type(exc).__name__,'symptom':str(exc),'rerun':False})
        raise
    finally:lock.unlink()
