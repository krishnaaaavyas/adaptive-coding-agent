"""Bounded allowlisted public-source acquisition only; no weight bodies/recipes."""
import sys
sys.dont_write_bytecode=True
import concurrent.futures
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import urllib.request
import urllib.error
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parent
REPO='zai-org/GLM-4.7-Flash'
SHA='7dd20894a642a0aa287e9827cb1a1f7f91386b67'
TF='02d8fb9784e8f14a1251e4c992cd82a5762417c6'
PEFT='532a05dd505c28993119b7715ee286f4234bf51b'
VLLM='ced6857afa0ea7b2e3f0846a62e1394e90f15607'
MODEL=['README.md','LICENSE','config.json','generation_config.json','tokenizer_config.json','special_tokens_map.json',
       'chat_template.jinja','tokenizer.json','model.safetensors.index.json']
SUPPORT={
 'huggingface/transformers':(TF,['src/transformers/__init__.py','setup.py',
   'src/transformers/models/glm4_moe_lite/modeling_glm4_moe_lite.py','src/transformers/models/glm4_moe_lite/configuration_glm4_moe_lite.py',
   'src/transformers/models/glm4_moe/modeling_glm4_moe.py','src/transformers/conversion_mapping.py','src/transformers/core_model_loading.py',
   'src/transformers/modeling_utils.py','src/transformers/utils/chat_template_utils.py','src/transformers/tokenization_utils_tokenizers.py']),
 'huggingface/peft':(PEFT,['src/peft/__init__.py','setup.py','src/peft/peft_model.py','src/peft/mapping_func.py',
   'src/peft/tuners/lora/config.py','src/peft/tuners/lora/layer.py','src/peft/tuners/lora/model.py',
   'src/peft/tuners/tuners_utils.py','src/peft/utils/save_and_load.py','src/peft/utils/other.py']),
 'vllm-project/vllm':(VLLM,['requirements/cuda.txt','requirements/common.txt','docker/Dockerfile','vllm/version.py',
   'vllm/model_executor/models/registry.py','vllm/model_executor/models/glm4_moe_lite.py','vllm/model_executor/models/deepseek_v2.py',
   'vllm/model_executor/models/glm4_moe.py','vllm/model_executor/layers/fused_moe/layer.py',
   'vllm/sampling_params.py','vllm/engine/arg_utils.py','vllm/entrypoints/llm.py','vllm/outputs.py',
   'vllm/v1/core/sched/utils.py','vllm/reasoning/glm4_moe_reasoning_parser.py','vllm/reasoning/glm45_reasoning_parser.py',
   'vllm/tool_parsers/glm47_tool_parser.py'])}

def fetch(url,path,limit=2_000_000):
    path=path.resolve();assert path.is_relative_to(ROOT)
    assert Path(urlparse(url).path).suffix not in {'.safetensors','.gguf','.pt','.pth','.bin'}
    row={'url':url,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'limit_bytes':limit}
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'GLM47-targeted-static-preflight/1.0'}),timeout=35) as response:
            data=response.read(limit+1)
            if len(data)>limit:return dict(row,status='size_limit')
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
            return dict(row,status='retrieved',path=path.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),http_date=response.headers.get('Date'),etag=response.headers.get('ETag'))
    except (urllib.error.URLError,TimeoutError) as exc:return dict(row,status='unavailable',error=str(exc))

def main():
    jobs=[(f'https://huggingface.co/api/models/{REPO}/revision/{SHA}?blobs=true',ROOT/'upstream/hub_metadata.json',2_000_000)]
    jobs.extend((f'https://huggingface.co/{REPO}/resolve/{SHA}/{n}',ROOT/'upstream'/n,21_000_000 if n=='tokenizer.json' else 2_000_000) for n in MODEL)
    for repo,(pin,names) in SUPPORT.items():
        directory=ROOT/'sources'/repo.replace('/','__')
        jobs.append((f'https://api.github.com/repos/{repo}/commits/{pin}',directory/'commit.json',2_000_000))
        jobs.extend((f'https://raw.githubusercontent.com/{repo}/{pin}/{n}',directory/n,2_000_000) for n in names)
    jobs.append(('https://docs.z.ai/guides/capabilities/thinking-mode',ROOT/'sources/zai/thinking-mode.html',2_000_000))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:rows=list(pool.map(lambda j:fetch(*j),jobs))
    path=ROOT/'source_manifest.json'
    existing=json.loads(path.read_text(encoding='utf-8')).get('files',[]) if path.exists() else []
    replaced={r['url'] for r in rows};rows=[r for r in existing if r['url'] not in replaced]+rows
    data={'subject_repository':REPO,'subject_revision':SHA,'implementation_pins':{k:v[0] for k,v in SUPPORT.items()},
          'scope':'explicit public text/config/index/tokenizer and source files only; no model/adapter instantiation or recipes',
          'weight_bodies_downloaded':False,'tokenizer_vocabulary_exception':'bounded exact tokenizer JSON up to21MB; not model weights',
          'files':rows}
    path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'retrieved':sum(r['status']=='retrieved' for r in rows),'unavailable':[(r['url'],r['status']) for r in rows if r['status']!='retrieved']},indent=2))

if __name__=='__main__':main()
