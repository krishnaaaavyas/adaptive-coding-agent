"""Prepared Linux native dispatcher. Separate authorization + complete proofs required.

Not called by0R. Docker creates exactly one container, start exactly once;
stdout/stderr and exit/inspect retained even on failure. No fallback/retry.
"""
import json
import os
from pathlib import Path
import platform
import subprocess
import time
from .interface import canonical, digest
from .isolation import command, inspect_receipt
from .observer import Observer
from .native_receipt import finalize


def dispatch(bundle, authority_path, model_dir, input_dir, output_dir, scratch_dir):
    if platform.system() != 'Linux':
        raise RuntimeError('PENDING_TARGET_LINUX_ATTESTATION')
    if Path(authority_path).resolve()!= (Path(input_dir)/'execution_authority.json').resolve():raise RuntimeError('Authority must be the exact read-only mounted input artifact')
    authority = json.loads(Path(authority_path).read_text(encoding='utf-8'))
    if authority.get('stage') != 'LATER_AUTHORIZED_EXECUTION':
        raise RuntimeError('No separate model execution authorization')
    if not all(authority.get('current_gate_results', {}).get(g) == 'PASS' for g in ['A', 'B', 'C', 'D', 'E', 'L']):
        raise RuntimeError('Missing current prerequisites')
    if not authority.get('target_attestation_pass') or not authority.get('build_self_test_pass'):
        raise RuntimeError('Target/build proof missing')
    if authority.get('gate_id')!='I':raise RuntimeError('This dispatcher supports the prerequisite-gated first native completion only; no A–S schedule execution or hidden reruns')
    for folder in [output_dir,scratch_dir]:
        if Path(folder).is_symlink() or any(Path(folder).iterdir()):raise RuntimeError('Fresh empty scoped output/scratch required')
    for artifact in authority['bound_artifacts']:
        p = Path(input_dir) / artifact['path']
        if p.is_symlink() or not p.resolve().is_relative_to(Path(input_dir).resolve()) or digest(p.read_bytes()) != artifact['sha256']:
            raise RuntimeError('Authority artifact hash/confinement mismatch')
    proof_paths=authority.get('proof_paths',{})
    if not {'target_attestation','build_self_test','build_verification','prior_isolation'}<=set(proof_paths):raise RuntimeError('Authenticated target/build/OS receipt paths missing')
    bound={a['path'] for a in authority['bound_artifacts']}
    if not set(proof_paths.values())<=bound or 'request.json' not in bound:raise RuntimeError('Proof/request not hash bound')
    from target_attestation_validator import validate as validate_target
    target=json.loads((Path(input_dir)/proof_paths['target_attestation']).read_text(encoding='utf-8'))
    if validate_target(target)['status']!='PASS' or target['selected_GPU_UUID']!=authority['selected_GPU_UUID']:raise RuntimeError('Actual target receipt not PASS')
    build=json.loads((Path(input_dir)/proof_paths['build_self_test']).read_text(encoding='utf-8'))
    verified=json.loads((Path(input_dir)/proof_paths['build_verification']).read_text(encoding='utf-8'))
    iso=json.loads((Path(input_dir)/proof_paths['prior_isolation']).read_text(encoding='utf-8'))
    if build.get('status')!='PASS' or build.get('stage')!='BUILD-TIME' or not verified.get('build_identity_verified') or verified.get('image_config_digest')!=authority['image_digest'] or not iso.get('all_pass'):raise RuntimeError('Bound executable/OS proof incomplete')
    request=json.loads((Path(input_dir)/'request.json').read_text(encoding='utf-8'))
    args = command(authority['image_digest'], model_dir, input_dir, output_dir, scratch_dir, bundle,
        authority['selected_GPU_UUID'], authority.get('AppArmor_available', False), mode='native')
    container = subprocess.check_output(args, timeout=30, text=True).strip()
    try:
        isolation = inspect_receipt(container, authority['image_digest'])
        if not isolation['configuration_matches']:
            raise RuntimeError('OS boundary config mismatch; do not start')
        start = time.monotonic_ns()
        process = subprocess.Popen(['docker', 'start', '--attach', container], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Resolve actual containerPID before observer launch; do not measure docker client's RSS as modelRAM.
        pid = None
        for _ in range(20):
            state = json.loads(subprocess.check_output(['docker', 'inspect', container], timeout=15))[0]['State']
            if state['Pid']:
                pid = state['Pid']
                break
            if not state['Running'] and state['Status'] == 'exited':
                break
            time.sleep(0.01)
        observer = Observer(pid, Path(output_dir) / 'native_telemetry.json', authority['selected_GPU_UUID']) if pid else None
        if observer:observer.start()
        try:stdout, stderr = process.communicate(timeout=authority['timeout_seconds'])
        except subprocess.TimeoutExpired:
            subprocess.run(['docker','kill',container],check=True,timeout=30)
            stdout,stderr=process.communicate()  # Same failed invocation, no second start.
        finally:telemetry=observer.finish() if observer else None
        (Path(output_dir) / 'native_worker.stdout').write_bytes(stdout)
        (Path(output_dir) / 'native_worker.stderr').write_bytes(stderr)
        final = json.loads(subprocess.check_output(['docker', 'inspect', container], timeout=15))[0]
        (Path(output_dir)/'container.inspect.json').write_bytes(canonical(final)+b'\n')
        authority=dict(authority,container_id=container)
        return finalize(bundle,authority,request,output_dir,stdout,stderr,telemetry,isolation,(time.monotonic_ns()-start)/1e9,final['State']['ExitCode'])
    finally:
        subprocess.run(['docker', 'rm', '--force', container], check=True, timeout=30)
