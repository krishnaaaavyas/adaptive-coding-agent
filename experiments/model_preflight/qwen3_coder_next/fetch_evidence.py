"""Allowlisted metadata/tokenizer/source acquisition; never downloads weights."""
import hashlib, json, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent
def sha(data): return hashlib.sha256(data).hexdigest()
def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'candidate-blind-static-preflight'}), timeout=60) as r: return r.read()
def dump(name, obj): (ROOT/name).write_text(json.dumps(obj, indent=2)+'\n', encoding='utf-8')
def main():
    repo='Qwen/Qwen3-Coder-Next'
    existing=ROOT/'upstream/hub_metadata.json'
    info=json.loads(existing.read_text()) if existing.exists() else json.loads(fetch(f'https://huggingface.co/api/models/{repo}?blobs=true'))
    rev=info['sha']
    info=json.loads(fetch(f'https://huggingface.co/api/models/{repo}/revision/{rev}?blobs=true'))
    assert info['sha']==rev
    (ROOT/'upstream').mkdir(exist_ok=True)
    dump('upstream/hub_metadata.json',info)
    names=['config.json','generation_config.json','tokenizer_config.json','tokenizer.json','vocab.json','merges.txt','chat_template.jinja','README.md','model.safetensors.index.json']
    records=[]
    for name in names:
        url=f'https://huggingface.co/{repo}/resolve/{rev}/{name}'
        data=fetch(url); (ROOT/'upstream'/name).write_bytes(data)
        records.append(dict(file=name,url=url,bytes=len(data),sha256=sha(data)))
    dump('upstream_manifest.json',dict(repository=repo,revision=rev,files=records,weight_bodies_downloaded=False))
    print('Model revision:',rev,flush=True)
    versions={'transformers':('huggingface/transformers','v4.57.6'),'peft':('huggingface/peft','v0.18.0'),'vllm':('vllm-project/vllm','v0.16.0'),'bitsandbytes':('bitsandbytes-foundation/bitsandbytes','0.49.1')}
    files={
      'transformers':['src/transformers/models/qwen3_next/modeling_qwen3_next.py','src/transformers/models/qwen3_next/configuration_qwen3_next.py','src/transformers/integrations/bitsandbytes.py'],
      'peft':['docs/source/developer_guides/lora.md','docs/source/developer_guides/quantization.md','docs/source/developer_guides/checkpoint.md','src/peft/utils/constants.py','src/peft/tuners/lora/model.py','src/peft/tuners/lora/layer.py'],
      'vllm':['vllm/model_executor/models/qwen3_next.py','vllm/model_executor/models/registry.py','vllm/sampling_params.py','vllm/v1/engine/processor.py','vllm/v1/engine/output_processor.py','vllm/engine/arg_utils.py','requirements/cuda.txt','requirements/common.txt'],
      'bitsandbytes':['README.md']}
    (ROOT/'sources').mkdir(exist_ok=True); manifest=[]; pins={}
    saved_pins=json.loads((ROOT/'implementation_pins.json').read_text()) if (ROOT/'implementation_pins.json').exists() else {}
    for key,(project,tag) in versions.items():
        try:
            commit=saved_pins.get(key,{}).get('revision') or json.loads(fetch(f'https://api.github.com/repos/{project}/commits/{tag}'))['sha']
            pins[key]=dict(repository=project,version=tag,revision=commit)
            for path in files[key]:
                name=key+'_'+path.replace('/','_'); url=f'https://raw.githubusercontent.com/{project}/{commit}/{path}'
                try:
                    data=fetch(url); (ROOT/'sources'/name).write_bytes(data)
                    manifest.append(dict(file=name,url=url,bytes=len(data),sha256=sha(data)))
                except Exception as e: manifest.append(dict(file=name,url=url,error=str(e)))
        except Exception as e: pins[key]=dict(error=str(e),version=tag)
    dump('implementation_pins.json',pins); dump('source_manifest.json',manifest)
    weights=[x for x in info['siblings'] if x['rfilename'].endswith('.safetensors')]
    dump('weight_manifest.json',dict(files=weights,checkpoint_bytes=sum(x.get('size',0) for x in weights),index_metadata=json.loads((ROOT/'upstream/model.safetensors.index.json').read_text())['metadata'],downloaded=False))
    print(json.dumps(pins,indent=2),flush=True)
if __name__=='__main__': main()
