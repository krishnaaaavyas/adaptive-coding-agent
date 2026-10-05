"""CPU-only Linux in-container probes, invented canaries only; no model imports."""
import json
import os
from pathlib import Path
import socket


def denied_write(path):
    try:
        Path(path).write_bytes(b'invented-deny-probe')
        return False
    except OSError as exc:
        return {'denied': True, 'errno': exc.errno}


def measure():
    status = Path('/proc/self/status').read_text(encoding='utf-8')
    fields = dict(line.split(':', 1) for line in status.splitlines() if ':' in line)
    canary = None
    try:
        canary = Path('/__denied_canary__/secret.txt').read_bytes()
        outside = False
    except OSError as exc:
        outside = {'denied': True, 'errno': exc.errno}
    try:
        with socket.create_connection(('198.18.0.1', 9), timeout=0.2):
            network = False
    except OSError as exc:
        network = {'denied': True, 'errno': exc.errno}
    Path('/outputs/scoped-probe.bytes').write_bytes(b'invented-scoped-probe')
    interfaces = sorted(p.name for p in Path('/sys/class/net').iterdir())
    prohibited = {name: name in os.environ for name in ['HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN', 'SSH_AUTH_SOCK',
        'DOCKER_HOST', 'AWS_SECRET_ACCESS_KEY', 'QWEN_ACQUISITION_CANARY']}
    mountinfo=Path('/proc/self/mountinfo').read_text(encoding='utf-8')
    # Exact destination set and flags supplement host Docker inspection; no host content is read.
    expected={'/models/original':'ro','/inputs':'ro','/outputs':'rw','/scratch':'rw'}
    mounted={s.split()[4]:s.split()[5].split(',') for s in mountinfo.splitlines()}
    allowed_mounts=all(k in mounted and flag in mounted[k] for k,flag in expected.items())
    root_readonly='ro' in mounted.get('/',[])
    probes = {'non_root_uid': os.getuid() != 0, 'capabilities_zero': int(fields['CapEff'].strip(), 16) == 0,
        'no_new_privileges': fields['NoNewPrivs'].strip() == '1', 'seccomp_filter': fields['Seccomp'].strip() == '2',
        'only_loopback': interfaces == ['lo'], 'network_attempt_denied': bool(network),
        'outside_canary_read_denied': bool(outside), 'model_mount_write_denied': bool(denied_write('/models/original/write_probe')),
        'input_mount_write_denied': bool(denied_write('/inputs/write_probe')), 'no_credentials': not any(prohibited.values()),
        'no_Docker_socket': not Path('/var/run/docker.sock').exists(), 'no_SSH_socket': not Path('/run/ssh-agent').exists(),
        'scoped_write': True,'allowed_mounts_verified':allowed_mounts and root_readonly}
    return {'kind': 'ACTUAL_LINUX_CPU_ONLY_ISOLATION_PROBE', 'probes': probes,
        'all_pass': all(probes.values()), 'mountinfo': mountinfo,
        'network_error': network, 'outside_read_error': outside, 'credential_presence_only': prohibited,
        'model_instantiated': False, 'GPU_used': False}

def main():print(json.dumps(measure()))


if __name__ == '__main__':
    main()
