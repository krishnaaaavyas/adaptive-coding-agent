"""Native stdout processor. Does not import a model; gate acceptance remains external/frozen."""
from datetime import datetime,timezone
import json
from pathlib import Path
from .interface import canonical,digest
from .schema_validator import check
from .semantic_validator import validate_event,validate_receipt
from .supervisor import append_provenance
def finalize(bundle,authority,request,output_dir,stdout,stderr,telemetry,isolation,elapsed,exit_code):
    root=Path(output_dir);gov=Path(bundle)/'frozen';schema_path=gov/'run_manifest_schema.json'
    (root/'native_worker.stdout').write_bytes(stdout);(root/'native_worker.stderr').write_bytes(stderr)
    controls=json.loads((gov/'generation_profile.json').read_text(encoding='utf-8'))['independent_literal_expected_controls']
    schema=json.loads(schema_path.read_text(encoding='utf-8'));payload={k:None for k in schema['required']}
    result='PENDING';failure='C';symptom='Native semantic/phase/runtime gate certification requires frozen later evidence';event=None;raw=None;norm=None;terminal=None
    try:
        if exit_code:raise ValueError('Single native worker failed; preserve, no retry')
        event=json.loads(stdout)
        if event.get('tools_executed')!=0 or event.get('history_present'):raise ValueError('Tool/stale state')
        authenticated_request=dict(request,byte_table=event['authenticated_token_byte_table'])
        raw,norm,terminal=validate_event(event,authenticated_request,controls)
        (root/'raw_generated.bytes').write_bytes(raw);(root/'normalized.bytes').write_bytes(norm)
        actual_iso=event.get('OS_isolation_receipt',{})
        if not actual_iso.get('all_pass'):raise ValueError('Execution-container enforcement proof missing')
        (root/'native_OS_probe.json').write_bytes(canonical(actual_iso)+b'\n')
        isolation=dict(isolation,actual_in_container_probe=actual_iso,enforcement_PASS=bool(isolation['configuration_matches'] and actual_iso['all_pass']))
    except (ValueError,KeyError,UnicodeDecodeError) as exc:
        result='QUARANTINED';failure='B';symptom=str(exc)
        if event is not None and 'raw_bytes_hex' in event:(root/'untrusted_raw.bytes').write_bytes(bytes.fromhex(event['raw_bytes_hex']))
    (root/'native_isolation.json').write_bytes(canonical(isolation)+b'\n')
    elapsed_first=None
    if event and event.get('native_metrics'):
        m=event['native_metrics']
        if m.get('first_token_time') is not None and m.get('arrival_time') is not None:elapsed_first=m['first_token_time']-m['arrival_time']
    payload.update(schema_version='qwen30-external-run-v1',run_id=request['run_id'],timestamp=datetime.now(timezone.utc).isoformat(),run_kind='generation',
        checkpoint_repo='Qwen/Qwen3-Coder-30B-A3B-Instruct',checkpoint_SHA='b2cff646eb4bb1d68355c01b18ae02e7cf42d120',parent_original_SHA='b2cff646eb4bb1d68355c01b18ae02e7cf42d120',
        checkpoint_body_hashes=authority.get('authenticated_checkpoint_body_hashes'),container_digest=authority['image_digest'],runtime_identities=authority.get('runtime_identities'),GPU=authority.get('GPU'),driver=authority.get('driver'),CUDA=authority.get('CUDA'),
        frozen_control_values=controls,effective_control_receipt_sha256=digest(canonical(event['effective_controls'])) if event else None,
        prompt_fixture_id=request.get('prompt_fixture_id'),prompt_fixture_sha256=digest(canonical(request)),exact_prompt_token_ids=request['prompt_token_ids'],exact_prompt_token_count=len(request['prompt_token_ids']),
        raw_generated_token_ids=event['raw_token_ids'] if event else None,generated_token_count=len(event['raw_token_ids']) if event else None,raw_byte_length=len(raw) if raw is not None else None,
        raw_generated_bytes_sha256=digest(raw) if raw is not None else None,raw_generated_bytes_artifact={'path':'raw_generated.bytes','bytes':len(raw),'sha256':digest(raw)} if raw is not None else None,
        finish_reason=event['finish_reason'] if event else 'ERROR',stop_reason=event.get('stop_reason') if event else None,terminal_token=event.get('terminal_token') if event else None,terminal_removal_receipt=terminal,normalized_completion_sha256=digest(norm) if norm is not None else None,
        wall_time=elapsed,TTFT=elapsed_first,throughput=None,peak_VRAM=telemetry.get('peak_VRAM') if telemetry else None,peak_host_RAM=telemetry.get('peak_host_RAM') if telemetry else None,
        resource_telemetry_sha256=digest((root/'native_telemetry.json').read_bytes()) if (root/'native_telemetry.json').exists() else None,
        isolation_result='PASS' if isolation.get('enforcement_PASS') else 'PENDING',isolation_receipt_sha256=digest((root/'native_isolation.json').read_bytes()),
        gate_id=authority['gate_id'],gate_result=result,failure_classification=failure,failure_id='native-evidence-'+request['run_id'],prerequisite_run_ids=authority.get('prerequisite_run_ids',[]),provenance_artifact_hashes=[{'path':'request.json','bytes':len(canonical(request)),'sha256':digest(canonical(request))}],
        invocation_count=1,retry_count=0,notes=[symptom,'No automatic gate acceptance; frozen acceptance evaluator and complete phase evidence required.'])
    receipt={'model_free':False,'schema_payload':payload,'process_identity':{'container':authority.get('container_id'),'worker_pid':event.get('process_id') if event else None},'single_start':1,'retry_count':0}
    check(payload,schema_path,digest(schema_path.read_bytes()))
    if raw is not None and result!='QUARANTINED':validate_receipt(receipt,authenticated_request,event,controls,raw,norm)
    receipt['artifact_hashes']=[{'path':p.name,'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())} for p in sorted(root.iterdir()) if p.is_file()]
    data=canonical(receipt)+b'\n';(root/'native_receipt.json').open('xb').write(data)
    append_provenance(root,{'native_receipt_sha256':digest(data),'gate_result':result,'failure_classification':failure,'invocation_count':1,'retries':0})
    return receipt
