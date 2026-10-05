"""Shape arithmetic and hand-authored channel tests; never model inference."""
import json, sys, ast, hashlib, tarfile, os
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.dont_write_bytecode=True
os.environ['TIKTOKEN_RS_CACHE_DIR']=str(ROOT/'encoding_cache')
sys.path.insert(0,str(ROOT/'dependencies'))
from openai_harmony import load_harmony_encoding,HarmonyEncodingName,Role
def dump(n,o): (ROOT/n).write_text(json.dumps(o,ensure_ascii=True,indent=2)+'\n',encoding='utf-8')
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    c=json.loads((ROOT/'upstream/config.json').read_text());L=c['num_hidden_layers'];D=c['hidden_size'];I=c['intermediate_size'];E=c['num_local_experts'];V=c['vocab_size'];Q=c['num_attention_heads']*c['head_dim'];KV=c['num_key_value_heads']*c['head_dim']
    components={'embedding_and_head':2*V*D,'attention_weights':L*(2*D*Q+2*D*KV),'attention_biases':L*(Q+2*KV+D),'attention_sinks':L*c['num_attention_heads'],
      'expert_weights':L*E*(D*2*I+I*D),'expert_biases':L*E*(2*I+D),'router':L*(E*D+E),'layer_norms_and_final':(2*L+1)*D}
    total=sum(components.values())
    dump('architecture_arithmetic.json',dict(basis='ESTIMATED from pinned complete module shapes; no tensor instantiation/header/body verification',components=components,total_parameters=total,
      source_reported_total='21B (rounded)',source_reported_active='3.6B (rounded)',bf16_weight_bytes=2*total,
      full_attention_kv_bytes_at_32768=12*2*KV*2*32768,sliding_kv_bytes_at_128=12*2*KV*2*128))
    attention=L*16*(2*(D+Q)+2*(D+KV));expert=L*E*16*((D+2*I)+(I+D))
    dump('adapter_parameter_estimates.json',dict(basis='ESTIMATED source-shape arithmetic, not instantiated; rank16 planning only',rank=16,
      attention_modules=['model.layers.<i>.self_attn.'+p for p in ['q_proj','k_proj','v_proj','o_proj']],attention_only=attention,
      expert_parameters=['model.layers.<i>.mlp.experts.gate_up_proj','model.layers.<i>.mlp.experts.down_proj'],all_experts_only=expert,attention_plus_all_experts=attention+expert,
      expert_formula='24 * 32 * 16 * ((2880+5760)+(2880+2880))',router_included=False,
      adapter_bf16_bytes=2*(attention+expert),conventional_adapter_training_state_bytes_at_16_bytes_per_parameter=16*(attention+expert)))
    enc=load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)
    examples={
      'analysis_then_final':'<|channel|>analysis<|message|>Synthetic reasoning.<|end|><|start|>assistant<|channel|>final<|message|>def synthetic():\n    return 1\n<|return|>',
      'final_only':'<|channel|>final<|message|>def synthetic():\n    return 1\n<|return|>',
      'handoff':' to=functions.synthetic<|channel|>commentary<|message|>{}<|call|>',
      'analysis_no_final':'<|channel|>analysis<|message|>Synthetic reasoning continues.'}
    rows=[]
    for name,text in examples.items():
        ids=enc.encode(text,allowed_special='all');stop=ids[-1] if ids[-1] in enc.stop_tokens_for_assistant_actions() else None
        try: parsed=[m.to_dict() for m in enc.parse_messages_from_completion_tokens(ids[:-1] if stop else ids,Role.ASSISTANT)]
        except Exception as e:parsed=dict(error=str(e))
        rows.append(dict(name=name,hand_authored=True,model_generated=False,raw_rendered=text,token_ids=ids,total_tokens=len(ids),terminal_token=stop,parsed=parsed))
    dump('channel_parser_checks.json',rows)
    # Distribution source evidence, never execute sdist. Keep flattened source members confined to ROOT.
    archive=ROOT/'sources/openai_harmony-0.0.8.tar.gz';members=[]
    with tarfile.open(archive) as tar:
        for m in tar.getmembers():
            if m.isfile() and (m.name.endswith(('Cargo.toml','Cargo.lock','__init__.py')) or '/src/tiktoken_ext/' in m.name or '/src/load/' in m.name):
                data=tar.extractfile(m).read();name='harmony_sdist_'+m.name.replace('/','_');(ROOT/'sources'/name).write_bytes(data)
                members.append(dict(archive_member=m.name,file='sources/'+name,sha256=sha(data),bytes=len(data)))
    dump('harmony_distribution_source_manifest.json',members)
    current=ROOT/'sources/harmony_python_openai_harmony___init__.py';installed=ROOT/'dependencies/openai_harmony/__init__.py'
    dump('harmony_source_correspondence.json',dict(installed_python_sha256=sha(installed.read_bytes()),pinned_github_python_sha256=sha(current.read_bytes()),equal=installed.read_bytes()==current.read_bytes(),
      equal_after_crlf_to_lf=installed.read_bytes().replace(b'\r\n',b'\n')==current.read_bytes(),
      note='Installed Python source equals pinned GitHub/sdist after Windows CRLF to LF. Wheel and sdist independently pinned by PyPI SHA256; compiled extension hashed separately; not a reproducible binary-build attestation.'))
    # Compare config, tokenizer/template and storage metadata only; no performance/candidate data.
    comparison=[]
    for model in ['qwen3_coder_30b_a3b','qwen3_coder_next']:
        p=ROOT.parent/model;c2=json.loads((p/'upstream/config.json').read_text());wm=json.loads((p/'weight_manifest.json').read_text())
        upstream=json.loads((p/'upstream_manifest.json').read_text())
        comparison.append(dict(model=model,repository=upstream['repository'],revision=upstream['revision'],config_sha256=sha((p/'upstream/config.json').read_bytes()),model_type=c2['model_type'],native_context=c2['max_position_embeddings'],layers=c2['num_hidden_layers'],hidden_size=c2['hidden_size'],weight_manifest=wm,
          tokenizer_sha256=sha((p/'upstream/tokenizer.json').read_bytes()),template_sha256=sha((p/'upstream/chat_template.jinja').read_bytes())))
    dump('factual_comparison.json',comparison)
    print(json.dumps(dict(total_parameters=total,attention_adapter_rank16=attention,expert_adapter_rank16=expert,broader_adapter_rank16=attention+expert,channel_tests=len(rows)),indent=2))
if __name__=='__main__': main()
