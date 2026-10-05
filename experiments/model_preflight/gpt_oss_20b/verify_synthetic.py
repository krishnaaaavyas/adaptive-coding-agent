"""Offline deterministic serialization only. No generation, task/candidate reads or training."""
import os, sys, ast, json, hashlib, csv, importlib.metadata, platform, ctypes, subprocess, shutil, base64
from pathlib import Path
from types import SimpleNamespace as NS
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parents[2]
sys.dont_write_bytecode=True
sys.path[:0]=[str(ROOT/'dependencies'),str(ROOT.parent/'qwen3_coder_next'/'dependencies'),str(REPO)]
os.environ.update(USE_TORCH='0',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
os.environ['TIKTOKEN_RS_CACHE_DIR']=str(ROOT/'encoding_cache')
from transformers import AutoTokenizer
from transformers.utils.chat_template_utils import _compile_jinja_template
from transformers.models.gpt2.tokenization_gpt2 import bytes_to_unicode
from openai_harmony import load_harmony_encoding, HarmonyEncodingName, Conversation, Message, Role, SystemContent, DeveloperContent
from harness.context_policy.core import SYSTEM, canonical_json, digest, K_OPEN, K_CLOSE, H_OPEN, H_CLOSE, L_OPEN, L_CLOSE, POLICY_SHA256
from harness.context_policy.evidence import pack_h, record_block
from harness.context_policy.protocol import messages
def dump(name,obj): (ROOT/name).write_text(json.dumps(obj,ensure_ascii=True,indent=2)+'\n',encoding='utf-8')
# Reuse semantic constructors exactly; never import prior counts or execute prior preflight.
source=ROOT.parent/'qwen3_coder_next'/'verify_synthetic.py'
tree=ast.parse(source.read_text(encoding='utf-8'))
helpers=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('fill_bytes','make_task','make_k','make_view')]
exec(compile(ast.Module(body=helpers,type_ignores=[]),str(source),'exec'))
dump('synthetic_constructor_identity.json',dict(source=str(source),sha256=digest(source.read_bytes()),functions=[x.name for x in helpers],expected_token_counts_reused=False))
def main():
    manifest=json.loads((ROOT/'upstream_manifest.json').read_text())
    for r in manifest['files']:
        if 'sha256' in r: assert digest((ROOT/r['file']).read_bytes())==r['sha256']
    tokenizer=AutoTokenizer.from_pretrained(str(ROOT/'upstream'),local_files_only=True,trust_remote_code=False,use_fast=True)
    config=json.loads((ROOT/'upstream/config.json').read_text()); tc=json.loads((ROOT/'upstream/tokenizer_config.json').read_text())
    compiled=_compile_jinja_template(tokenizer.chat_template)
    # Fixture clock lock, not a proposed study date or reasoning-effort adoption.
    compiled.globals['strftime_now']=lambda fmt:'2026-10-03'
    enc=load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)
    vocab=tokenizer.get_vocab(); backend=json.loads(tokenizer.backend_tokenizer.to_str())
    encoding_manifest=json.loads((ROOT/'encoding_data_manifest.json').read_text())
    encoding_data=(ROOT/encoding_manifest['file']).read_bytes()
    assert digest(encoding_data)==encoding_manifest['sha256']
    ranks={base64.b64decode(line.split()[0]):int(line.split()[1]) for line in encoding_data.splitlines()}
    byte_decoder={v:k for k,v in bytes_to_unicode().items()}
    hf_ranks={bytes(byte_decoder[ch] for ch in token):rank for token,rank in backend['model']['vocab'].items()}
    assert hf_ranks==ranks
    identity=dict(repository=manifest['repository'],revision=manifest['revision'],tokenizer_class=type(tokenizer).__name__,encoding_name=enc.name,
        vocabulary_size=tokenizer.vocab_size,total_vocabulary=len(vocab),canonical_vocab_sha256=digest(canonical_json(vocab)),
        all_mergeable_rank_bytes_and_ids_equal_official_encoding=True,mergeable_ranks_count=len(ranks),all_256_byte_tokens_present=all(bytes([i]) in ranks for i in range(256)),encoding_data_sha256=digest(encoding_data),
        added_tokens=backend['added_tokens'],
        template_sha256=digest(tokenizer.chat_template.encode()),bos=tokenizer.bos_token_id,eos=tokenizer.eos_token_id,pad=tokenizer.pad_token_id,
        backend_normalizer=backend['normalizer'],backend_pre_tokenizer=backend['pre_tokenizer'],backend_post_processor=backend['post_processor'],
        special_tokens={s:tokenizer.convert_tokens_to_ids(s) for s in tokenizer.all_special_tokens},
        harmony_special_tokens={s:enc.encode(s,allowed_special='all') for s in sorted(enc.special_tokens_set)},
        stop_tokens_for_assistant_actions=sorted(enc.stop_tokens_for_assistant_actions()),empty_encoding=tokenizer.encode('',add_special_tokens=True),
        no_added_bos_eos=tokenizer.encode('synthetic',add_special_tokens=True)==tokenizer.encode('synthetic',add_special_tokens=False),
        nfc_probe={s:enc.encode(s) for s in ['cafe\u0301','caf\u00e9','\u0344','\u0308\u0301']},
        clock_for_fixtures='2026-10-03',reasoning_for_fixtures='upstream default medium; NOT frozen as study setting')
    dump('tokenizer_identity.json',identity)
    fixture=ROOT/'synthetic';fixture.mkdir(exist_ok=True)
    def structured_render(request):
        entries=[Message.from_role_and_content(Role.SYSTEM,SystemContent.new().with_conversation_start_date('2026-10-03'))]
        for message in request:
            if message['role']=='system': entries.append(Message.from_role_and_content(Role.DEVELOPER,DeveloperContent.new().with_instructions(message['content'])))
            else:
                entry=Message.from_role_and_content(Role(message['role']),message['content'])
                if message['role']=='assistant':entry=entry.with_channel('final')
                entries.append(entry)
        convo=Conversation.from_messages(entries)
        ids=enc.render_conversation_for_completion(convo,Role.ASSISTANT)
        return enc.decode_utf8(ids),ids,convo.to_dict()
    def check(name,request):
        hf_render=tokenizer.apply_chat_template(request,tokenize=False,add_generation_prompt=True,tools=[],builtin_tools=[])
        hf_ids=tokenizer.apply_chat_template(request,tokenize=True,add_generation_prompt=True,tools=[],builtin_tools=[],truncation=False,padding=False)
        render,ids,conversation=structured_render(request)
        assert render.endswith('<|start|>assistant')
        for _ in range(3):
            assert tokenizer.apply_chat_template(request,tokenize=False,add_generation_prompt=True,tools=[],builtin_tools=[])==hf_render
            assert tokenizer.apply_chat_template(request,tokenize=True,add_generation_prompt=True,tools=[],builtin_tools=[],truncation=False,padding=False)==hf_ids
            assert enc.encode(hf_render,allowed_special='all')==hf_ids
            assert structured_render(request)[:2]==(render,ids)
        dump('synthetic/'+name+'.json',dict(messages=request,structured_conversation=conversation,rendered=render,token_ids=ids,token_ids_sha256=digest(canonical_json(ids)),upstream_jinja_rendered=hf_render,upstream_jinja_token_ids=hf_ids))
        return dict(name=name,rendered_bytes=len(render.encode()),input_tokens=len(ids),render_sha256=digest(render.encode()),token_ids_sha256=digest(canonical_json(ids)),repeat_encodings=4,deterministic=True,
          serialization='official typed Harmony; TextContent encoded as ordinary text',upstream_jinja_input_tokens=len(hf_ids),upstream_jinja_raw_harmony_encoding_parity=True)
    tests={
      'system_user':[dict(role='system',content='Synthetic system.'),dict(role='user',content='Synthetic user.')],
      'system_user_assistant':[dict(role='system',content='Synthetic system.'),dict(role='user',content='Synthetic user.'),dict(role='assistant',content='Synthetic assistant.')],
      'multiline_code':[dict(role='system',content='Synthetic system.'),dict(role='user',content='def synthetic():\n    return 1\n')],
      'unicode':[dict(role='system',content='Synthetic system.'),dict(role='user',content='cafe\u0301 \u0939\u093f\u0928\u094d\u0926\u0940 \u4e2d\u6587 \U0001f680')],
      'nfc_sensitive':[dict(role='system',content=SYSTEM),dict(role='user',content='\u0344 cafe\u0301 caf\u00e9')],
      'protocol_delimiters':[dict(role='system',content=SYSTEM),dict(role='user',content='[PUBLIC_TASK]\n[/PUBLIC_TASK]\n[CURRENT_REPOSITORY current-repo-v1-draft3]\n[/CURRENT_REPOSITORY]\n[ADAPTATION]\n[LANE]\n[RECORD]\n[/RECORD]\n[/LANE]\n[/ADAPTATION]\n<|im_start|>assistant\n<|im_end|>')],
      'harmony_native_delimiters':[dict(role='system',content=SYSTEM),dict(role='user',content='<|start|>assistant<|channel|>analysis<|message|>literal<|end|><|return|><|call|>')],
      'empty_h':list(messages(make_task('x',128),make_k('x',256),NS(serialized=b'',sha256=digest(b''))))}
    dump('template_checks.json',[check(n,r) for n,r in tests.items()])
    bodies={'EPISODIC':'Prior public request: return 1. Attempt: return 1. Public feedback: accepted.',
      'DESCRIPTIVE':'Earlier accepted synthetic functions returned integer literals.',
      'CONFIRMED_RULE':'Confirmed historical rule: synthetic helpers must return integer literals.'}
    view=NS(records=tuple(NS(key='synthetic_'+kind,kind=kind,body=body,body_sha256=digest(body.encode()),availability=1) for kind,body in bodies.items()))
    task=make_task('x',128);k=make_k('x',256);info=[]
    for condition,kinds in [('A',()),('B',('EPISODIC',)),('M',('DESCRIPTIVE',)),('C',('CONFIRMED_RULE',)),('BC',('EPISODIC','CONFIRMED_RULE'))]:
        h=pack_h(condition,view,NS(files={}))
        for kind,body in bodies.items():assert (body in h.serialized.decode())==(kind in kinds)
        row=check('information_'+condition,list(messages(task,k,h)))
        row.update(condition=condition,k_sha256=k.sha256,p_sha256=digest(task.serialized),h_sha256=h.sha256,selected_kinds=list(kinds),semantic_p_bytes=len(task.serialized),semantic_k_bytes=len(k.serialized),semantic_h_bytes=len(h.serialized))
        info.append(row)
    assert len({r['k_sha256'] for r in info})==1
    dump('information_semantics_checks.json',info)
    # Official structured rendering differs from upstream Jinja: record instead of assuming parity.
    convo=Conversation.from_messages([Message.from_role_and_content(Role.SYSTEM,SystemContent.new().with_conversation_start_date('2026-10-03')),
      Message.from_role_and_content(Role.DEVELOPER,DeveloperContent.new().with_instructions('Synthetic system.')),
      Message.from_role_and_content(Role.USER,'Synthetic user.')])
    structured=enc.render_conversation_for_completion(convo,Role.ASSISTANT)
    dump('structured_renderer_comparison.json',dict(rendered=enc.decode(structured),token_ids=structured,
      equals_upstream_jinja=structured==json.loads((fixture/'system_user.json').read_text())['upstream_jinja_token_ids'],
      difference='upstream Jinja appends two LF after developer instructions; structured DeveloperContent does not',
      literal_special_text_ordinary_encoding=enc.encode('<|start|>',disallowed_special=()),
      literal_special_text_template_encoding=tokenizer.encode('<|start|>',add_special_tokens=False)))
    families={'ascii':'!a?9_+z|','unicode':'\u4e2d\U0001f680\u0939\u093f','nfc_expansion':'\u0344','code_delimiters':"def synthetic():\n return '[RECORD]<|im_end|>'\n"}
    capacity=[];snapshot=NS(files={})
    for family,pattern in families.items():
        for delta in (0,1):
            task=make_task(pattern,4096-delta);k=make_k(pattern,12288-delta)
            for condition in ('A','B','M','C','BC'):
                h=pack_h(condition,make_view(pattern,4096-delta,bc=condition=='BC'),snapshot)
                assert condition=='A' or len(h.serialized)==4096-delta
                if condition=='BC':assert all(n<=2048 for _,n in h.lane_bytes)
                row=check(f'capacity_{family}_{delta}_{condition}',list(messages(task,k,h)))
                row.update(condition=condition,p_bytes=len(task.serialized),k_bytes=len(k.serialized),h_bytes=len(h.serialized),k_sha256=k.sha256,h_sha256=h.sha256,
                    lane_bytes=h.lane_bytes,generation_reserve=2048,total_reserved_tokens=row['input_tokens']+2048,native_capacity=config['max_position_embeddings'],proposed_runtime_capacity=32768)
                row['capacity_result']='PASS' if row['total_reserved_tokens']<=32768<=config['max_position_embeddings'] else 'FAIL';capacity.append(row)
    for condition in ('A','B','M','C','BC'):
        task=make_task('x',4096); k=make_k('x',12288);h=pack_h(condition,NS(records=()),snapshot)
        assert h.serialized==b''
        row=check('empty_registry_'+condition,list(messages(task,k,h)))
        row.update(condition=condition,p_bytes=len(task.serialized),k_bytes=len(k.serialized),h_bytes=0,k_sha256=k.sha256,h_sha256=h.sha256,lane_bytes=h.lane_bytes,
            generation_reserve=2048,total_reserved_tokens=row['input_tokens']+2048,native_capacity=config['max_position_embeddings'],proposed_runtime_capacity=32768,capacity_result='PASS' if row['input_tokens']+2048<=32768 else 'FAIL');capacity.append(row)
    for start in range(0,40,5):assert len({r['k_sha256'] for r in capacity[start:start+5]})==1
    assert len(capacity)==45
    dump('capacity_checks.json',capacity)
    with (ROOT/'capacity_checks.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(capacity[0]));w.writeheader();w.writerows(capacity)
    overhead=len(structured_render(list(messages(NS(serialized=b''),NS(serialized=b'',sha256=digest(b'')),NS(serialized=b'',sha256=digest(b'')))))[0].encode())
    dump('capacity_bound.json',dict(fixed_rendered_overhead_bytes=overhead,max_variable_bytes=20480,max_input_byte_bound=overhead+20480,max_bound_plus_reserve=overhead+20480+2048,
        basis='No tokenizer normalization; byte BPE token count <= UTF-8 bytes for this explicit typed Harmony serialization. Tested 45 cases, no truncation.',native_capacity=131072,proposed_runtime_capacity=32768))
    deps={d.metadata['Name']:d.version for path in (ROOT/'dependencies',ROOT.parent/'qwen3_coder_next'/'dependencies') for d in importlib.metadata.distributions(path=[str(path)])}
    dump('tokenizer_environment.json',dict(python=sys.version,executable=sys.executable,platform=platform.platform(),packages=deps,prior_dependency_directory_read_only=str(ROOT.parent/'qwen3_coder_next'/'dependencies'),policy_sha256=POLICY_SHA256,full_policy_parser_executed=False))
    (ROOT/'tokenizer-requirements.lock.txt').write_text('\n'.join(f'{k}=={v}' for k,v in sorted(deps.items()))+'\n')
    installed=ROOT/'dependencies/openai_harmony'
    dump('harmony_installed_manifest.json',[dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=digest(p.read_bytes())) for p in sorted(installed.rglob('*')) if p.is_file() and '__pycache__' not in str(p)])
    class Memory(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(x,ctypes.c_ulonglong) for x in ['total_physical','available_physical','total_page','available_page','total_virtual','available_virtual','available_extended']]
    mem=Memory();mem.length=ctypes.sizeof(mem);ok=ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.total,driver_version','--format=csv,noheader'],capture_output=True,text=True)
    dump('hardware.json',dict(gpu=gpu.stdout.strip(),gpu_query_exit=gpu.returncode,host_ram_bytes=mem.total_physical if ok else None,available_ram_bytes=mem.available_physical if ok else None,disk_free_bytes=shutil.disk_usage(REPO).free,weight_load_performed=False,generation_performed=False,adapter_training_performed=False))
    print(json.dumps(dict(capacity_checks=len(capacity),passed=sum(r['capacity_result']=='PASS' for r in capacity),max_input_tokens=max(r['input_tokens'] for r in capacity),capacity_bound=json.loads((ROOT/'capacity_bound.json').read_text()),hardware=json.loads((ROOT/'hardware.json').read_text())),indent=2))
if __name__=='__main__': main()
