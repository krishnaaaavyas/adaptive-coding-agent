"""Exact public code archives, no model repository URLs or checkpoint bodies."""
import sys
sys.dont_write_bytecode = True
import concurrent.futures
import hashlib
import json
from pathlib import Path
import tarfile
import urllib.request

HERE = Path(__file__).resolve().parent
SOURCES = [('cpython', 'python/cpython', 'de54cf5be371a6f5e2e9f208c38def5f81d3ef02'),
    ('vllm', 'vllm-project/vllm', '275de34170654274616082721348b7edd9741d32'),
    ('transformers', 'huggingface/transformers', '753d61104116eefc8ffc977327b441ee0c8d599f'),
    ('peft', 'huggingface/peft', '77daa8d3b7decf2b40238ab47e2c1bd0f26c7749'),
    ('cutlass', 'NVIDIA/cutlass', 'f3fde58372d33e9a5650ba7b80fc48b3b49d40c8'),
    ('vllm-flash-attention', 'vllm-project/flash-attention', '58e0626a692f09241182582659e3bf8f16472659')]


def fetch(job):
    name, repo, commit = job
    p = HERE / ('sources/archives/' + name + '.tar.gz')
    url = f'https://codeload.github.com/{repo}/tar.gz/{commit}'
    if not p.exists():
        with urllib.request.urlopen(url, timeout=90) as response:
            data = response.read(100000001)
        assert len(data) <= 100000000
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    data = p.read_bytes()
    modules = []
    # Read only build declarations, not upstream test fixtures or model data.
    with tarfile.open(p) as tar:
        for member in tar:
            if member.isfile() and member.name.count('/') == 1 and member.name.split('/')[-1] in {'.gitmodules', 'pyproject.toml'}:
                text = tar.extractfile(member).read().decode('utf-8')
                modules.append({'file': member.name.split('/')[-1], 'text': text, 'sha256': hashlib.sha256(text.encode()).hexdigest()})
    return {'name': name, 'repository': repo, 'commit': commit, 'url': url,
        'path': p.relative_to(HERE).as_posix(), 'filename': p.name, 'bytes': len(data),
        'sha256': hashlib.sha256(data).hexdigest(), 'body_downloaded': True, 'body_hash_verified': True,
        'kind': 'Public runtime source code archive, not a model checkpoint', 'build_declarations': modules}


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(fetch, SOURCES))
    (HERE / 'source_archive_lock.json').write_text(json.dumps({'sources': rows}, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'source_archives': len(rows), 'bytes': sum(r['bytes'] for r in rows),
        'submodule_declarations': [(r['name'], [d['file'] for d in r['build_declarations']]) for r in rows]}))


if __name__ == '__main__':
    main()
