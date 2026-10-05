"""Allowlisted static source acquisition; never fetches model weight bodies."""
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parent
REPO='mistralai/Devstral-Small-2-24B-Instruct-2512'
SHA='55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128'
MODEL_FILES=['README.md','config.json','generation_config.json','tokenizer_config.json',
 'chat_template.jinja','tokenizer.json','tekken.json','params.json','processor_config.json',
 'model.safetensors.index.json','consolidated.safetensors.index.json']
PINS={
 'huggingface/transformers':'02d8fb9784e8f14a1251e4c992cd82a5762417c6',
 'huggingface/peft':'532a05dd505c28993119b7715ee286f4234bf51b',
 'vllm-project/vllm':'5f30fc7031cae49bf51073fc953d419b08f8887c',
}
SUPPORT={
 'huggingface/transformers':['pyproject.toml','setup.py','src/transformers/__init__.py',
 'src/transformers/quantizers/quantizer_finegrained_fp8.py','src/transformers/integrations/finegrained_fp8.py',
 'src/transformers/utils/quantization_config.py','src/transformers/models/mistral3/modeling_mistral3.py',
 'src/transformers/models/ministral3/modeling_ministral3.py','src/transformers/models/ministral3/configuration_ministral3.py',
 'src/transformers/models/pixtral/modeling_pixtral.py','src/transformers/conversion_mapping.py',
 'src/transformers/modeling_utils.py','src/transformers/core_model_loading.py',
 'src/transformers/tokenization_utils_tokenizers.py','src/transformers/tokenization_utils_base.py',
 'src/transformers/utils/chat_template_utils.py','docs/source/en/quantization/finegrained_fp8.md'],
 'huggingface/peft':['pyproject.toml','src/peft/__init__.py','src/peft/mapping_func.py','src/peft/peft_model.py',
 'src/peft/tuners/lora/config.py','src/peft/tuners/lora/model.py','src/peft/tuners/lora/layer.py',
 'src/peft/tuners/tuners_utils.py','src/peft/utils/save_and_load.py','src/peft/utils/other.py'],
 'vllm-project/vllm':['pyproject.toml','vllm/_version.py','requirements/cuda.txt','requirements/common.txt',
 'vllm/sampling_params.py','vllm/engine/arg_utils.py','vllm/config/model.py',
 'vllm/model_executor/models/mistral3.py','vllm/model_executor/models/llama.py',
 'vllm/model_executor/models/registry.py','vllm/tokenizers/mistral.py',
 'vllm/transformers_utils/tokenizers/mistral.py','vllm/v1/core/sched/utils.py',
 'vllm/v1/engine/output_processor.py','vllm/v1/engine/input_processor.py',
 'vllm/outputs.py','vllm/entrypoints/llm.py','docs/models/supported_models.md']}

def fetch(url,path,limit=2_000_000):
    result={'url':url,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'limit_bytes':limit}
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Devstral-static-preflight/1.0'}),timeout=35) as response:
            body=response.read(limit+1)
            if len(body)>limit: return dict(result,status='size_limit')
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
            return dict(result,status='retrieved',path=str(path.relative_to(ROOT)).replace('\\','/'),
                        bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),
                        http_date=response.headers.get('Date'),etag=response.headers.get('ETag'))
    except (urllib.error.URLError,TimeoutError) as exc:return dict(result,status='unavailable',error=str(exc))

def main():
    jobs=[(f'https://huggingface.co/api/models/{REPO}/revision/{SHA}?blobs=true',ROOT/'upstream/hub_metadata.json',2_000_000)]
    jobs += [(f'https://huggingface.co/{REPO}/resolve/{SHA}/{name}',ROOT/'upstream'/name,
              20_000_000 if name in {'tokenizer.json','tekken.json'} else 2_000_000) for name in MODEL_FILES]
    for repo,paths in SUPPORT.items():
        jobs.append((f'https://api.github.com/repos/{repo}/commits/{PINS[repo]}',ROOT/'sources'/repo.replace('/','__')/'commit.json',2_000_000))
        jobs += [(f'https://raw.githubusercontent.com/{repo}/{PINS[repo]}/{name}',ROOT/'sources'/repo.replace('/','__')/name,2_000_000) for name in paths]
    # Dependency release metadata only; no installation, wheel execution or model imports.
    jobs += [(f'https://pypi.org/pypi/{name}/json',ROOT/'sources/pypi'/f'{name}.json',2_000_000) for name in ['vllm','torch','transformers','peft','tokenizers','mistral-common']]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        records=list(pool.map(lambda j:fetch(*j),jobs))
    manifest={'subject_repository':REPO,'subject_revision':SHA,'weight_bodies_downloaded':False,
              'acquisition_rule':'only explicitly allowlisted public metadata/source/tokenizer files; no model code executed',
              'tokenizer_data_exception':'two ~17MB JSON vocabulary artifacts are required for exact tokenization; neither is a model weight',
              'implementation_pins':PINS,'files':records}
    (ROOT/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'retrieved':sum(r['status']=='retrieved' for r in records),
                      'unavailable':[{k:r[k] for k in ('url','status')} for r in records if r['status']!='retrieved']},indent=2))
if __name__=='__main__':main()
