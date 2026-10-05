"""Candidate-blind allowlisted source/metadata acquisition; no weight bodies."""
import hashlib, json, urllib.request, concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'static-model-preflight'}),timeout=50) as r: return r.read()
def dump(p,obj): (ROOT/p).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
def main():
    (ROOT/'upstream').mkdir(exist_ok=True); (ROOT/'sources').mkdir(exist_ok=True)
    old=ROOT/'upstream/hub_metadata.json'
    info=json.loads(old.read_text()) if old.exists() else json.loads(fetch('https://huggingface.co/api/models/openai/gpt-oss-20b?blobs=true'))
    rev=info['sha']; info=json.loads(fetch(f'https://huggingface.co/api/models/openai/gpt-oss-20b/revision/{rev}?blobs=true'))
    assert info['sha']==rev; dump('upstream/hub_metadata.json',info)
    names=['config.json','generation_config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','chat_template.jinja','model.safetensors.index.json','LICENSE','README.md']
    jobs=[('upstream/'+n,f'https://huggingface.co/openai/gpt-oss-20b/resolve/{rev}/{n}') for n in names]
    pins={
      'transformers':dict(repository='huggingface/transformers',version='4.57.6',revision='753d61104116eefc8ffc977327b441ee0c8d599f'),
      'peft':dict(repository='huggingface/peft',version='0.18.0',revision='77daa8d3b7decf2b40238ab47e2c1bd0f26c7749'),
      'vllm':dict(repository='vllm-project/vllm',version='0.16.0',revision='89a77b10846fd96273cce78d86d2556ea582d26e')}
    for key,repo in [('harmony','openai/harmony'),('gpt_oss','openai/gpt-oss'),('cookbook','openai/openai-cookbook')]:
        saved=ROOT/'implementation_pins.json'
        prior=json.loads(saved.read_text()) if saved.exists() else {}
        commit=prior.get(key,{}).get('revision') or json.loads(fetch(f'https://api.github.com/repos/{repo}/commits/HEAD'))['sha']
        pins[key]=dict(repository=repo,revision=commit,version='source-commit')
    dump('implementation_pins.json',pins)
    files={
      'transformers':['src/transformers/models/gpt_oss/modeling_gpt_oss.py','src/transformers/models/gpt_oss/configuration_gpt_oss.py','src/transformers/integrations/mxfp4.py','src/transformers/quantizers/quantizer_mxfp4.py'],
      'peft':['src/peft/tuners/lora/layer.py','src/peft/tuners/lora/model.py','src/peft/utils/constants.py','src/peft/utils/save_and_load.py','src/peft/peft_model.py','docs/source/developer_guides/lora.md','docs/source/developer_guides/quantization.md'],
      'vllm':['vllm/model_executor/models/gpt_oss.py','vllm/sampling_params.py','vllm/v1/core/sched/utils.py','vllm/outputs.py','vllm/v1/engine/input_processor.py','vllm/engine/arg_utils.py','requirements/common.txt','requirements/cuda.txt'],
      'harmony':['README.md','Cargo.toml','pyproject.toml','python/openai_harmony/__init__.py','src/lib.rs','src/encoding.rs'],
      'gpt_oss':['README.md','gpt_oss/torch/model.py','gpt_oss/torch/generate.py','gpt_oss/tokenizer.py'],
      'cookbook':['articles/openai-harmony.md','articles/gpt-oss/run-transformers.md','articles/gpt-oss/fine-tune-transfomers.md','articles/gpt-oss/handle-raw-cot.md','articles/gpt-oss/verifying-implementations.md']}
    for key,paths in files.items():
        p=pins[key]
        jobs.extend(('sources/'+key+'_'+path.replace('/','_'),f'https://raw.githubusercontent.com/{p["repository"]}/{p["revision"]}/{path}') for path in paths)
    def acquire(job):
        name,url=job
        try:
            b=fetch(url); (ROOT/name).write_bytes(b)
            return dict(file=name,url=url,bytes=len(b),sha256=sha(b))
        except Exception as e: return dict(file=name,url=url,error=str(e))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex: records=list(ex.map(acquire,jobs))
    dump('source_manifest.json',records)
    dump('upstream_manifest.json',dict(repository='openai/gpt-oss-20b',revision=rev,files=[r for r in records if r['file'].startswith('upstream/')],weight_bodies_downloaded=False))
    weights=[x for x in info['siblings'] if x['rfilename'].endswith(('.safetensors','.pt'))]
    dump('weight_manifest.json',dict(files=weights,all_weight_bytes=sum(x.get('size',0) for x in weights),safetensors_bytes=sum(x.get('size',0) for x in weights if x['rfilename'].endswith('.safetensors')),downloaded=False))
    dump('harmony_pypi.json',json.loads(fetch('https://pypi.org/pypi/openai-harmony/json')))
    print(json.dumps(dict(model_revision=rev,pins=pins,errors=[r for r in records if 'error' in r]),indent=2))
if __name__=='__main__': main()
