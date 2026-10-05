"""Audit static evidence and create final inventory without model or product access."""
import json, hashlib, subprocess, datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(n,o): (ROOT/n).write_text(json.dumps(o,ensure_ascii=True,indent=2)+'\n',encoding='utf-8')
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,text=True).strip()
def main():
    assert git('rev-parse','HEAD')=='7fcdecbe26f4fd01138edf8f58c02ce4b947db0b'
    assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
    policy=REPO/'benchmark_design/context_policy/current-repo-v1-draft3.json'
    assert sha(policy.read_bytes())=='d93f5136339153e65e35ef720333e21260292bc680f2cd3cfe608dfa46939a3b'
    src=json.loads((ROOT/'source_manifest.json').read_text())
    for r in src:
        if 'sha256' in r:assert sha((ROOT/r['file']).read_bytes())==r['sha256'],r['file']
    weights=json.loads((ROOT/'weight_manifest.json').read_text());index=json.loads((ROOT/'upstream/model.safetensors.index.json').read_text())
    selected=sorted(set(index['weight_map'].values()))
    records={x['rfilename']:x for x in weights['files']}
    assert len(selected)==3 and all(n in records for n in selected)
    weights.update(selected_package='root HF indexed shards',selected_files=selected,selected_checkpoint_bytes=sum(records[n]['size'] for n in selected),
      index_tensor_payload_bytes=index['metadata']['total_size'],alternative_original_bytes=records['original/model.safetensors']['size'],
      warning='all_weight_bytes includes both alternate packages; use selected_checkpoint_bytes for the proposed runtime',local_weight_body_verification=False)
    dump('weight_manifest.json',weights)
    # Archive additional implementation evidence already acquired at the same immutable pins.
    extra=['transformers_src_transformers_integrations_bitsandbytes.py','peft_src_peft_tuners_lora_bnb.py']
    prior=json.loads((ROOT.parent/'qwen3_coder_next'/'source_manifest.json').read_text())
    for name in extra:
        origin=ROOT.parent/'qwen3_coder_next'/'sources'/name;target=ROOT/'sources'/name
        if not target.exists():target.write_bytes(origin.read_bytes())
        record=next(r for r in prior if Path(r.get('file','')).name==name and 'sha256' in r)
        assert sha(target.read_bytes())==record['sha256']
        if not any(r.get('file')=='sources/'+name for r in src):src.append(dict(file='sources/'+name,url=record['url'],sha256=record['sha256'],bytes=target.stat().st_size,acquisition='copied unchanged from prior pinned source acquisition; no prior results used'))
    dump('source_manifest.json',src)
    checks=json.loads((ROOT/'capacity_checks.json').read_text());info=json.loads((ROOT/'information_semantics_checks.json').read_text());template=json.loads((ROOT/'template_checks.json').read_text())
    assert len(checks)==45 and all(r['capacity_result']=='PASS' for r in checks)
    assert len(info)==5 and len({r['k_sha256'] for r in info})==1 and [r['selected_kinds'] for r in info]==[[],['EPISODIC'],['DESCRIPTIVE'],['CONFIRMED_RULE'],['EPISODIC','CONFIRMED_RULE']]
    for row in checks+info+template:
        data=json.loads((ROOT/'synthetic'/(row['name']+'.json')).read_text(encoding='utf-8'))
        assert len(data['token_ids'])==row['input_tokens']
        canonical=json.dumps(data['token_ids'],sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()
        assert sha(canonical)==row['token_ids_sha256']
    pins=json.loads((ROOT/'implementation_pins.json').read_text())
    dump('proposed_runtime.json',dict(certified=False,model_repository='openai/gpt-oss-20b',model_revision=json.loads((ROOT/'upstream_manifest.json').read_text())['revision'],
      selected_model_package=selected,runtime=pins['vllm'],platform='Linux/CUDA; not installed or launched',source_dependencies={'torch':'2.9.1','flashinfer-python':'0.6.3','transformers':'4.57.6'},
      full_binary_kernel_container_lock_verified=False,serializer='openai-harmony 0.0.8 typed conversations; ordinary TextContent; exact token-ID input',
      system_instructions_sha256=json.loads(policy.read_text())['system'] and sha(json.loads(policy.read_text())['system'].encode()),
      reasoning_effort_proposal='medium',reasoning_effort_frozen=False,clock_and_metadata_frozen_for_study=False,fixture_date='2026-10-03',
      engine_proposal={'max_model_len':32768,'max_num_seqs':1,'tensor_parallel_size':1,'dtype':'bfloat16','checkpoint_quantization':'native mxfp4','generation_config':'vllm','enable_prefix_caching':False,'speculative_decoding':False},
      sampling_proposal={'temperature':0.0,'top_p':1.0,'top_k':0,'min_p':0.0,'repetition_penalty':1.0,'frequency_penalty':0.0,'presence_penalty':0.0,'seed':0,'stop':[],
        'stop_token_ids':[200002,199999,200012],'ignore_eos':False,'max_tokens':2048,'min_tokens':0,'n':1,'truncate_prompt_tokens':None,'skip_special_tokens':False},
      generated_token_counter='one max_tokens counter includes analysis/final/header/control/terminal tokens',retries=0,tools=[],builtin_tools=[],history=[],
      completion_projection_certified=False,request_isolation_certified=False,native_quantized_training_supported_at_transformers_pin=False))
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5,minutes=30))).isoformat()
    dump('workspace_audit.json',dict(audited_at=now,workspace=str(REPO),head=git('rev-parse','HEAD'),expected_head_matches=True,tracked_diff=git('diff','--name-only'),staged_diff=git('diff','--cached','--name-only'),
      status=git('status','--short'),policy_sha256=sha(policy.read_bytes()),artifact_scope='experiments/model_preflight/gpt_oss_20b/',excluded_from_model_context='frozen EXCLUDED_DIRS includes experiments',
      model_generation_performed=False,benchmark_tasks_inspected=False,candidate_artifacts_inspected=False,adaptation_performed=False,step_8k_b_rerun=False,committed=False,
      synthetic_capacity_cases=len(checks),synthetic_input_fixtures=len(list((ROOT/'synthetic').glob('*.json'))),hand_authored_channel_examples=4,full_parser_executed=False))
    report=(ROOT/'REPORT.md').read_text(encoding='utf-8')
    assert len(__import__('re').findall(r'^## \d+\.',report,__import__('re').M))==23
    # Files installed by pip are recorded separately; dependencies and pycache excluded from delivery inventory.
    records=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or p.name=='artifact_manifest.json' or any(x in ('dependencies','__pycache__') for x in p.relative_to(ROOT).parts):continue
        b=p.read_bytes();records.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(b),sha256=sha(b)))
    dump('artifact_manifest.json',dict(files=records,excluded=['dependencies/','__pycache__/','artifact_manifest.json'],model_weight_bodies_included=False))
    print(json.dumps(dict(head=git('rev-parse','HEAD'),tracked_changes=False,capacity_passes=45,fixtures=len(list((ROOT/'synthetic').glob('*.json'))),inventoried_files=len(records),selected_checkpoint_bytes=weights['selected_checkpoint_bytes'],report_sections=23),indent=2))
if __name__=='__main__':main()
