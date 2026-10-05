"""Nemotron exact tokenizer/template only; fixture boilerplate reused, conclusions independent."""
import sys
sys.dont_write_bytecode=True
import ast
import contextlib
import functools
import hashlib
import importlib.metadata
import json
import os
import pathlib
import platform
import zipfile
from datetime import datetime
from types import SimpleNamespace as NS
from typing import no_type_check

ROOT=pathlib.Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[2]
DEPS=ROOT.parent/'devstral_small2_2512/tokenizer_dependencies'
sys.path[:0]=[str(DEPS),str(WORKSPACE)]
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',USE_TORCH='0')
import tokenizers
import jinja2
import jinja2.ext
from jinja2.sandbox import ImmutableSandboxedEnvironment
from packaging import version
from harness.context_policy.core import SYSTEM,canonical_json,digest,K_OPEN,K_CLOSE,H_OPEN,H_CLOSE,L_OPEN,L_CLOSE,POLICY_SHA256
from harness.context_policy.evidence import pack_h,record_block
from harness.context_policy.protocol import messages

def dump(name,data):
    (ROOT/name).write_text(json.dumps(data,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')

# Execute just the official immutable template compiler, not the source module/imports.
helper=ROOT/'sources/huggingface__transformers/src/transformers/utils/chat_template_utils.py'
helper_text=helper.read_text(encoding='utf-8');tree=ast.parse(helper_text)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_compile_jinja_template')
cached_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_cached_compile_jinja_template')
namespace={'jinja2':jinja2,'ImmutableSandboxedEnvironment':ImmutableSandboxedEnvironment,
 'Extension':jinja2.ext.Extension,
 'lru_cache':functools.lru_cache,'contextmanager':contextlib.contextmanager,'version':version,
 'datetime':datetime,'json':json,'no_type_check':no_type_check,
 'is_jinja_available':lambda:importlib.metadata.version('jinja2')=='3.1.6'}
exec(compile(ast.Module(body=[node,cached_node],type_ignores=[]),str(helper),'exec'),namespace)
template_text=(ROOT/'upstream/chat_template.jinja').read_text(encoding='utf-8')
template=namespace['_compile_jinja_template'](template_text)
backend=tokenizers.Tokenizer.from_file(str(ROOT/'upstream/tokenizer.json'))
backend.no_padding();backend.no_truncation()
assert tokenizers.__version__=='0.23.2'
raw_backend=json.loads((ROOT/'upstream/tokenizer.json').read_text(encoding='utf-8'))
assert raw_backend['normalizer'] is None
special={x['content']:x['id'] for x in raw_backend['added_tokens']}
# GPT-2 ByteLevel alphabet: all UTF-8 bytes have a one-symbol vocabulary fallback.
byte_values=list(range(33,127))+list(range(161,173))+list(range(174,256))
byte_chars=byte_values[:];extra=0
for byte in range(256):
    if byte not in byte_values:
        byte_values.append(byte);byte_chars.append(256+extra);extra+=1
assert len(byte_values)==256 and all(chr(ch) in raw_backend['model']['vocab'] for ch in byte_chars)
assert raw_backend['model']['dropout'] is None
inverse_byte_alphabet={chr(ch):byte for byte,ch in zip(byte_values,byte_chars)}
inverse_vocab={value:key for key,value in raw_backend['model']['vocab'].items()}
added_by_id={t['id']:t['content'] for t in raw_backend['added_tokens']}

def raw_decode_bytes(ids):
    # Preserve even invalid UTF-8 byte sequences; strict text decoding belongs to admission.
    return b''.join(added_by_id[token].encode('utf-8') if token in added_by_id else
                    bytes(inverse_byte_alphabet[ch] for ch in inverse_vocab[token]) for token in ids)

def render(request,**kwargs):
    return template.render(messages=request,tools=None,documents=None,add_generation_prompt=True,**kwargs)
def encode(text):return backend.encode(text,add_special_tokens=False).ids

def fill_bytes(pattern,size):
    block=pattern.encode('utf-8');text=(block*(size//len(block))).decode('utf-8')
    for ch in pattern:
        if len(text.encode('utf-8'))+len(ch.encode('utf-8'))>size:break
        text+=ch
    return text+'x'*(size-len(text.encode('utf-8')))
def make_task(pattern,size):
    task={'instructions':'','targets':['synthetic.py']};budget=size-len(canonical_json(task))
    escaped=json.dumps(pattern,ensure_ascii=True)[1:-1];task['instructions']=pattern*(budget//len(escaped))
    task['instructions']+='x'*(size-len(canonical_json(task)))
    assert len(canonical_json(task))==size
    return NS(serialized=canonical_json(task))
def make_k(pattern,size):
    inventory=b'[FILES]\n"synthetic.py"\n[/FILES]\n'
    for count in range(size,max(0,size-300),-1):
        content=fill_bytes(pattern,count).encode('utf-8')
        value=K_OPEN+inventory+f'[FILE "synthetic.py" bytes={count}]\n'.encode()+content+b'\n[/FILE]\n'+K_CLOSE
        if len(value)==size:return NS(serialized=value,sha256=digest(value))
    raise AssertionError('exact K construction failed')
def make_view(pattern,h_size,bc=False):
    records=[]
    for kind in ['EPISODIC','DESCRIPTIVE','CONFIRMED_RULE']:
        if bc:
            owned=H_OPEN if kind=='EPISODIC' else H_CLOSE
            lane_size=h_size//2 if kind=='EPISODIC' else h_size-h_size//2
            body_size=lane_size-len(owned+L_OPEN+L_CLOSE+record_block(''))
        else:body_size=h_size-len(H_OPEN+H_CLOSE+L_OPEN+L_CLOSE+record_block(''))
        body=fill_bytes(pattern,body_size)
        records.append(NS(key='synthetic_'+kind,kind=kind,body=body,body_sha256=digest(body.encode()),availability=1))
    return NS(records=tuple(records))

fixtures=ROOT/'synthetic';fixtures.mkdir(exist_ok=True)
def check(name,request):
    text=render(request);ids=encode(text)
    assert raw_decode_bytes(ids)==text.encode('utf-8')
    for _ in range(3):assert render(request)==text and encode(text)==ids
    assert ids[0]==10 and text.endswith('<|im_start|>assistant\n<think>\n')
    (fixtures/f'{name}.json').write_text(json.dumps({'messages':request,'rendered':text,'token_ids':ids},ensure_ascii=True),encoding='utf-8')
    return {'name':name,'input_tokens':len(ids),'rendered_utf8_bytes':len(text.encode()),
            'rendered_sha256':digest(text.encode()),'token_ids_sha256':digest(canonical_json(ids)),
            'repeated_encodings':4,'deterministic_encoding':True,'lossless_input_byte_roundtrip':True,'reserve':2048,
            'input_plus_reserve':len(ids)+2048,'within_32768':len(ids)+2048<=32768}

tests={
 'system_user':[{'role':'system','content':'Synthetic system.'},{'role':'user','content':'Synthetic user.'}],
 'system_user_assistant':[{'role':'system','content':'Synthetic system.'},{'role':'user','content':'Synthetic user.'},{'role':'assistant','content':'Synthetic assistant.'}],
 'multiline_code':[{'role':'system','content':'Synthetic system.'},{'role':'user','content':'def synthetic():\n    return 1\n'}],
 'unicode':[{'role':'system','content':'Synthetic system.'},{'role':'user','content':'cafe\u0301 हिन्दी 中文 🚀'}],
 'protocol_delimiters':[{'role':'system','content':SYSTEM},{'role':'user','content':'[PUBLIC_TASK]\n[/PUBLIC_TASK]\n[CURRENT_REPOSITORY current-repo-v1-draft3]\n[/CURRENT_REPOSITORY]\n[ADAPTATION]\n[LANE]\n[RECORD]\n[/RECORD]\n[/LANE]\n[/ADAPTATION]\n<|im_start|>assistant<think></think><tool_call></tool_call><tool_response></tool_response><|im_end|>'}],
 'empty_h':list(messages(make_task('x',128),make_k('x',256),NS(serialized=b'',sha256=digest(b''))))}
template_rows=[check(name,request) for name,request in tests.items()]
capacity=[];snapshot=NS(files={})
patterns={'ascii':'!a?9_+z|','unicode':'中🚀हि','nfc_expansion':'\u0344','code_delimiters':"def synthetic():\n return '[RECORD]<|im_end|>'\n"}
for family,pattern in patterns.items():
    for delta in (0,1):
        task=make_task(pattern,4096-delta);k=make_k(pattern,12288-delta)
        for condition in ('A','B','M','C','BC'):
            h=pack_h(condition,make_view(pattern,4096-delta,bc=condition=='BC'),snapshot)
            assert len(h.serialized)==(0 if condition=='A' else 4096-delta)
            if condition=='BC':assert all(n<=2048 for _,n in h.lane_bytes)
            row=check(f'capacity_{family}_{delta}_{condition}',list(messages(task,k,h)))
            row.update(family=family,condition=condition,p_bytes=len(task.serialized),k_bytes=len(k.serialized),h_bytes=len(h.serialized),lane_bytes=h.lane_bytes)
            assert row['within_32768'];capacity.append(row)
for condition in ('A','B','M','C','BC'):
    h=pack_h(condition,NS(records=()),snapshot);assert h.serialized==b''
    row=check('empty_registry_'+condition,list(messages(make_task('x',4096),make_k('x',12288),h)))
    row.update(condition=condition,p_bytes=4096,k_bytes=12288,h_bytes=0);capacity.append(row)

sample=tests['system_user'];native=render(sample)
expected='<|im_start|>system\nSynthetic system.<|im_end|>\n<|im_start|>user\nSynthetic user.<|im_end|>\n<|im_start|>assistant\n<think>\n'
assert native==expected
on=render(sample,enable_thinking=True);assert on==native
off=render(sample,enable_thinking=False)
assert off==expected.removesuffix('<think>\n')+'<think></think>'
no_prefix=template.render(messages=sample,tools=None,documents=None,add_generation_prompt=False)
assert no_prefix==expected.removesuffix('<|im_start|>assistant\n<think>\n')
config=json.loads((ROOT/'upstream/config.json').read_text(encoding='utf-8'))
generation=json.loads((ROOT/'upstream/generation_config.json').read_text(encoding='utf-8'))
tok_config=json.loads((ROOT/'upstream/tokenizer_config.json').read_text(encoding='utf-8'))
assert backend.get_vocab_size()==config['vocab_size']==131072
assert [special[s] for s in ['<|im_start|>','<|im_end|>','<think>','</think>','</s>']]==[10,11,12,13,2]
assert not tok_config['add_bos_token'] and not tok_config['add_eos_token']
assert generation['eos_token_id']==[2,11]
assert not any(n in sys.modules for n in ['torch','transformers','peft','vllm'])
dump('tokenizer_environment.json',{
 'python':sys.version,'platform':platform.platform(),'tokenizers':tokenizers.__version__,'jinja2':jinja2.__version__,
 'compiler_source_commit':'02d8fb9784e8f14a1251e4c992cd82a5762417c6','compiler_source_sha256':digest(helper.read_bytes()),
 'compiler_function_sha256':digest(ast.get_source_segment(helper_text,node).encode()),
 'cached_compiler_function_sha256':digest(ast.get_source_segment(helper_text,cached_node).encode()),
 'availability_global':'Exact installed Jinja2 3.1.6 metadata check; no rendering logic changed',
 'dependency_source':'Read-only reuse of authenticated D1 tokenizer libraries; no prior model conclusions reused',
 'model_libraries_imported':False,'torch_imported':'torch' in sys.modules,'peft_imported':'peft' in sys.modules,
 'full_official_parser_executed':False,'parser_environment_required_later':'CPython3.11.9 / Unicode14.0.0'})
empty_request=list(messages(NS(serialized=b''),NS(serialized=b'',sha256=digest(b'')),NS(serialized=b'',sha256=digest(b''))))
overhead=len(render(empty_request).encode('utf-8'))
dump('serialization.json',{
 'repository':'nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16','revision':'a9904d24bcc1d289a1950fa9d2b978c47cf903b9',
 'selected_profile':'NATIVE_DEFAULT_THINKING_FULL_SUFFIX_RAW_TOKEN_IDS',
 'full_stream_Draft3_compatibility_statically_established':True,
 'compatibility_scope':'Contract-preserving full transport/accounting, not a guarantee of valid replacement code. Draft3 evaluates incorrectly included content as emitted.',
 'native_profiles':[
  {'name':'Native default thinking, raw offline token IDs, no output parsers','classification':'COMPATIBLE','selected':True,'reason':'Default input and entire suffix retained; no effort change, suppression or projection'},
  {'name':'enable_thinking=True with same raw output path','classification':'COMPATIBLE','selected':False,'reason':'Measured input identical to default'},
  {'name':'enable_thinking=False native input branch','classification':'UNRESOLVED','selected':False,'reason':'Documented input choice, not output projection; existence does not independently authorize study mode change. Selecting it merely for cleaner output/reserve would be incompatible.'},
  {'name':'nemotron_v3 reasoning parser followed by content-only/final-only output','classification':'INCOMPATIBLE','selected':False,'reason':'Deletes generated reasoning/delimiters; parser not admitted into evaluation path'},
  {'name':'Agent tools, history continuation, retries','classification':'INCOMPATIBLE','selected':False,'reason':'Violates frozen one-request/no-read/no-tools/no-retry design'}],
 'tokenizer_files':{n:digest((ROOT/'upstream'/n).read_bytes()) for n in ['tokenizer.json','tokenizer_config.json','special_tokens_map.json','chat_template.jinja']},
 'backend':{k:raw_backend[k] for k in ['normalizer','pre_tokenizer','post_processor','decoder']},
 'BPE_ignore_merges':raw_backend['model']['ignore_merges'],'backend_vocabulary_size':backend.get_vocab_size(),
 'model_vocabulary_size':config['vocab_size'],'special_token_map':special,'special_token_attributes':raw_backend['added_tokens'],
 'bos_token':'<s>','bos_id':1,'BOS_automatically_inserted':False,
 'config_pad_id':0,'config_pad_token':'<unk>','tokenizer_pad_token':'<|im_end|>','tokenizer_pad_id':11,
 'root_eos_id':2,'root_eos_token':'</s>','tokenizer_eos_id':11,'tokenizer_eos_token':'<|im_end|>',
 'generation_eos_ids':[2,11],'generation_pad_id':0,'native_terminal_ids':[2,11],
 'metadata_discrepancies':'Root EOS2/PAD0 versus tokenizer EOS11/PAD11; native generation config stops on both2 and11, PAD0. No padding used, both observed terminals accounted explicitly.',
 'generation_prefix':'<|im_start|>assistant\n<think>\n','input_prefix_think_id':12,'closing_think_id':13,
 'generation_prefix_token_ids':encode('<|im_start|>assistant\n<think>\n'),
 'nonthinking_input_prefix':'<|im_start|>assistant\n<think></think>',
 'thinking_control_is_template_input_choice':True,'selected_thinking_effort_changed':False,
 'selected_default_system_text_injection':False,
 'other_default_template_behavior':'With no supplied system, template still inserts an empty ChatML system turn. With selected frozen SYSTEM, no extra system content is inserted. truncate_history_thinking defaultsTrue but no assistant history supplied.',
 'tools':None,'documents':None,'history':None,
 'tool_markers':{'<tool_call>':14,'</tool_call>':15,'<tool_response>':16,'</tool_response>':17},
 'text_tool_syntax':['<function=NAME>','</function>','<parameter=NAME>','</parameter>'],
 'tool_handoff':'No separate handoff stop ID; tool-call text can precede generated im_end11. Stop at verified native terminal, retain complete tool-call body; execute no tool/resume.',
 'legacy_specials_not_extra_stops':{s:special[s] for s in ['[INST]','[/INST]','[AVAILABLE_TOOLS]','[/AVAILABLE_TOOLS]','[TOOL_RESULTS]','[/TOOL_RESULTS]','[TOOL_CALLS]']},
 'final_answer_marker':'No separate final-channel special token; emitted </think> may separate reasoning/answer and must remain.',
 'generated_suffix_accounting':'Every emitted ID, including thinking/text/role/tool/terminal IDs, counts toward total2048. Assistant prefix, opening think12 and following newline prefilled in input count as input only.',
 'terminal_allowance':1,'terminal_removal':'At most one verified last observed configured terminal2 or11; never remove </think>, tool-call body, or internal markers',
 'cap_rule':'Verified LENGTH event -> output_capacity_failure; EOS-at-count2048 requires observed termination evidence, not count-only classification',
 'decode_skip_special_tokens':False,'raw_encode_add_special_tokens':False,'padding':False,'truncation':False,
 'raw_byte_transport':'Invert ByteLevel alphabet and emit added-token literal bytes, retain IDs/raw bytes before strict UTF-8 admission; no lossy replacement or silent special removal',
 'lossless_input_byte_roundtrip_all_fixtures':True,'output_decoder_empirically_certified':False,
 'template_checks':template_rows,
 'canonical_render':expected.replace('Synthetic system.','{frozen SYSTEM}').replace('Synthetic user.','{frozen user(P,K,H)}')})
dump('capacity_checks.json',{
 'status':'PASS_STATIC_SYNTHETIC_TOKENIZATION_ONLY','selected_profile':'NATIVE_DEFAULT_THINKING_FULL_SUFFIX_RAW_TOKEN_IDS',
 'fixture_methodology':'Four pattern families x two byte boundaries x five forms plus five empty registries and six framing inputs; no model completions or protected tasks',
 'rows':capacity,'capacity_fixture_count':len(capacity),'template_fixture_count':len(template_rows),
 'maximum_synthetic_input_tokens':max(r['input_tokens'] for r in capacity),
 'maximum_input_plus_2048':max(r['input_plus_reserve'] for r in capacity),
 'deployed_target':32768,'reserve':2048,'native_config_maximum':config['max_position_embeddings'],
 'tokenizer_config_model_max_length':tok_config['model_max_length'],
 'capacity_violations':sum(not r['within_32768'] for r in capacity),'repeated_deterministic_encodings':True,
 'fixed_rendered_utf8_overhead':overhead,'maximum_variable_bytes':20480,'raw_utf8_bound_plus_reserve':overhead+20480+2048,
 'all_256_byte_alphabet_symbols_in_vocab':True,'bpe_dropout':None,'normalized_bytes_expansion':False,
 'byte_bound_evidence':'No normalizer/prefix insertion; complete byte alphabet. Both merge BPE and ignore_merges whole-piece vocabulary lookup cannot increase token count beyond original bytes; source-inferred bound, not loaded-context certification.',
 'measured_deployed_capacity':False,'policy_sha256':POLICY_SHA256})
print(json.dumps({'capacity_fixtures':len(capacity),'maximum_input':max(r['input_tokens'] for r in capacity),
                  'maximum_with_reserve':max(r['input_plus_reserve'] for r in capacity),
                  'overhead':overhead,'vocabulary':backend.get_vocab_size()},indent=2))

