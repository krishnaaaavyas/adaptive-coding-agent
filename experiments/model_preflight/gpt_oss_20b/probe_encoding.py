import os, sys, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path[:0]=[str(ROOT/'dependencies'),str(ROOT.parent/'qwen3_coder_next'/'dependencies')]
os.environ['USE_TORCH']='0'
os.environ['TIKTOKEN_RS_CACHE_DIR']=str(ROOT/'encoding_cache')
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
from transformers import AutoTokenizer
from transformers.utils.chat_template_utils import _compile_jinja_template
from openai_harmony import *
t=AutoTokenizer.from_pretrained(str(ROOT/'upstream'),local_files_only=True,trust_remote_code=False)
compiled=_compile_jinja_template(t.chat_template)
compiled.globals['strftime_now']=lambda fmt:'2026-10-03'
e=load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)
request=[{'role':'system','content':'Synthetic system.'},{'role':'user','content':'Synthetic user.'}]
s=t.apply_chat_template(request,tokenize=False,add_generation_prompt=True)
ids=t.apply_chat_template(request,tokenize=True,add_generation_prompt=True)
print(s); print(ids)
convo=Conversation.from_messages([Message.from_role_and_content(Role.SYSTEM,SystemContent.new().with_conversation_start_date('2026-10-03')),Message.from_role_and_content(Role.DEVELOPER,DeveloperContent.new().with_instructions('Synthetic system.')),Message.from_role_and_content(Role.USER,'Synthetic user.')])
hids=e.render_conversation_for_completion(convo,Role.ASSISTANT)
print(e.decode(hids));print('structured parity:',ids==hids)
print('raw full encode parity:',ids==e.encode(s,allowed_special='all'))
print('library file:',__import__('openai_harmony').__file__)
print('NFC:',e.encode('cafe\u0301'),e.encode('caf\u00e9'))
