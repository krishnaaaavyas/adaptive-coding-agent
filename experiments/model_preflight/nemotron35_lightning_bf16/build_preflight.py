"""Source-derived Nemotron static catalog/maps. Standard library only; no model imports."""
import sys
sys.dont_write_bytecode = True
import csv
import hashlib
import json
import math
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[2]
REPO='nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16'
SHA='a9904d24bcc1d289a1950fa9d2b978c47cf903b9'
TF='02d8fb9784e8f14a1251e4c992cd82a5762417c6'
PEFT='532a05dd505c28993119b7715ee286f4234bf51b'
VLLM='ced6857afa0ea7b2e3f0846a62e1394e90f15607'

def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def dump(name,value):(ROOT/name).write_text(json.dumps(value,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
def digest(data):return hashlib.sha256(data).hexdigest()
def model_url(name):return f'https://huggingface.co/{REPO}/blob/{SHA}/{name}'
def tf_url(name):return f'https://github.com/huggingface/transformers/blob/{TF}/src/transformers/{name}'
def peft_url(name):return f'https://github.com/huggingface/peft/blob/{PEFT}/src/peft/{name}'
def runtime_url(name):return f'https://github.com/vllm-project/vllm/blob/{VLLM}/{name}'
def gib(value):return round(value/2**30,6)

def main():
    config=read('upstream/config.json');meta=read('upstream/hub_metadata.json');index=read('upstream/model.safetensors.index.json')
    assert meta['id']==REPO and meta['sha']==SHA
    with (WORKSPACE/'experiments/model_preflight/landscape_closure/landscape.csv').open(encoding='utf-8',newline='') as f:
        historical=next(r for r in csv.DictReader(f) if r['repository']==REPO)
    assert historical['revision']==SHA
    shards=[s for s in meta['siblings'] if re.fullmatch(r'model-\d{5}-of-00014\.safetensors',s['rfilename'])]
    assert len(shards)==14 and sum(s['size'] for s in shards)==int(historical['selected_weight_bytes_declared'])==65_827_374_264
    assert historical['selected_weight_files'].split('; ')==[s['rfilename'] for s in shards]
    assert historical['weight_lfs_hashes_declared'].split('; ')==[s['lfs']['sha256'] for s in shards]
    kinds=config['layers_block_type'];layer_ids={k:[i for i,v in enumerate(kinds) if v==k] for k in ['mamba','attention','moe']}
    assert {k:len(v) for k,v in layer_ids.items()}=={'mamba':23,'attention':6,'moe':23}
    catalog=[];layers=[];attention=[];recurrent=[];experts=[]
    def add(name,shape,category,group,buffer=False,training_name=None):
        assert name in index['weight_map'],name
        row={'checkpoint_tensor':name,'training_tensor':training_name or name.replace('backbone.','model.'),
             'shape_inferred':shape,'elements':math.prod(shape),'classification':category,'group':group,'buffer':buffer,
             'dtype_declared_or_inferred':'F32' if buffer else 'BF16','shard':index['weight_map'][name],
             'evidence':'Exact config + pinned constructor; not a body/header/value measurement'}
        if match:=re.fullmatch(r'(.*\.experts)\.(\d+)\.(up_proj|down_proj)\.weight',name):
            row['training_tensor']=match[1].replace('backbone.','model.')+'.'+match[3]
            row['training_expert_axis0_index']=int(match[2])
            row['training_classification']='ORDINARY PARAMETER (stacked3D), not Linear'
        catalog.append(row);return row
    def linear(name,shape,group,targets=None):
        add(name+'.weight',shape,'ORDINARY LINEAR MODULE',group)
        if targets is not None:
            targets.append({'module':name.replace('backbone.','model.'),'weight_shape':shape,'target_type':'module',
                            'A_shape_rank16':[16,shape[1]],'B_shape_rank16':[shape[0],16],'rank16_parameters':16*sum(shape)})
    def block(prefix,kind,group,main=False):
        add(prefix+'norm.weight',[2688],'ORDINARY PARAMETER',group+'_norm')
        mixer=prefix+'mixer.'
        if kind=='attention':
            for name,shape in [('q_proj',[4096,2688]),('k_proj',[256,2688]),('v_proj',[256,2688]),('o_proj',[2688,4096])]:
                linear(mixer+name,shape,group+'_attention',attention if main else None)
        elif kind=='mamba':
            linear(mixer+'in_proj',[10304,2688],group+'_mamba',recurrent if main else None)
            linear(mixer+'out_proj',[2688,4096],group+'_mamba')
            for name,shape in [('conv1d.weight',[6144,1,4]),('conv1d.bias',[6144]),('norm.weight',[4096]),
                               ('A_log',[64]),('D',[64]),('dt_bias',[64])]:
                add(mixer+name,shape,'CUSTOM PARAMETER' if name in ['A_log','D','dt_bias'] else 'ORDINARY PARAMETER',group+'_mamba')
        elif kind=='moe':
            add(mixer+'gate.weight',[128,2688],'ORDINARY PARAMETER',group+'_router')
            add(mixer+'gate.e_score_correction_bias',[128],'NON-TRAINABLE BUFFER',group+'_router',True)
            linear(mixer+'shared_experts.up_proj',[3712,2688],group+'_shared')
            linear(mixer+'shared_experts.down_proj',[2688,3712],group+'_shared')
            for projection,shape in [('up_proj',[1856,2688]),('down_proj',[2688,1856])]:
                for expert in range(128):linear(mixer+f'experts.{expert}.'+projection,shape,group+'_routed')
                if main:
                    experts.append({'parameter':mixer.replace('backbone.','model.')+'experts.'+projection,
                                    'target_type':'parameter','training_shape':[128,*shape],
                                    'A_shape_rank16':[2048,shape[1]],'B_shape_rank16':[shape[0],2048],
                                    'rank16_parameters':128*16*sum(shape),'expert_count':128,
                                    'original_pattern':mixer+'experts.{0..127}.'+projection+'.weight',
                                    'conversion':'Natural numeric expert order, MergeModulelist(dim=0); no gate/up concatenation'})
        else:raise AssertionError(kind)
    for i,kind in enumerate(kinds):
        before=len(catalog);block(f'backbone.layers.{i}.',kind,'main',True)
        layers.append({'index':i,'config_type':kind,'current_transformers_type':{'mamba':'linear_attention','attention':'full_attention','moe':'moe'}[kind],
                       'training_block':'NemotronHBlock','training_mixer':{'mamba':'NemotronHMamba2Mixer','attention':'NemotronHAttention','moe':'NemotronHMoE'}[kind],
                       'training_prefix':f'model.layers.{i}.','original_prefix':f'backbone.layers.{i}.',
                       'tensors':catalog[before:]})
    add('backbone.embeddings.weight',[131072,2688],'ORDINARY PARAMETER','main_vocab')
    add('backbone.norm_f.weight',[2688],'ORDINARY PARAMETER','main_norm')
    add('lm_head.weight',[131072,2688],'ORDINARY LINEAR MODULE','main_vocab')
    for i,kind in enumerate(config['mtp_layers_block_type']):block(f'mtp.layers.{i}.',kind,'mtp')
    for name,shape in [('mtp.layers.0.eh_proj.weight',[2688,5376]),('mtp.layers.0.enorm.weight',[2688]),
                       ('mtp.layers.0.hnorm.weight',[2688]),('mtp.layers.1.final_layernorm.weight',[2688])]:
        add(name,shape,'ORDINARY LINEAR MODULE' if 'eh_proj' in name else 'ORDINARY PARAMETER','mtp_aux')
    assert len(catalog)==len(index['weight_map'])==6513
    assert {r['checkpoint_tensor'] for r in catalog}==set(index['weight_map'])
    total=sum(r['elements'] for r in catalog);buffers=sum(r['elements'] for r in catalog if r['buffer'])
    main_rows=[r for r in catalog if r['group'].startswith('main')];mtp_rows=[r for r in catalog if r['group'].startswith('mtp')]
    main_count=sum(r['elements'] for r in main_rows);main_buffers=sum(r['elements'] for r in main_rows if r['buffer'])
    assert total-buffers==meta['safetensors']['parameters']['BF16']==32_913_263_168
    assert buffers==meta['safetensors']['parameters']['F32']==3072
    assert main_count-main_buffers==index['metadata']['total_parameters']==meta['safetensors']['total']==31_577_937_344
    payload=2*(total-buffers)+4*buffers;main_bytes=2*(main_count-main_buffers)+4*main_buffers
    tensor_count=len(main_rows)-23*(256-2)
    assert len(mtp_rows)==270 and tensor_count==401
    dump('weight_layout_catalog.json',{'body_verified':False,'shapes_inferred':True,'rows':catalog,
         'original_total_elements_including_buffers':total,'original_F32_buffers':buffers,
         'main_elements_including_buffers':main_count,'main_F32_buffers':main_buffers,'main_raw_entries':len(main_rows),
         'main_stacked_tensor_buffer_entries':tensor_count,'mtp_elements_including_buffers':total-main_count,'mtp_raw_entries':len(mtp_rows),
         'all_index_keys_covered':True})
    discrepancies=[
      {'field':'EOS/PAD metadata','historical':'root EOS2/BOS1','fresh':'generation EOS[2,11], PAD0; tokenizer EOS/PAD11; no automatic BOS; no padding','effect':'Explicit mapping refinement, no source hidden/default inheritance'},
      {'field':'Hub total versus per-dtype totals','historical':'not reconciled','fresh':f'Hub total{main_count-main_buffers} matches main parameters excluding buffers; per-dtype sum{total} includes all buffers and MTP','effect':'Do not treat Hub total as complete original body count'},
      {'field':'index total_size','historical':'not reconciled','fresh':f'index declares{index["metadata"]["total_size"]} bytes; mixed-dtype source arithmetic{payload}; shards{sum(s["size"] for s in shards)}','effect':'Preserve conflict and verify later, use declared shard sizes for disk'},
      {'field':'MTP branch','historical':'main52 blocks; MTP not separately counted','fresh':'270 unused original mtp.* entries; native main loaders ignore/drop prefix','effect':'Keep all original bodies, exclude exact unused keys and disable speculation'},
      {'field':'Mamba out_proj LoRA','historical':'official station path excludes out_proj because raw-weight kernels bypass wrapping',
       'fresh':'Pinned training fused path confirms bypass; reference torch path reaches out_proj.forward, but it is not in admitted hybrid scope','effect':'Hybrid scope targets in_proj only; fused out_proj adaptation unresolved'}]
    identity={'repository':REPO,'revision':SHA,'created_at_utc':meta['createdAt'],'modified_at_utc':meta['lastModified'],
              'private':meta['private'],'gated':meta['gated'],'license':'OpenMDW-1.1','license_source':model_url('LICENSE'),
              'product_use_eligibility':'PASS_STATIC: exact license permits use/modification/distribution subject to notices/terms; card documents coding-agent evaluation existence, no score magnitude',
              'model_type':config['model_type'],'architecture':config['architectures'][0],'original_config':config,
              'native_representation':'BF16 tensors plus F32 router correction buffers; no quantization_config',
              'checkpoint_pretraining_precision_note':'Card describes NVFP4 pretraining ancestry; selected released original is explicitly BF16, not a substituted NVFP4 export',
              'main_layers':52,'layer_ids':layer_ids,'mtp_blocks':config['mtp_layers_block_type'],'MTP_unused_original_entries':270,
              'routed_experts':128,'active_routed_experts':6,'shared_experts':1,'latent_moe':False,
              'original_total_elements_including_buffers':total,'main_elements_including_buffers':main_count,
              'original_nonbuffer_parameters':total-buffers,'main_nonbuffer_parameters':main_count-main_buffers,
              'active_topology':'Main sparse blocks activate6 of128 ReLU2 two-matrix experts plus one3712 shared expert; Mamba and attention always active; full resident base counts all experts',
              'active_decoder_elements_estimate_excluding_vocab':sum(r['elements']*(6/128 if r['group']=='main_routed' else 1) for r in main_rows if r['group']!='main_vocab'),
              'native_config_context':config['max_position_embeddings'],'tokenizer_model_max_length':read('upstream/tokenizer_config.json')['model_max_length'],
              'card_extended_context_declaration':1_048_576,'deployed_target':32768,'reserve':2048,
              'weight_packaging':'14 model-* safetensors shards','declared_weight_bytes':sum(s['size'] for s in shards),'selected_lfs_identities':shards,
              'hub_tensor_metadata':meta['safetensors'],'index_metadata':index['metadata'],'payload_bytes_from_public_dtype_counts':payload,
              'declared_shard_overhead_over_inferred_payload':sum(s['size'] for s in shards)-payload,
              'index_declared_bytes_minus_inferred_payload':index['metadata']['total_size']-payload,
              'body_dtype_shape_value_hashes_verified':False,'weight_bodies_downloaded':False,'headers_downloaded':False,
              'comparison_discrepancies':discrepancies,'source_urls':[model_url(n) for n in ['README.md','LICENSE','config.json','generation_config.json','model.safetensors.index.json']]}
    dump('identity.json',identity)
    architecture={'repository':REPO,'revision':SHA,'layer_order':kinds,'layer_ids':layer_ids,'layers':layers,
      'attention':{'ordinary_modules':attention,'query_heads':32,'KV_heads':2,'head_dim':128,'KV_groups':16,
                   'positional_path':'No rotary/position operation in pinned TF or vLLM NemotronHAttention.forward; rope_theta/partial_rotary_factor in original config do not by themselves enable RoPE'},
      'mamba':{'ordinary_in_projection_modules':recurrent,'intermediate':4096,'conv_channels':6144,'in_projection_out':10304,
               'projection_split':'z4096 | x4096 | B1024 | C1024 | dt64','heads':64,'head_dim':64,'SSM_state_size':128,'BC_groups':8,
               'depthwise_conv_weight':[6144,1,4],'depthwise_conv_bias':[6144],'gated_norm_weight':[4096],'gated_norm_group_size':512,
               'custom_vectors':{'A_log':[64],'D':[64],'dt_bias':[64]},
               'A':'-exp(A_log.float()); continuous state transition rates; not a Linear',
               'dt':'softplus(input_dt + dt_bias), clamp floor0.001, no upper bound in resolved mixer source',
               'out_projection_weight':[2688,4096],
               'out_projection_admissibility':'UNRESOLVED for fused training adapter path: nn.Linear exists but its raw .weight is passed to combined kernel. Reference torch path calls forward; not selected as adaptation target.',
               'training_cache':'use_cache=False, past_key_values=None; reference scan creates zero initial state, no detached decode state',
               'transformers_cache':'DynamicCache hybrid layers, conv [batch,6144,4], recurrent [batch,64,64,128], FP32 SSM declaration',
               'vllm_cache':'TP1 per state slot: conv [3,6144] in SD orientation; temporal [64,64,128]; runtime cache page padding/slot count additional',
               'fused_runtime_representation':'Merged/TP-sharded in_proj segments, conv kernel reshaping, A_log->A=-exp(A_log), custom Triton Mamba2 prefill/decode; buffers are derived execution state, not a new original'},
      'moe':{'routed':128,'active':6,'shared':1,'intermediate':1856,'shared_intermediate':3712,'activation':'ReLU squared; two projections, no gate_proj',
             'router_weight':[128,2688],'router_buffer':[128],'routing':'FP32 sigmoid + correction-bias selection, group1/top-group1, top6 normalized and scaled2.5',
             'training_parameter_targets':experts,'original_expert_layout':'Individual up_proj/down_proj.weight tensors per expert',
             'training_expert_layout':'Two3D nn.Parameters per main MoE layer, first axis128 experts; eager functional.linear inside expert parent forward',
             'shared_experts':'Ordinary two-module MLP, frozen in all proposed scopes','latent_projections':'nn.Identity because moe_latent_size=None',
             'serving_layout':'FusedMoE/non-gated w3/w2 mapping, TP/EP-dependent packing, optional shared expert overlap; not PEFT ParamWrapper forward'},
      'classification_policy':'CUSTOM PARAMETER means architecture-specific A_log/D/dt_bias nn.Parameter vectors, not a new torch class. Ordinary3D expert parameters are not Linear modules. Recurrent/KV/cache arrays are non-trainable derived state, absent from original index.',
      'source_urls':[tf_url('models/nemotron_h/modeling_nemotron_h.py'),tf_url('models/nemotron_h/configuration_nemotron_h.py'),runtime_url('vllm/model_executor/models/nemotron_h.py'),runtime_url('vllm/model_executor/layers/mamba/mamba_mixer2.py')]}
    dump('architecture_map.json',architecture)
    attention_regex=r'^model\.layers\.(?:5|12|19|26|33|42)\.mixer\.(?:q_proj|k_proj|v_proj|o_proj)$'
    recurrent_pattern='(?:'+'|'.join(str(i) for i in layer_ids['mamba'])+')'
    hybrid_regex=r'^model\.layers\.(?:(?:5|12|19|26|33|42)\.mixer\.(?:q_proj|k_proj|v_proj|o_proj)|'+recurrent_pattern+r'\.mixer\.in_proj)$'
    scopes={}
    for name,modules,parameters in [('conservative_attention',attention,[]),('hybrid_attention_mamba_in',attention+recurrent,[]),
                                    ('expert_hybrid_plus_routed',attention+recurrent,experts)]:
        count=sum(m['rank16_parameters'] for m in modules)+sum(p['rank16_parameters'] for p in parameters)
        scopes[name]={'status':'SOURCE_SUPPORTED / EMPIRICALLY_UNVERIFIED' if not parameters else 'CONDITIONALLY_SOURCE_SUPPORTED / EMPIRICALLY_UNVERIFIED',
                      'rank_for_estimate':16,'target_modules':attention_regex if name=='conservative_attention' else hybrid_regex,
                      'expanded_module_names':[m['module'] for m in modules],'target_parameters':[p['parameter'] for p in parameters],
                      'module_count':len(modules),'stacked_parameter_count':len(parameters),'rank16_trainable_parameters':count,
                      'A_B_tensor_count':2*(len(modules)+len(parameters)),'BF16_adapter_payload_bytes':2*count,'FP32_adapter_payload_bytes':4*count,
                      'working_adapter_state_bytes_estimate':16*count,'primary_serving_route':'Independently reload same original+saved adapter, safe BF16 merge, original-layout export, raw-token vLLM'}
    assert scopes['conservative_attention']['rank16_trainable_parameters']==1_867_776
    assert scopes['hybrid_attention_mamba_in']['rank16_trainable_parameters']==6_648_832
    assert scopes['expert_hybrid_plus_routed']['rank16_trainable_parameters']==434_729_984
    dump('adaptation_targets.json',{'repository':REPO,'revision':SHA,'scopes':scopes,'attention_modules':attention,'mamba_in_modules':recurrent,'expert_parameters':experts,
      'PEFT_mechanism':'Ordinary module LoRA for24 attention modules /23 Mamba in_proj; explicit LIST target_parameters for46 routed3D tensors, nested ParamWrapper',
      'training_restrictions':{'use_cache':False,'past_key_values':None,'use_kernels':False,'USE_HUB_KERNELS':'NO','experts_implementation':'eager',
                              'torch_compile':False,'adapter_count':1,'reference_training_profile':'Do not install mamba_ssm/causal_conv1d; exact decorator then selects bundled differentiable torch functions. Native fused-kernel backward support not asserted.'},
      'parameter_wrapper_restrictions':{'lora_dropout':0,'fan_in_fan_out':False,'lora_bias':False,'use_dora':False,'other_variants':'Not admitted'},
      'expert_coverage':'Both up/down tensor types across23 main MoE layers, all128 experts per targeted stack. No parameter slicing or individual-expert subset claim.',
      'excluded':['Mamba out_proj under fused wrapper-bypass path','A_log/D/dt_bias, conv parameters, norms','routers/correction buffers/shared expert MLP',
                  'embeddings/lm_head/norm_f','all270 MTP original keys, speculative/draft models','latent expert projection modules absent in exact checkpoint'],
      'gradient_limitations':'Base remains frozen; some expert branches may get no tokens. Standard zero B initialization can yield zero A gradients on first step; check meaningful gradient flow, not all-target nonzero immediately.',
      'adapter_dtype':'Actual PEFT adapter autocast may yield FP32; both payload estimates conditional',
      'direct_serving':'Declared SupportsLoRA + QKV packing is source support, not measured full target coverage. Mamba in_proj custom TP slicing and routed ParamWrapper direct-serving mappings require separate verification. Merge/export primary.',
      'source_urls':[peft_url('tuners/lora/config.py'),peft_url('tuners/lora/layer.py'),tf_url('models/nemotron_h/modeling_nemotron_h.py'),tf_url('integrations/hub_kernels.py')]})
    dump('training_serving_map.json',{'repository':REPO,'revision':SHA,
      'training':{'stack':{'transformers':TF,'PEFT':PEFT},'original_prefix':'backbone.','model_prefix':'model.',
                  'load_conversion':'backbone.->model.; numeric individual expert stacking into up_proj/down_proj3D parameters; no dtype conversion/dequantization',
                  'backward':'Source-visible differentiable reference torch Mamba chunk scan and eager experts; standard LoRA module forward. Kernel package absence + Hub kernels disabled selects reference path.',
                  'out_proj_limit':'Combined training kernel reads raw out_proj.weight, bypasses module adapter; excluded. use_mamba_kernels=False is deprecated/no-op, not a reliable bypass switch.',
                  'training_cache':'use_cache=False, fresh None states every sample/step; no reused inference state',
                  'weight_manifest_entries':tensor_count},
      'serving':{'runtime':'vLLM0.30.0','commit':VLLM,'original_mapper':'backbone.->model.; embeddings->embed_tokens; A_log->A; mtp->None; q/k/v->qkv_proj',
                 'config_resolution':'Current vLLM config registry does not override nemotron_h; pinned native Transformers config remaps legacy block names and provides hybrid_override_pattern property, consumed by runtime. No hand-authored model patch.',
                 'known_time_step_difference':'Pinned Transformers reference mixer dt_limit=(0.001,inf), vLLM Mamba kernel calls dt_limit=(0.0,inf). Native implementation difference must be tested, not silently declared cross-runtime logit parity.',
                 'Mamba':'Fused/custom Triton conv/SSM scan/selective-state kernels; Mamba in/out modules are sharded; recurrent cache external per slot',
                 'MoE':'Non-gated FusedMoE w3/w2 individual-expert mapping; shared expert overlap may use separate/fused paths',
                 'direct_LoRA':'SupportsLoRA, packed qkv declarations and MTP skip; actual full scope and parameter-adapter coverage unresolved',
                 'primary':'Safe merged original-layout BF16 main export; no direct ParamWrapper kernel bypass claim'},
      'export':{'save_original_format':True,'safe_serialization':True,'inverse':'Split expert dimension0 into indexed up/down.weight tensors; reverse model.->backbone. rename; verify numeric ordering/config aliases',
                'precision':'BF16 merge rounding with actual adapter dtype; source deterministic arithmetic route, numerical/decision parity NOT_RUN',
                'not_new_original':True,'MTP':'Evaluation main export excludes unused270 MTP keys; authenticated original store retains all14 bodies'},
      'source_urls':[tf_url('conversion_mapping.py'),tf_url('core_model_loading.py'),tf_url('modeling_utils.py'),runtime_url('vllm/model_executor/models/nemotron_h.py'),runtime_url('vllm/transformers_utils/config.py'),tf_url('models/nemotron_h/configuration_nemotron_h.py')]})
    lifecycle={'repository':REPO,'revision':SHA,'status':'STATIC DESIGN; all model lifecycle execution NOT_RUN','credible_fresh_original_path':True,
      'original_representation':'BF16 tensors plus FP32 router correction buffers; selected release unquantized',
      'original_conversion':'Lossless prefix rename and expert stack layout, no calibration or new base identity; serving also derives A=-exp(A_log) as native representation',
      'cycle':['Authenticate14 original bodies/config/index/tokenizer/template','Fresh pristine main load and lossless expert stacking',
               'Verify401-entry main tensor/buffer root and exact270 MTP exclusions before adapters','Fresh named adapter/optimizer/scheduler/RNG state',
               'Separately authorized future adaptation','Safe adapter/config/provenance save','Destroy adapter/base/optimizer/caches/process',
               'Reload SAME ORIGINAL14-body manifest','Verify pristine main root before adapter application','Reload exact saved adapter and verify key coverage',
               'Safe merge + original-format export for evaluation or separately verified direct serving','Fresh empty recurrent/convolution/KV state; full raw suffix capture',
               'Destroy all evaluation state','Next cycle authenticates ORIGINAL again; never use adapter or merged derivative as parent'],
      'MTP_policy':{'count':270,'exact_excluded_keys':sorted(r['checkpoint_tensor'] for r in mtp_rows),'rule':'Only exact declared MTP keys unused; no missing/unexpected main weights; retain original bodies; speculation disabled'},
      'proof_records':{'ORIGINAL':['repository+SHA','all14 SHA256/size receipts','small source/config/tokenizer/template hashes'],
                       'PRISTINE':['all401 tensors/buffers: sorted name, shape, dtype, actual byte hash','load key coverage','expert conversion order and content parity'],
                       'ADAPTER':['scope and expanded target manifest','config/adapter file hashes, actual dtype/rank','fresh-original parent root, optimizer/RNG step-zero receipt'],
                       'EVALUATION_DERIVATIVE':['same-original load receipt','adapter reload and merge/inverse-loader key coverage','output/control/reset receipts; never adaptation parent']},
      'adapter_format':{'files':['adapter_model.safetensors','adapter_config.json','external cycle/base hashes'], 'safe_serialization':True,'save_embedding_layers':False,
                        'reload':'PeftModel.from_pretrained(fresh exact original-main, saved adapter, is_trainable=False); verify module+ParamWrapper keys'},
      'merge_export':{'primary':True,'safe_merge':True,'save_original_format':True,'safe_serialization':True,'native_precision':'BF16 + retained F32 correction buffers',
                      'route':'Fresh original + independently reloaded adapter -> merge_and_unload(safe_merge=True) -> inverse original expert/prefix export -> vLLM',
                      'body_parity_NOT_RUN':True,'merged_derivative_cannot_parent_next_cycle':True},
      'state_reset':{'training':'No persistent recurrent/KV state, cacheFalse/None; fresh zero-initial reference scan; fresh optimizer/scheduler/RNG',
                     'serving':'Fresh request at token0, no past initial states; prefix/Mamba caching/replay/speculation disabled; destruction and zero/fresh slot receipts for SSM, conv, KV, counters, warmed kernels/RNG',
                     'same_process_test':'Exercise slot reuse with divergent preceding synthetic request; require equal raw outputs and initial-state receipts',
                     'fresh_process_boundary':'Destroy process and state allocations between independent cycles; same original identity alone is insufficient',
                     'certified':False},
      'isolation':{'status':'DESIGN, NOT_CERTIFIED','network':'deny sockets/egress; offline flags; Hub kernels disabled',
                   'mounts':'read-only authenticated model/runtime, one immutable token input, scoped output, fresh tmpfs; no candidate/product/benchmark/home/history/credentials',
                   'tools':'No tool callbacks/retrieval/chat/reasoning parser; one request, zero retries',
                   'verification':'Independent negative probes/traces required; runtime OS/driver/kernel reads explicitly allowlisted'},
      'protocol_modified':False,'inference_occurred':False,'model_instantiated':False,'adapter_instantiated':False}
    dump('original_base_lifecycle.json',lifecycle)
    # All controls are copied from the policy data, not inherited runtime defaults.
    policy=json.loads((WORKSPACE/'benchmark_design/context_policy/current-repo-v1-draft3.json').read_text(encoding='utf-8'))
    controls=policy['profile_schema']['controls']
    mapping={'decoding':('temperature',0.0,'decimal'),'temperature':('temperature',0.0,'decimal'),'top_p':('top_p',1.0,'decimal'),
      'top_k':('top_k',0,'integer'),'repetition_penalty':('repetition_penalty',1.0,'decimal'),'frequency_penalty':('frequency_penalty',0.0,'decimal'),
      'presence_penalty':('presence_penalty',0.0,'decimal'),'seed':('seed',0,'integer'),'text_stops':('stop',[],'array'),
      'max_generation':('max_tokens',2048,'integer'),'completions':('n',1,'integer'),'retries':('orchestrator retry count',0,'integer'),
      'clipping':('lossless raw capture; no clipping',False,'boolean'),'context_shifting':('one fixed sequence; no shift',False,'boolean'),
      'truncation':('truncate_prompt_tokens=None; overflow rejection',False,'boolean')}
    assert set(mapping)==set(controls) and len(mapping)==15
    runtime={'status':'STATIC PROPOSAL, NOT AUTHENTICATED RUN PROFILE','selected_profile':'NATIVE_DEFAULT_THINKING_FULL_SUFFIX_RAW_TOKEN_IDS',
      'stack':{'vllm':{'version':'0.30.0','commit':VLLM},'python':'3.11.9','torch':'2.13.0',
               'transformers':{'version':'5.19.0.dev0','commit':TF},'peft':{'version':'0.21.3.dev0','commit':PEFT},
               'tokenizers':'0.23.2','jinja2':'3.1.6','markupsafe':'3.0.4','packaging':'26.3',
               'CUDA':'13.0.3 pinned Dockerfile assumption, Linuxx86_64; compatible driver/container/wheels not locked',
               'Python_Docker_note':'Dockerfile default Python3.12 is not the proposed CPython3.11.9 parser/runtime lock. Custom build override or separate parser process requires later verification; no Docker image execution.',
               'serving_kernel_dependencies':{'Triton':'Bundled vLLM Mamba conv/chunk-scan/selective-state kernels; exact Triton distribution/driver hashes NOT_ESTABLISHED',
                                             'flashinfer_python':'0.6.18.post1 requirement','flashinfer_cubin':'0.6.18.post1 requirement; main selected SSU backendTriton',
                                             'apache_tvm_ffi':'0.1.11 requirement'},
               'training_kernel_profile':'Separate environment: no mamba_ssm/causal_conv1d package, no Hub kernel replacement; bundled source torch Mamba fallback and eager MoE. No speculative patch.'},
      'installation_success':False,'complete_transitive_lock':'NOT_ESTABLISHED; source pin is not runnable dependency/container certificate',
      'engine_args':{'max_model_len':32768,'dtype':'bfloat16','quantization':None,'tensor_parallel_size':1,'max_num_seqs':1,'seed':0,
                     'enforce_eager':True,'enable_prefix_caching':False,'generation_config':'vllm','skip_tokenizer_init':True,'trust_remote_code':False,
                     'speculative_config':None,'enable_chunked_prefill':False,'max_num_batched_tokens':32768,
                     'mamba_backend':'triton','mamba_cache_dtype':'bfloat16','mamba_ssm_cache_dtype':'float32','mamba_cache_mode':'none',
                     'enable_mamba_cache_stochastic_rounding':False,'mamba_cache_philox_rounds':0,
                     'use_replayssm':False,'enable_mamba_fine_grained_prefix_cache':False,'enable_flashinfer_autotune':False},
      'sampling_params':{'temperature':0.0,'top_p':1.0,'top_k':0,'min_p':0.0,'repetition_penalty':1.0,'frequency_penalty':0.0,'presence_penalty':0.0,
                         'seed':0,'n':1,'max_tokens':2048,'min_tokens':0,'stop':[],'stop_token_ids':[2,11],'ignore_eos':False,
                         'detokenize':False,'skip_special_tokens':False,'truncate_prompt_tokens':None,'logit_bias':None,
                         'allowed_token_ids':None,'bad_words':None,'structured_outputs':None,'repetition_detection':None},
      'frozen_control_map':{k:{'requested':controls[k],'runtime_parameter':v[0],'runtime_value':v[1],'runtime_argument_type':v[2],
                               'source_status':'SOURCE-SUPPORTED' if k not in ['retries','clipping','context_shifting'] else 'STATIC TRANSPORT DESIGN',
                               'infrastructure_status':'INFRASTRUCTURE-UNVERIFIED'} for k,v in mapping.items()},
      'input':'Exact default thinking two-message template + backend encode(add_special_tokens=False); raw prompt_token_ids, no BOS/history/tools/parsers',
      'output':'Every raw generated ID and lossless ByteLevel/literal-special bytes; no reasoning split/content projection',
      'native_terminal_ids':[2,11],'terminal_allowance':1,
      'cap_accounting':'All emitted IDs inclthinking/roles/tools/terminal count toward2048; verified LENGTH -> capacity failure. EOS at count2048 requires actual native event.',
      'state_policy':'No prefix cache/replay/speculation; fresh token0 state, explicit BF16 conv/FP32 temporal cache; reset exact arrays and slot/counters, verify same-process and fresh-process; no reset certification',
      'stochastic_rounding_note':'Card throughput profile enablesFP16 SSM cache stochastic rounding. Not adopted: source supportsFP32 temporal cache with explicitFalse; greedy still does not prove deterministic kernels/reductions.',
      'kernel_warmup_note':'MambaMixer2 source warmup allocates random diagnostic tensors/autotunes kernels. Later separatewarmup then reset/reseed/runtime receipts required; no model warmup executed here.',
      'LoRA':'Class SupportsLoRA/QKV mapping/MTP skip declared. Direct full scope and ParamWrapper coverage unresolved; safe merge/export primary.',
      'source_urls':[runtime_url(n) for n in ['vllm/model_executor/models/nemotron_h.py','vllm/model_executor/layers/mamba/mamba_mixer2.py','vllm/config/mamba.py',
                      'vllm/config/cache.py','vllm/engine/arg_utils.py','vllm/sampling_params.py','requirements/cuda.txt','docker/Dockerfile']]}
    dump('runtime_profile.json',runtime)
    kv=6*32768*2*128*2*2;ssm=23*64*64*128*4;conv=23*6144*3*2;tf_conv=23*6144*4*2
    one_expert=128*(1856*2688+2688*1856)*2
    resources={'status':'SOURCE/ARITHMETIC ESTIMATES; NO MEASURED RESOURCES','original_disk_bytes':sum(s['size'] for s in shards),
      'original_disk_GiB':gib(sum(s['size'] for s in shards)),'full_original_payload_inferred_bytes':payload,
      'main_resident_payload_bytes':main_bytes,'main_resident_payload_GiB':gib(main_bytes),'unused_MTP_payload_bytes':payload-main_bytes,
      'residency_rule':'All128 routed experts per23 MoE blocks plus shared/attention/Mamba/vocab/norms count; neverA3B shortcut',
      'attention_KV_one_sequence_32768':{'formula':'6*32768*2KVheads*128dim*2(K,V)*2BF16bytes','bytes':kv,'GiB':gib(kv)},
      'Mamba_temporal_one_state_slot':{'formula':'23*64heads*64dim*128state*4FP32bytes','bytes':ssm,'GiB':gib(ssm)},
      'Mamba_conv_one_state_slot':{'formula':'23*6144channels*3history*2BF16bytes','bytes':conv,'GiB':gib(conv)},
      'TF_conv_one_sequence':{'formula':'23*6144channels*4kernel*2BF16bytes','bytes':tf_conv,'note':'TF convolution cache uses4 versus native serving minimal history3; runtime pages/slots/padding add cost'},
      'state_caveat':'SSM/conv fixed-size per slot, not multiplied by32768 unless checkpoint/cache strategy requests more slots. Hybrid cache manager padding/group balancing/allocator can exceed minimum arithmetic.',
      'serving_main_state_plus_workspace_GiB':[gib(main_bytes+kv+ssm+conv)+3,gib(main_bytes+kv+ssm+conv)+10],
      'workspace_caveat':'3–10GiB planning allowance is not upperbound; prefill activations, fused/packed weights, cache pages/autotune/allocator add unmeasured peaks',
      'adapters_by_scope':{name:{'rank16_parameters':s['rank16_trainable_parameters'],'BF16_bytes':s['BF16_adapter_payload_bytes'],
                                'FP32_bytes':s['FP32_adapter_payload_bytes'],'working_state_16bytes_each':s['working_adapter_state_bytes_estimate'],
                                'base_plus_adapter_working_GiB':gib(main_bytes+s['working_adapter_state_bytes_estimate'])} for name,s in scopes.items()},
      'working_state_formula':'BF16 adapter2+gradient2+master4+Adam8 or FP32 adapter4+gradient4+Adam8; actualoptimizer/dtype may differ',
      'expert_effective_weights':{'one_layer_BF16_bytes':one_expert,'all23_BF16_bytes':23*one_expert,'all23_GiB':gib(23*one_expert),
                                'note':'ParamWrapper baddbmm can materialize full effective3D expert weights; autograd retention additional to rank-only optimizer state'},
      'training_activation_note':'Reference Mamba scan casts toFP32, expands B/C groups and creates intra-/interchunk matrices/states; cacheFalse does not eliminate autograd intermediates. No sequence/microbatch/recipe selected; checkpointing/sharding/peak measurements required.',
      'host_RAM_starting_GiB':[128,192],'host_RAM_basis':'~65.827GB original + ~63.156GB pristine main plus layout/serializer/merge temporaries; streaming lower/full duplicates higher',
      'merge_storage':{'original_plus_one_main_export_bytes':sum(s['size'] for s in shards)+main_bytes,
                       'original_plus_main_plus_atomic_second_main_bytes':sum(s['size'] for s in shards)+2*main_bytes,'planning_free_GB_decimal':[210,280]},
      'reset_burden':'Authenticate14 bodies and pristine401-tensor root, fresh optimizer/RNG and zero/new recurrent+KV state each independent cycle; no reuse of derivatives',
      'later_starting_points':'Investigate80GiB-class serving/conservative/hybrid training with separately authorized checkpointing; measured resources can require multi-GPU. Expert scope full materialized stacks warrants sharding/checkpointing investigation. No arbitrary ceiling/device admission or spending.'}
    dump('resource_estimates.json',resources)
    tests=[
      ('A','Exact bodies/hash/layout','Later authorized14-body hashes/sizes/dtypes/shapes; reconcile Hub/index totals','Authenticated ORIGINAL and discrepancy resolution'),
      ('B','Exact original load','Fresh BF16 load/rename/stack;401 main tensors,270 exact unused MTP keys; zero missing main','Pristine tensor root and load-key receipt'),
      ('C','32768 deployed context','Main52 layers,32768 target plus full2048 reserve; no context extension/speculation','Effective capacity/load/prefill receipt'),
      ('D','Prompt/token parity','All51 native-default synthetic inputs, exact tokenizer/template, no automatic BOS','Matching input/token hashes'),
      ('E','Entire emitted suffix','Raw reasoning/content/markers all retained; no reasoning/chat/tool output parser','Raw full-suffix receipt'),
      ('F','Terminal/stop behavior','Observe EOS2 and11; distinguish im_end from internal roles/tools/think; one verified final removal','Native event and removal audit'),
      ('G','Natural termination','Single synthetic request natural terminal before cap; zero retry','Finish/count/stop evidence'),
      ('H','Forced2048 cap','Verified LENGTH2048 failure; separately test EOS-at-cap event; no clipping/retry','Capacity failure with full raw retention'),
      ('I','Raw tokens/bytes','ByteLevel inverse + literal special bytes; strict UTF8 with raw invalid bytes retained','Raw/normalized/removal receipts'),
      ('J','Frozen controls','All15 controls/types + explicit neutral processors; no inherited sampled card defaults','Independent effective control certificate'),
      ('K','Same-process greedy repeat','Fixed original/input/settings/hardware; slot reuse reset then compare raw outputs','Determinism or explicit failure boundary'),
      ('L','Fresh-process greedy repeat','Cold process same authenticated original+runtime; compare raw tokens/bytes','Repeatability certificate'),
      ('M','Recurrent/cache reset','Divergent prior synthetic request then fresh token0; verifySSM/conv/KV/slot/counters zero/new, no prefix/replay','State reset traces and sequence independence'),
      ('N','Isolation/no-read/no-tools','Negative network/files/tool/history/candidate/product mount/cache probes','Independent isolation traces'),
      ('O','Measured resources','Load/prefill/decode/train/save/reload/export state/activations/pages/allocator peaks','VRAM/RAM/disk table'),
      ('P','Throughput/timing/reset','Measure cold load/hash/stack/prefill/decode/adapter/save/reload/merge/destroy/reset','Timings, no quality ranking'),
      ('Q','Conservative backward','Exact24 attention targets and1,867,776 rank16 trainables; frozen base, finite meaningful gradients','Scope/name/gradient/base-hash audit'),
      ('R','Hybrid backward','Add23 Mamba in_proj,6,648,832 total; reference dispatch verified; no out_proj raw-weight bypass; cacheFalse','Gradient and dispatch/activation audit'),
      ('S','Expert backward','46 explicit3D parameters across23 blocks;128 experts each;434,729,984 combined; eager ParamWrapper restrictions','Selected branch gradient/restore/memory audit; zero-init A not all nonzero'),
      ('T','Adapter save/reload','Save exact scope/config/dtype/hash; destroy; SAME original pristine root before adapter; reload module+parameter keys','Adapter coverage and numerical parity'),
      ('U','Direct serve or merge/export','Optional direct scope coverage; primary safe BF16 merge/inverse expert+backbone export; config aliases and TFdt-floor0.001 versus vLLM0.0 parity check','Evaluation derivative/provenance/output parity or explicit implementation difference'),
      ('V','Second fresh ORIGINAL cycle','Repeat original acquisition authentication/pristine load before fresh adapter/optimizer/RNG','Same pristine root/step-zero receipts'),
      ('W','Contamination/state audit','Prior adapter/optimizer/derivative/history/recurrent/KV unavailable; reject nonoriginal parents','Destruction/reset and fail-closed provenance'),
      ('X','Immutable runtime lock','Linux packages/kernel/container/driver hashes, reference train dispatch, serving Triton/FP32/no-rounding; parserCPython3.11.9','Complete runnable lock + official output/control certificate')]
    with (ROOT/'infrastructure_test_matrix.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['id','test','procedure','acceptance','status']);writer.writeheader()
        writer.writerows({'id':i,'test':t,'procedure':p,'acceptance':a,'status':'NOT_RUN'} for i,t,p,a in tests)
    source=read('source_manifest.json')
    project=[WORKSPACE/'experiments/model_preflight/landscape_closure'/n for n in ['REPORT.md','landscape.csv','source_manifest.json']]
    project += [WORKSPACE/'experiments/model_preflight/cross_model_audit'/n for n in ['REPORT.md','sources/draft2.txt','sources/draft3.txt']]
    project += [WORKSPACE/n for n in ['benchmark_design/context_policy/current-repo-v1-draft3.json','harness/context_policy/core.py','harness/context_policy/protocol.py','harness/context_policy/evidence.py']]
    project += [WORKSPACE/'experiments/model_preflight'/n for n in ['qwen3_coder_30b_a3b/REPORT.md','qwen3_coder_next/REPORT.md','devstral_small2_2512/REPORT.md','glm47_flash/REPORT.md','glm47_flash/check_tokenizer.py','devstral_small2_2512/artifact_manifest.json']]
    source['local_project_inputs']=[{'path':p.relative_to(WORKSPACE).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())} for p in project]
    d1=WORKSPACE/'experiments/model_preflight/devstral_small2_2512';prior=json.loads((d1/'artifact_manifest.json').read_text(encoding='utf-8'))
    source['reused_dependency_artifacts']=[{'path':(d1/r['path']).relative_to(WORKSPACE).as_posix(),'bytes':r['bytes'],'sha256':r['sha256']} for r in prior['files'] if r['path'].startswith(('dependencies_wheels/','tokenizer_dependencies/'))]
    source['execution_scope']='Tokenizer/Jinja compiler and canonical synthetic framing/packing + standard-library maps/arithmetic only. No model library imports, recipes, generation, GPU or protected access.'
    source['reuse_scope']='Workflow/provenance, canonical fixture boilerplate and authenticated dependency software only; exact Nemotron conclusions independently derived.'
    dump('source_manifest.json',source)
    print(json.dumps({'original_elements':total,'main_elements':main_count,'mtp_elements':total-main_count,'payload_bytes':payload,'main_bytes':main_bytes,
                      'main_tensors':tensor_count,'rank16_scopes':{n:s['rank16_trainable_parameters'] for n,s in scopes.items()},'infrastructure_NOT_RUN':len(tests)},indent=2))

if __name__=='__main__':main()
