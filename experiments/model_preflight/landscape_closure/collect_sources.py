"""Bounded public static-source acquisition. Never retrieves weight bodies or runs model code."""
import concurrent.futures
import hashlib
import json
import pathlib
import urllib.request
import urllib.error

ROOT = pathlib.Path(__file__).resolve().parent
LIMIT = 2_000_000
REPOS = [
    'Qwen/Qwen3-Coder-30B-A3B-Instruct', 'Qwen/Qwen3-Coder-Next',
    'Qwen/Qwen3-Coder-480B-A35B-Instruct', 'Qwen/Qwen3.8-27B',
    'Qwen/Qwen3.8-Flash-Next',
    'mistralai/Devstral-Small-2-24B-Instruct-2512',
    'mistralai/Devstral-Small-2507', 'mistralai/Devstral-2-123B-Instruct-2512',
    'openai/gpt-oss-20b', 'openai/gpt-oss-120b',
    'deepseek-ai/DeepSeek-V4.1-Flash', 'deepseek-ai/DeepSeek-V4-Flash-0731',
    'deepseek-ai/DeepSeek-V3.2', 'deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct',
    'zai-org/GLM-4.7-Flash', 'zai-org/GLM-5.3-Flash', 'zai-org/GLM-5.3',
    'moonshotai/Kimi-K3', 'moonshotai/Kimi-K2.7-Code',
    'moonshotai/Kimi-Linear-48B-A3B-Instruct', 'moonshotai/Kimi-Dev-72B',
    'MiniMaxAI/MiniMax-M3', 'MiniMaxAI/MiniMax-M2.7',
    'nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16',
    'nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16',
    'nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16',
    'google/gemma-4-31B-it', 'google/gemma-4-26B-A4B-it',
    'meta-llama/Llama-4-Scout-17B-16E-Instruct',
    'allenai/Olmo-3-32B-Think',
    'MiniMaxAI/MiniMax-M2.5', 'ibm-granite/granite-4.1-30b',
    'microsoft/phi-4', 'ibm-granite/granite-4.2-8b',
    'allenai/Olmo-3.1-32B-Instruct', 'microsoft/Phi-4-reasoning-plus',
]
FILES = ('README.md', 'config.json', 'generation_config.json',
         'tokenizer_config.json', 'chat_template.jinja', 'LICENSE', 'LICENSE.txt', 'LICENSE.md',
         'LICENSE-MODEL', 'LICENSE-CODE')

def fetch(url, destination):
    request = urllib.request.Request(url, headers={'User-Agent': 'static-landscape-audit/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            body = response.read(LIMIT + 1)
            if len(body) > LIMIT:
                return {'url': url, 'status': 'size_limit', 'limit': LIMIT}
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(body)
            return {'url': url, 'status': 'retrieved', 'path': str(destination.relative_to(ROOT)),
                    'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest(),
                    'retrieved_at_utc': response.headers.get('Date'), 'etag': response.headers.get('ETag')}
    except (urllib.error.URLError, TimeoutError) as exc:
        return {'url': url, 'status': 'unavailable', 'error': str(exc)}

def collect(repo):
    directory = ROOT / 'sources' / repo.replace('/', '__')
    metadata = fetch('https://huggingface.co/api/models/' + repo + '?blobs=true', directory / 'hub_metadata.json')
    record = {'repository': repo, 'metadata': metadata, 'files': []}
    if metadata['status'] != 'retrieved':
        return record
    data = json.loads((directory / 'hub_metadata.json').read_text(encoding='utf-8'))
    revision = data['sha']
    record.update(revision=revision, created_at=data.get('createdAt'), modified_at=data.get('lastModified'),
                  gated=data.get('gated'), disabled=data.get('disabled'))
    names = {s['rfilename'] for s in data.get('siblings', [])}
    for name in FILES:
        if name in names:
            record['files'].append(fetch('https://huggingface.co/' + repo + '/resolve/' + revision + '/' + name,
                                         directory / name))
    return record

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        records = list(pool.map(collect, REPOS))
    manifest = {'cutoff': '2026-10-03 Asia/Calcutta', 'scope': 'Public metadata and allowlisted small text only; no weights',
                'per_response_limit_bytes': LIMIT, 'models': records}
    (ROOT / 'source_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    for record in records:
        print(record['repository'], record.get('revision', 'UNAVAILABLE'),
              sum(f['status'] == 'retrieved' for f in record['files']), flush=True)
