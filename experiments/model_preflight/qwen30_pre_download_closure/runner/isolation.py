"""Exact Docker OS boundary. Configuration is never itself an enforcement PASS."""
import json
from pathlib import Path
import re
import subprocess


def command(image_digest, model, inputs, outputs, scratch, bundle, gpu_uuid=None, apparmor=False, mode='probe'):
    if not re.fullmatch(r'sha256:[a-f0-9]{64}', image_digest):
        raise ValueError('content-addressed image required')
    mounts = [(model, '/models/original', True), (inputs, '/inputs', True),
              (outputs, '/outputs', False), (scratch, '/scratch', False)]
    args = ['docker', 'create', '--network=none', '--read-only', '--user=65532:65532', '--cap-drop=ALL',
        '--security-opt=no-new-privileges', '--security-opt=seccomp=' + str(Path(bundle).resolve() / 'isolation/seccomp.json'),
        '--pids-limit=256', '--ipc=private', '--ulimit=core=0', '--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=1073741824']
    if apparmor:
        args += ['--security-opt=apparmor=qwen30-worker-v1']
    if gpu_uuid is not None:
        if not re.fullmatch(r'GPU-[0-9a-fA-F-]+', gpu_uuid):
            raise ValueError('one full-device UUID required, no all/MIG/TP2')
        args += ['--gpus=device=' + gpu_uuid]
    if mode not in {'native', 'probe'}:
        raise ValueError('Only fixed worker entrypoints; no tool/callback command')
    if mode == 'native':
        args += ['--env=QWEN30_SEPARATE_EXECUTION_AUTHORIZATION=AUTHENTICATED_LATER_STAGE',
                 '--env=QWEN30_IMAGE_DIGEST=' + image_digest]
    for source, target, readonly in mounts:
        source = Path(source).resolve(strict=True)
        if not source.is_dir() or ',' in str(source):
            raise ValueError('invalid mount root')
        args += ['--mount=type=bind,source=' + str(source) + ',target=' + target + (',readonly' if readonly else '')]
    for env in ['HF_HUB_OFFLINE=1', 'TRANSFORMERS_OFFLINE=1', 'VLLM_USE_V1=1',
                'VLLM_ENABLE_V1_MULTIPROCESSING=0', 'VLLM_LOGGING_LEVEL=ERROR',
                'CUBLAS_WORKSPACE_CONFIG=:4096:8', 'PYTHONDONTWRITEBYTECODE=1']:
        args += ['--env=' + env]
    return args + [image_digest, '/opt/python3.11.9/bin/python3.11', '-B', '-m',
                    'runner.native_worker' if mode == 'native' else 'runner.isolation_probe']


def inspect_receipt(container_id, expected_image):
    obj = json.loads(subprocess.check_output(['docker', 'inspect', container_id], timeout=15))[0]
    h = obj['HostConfig']
    mounts = obj['Mounts']
    allowed = {'/models/original': False, '/inputs': False, '/outputs': True, '/scratch': True}
    bind = [m for m in mounts if m['Type'] == 'bind']
    ok = (obj['Image'] == expected_image and h['NetworkMode'] == 'none' and h['ReadonlyRootfs'] and
          obj['Config']['User'] == '65532:65532' and 'ALL' in h['CapDrop'] and
          any('no-new-privileges' in s for s in h['SecurityOpt']) and
          any('seccomp=' in s for s in h['SecurityOpt']) and
          len(bind) == 4 and all(m['Destination'] in allowed and m['RW'] == allowed[m['Destination']] for m in bind))
    env_names = {s.split('=', 1)[0] for s in obj['Config']['Env']}
    denied = {'HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN', 'AWS_SECRET_ACCESS_KEY', 'SSH_AUTH_SOCK', 'DOCKER_HOST', 'QWEN_ACQUISITION_CANARY'}
    ok = ok and not env_names & denied
    return {'Docker_inspect': obj, 'configuration_matches': bool(ok),
            'OS_probe_required': True, 'enforcement_PASS': False}
