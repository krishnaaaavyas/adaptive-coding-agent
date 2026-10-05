"""Allowlisted public build metadata/source only; never checkpoint endpoints."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
JOBS = [('https://flashinfer.ai/whl/cu128/flashinfer-jit-cache/', 'sources/flashinfer-jit-cache-index.html', 2000000),
    ('https://snapshot.ubuntu.com/ubuntu/20261003T000000Z/dists/jammy/InRelease', 'sources/apt/jammy-InRelease', 1000000),
    ('https://snapshot.ubuntu.com/ubuntu/20261003T000000Z/dists/jammy-updates/InRelease', 'sources/apt/jammy-updates-InRelease', 1000000),
    ('https://snapshot.ubuntu.com/ubuntu/20261003T000000Z/dists/jammy-security/InRelease', 'sources/apt/jammy-security-InRelease', 1000000)]


def main():
    rows = []
    for url, rel, limit in JOBS:
        try:
            with urllib.request.urlopen(url, timeout=35) as response:
                data = response.read(limit + 1)
            assert len(data) <= limit
            path = HERE / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            rows.append({'url': url, 'path': rel, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'status': 'retrieved'})
            print(json.dumps({'path': rel, 'bytes': len(data)}), flush=True)
        except Exception as exc:
            rows.append({'url': url, 'path': rel, 'status': 'PENDING', 'error': repr(exc)})
            print(json.dumps(rows[-1]), flush=True)
    (HERE / 'build_source_fetch_manifest.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
