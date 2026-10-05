"""Bounded allowlisted public runtime metadata only. No packages, images or weights."""
import sys
sys.dont_write_bytecode = True
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
LIMIT = 2_000_000
ALLOWED_HOSTS = {'api.github.com', 'raw.githubusercontent.com', 'pypi.org',
                 'docs.nvidia.com', 'download.pytorch.org', 'download-r2.pytorch.org', 'hub.docker.com'}
REJECTED_SUFFIXES = {'.whl', '.gz', '.zip', '.deb', '.safetensors', '.gguf', '.pt', '.pth', '.bin'}


def fetch(url, relative):
    path = (ROOT / relative).resolve()
    assert path.is_relative_to(ROOT)
    parsed = urlparse(url)
    assert parsed.scheme == 'https' and parsed.hostname in ALLOWED_HOSTS
    suffix = Path(parsed.path).suffix.lower()
    assert suffix not in REJECTED_SUFFIXES
    row = {'url': url, 'path': relative, 'retrieved_at_utc': datetime.now(timezone.utc).isoformat(), 'limit_bytes': LIMIT}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Qwen30-runtime-static-lock/1.0'}), timeout=35) as response:
            redirected = urlparse(response.geturl())
            assert redirected.scheme == 'https' and redirected.hostname in ALLOWED_HOSTS
            assert Path(redirected.path).suffix.lower() not in REJECTED_SUFFIXES
            data = response.read(LIMIT + 1)
            assert len(data) <= LIMIT, 'response exceeds bound'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            return dict(row, status='retrieved', bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), http_date=response.headers.get('Date'))
    except (urllib.error.URLError, TimeoutError, AssertionError) as error:
        return dict(row, status='PENDING', error=str(error))


def save(rows):
    p = ROOT / 'source_manifest.json'
    prior = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
    urls = {r['url'] for r in rows}
    prior['public_runtime_metadata'] = [r for r in prior.get('public_runtime_metadata', []) if r['url'] not in urls] + rows
    prior['acquisition_scope'] = 'Bounded runtime source/package/container metadata only; no model refresh, package/image layers or weight bodies'
    p.write_text(json.dumps(prior, indent=2) + '\n', encoding='utf-8')


def main():
    jobs = [(f'https://api.github.com/repos/{repo}/git/ref/tags/{tag}', f'sources/{repo.replace("/", "__")}/tag.json')
            for repo, tag in [('vllm-project/vllm', 'v0.11.2'), ('huggingface/transformers', 'v4.57.6'), ('huggingface/peft', 'v0.18.0')]]
    jobs += [(f'https://pypi.org/pypi/{package}/{version}/json', f'sources/package_metadata/{package}-{version}.json')
             for package, version in [('vllm', '0.11.2'), ('torch', '2.9.0'), ('transformers', '4.57.6'), ('peft', '0.18.0'),
                 ('tokenizers', '0.22.2'), ('jinja2', '3.1.6'), ('triton', '3.5.0'), ('flashinfer-python', '0.5.2')]]
    jobs += [('https://docs.nvidia.com/cuda/archive/12.8.1/cuda-toolkit-release-notes/index.html', 'sources/cuda-12.8.1-release-notes.html'),
             ('https://download.pytorch.org/whl/cu128/torch/', 'sources/pytorch-cu128-torch-index.html')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(lambda args: fetch(*args), jobs))
    save(rows)
    pins = {}
    for repo in ['vllm-project/vllm', 'huggingface/transformers', 'huggingface/peft']:
        directory = repo.replace('/', '__')
        p = ROOT / f'sources/{directory}/tag.json'
        if not p.exists():
            continue
        obj = json.loads(p.read_text())['object']
        if obj['type'] == 'tag':
            row = fetch(obj['url'], f'sources/{directory}/annotated_tag.json')
            save([row])
            if row['status'] != 'retrieved':
                continue
            obj = json.loads((ROOT / row['path']).read_text())['object']
        assert obj['type'] == 'commit'
        pins[repo] = obj['sha']
    save([fetch(f'https://api.github.com/repos/{repo}/commits/{pin}', f'sources/{repo.replace("/", "__")}/commit.json') for repo, pin in pins.items()])
    if 'vllm-project/vllm' in pins:
        pin = pins['vllm-project/vllm']
        files = ['pyproject.toml', 'setup.py', 'CMakeLists.txt', 'docker/Dockerfile', 'requirements/build.txt', 'requirements/common.txt',
                 'requirements/cuda.txt', 'vllm/version.py', 'vllm/sampling_params.py', 'vllm/v1/core/sched/utils.py',
                 'vllm/v1/engine/processor.py', 'vllm/v1/engine/output_processor.py', 'vllm/engine/arg_utils.py',
                 'vllm/model_executor/models/qwen3_moe.py', 'vllm/model_executor/models/qwen2.py']
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            rows = list(pool.map(lambda name: fetch(f'https://raw.githubusercontent.com/vllm-project/vllm/{pin}/{name}', f'sources/vllm-project__vllm/{name}'), files))
        save(rows)
    if 'huggingface/transformers' in pins:
        pin = pins['huggingface/transformers']
        save([fetch(f'https://raw.githubusercontent.com/huggingface/transformers/{pin}/src/transformers/models/qwen3_moe/modeling_qwen3_moe.py',
                    'sources/huggingface__transformers/modeling_qwen3_moe.py')])
    print(json.dumps({'resolved_source_pins': pins, 'metadata_only': True}, indent=2))


if __name__ == '__main__':
    main()
