import json
from fetch_evidence import ROOT,fetch,sha,dump
pins=json.loads((ROOT/'implementation_pins.json').read_text())
items={
 'vllm':['vllm/v1/engine/input_processor.py','vllm/v1/core/sched/utils.py','vllm/outputs.py','vllm/lora/models.py','vllm/model_executor/layers/fused_moe/layer.py'],
 'peft':['src/peft/peft_model.py','src/peft/utils/save_and_load.py','src/peft/utils/other.py','src/peft/tuners/lora/bnb.py']}
m=json.loads((ROOT/'source_manifest.json').read_text())
for key,paths in items.items():
 for path in paths:
  pin=pins[key]; url=f"https://raw.githubusercontent.com/{pin['repository']}/{pin['revision']}/{path}"
  name=key+'_'+path.replace('/','_')
  try:
   data=fetch(url); (ROOT/'sources'/name).write_bytes(data); m.append(dict(file=name,url=url,bytes=len(data),sha256=sha(data)))
  except Exception as e: m.append(dict(file=name,url=url,error=str(e)))
dump('source_manifest.json',m)
print(json.dumps([x for x in m if 'error' in x],indent=2))
