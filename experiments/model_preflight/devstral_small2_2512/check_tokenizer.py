"""Exact pinned tokenizer and Jinja helper only. No model, generation or adapter imports."""
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
OLD_DEPS=ROOT.parent/'qwen3_coder_next/dependencies'
DEPS=ROOT/'tokenizer_dependencies'
for wheel in (ROOT/'dependencies_wheels').glob('*.whl'):
    with zipfile.ZipFile(wheel) as archive:
        for member in archive.infolist():
            target=(DEPS/member.filename).resolve()
            assert target.is_relative_to(DEPS.resolve())
        archive.extractall(DEPS)
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
    return template.render(messages=request,tools=None,documents=None,add_generation_prompt=True,
                           bos_token='<s>',eos_token='</s>',pad_token='<pad>',unk_token='<unk>',**kwargs)
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
    assert ids[0]==1
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
 'protocol_delimiters':[{'role':'system','content':SYSTEM},{'role':'user','content':'[PUBLIC_TASK]\n[/PUBLIC_TASK]\n[CURRENT_REPOSITORY current-repo-v1-draft3]\n[/CURRENT_REPOSITORY]\n[ADAPTATION]\n[LANE]\n[RECORD]\n[/RECORD]\n[/LANE]\n[/ADAPTATION]\n[INST][/INST]</s>[TOOL_CALLS][IMG]'}],
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

tokenizer_env={'python':sys.version,'python_executable':sys.executable,'platform':platform.platform(),
 'tokenizers':tokenizers.__version__,'jinja2':jinja2.__version__,
 'compiler_source_commit':'02d8fb9784e8f14a1251e4c992cd82a5762417c6',
 'compiler_source_sha256':digest(helper.read_bytes()),
 'compiler_function_sha256':digest(ast.get_source_segment(helper_text,node).encode()),
 'cached_compiler_function_sha256':digest(ast.get_source_segment(helper_text,cached_node).encode()),
 'availability_global':'is_jinja_available supplied as exact installed Jinja2 3.1.6 metadata check; no rendering logic changed',
 'model_libraries_imported':False,'torch_imported':'torch' in sys.modules,
 'full_official_parser_executed':False,'parser_environment_required_later':'CPython3.11.9 / Unicode14.0.0',
 'note':'Only tokenizer backend and exact official immutable Jinja compiler function executed; policy synthetic framing/packing helpers only.'}
assert 'torch' not in sys.modules and 'peft' not in sys.modules
dump('tokenizer_environment.json',tokenizer_env)
empty_request=list(messages(NS(serialized=b''),NS(serialized=b'',sha256=digest(b'')),NS(serialized=b'',sha256=digest(b''))))
overhead=len(render(empty_request).encode())
sample=tests['system_user'];rendered=render(sample)
assert rendered=='<s>[SYSTEM_PROMPT]Synthetic system.[/SYSTEM_PROMPT][INST]Synthetic user.[/INST]'
assert render(sample)==template.render(messages=sample,tools=None,documents=None,add_generation_prompt=False,bos_token='<s>',eos_token='</s>',pad_token='<pad>',unk_token='<unk>')
without_system=render([{'role':'user','content':'Synthetic user.'}])
assert 'Mistral Vibe' in without_system and 'Mistral Vibe' not in rendered
added=raw_backend['added_tokens']
serialization={'repository':'mistralai/Devstral-Small-2-24B-Instruct-2512','revision':'55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128',
 'tokenizer_files':{n:digest((ROOT/'upstream'/n).read_bytes()) for n in ['tokenizer.json','tekken.json','tokenizer_config.json','chat_template.jinja']},
 'normalizer':None,'backend':{k:raw_backend[k] for k in ['normalizer','pre_tokenizer','post_processor','decoder']},
 'vocab_size':backend.get_vocab_size(),'tekken_version':'v13','special_token_map':special,
 'special_token_attributes':added,'bos':1,'eos':2,'pad':11,'unk':0,'native_terminal_ids':[2],
 'generation_prefix':'No appended assistant prefix; ends with [/INST] after the single user turn',
 'canonical_render':'<s>[SYSTEM_PROMPT]{frozen SYSTEM}[/SYSTEM_PROMPT][INST]{frozen user(P,K,H)}[/INST]',
 'add_generation_prompt_has_no_effect':True,'default_system_injected_when_system_absent':True,
 'default_system_injected_in_Draft3':False,'native_reasoning_channel_inserted':False,
 'tools':None,'documents':None,'multimodal_content':None,'text_only':True,
 'tool_markers':['[AVAILABLE_TOOLS]','[TOOL_RESULTS]','[TOOL_CALLS]','[ARGS]','[CALL_ID]'],
 'modality_markers':['[IMG]','[IMG_BREAK]','[IMG_END]','[AUDIO]','[BEGIN_AUDIO]'],
 'prohibited_output_projection':True,'decode_skip_special_tokens':False,'strip_only_final_observed_eos':2,
 'raw_byte_transport':'Invert complete ByteLevel alphabet for ordinary IDs and retain added-token literal UTF-8 bytes; keep byte stream before strict UTF-8 decoding. A string decoder may replace invalid UTF-8 and cannot alone prove raw-byte retention.',
 'lossless_input_byte_roundtrip_all_fixtures':True,'output_decoder_empirically_certified':False,
 'template_checks':template_rows,'raw_encode_add_special_tokens_false':True,
 'literal_native_marker_collision_note':'Tokenizer recognizes native special strings even inside supplied text. Preserve canonical bytes/hashes and do not parse machine input by delimiter search.'}
dump('serialization.json',serialization)
dump('capacity_checks.json',{'status':'PASS_STATIC_SYNTHETIC_TOKENIZATION_ONLY','fixture_methodology':'same canonical helpers and 4 pattern families × 2 byte boundaries × 5 forms, plus 5 empty registries; no experimental A/B/M/C/BC generation',
 'rows':capacity,'template_fixture_count':len(template_rows),'capacity_fixture_count':len(capacity),
 'maximum_synthetic_input_tokens':max(r['input_tokens'] for r in capacity),
 'maximum_input_plus_2048':max(r['input_plus_reserve'] for r in capacity),
 'deployed_target':32768,'reserve':2048,'native_config_maximum':393216,
 'capacity_violations':sum(not r['within_32768'] for r in capacity),'repeated_deterministic_encodings':True,
 'fixed_rendered_utf8_overhead':overhead,'maximum_variable_bytes':20480,
 'raw_utf8_bound_plus_reserve':overhead+20480+2048,
 'all_256_byte_alphabet_symbols_in_vocab':True,'bpe_dropout':None,
 'byte_bound_evidence':'Source-code inference: no normalizer, no prefix insertion in ByteLevel pretokenizer, complete byte alphabet and merge-only BPE; token count cannot exceed rendered UTF-8 bytes. Not model/runtime certification.',
 'normalized_bytes_expansion':False,'measured_deployed_capacity':False,
 'policy_sha256':POLICY_SHA256})
print(json.dumps({'capacity_fixtures':len(capacity),'max_input':max(r['input_tokens'] for r in capacity),
                  'max_with_reserve':max(r['input_plus_reserve'] for r in capacity),'torch_imported':False},indent=2))
