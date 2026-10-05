"""Archive bounded upstream implementation and training documentation, never execute it."""
import hashlib
import json
from collect_sources import ROOT, fetch

GITHUB = {
 'huggingface/transformers': [
  'src/transformers/models/glm4_moe_lite/modeling_glm4_moe_lite.py',
  'src/transformers/models/nemotron_h/modeling_nemotron_h.py',
  'src/transformers/models/mistral3/modeling_mistral3.py',
  'src/transformers/models/ministral3/modeling_ministral3.py',
  'src/transformers/models/gemma4/modeling_gemma4.py',
  'src/transformers/models/qwen3_5/modeling_qwen3_5.py',
  'src/transformers/quantizers/quantizer_finegrained_fp8.py',
 ],
 'huggingface/peft': ['docs/source/developer_guides/lora.md', 'docs/source/developer_guides/lora.mdx',
  'src/peft/tuners/lora/config.py', 'src/peft/peft_model.py', 'src/peft/tuners/lora/model.py'],
 'hiyouga/LlamaFactory': ['README.md'],
 'NVIDIA-NeMo/Nemotron': ['README.md',
  'usage-cookbook/Nemotron-3.5-Lightning/dgx-station-recipes/lora.md',
  'docs/nemotron/lightning35/README.md', 'docs/nemotron/super3/sft.md'],
 'NVIDIA-NeMo/Megatron-Bridge': ['README.md', 'docs/models/nemotron/nemotron3.5-lightning.md'],
 'vllm-project/recipes': ['models/Qwen/Qwen3.8-Flash-Next.yaml'],
 'vllm-project/vllm': ['docs/models/supported_models.md', 'docs/features/lora.md', 'vllm/model_executor/models/glm4_moe_lite.py'],
 'MoonshotAI/Kimi-Dev': ['README.md', 'LICENSE.md'],
 'deepseek-ai/DeepSeek-Coder-V2': ['README.md', 'LICENSE-MODEL'],
}
WEB = [
 'https://docs.nvidia.com/nemotron/latest/nemotron/super3/sft.html',
 'https://docs.nvidia.com/nemo/automodel/latest/model-coverage/llm.html',
 'https://ai.google.dev/gemma/docs/gemma_4_license',
 'https://deepmind.google/models/gemma/gemma-4/',
 'https://mistral.ai/news/devstral-2-vibe-cli',
 'https://developers.openai.com/cookbook/articles/gpt-oss/verifying-implementations',
 'https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-nemotron-open-model-license/',
 'https://raw.githubusercontent.com/OpenMDW/OpenMDW/main/1.1/LICENSE.OpenMDW-1.1',
 'https://huggingface.co/blog/gemma4',
 'https://deploymentsafety.openai.com/gpt-oss',
]
manifest_path = ROOT / 'source_manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
records = []
for repo, paths in GITHUB.items():
 directory = ROOT / 'sources' / ('github__' + repo.replace('/', '__'))
 identity = fetch('https://api.github.com/repos/' + repo + '/commits/HEAD', directory/'commit.json')
 record = {'repository': repo, 'identity': identity, 'files': []}
 if identity['status'] == 'retrieved':
  commit = json.loads((directory/'commit.json').read_text(encoding='utf-8'))
  record.update(revision=commit['sha'], commit_date=commit['commit']['committer']['date'])
  for path in paths:
   record['files'].append(fetch('https://raw.githubusercontent.com/' + repo + '/' + record['revision'] + '/' + path, directory/path))
 records.append(record)
 print(repo, record.get('revision'), flush=True)
manifest['support_repositories'] = records
manifest['support_pages'] = [fetch(url, ROOT/'sources'/'web'/(hashlib.sha256(url.encode()).hexdigest()[:16]+'.html')) for url in WEB]
manifest_path.write_text(json.dumps(manifest, indent=2)+'\n',encoding='utf-8')
