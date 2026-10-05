"""Bounded explicit official text/metadata acquisition. Never fetch weights."""
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
REPO = 'nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16'
SHA = 'a9904d24bcc1d289a1950fa9d2b978c47cf903b9'
TF = '02d8fb9784e8f14a1251e4c992cd82a5762417c6'
PEFT = '532a05dd505c28993119b7715ee286f4234bf51b'
VLLM = 'ced6857afa0ea7b2e3f0846a62e1394e90f15607'
NVIDIA = '8749344f8ccefd50181c56b013ddc5c8a6154a8c'
BRIDGE = '721356847b79c4bf78e5b8e9ceb6ed87835d3872'
MODEL = ['README.md', 'LICENSE', 'config.json', 'generation_config.json', 'tokenizer_config.json',
         'special_tokens_map.json', 'chat_template.jinja', 'tokenizer.json', 'model.safetensors.index.json']
SUPPORT = {
    'huggingface/transformers': (TF, ['src/transformers/__init__.py', 'setup.py',
        'src/transformers/models/nemotron_h/modeling_nemotron_h.py',
        'src/transformers/models/nemotron_h/configuration_nemotron_h.py',
        'src/transformers/conversion_mapping.py', 'src/transformers/core_model_loading.py',
        'src/transformers/modeling_utils.py', 'src/transformers/cache_utils.py',
        'src/transformers/integrations/moe.py', 'src/transformers/integrations/hub_kernels.py',
        'src/transformers/utils/chat_template_utils.py', 'src/transformers/tokenization_utils_tokenizers.py']),
    'huggingface/peft': (PEFT, ['src/peft/__init__.py', 'setup.py', 'src/peft/peft_model.py',
        'src/peft/mapping_func.py', 'src/peft/tuners/lora/config.py', 'src/peft/tuners/lora/layer.py',
        'src/peft/tuners/lora/model.py', 'src/peft/tuners/tuners_utils.py', 'src/peft/utils/save_and_load.py',
        'src/peft/utils/other.py']),
    'vllm-project/vllm': (VLLM, ['requirements/cuda.txt', 'requirements/common.txt', 'docker/Dockerfile',
        'vllm/version.py', 'vllm/model_executor/models/registry.py',
        'vllm/model_executor/models/nemotron_h.py', 'vllm/model_executor/models/nemotron_h_mtp.py',
        'vllm/model_executor/layers/mamba/mamba_mixer2.py', 'vllm/model_executor/layers/mamba/abstract.py',
        'vllm/model_executor/layers/mamba/mamba_utils.py', 'vllm/model_executor/layers/fused_moe/layer.py',
        'vllm/config/model.py', 'vllm/config/cache.py', 'vllm/config/lora.py',
        'vllm/sampling_params.py', 'vllm/engine/arg_utils.py', 'vllm/entrypoints/llm.py',
        'vllm/v1/core/sched/utils.py', 'vllm/outputs.py',
        'vllm/reasoning/__init__.py', 'vllm/tool_parsers/__init__.py']),
    'NVIDIA-NeMo/Nemotron': (NVIDIA, ['usage-cookbook/Nemotron-3.5-Lightning/dgx-station-recipes/lora.md',
        'docs/nemotron/lightning35/README.md']),
    'NVIDIA-NeMo/Megatron-Bridge': (BRIDGE, ['docs/models/nemotron/nemotron3.5-lightning.md'])
}


def fetch(url, path, limit=2_000_000):
    path = path.resolve()
    assert path.is_relative_to(ROOT)
    assert Path(urlparse(url).path).suffix.lower() not in {'.safetensors', '.gguf', '.pt', '.pth', '.bin'}
    row = {'url': url, 'retrieved_at_utc': datetime.now(timezone.utc).isoformat(), 'limit_bytes': limit}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Nemotron35-static-preflight/1.0'}), timeout=35) as response:
            data = response.read(limit + 1)
            if len(data) > limit:
                return dict(row, status='size_limit')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            return dict(row, status='retrieved', path=path.relative_to(ROOT).as_posix(), bytes=len(data),
                        sha256=hashlib.sha256(data).hexdigest(), http_date=response.headers.get('Date'), etag=response.headers.get('ETag'))
    except (urllib.error.URLError, TimeoutError) as error:
        return dict(row, status='unavailable', error=str(error))


def main():
    jobs = [(f'https://huggingface.co/api/models/{REPO}/revision/{SHA}?blobs=true', ROOT/'upstream/hub_metadata.json', 2_000_000)]
    # Exact 17,077,484-byte public JSON vocabulary; explicit bounded text exception.
    jobs += [(f'https://huggingface.co/{REPO}/resolve/{SHA}/{name}', ROOT/'upstream'/name,
              18_000_000 if name == 'tokenizer.json' else 2_000_000) for name in MODEL]
    for repo, (pin, names) in SUPPORT.items():
        directory = ROOT/'sources'/repo.replace('/', '__')
        jobs.append((f'https://api.github.com/repos/{repo}/commits/{pin}', directory/'commit.json', 2_000_000))
        jobs += [(f'https://raw.githubusercontent.com/{repo}/{pin}/{name}', directory/name, 2_000_000) for name in names]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(lambda args: fetch(*args), jobs))
    manifest_path = ROOT/'source_manifest.json'
    prior = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
    replaced = {r['url'] for r in rows}
    prior.update(subject_repository=REPO, subject_revision=SHA, implementation_pins={k:v[0] for k,v in SUPPORT.items()},
                 scope='Explicit bounded immutable public text/source/config/tokenizer/index only', weight_bodies_downloaded=False,
                 tokenizer_vocabulary_exception='Exact 17,077,484-byte public tokenizer JSON, bounded to18MB; not weights',
                 files=[r for r in prior.get('files', []) if r['url'] not in replaced] + rows)
    manifest_path.write_text(json.dumps(prior, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'retrieved': sum(r['status']=='retrieved' for r in rows),
                      'unavailable': [(r['url'], r['status']) for r in rows if r['status']!='retrieved']}, indent=2))


if __name__ == '__main__':
    main()
