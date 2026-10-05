"""Generate static identity/maps/lifecycle/resource artifacts. No model library imports."""
import sys
sys.dont_write_bytecode=True
import ast
import csv
import hashlib
import json
import math
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[2]
REPO='zai-org/GLM-4.7-Flash'
SHA='7dd20894a642a0aa287e9827cb1a1f7f91386b67'
TF='02d8fb9784e8f14a1251e4c992cd82a5762417c6'
PEFT='532a05dd505c28993119b7715ee286f4234bf51b'
VLLM='ced6857afa0ea7b2e3f0846a62e1394e90f15607'
VERDICT='PROCEED TO INFRASTRUCTURE VERIFICATION'
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def dump(name,data):(ROOT/name).write_text(json.dumps(data,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
def digest(data):return hashlib.sha256(data).hexdigest()
def model_url(name):return f'https://huggingface.co/{REPO}/blob/{SHA}/{name}'
def tf_url(name):return f'https://github.com/huggingface/transformers/blob/{TF}/src/transformers/{name}'
def peft_url(name):return f'https://github.com/huggingface/peft/blob/{PEFT}/src/peft/{name}'
def vllm_url(name):return f'https://github.com/vllm-project/vllm/blob/{VLLM}/{name}'

def main():
    config=read('upstream/config.json');meta=read('upstream/hub_metadata.json');index=read('upstream/model.safetensors.index.json')
    assert meta['id']==REPO and meta['sha']==SHA
    with (WORKSPACE/'experiments/model_preflight/landscape_closure/landscape.csv').open(encoding='utf-8',newline='') as f:
        landscape=next(r for r in csv.DictReader(f) if r['repository']==REPO)
    assert landscape['revision']==SHA
    shards=[s for s in meta['siblings'] if re.fullmatch(r'model-\d{5}-of-00048\.safetensors',s['rfilename'])]
    declared_bytes=sum(s['size'] for s in shards)
    assert len(shards)==48 and declared_bytes==62_444_175_504
    assert landscape['selected_weight_files'].split('; ')==[s['rfilename'] for s in shards]
    assert landscape['weight_lfs_hashes_declared'].split('; ')==[s['lfs']['sha256'] for s in shards]
    catalog=[]
    def add(name,shape,group,buffer=False):
        assert name in index['weight_map'],name
        catalog.append({'checkpoint_tensor':name,'shape_inferred':shape,'elements':math.prod(shape),'group':group,
                        'buffer':buffer,'dtype_declared_or_inferred':'F32' if buffer else 'BF16',
                        'shape_evidence':'exact config and pinned constructors, not body/header measurement','shard':index['weight_map'][name]})
    dims={'q_a_proj':[768,2048],'q_b_proj':[5120,768],'kv_a_proj_with_mqa':[576,2048],
          'kv_b_proj':[8960,512],'o_proj':[2048,5120]}
    attention=[];parameters=[];expert_groups=[]
    for layer in range(48):
        mtp=layer==47;prefix=f'model.layers.{layer}.';suffix='mtp' if mtp else 'main'
        for name,shape in dims.items():
            raw=prefix+'self_attn.'+name+'.weight';add(raw,shape,suffix+'_attention')
            if not mtp:attention.append({'module':raw.removesuffix('.weight'),'type':'nn.Linear','weight_shape':shape,
                                         'rank16_A_shape':[16,shape[1]],'rank16_B_shape':[shape[0],16],
                                         'rank16_parameters':16*sum(shape)})
        for norm,shape in [('input_layernorm',[2048]),('post_attention_layernorm',[2048]),('self_attn.q_a_layernorm',[768]),('self_attn.kv_a_layernorm',[512])]:
            add(prefix+norm+'.weight',shape,suffix+'_norm')
        if layer==0:
            for projection in ['gate_proj','up_proj','down_proj']:
                add(prefix+'mlp.'+projection+'.weight',[2048,10240] if projection=='down_proj' else [10240,2048],'main_dense_mlp')
        else:
            add(prefix+'mlp.gate.weight',[64,2048],suffix+'_router')
            add(prefix+'mlp.gate.e_score_correction_bias',[64],suffix+'_router_correction',True)
            for projection in ['gate_proj','up_proj','down_proj']:
                shape=[2048,1536] if projection=='down_proj' else [1536,2048]
                add(prefix+'mlp.shared_experts.'+projection+'.weight',shape,suffix+'_shared_expert')
                for expert in range(64):add(prefix+f'mlp.experts.{expert}.{projection}.weight',shape,suffix+'_routed_expert')
            if not mtp:
                group={'layer':layer,'parent_module':prefix+'mlp.experts','type':'Glm4MoeLiteExperts, 3D nn.Parameters',
                       'gate_up_proj':{'parameter':prefix+'mlp.experts.gate_up_proj','shape':[64,3072,2048],
                                       'source_patterns':[prefix+'mlp.experts.{0..63}.gate_proj.weight',prefix+'mlp.experts.{0..63}.up_proj.weight'],
                                       'conversion':'MergeModulelist(dim=0) for each projection then Concatenate(dim=1), [gate;up] order'},
                       'down_proj':{'parameter':prefix+'mlp.experts.down_proj','shape':[64,2048,1536],
                                    'source_pattern':prefix+'mlp.experts.{0..63}.down_proj.weight','conversion':'MergeModulelist(dim=0)'}}
                expert_groups.append(group)
                for field in ['gate_up_proj','down_proj']:
                    p=group[field];e,out_dim,in_dim=p['shape'];trainables=e*16*(out_dim+in_dim)
                    parameters.append({'parameter':p['parameter'],'type':'nn.Parameter (3D, experts,out,in)','shape':p['shape'],
                                       'rank16_A_shape':[e*16,in_dim],'rank16_B_shape':[out_dim,e*16],
                                       'rank16_parameters':trainables,'expert_count':e})
    add('model.embed_tokens.weight',[154880,2048],'main_embedding')
    add('lm_head.weight',[154880,2048],'main_lm_head');add('model.norm.weight',[2048],'main_norm')
    for name,shape in [('embed_tokens',[154880,2048]),('shared_head.head',[154880,2048]),('eh_proj',[2048,4096]),
                       ('enorm',[2048]),('hnorm',[2048]),('shared_head.norm',[2048])]:
        add('model.layers.47.'+name+'.weight',shape,'mtp_auxiliary')
    assert {r['checkpoint_tensor'] for r in catalog}==set(index['weight_map']) and len(catalog)==9703
    full=sum(r['elements'] for r in catalog);main_rows=[r for r in catalog if r['group'].startswith('main_')]
    mtp_rows=[r for r in catalog if r['group'].startswith('mtp')]
    main=sum(r['elements'] for r in main_rows);buffers=sum(r['elements'] for r in catalog if r['buffer'])
    assert full==meta['safetensors']['total']==31_221_488_576
    assert full-buffers==meta['safetensors']['parameters']['BF16'] and buffers==meta['safetensors']['parameters']['F32']==3008
    payload=2*(full-buffers)+4*buffers
    main_buffers=sum(r['elements'] for r in main_rows if r['buffer'])
    main_bytes=2*(main-main_buffers)+4*main_buffers
    assert main==29_943_393_920 and len(main_rows)==9491 and len(mtp_rows)==212
    dump('weight_layout_catalog.json',{'body_verified':False,'shapes_inferred':True,'rows':catalog,
         'original_total_elements':full,'original_F32_buffer_elements':buffers,'main_model_elements_including_buffers':main,
         'main_model_BF16_elements':main-main_buffers,'main_model_F32_buffer_elements':main_buffers,
         'mtp_elements_including_buffers':full-main,'catalog_matches_every_index_key':True})
    differences=[]
    for field,new in [('repository_created_at_utc',meta['createdAt']),('repository_modified_at_utc',meta['lastModified']),
                      ('model_type',config['model_type']),('architecture',config['architectures'][0]),
                      ('native_config_context',str(config['max_position_embeddings'])),('hidden_size',str(config['hidden_size'])),
                      ('layers',str(config['num_hidden_layers'])),('selected_weight_bytes_declared',str(declared_bytes))]:
        if landscape[field]!=new:differences.append({'field':field,'landscape':landscape[field],'fresh':new})
    assert not differences
    differences.append({'field':'license_evidence','landscape':landscape['license_evidence'],
                        'fresh':'MIT authoritative card/Hub declaration; no standalone LICENSE in exact repository listing, resolve returned404',
                        'effect':'correct unsupported standalone-file wording; declared MIT eligibility remains source-supported'})
    identity={'repository':REPO,'revision':SHA,'created_at_utc':meta['createdAt'],'modified_at_utc':meta['lastModified'],
              'gated':meta['gated'],'private':meta['private'],'license':'MIT','license_source':model_url('README.md'),
              'standalone_license_present':False,'official_deployment_repo_license':'MIT; supplementary evidence, not a substitute model checkpoint',
              'product_use_eligibility':'PASS_STATIC: MIT declaration and software-engineering benchmark/use documentation; no score comparison',
              'model_type':config['model_type'],'architecture':config['architectures'][0],'original_config':config,
              'native_representation':'BF16 weights plus F32 router correction buffers, no native quantization_config',
              'source_declared_tensor_elements':full,'source_declared_BF16_elements':full-buffers,'source_declared_F32_elements':buffers,
              'main_model_elements_including_buffers':main,'main_trainable_base_parameters_if_unfrozen':main-main_buffers,
              'mtp_elements_including_buffers':full-main,'main_layers':47,'additional_original_MTP_layers':1,
              'dense_layers':[0],'moe_layers':list(range(1,47)),'routed_experts_per_layer':64,'selected_experts_per_token':4,'shared_experts_per_moe_layer':1,
              'active_parameter_description':'Card30B-A3B is approximate; main decoder topology activates four routed plus one shared expert per sparse layer. Full residency counts all64 experts and retained original storage, never3B shortcut.',
              'active_decoder_elements_per_token_estimate_excluding_vocab':sum(r['elements'] for r in main_rows if r['group'] not in ('main_embedding','main_lm_head','main_routed_expert'))+sum(r['elements'] for r in main_rows if r['group']=='main_routed_expert')//16,
              'native_context':202752,'tokenizer_max_length_declaration':128000,'deployed_context':32768,'reserve':2048,
              'selected_weight_packaging':'48 model-* safetensors shards','declared_shard_count':48,'declared_weight_bytes':declared_bytes,
              'selected_lfs_identities':shards,'hub_declared_safetensors':meta['safetensors'],
              'index_total_size_declared':index['metadata']['total_size'],'payload_bytes_from_public_dtype_counts':payload,
              'index_size_inconsistency':'Index total_size equals element count31,221,488,576, not mixed BF16/F32 byte count62,442,983,168; selected bodies62,444,175,504 include headers. Treat as source metadata inconsistency, verify bodies later.',
              'body_dtype_shape_hashes_verified':False,'weight_bodies_downloaded':False,'headers_downloaded':False,
              'comparison_discrepancies':differences,'source_urls':[model_url(n) for n in ['README.md','config.json','generation_config.json','model.safetensors.index.json','tokenizer_config.json']]}
    dump('identity.json',identity)
    mla={'repository':REPO,'revision':SHA,'module_prefix':'model.layers.{0..46}.self_attn',
         'projection_modules':attention,'head_count':20,'q_low_rank':768,'kv_low_rank':512,
         'qk_nonpositional_head_dim':192,'qk_rope_head_dim':64,'qk_total_head_dim':256,'v_head_dim':256,
         'normalizations':{'q_a_layernorm':[768],'kv_a_layernorm':[512]},
         'q_proj':'None because q_lora_rank768; do not target an absent full q_proj',
         'rope':'Current pinned config default rope_interleave=True, theta1e6, full64-dimensional positional component; record resolved config and parity later',
         'compressed_cache':'TF source caches512 latent+64 positional values per token per layer, then expands K/V transiently; vLLM native MLA uses custom kernels/weight absorption',
         'ordinary_training_path':'Five nn.Linear modules plus RMSNorm; standard autograd under pinned eager experts/SDPA attention. No inference-only fused MLA kernel used for training.',
         'serving_difference':'q_a and kv_a may be fused_qkv_a_proj; kv_b weights fed to MLA custom/absorption path. Class SupportsLoRA alone does not prove every selected projection adapter is applied.',
         'source_urls':[tf_url('models/glm4_moe_lite/modeling_glm4_moe_lite.py'),vllm_url('vllm/model_executor/models/glm4_moe_lite.py'),vllm_url('vllm/model_executor/models/deepseek_v2.py'),vllm_url('vllm/model_executor/layers/mla.py')]}
    dump('mla_map.json',mla)
    expert={'repository':REPO,'revision':SHA,'main_sparse_layers':list(range(1,47)),'routed_experts':64,'active_routed_experts':4,
            'shared_experts':1,'expert_intermediate_dim':1536,'dense_first_layer_intermediate':10240,
            'router':{'weight_shape':[64,2048],'correction_buffer_shape':[64],'correction_dtype':'FP32','method':'sigmoid scores; noaux_tc, grouped topk1 of1; top4; renormalize and scale1.8'},
            'checkpoint_layout':'Individual gate/up/down .weight tensors for each of64 experts; NOT current training modules',
            'transformers_layout':'Two stacked3D nn.Parameters per sparse layer; no nn.Linear.forward for each routed expert',
            'groups':expert_groups,'target_parameter_map':parameters,
            'shared_expert_modules':'model.layers.{1..46}.mlp.shared_experts.{gate_proj,up_proj,down_proj}, ordinary Linear, frozen in proposed scopes',
            'conversion':'glm4_moe_lite aliases qwen2_moe conversion; natural numeric expert-key ordering, stack dim0, gate/up concatenate dim1; lossless repacking, no dtype conversion/calibration',
            'runtime_layout':'vLLM FusedMoE w13/w2 expert mapping; may fuse shared experts; native packed kernels differ from Transformers parameter wrappers',
            'MTP':'One original layer47 with64+1 experts exists; excluded from loading/adaptation/inference/speculation, exact212 keys accounted separately',
            'source_urls':[tf_url('models/glm4_moe_lite/modeling_glm4_moe_lite.py'),tf_url('conversion_mapping.py'),tf_url('core_model_loading.py'),vllm_url('vllm/model_executor/models/glm4_moe_lite.py')]}
    dump('expert_map.json',expert)
    attention_params=sum(m['rank16_parameters'] for m in attention);expert_params=sum(p['rank16_parameters'] for p in parameters)
    assert len(attention)==235 and attention_params==21_031_936
    assert len(parameters)==92 and expert_params==409_993_216
    pattern=r'^model\.layers\.(?:[0-9]|[1-3][0-9]|4[0-6])\.self_attn\.(?:q_a_proj|q_b_proj|kv_a_proj_with_mqa|kv_b_proj|o_proj)$'
    assert all(re.fullmatch(pattern,m['module']) for m in attention)
    scopes={}
    for name,p,parameter_names in [('MLA_attention_only',attention_params,[]),('MLA_plus_routed_expert_parameters',attention_params+expert_params,[x['parameter'] for x in parameters])]:
        scopes[name]={'status':'SOURCE_SUPPORTED / EMPIRICALLY_UNVERIFIED','rank_for_estimate':16,'target_modules':pattern,
                      'expanded_module_names':[x['module'] for x in attention],'target_parameters':parameter_names,
                      'module_count':235,'stacked_parameter_count':len(parameter_names),'rank16_trainable_parameters':p,
                      'adapter_BF16_payload_bytes':2*p,'adapter_FP32_payload_bytes':4*p,'adapter_A_B_tensor_count':2*(235+len(parameter_names)),
                      'optimizer_working_state_estimate_bytes':16*p,'serving_route':'fresh-original+saved adapter -> BF16 safe merge -> original-layout export -> vLLM raw token generation'}
    adaptation={'repository':REPO,'revision':SHA,'scopes':scopes,'attention_modules':attention,'stacked_parameters':parameters,
                'expert_scope_selection':'Both routed gate_up/down parameter types across all46 main MoE layers. Every targeted stack covers64 experts; no claim of selective expert-index targeting or router/shared-expert adaptation.',
                'expert_scope_requirements':{'PEFT':'target_parameters explicit fully qualified LIST; target_modules same MLA regex','experts_implementation':'eager',
                                            'USE_HUB_KERNELS':'NO','torch_compile':False,'lora_dropout':0,'fan_in_fan_out':False,
                                            'lora_bias':False,'use_dora':False,'adapter_count_per_fresh_cycle':1,
                                            'other_LoRA_variants':'Not admitted for parameter wrappers'},
                'expert_backward_evidence':'ParamWrapper temporarily parametrizes base parent during forward;3D expert axis supported; eager GLM expert indexing/functional linear is inside wrapped forward. Requires gradient and restore tests.',
                'parameter_forward_limit':'Reading a targeted nn.Parameter outside its wrapped parent forward does not activate adapter; do not bypass via custom/fused serving kernels.',
                'excluded':['router/correction buffers','q_a/kv_a norms and all layer norms','dense first-layer MLP','shared experts','embeddings/head','all MTP layer47 tensors'],
                'adapter_dtype':'PEFT default autocast may promote adapters toFP32; both storage estimates conditional, record actual dtype',
                'direct_adapter_serving':'UNRESOLVED for full MLA five-projection scope, and unsupported mapping claim for PEFT stacked-parameter adapters. Merge/export is primary; no direct target_parameters runtime equivalence claimed.',
                'alpha_schedule_training_data':'Not selected; expert zero-dropout is an implementation admissibility constraint, not executed training',
                'source_urls':[peft_url('tuners/lora/config.py'),peft_url('tuners/lora/layer.py'),peft_url('tuners/lora/model.py'),peft_url('peft_model.py')]}
    dump('adaptation_targets.json',adaptation)

    protocol_tree=ast.parse((WORKSPACE/'harness/context_policy/protocol.py').read_text(encoding='utf-8'))
    frozen=ast.literal_eval(next(n.value for n in protocol_tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CONTROL_VALUES' for t in n.targets)))
    mapping={'decoding':('temperature',0.0,'decimal'),'temperature':('temperature',0.0,'decimal'),'top_p':('top_p',1.0,'decimal'),
             'top_k':('top_k',0,'integer'),'repetition_penalty':('repetition_penalty',1.0,'decimal'),'frequency_penalty':('frequency_penalty',0.0,'decimal'),
             'presence_penalty':('presence_penalty',0.0,'decimal'),'seed':('seed',0,'integer'),'text_stops':('stop',[],'array'),
             'max_generation':('max_tokens',2048,'integer'),'completions':('n',1,'integer'),'retries':('orchestrator retry count',0,'integer'),
             'context_shifting':('one fixed prompt sequence; no shifting',False,'boolean'),'clipping':('lossless output; no clipping',False,'boolean'),
             'truncation':('truncate_prompt_tokens=None; reject overflow',False,'boolean')}
    assert set(mapping)==set(frozen)
    runtime={'status':'STATIC PROPOSAL, NOT AUTHENTICATED RUN PROFILE','selected_profile':'NATIVE_DEFAULT_THINKING_FULL_SUFFIX_RAW_TOKEN_IDS',
             'stack':{'vllm':{'version':'0.30.0','commit':VLLM},'python':'3.11.9','torch':'2.13.0',
                      'transformers':{'version':'5.19.0.dev0','commit':TF},'peft':{'version':'0.21.3.dev0','commit':PEFT},
                      'tokenizers':'0.23.2','jinja2':'3.1.6','markupsafe':'3.0.4','packaging':'26.3',
                      'CUDA':'13.0.3 pinned Dockerfile assumption; actual driver/wheels/container/kernel lock unverified','OS_architecture':'Linux x86_64 CUDA; local tokenizer checks Windows CPython3.12.14'},
             'installation_success':False,'complete_transitive_lock':'NOT_ESTABLISHED; freeze exact package/container/driver/kernel hashes before later execution',
             'engine_args':{'max_model_len':32768,'dtype':'bfloat16','quantization':None,'tensor_parallel_size':1,'max_num_seqs':1,
                            'seed':0,'enforce_eager':True,'enable_prefix_caching':False,'generation_config':'vllm','skip_tokenizer_init':True,
                            'trust_remote_code':False,'speculative_config':None},
             'sampling_params':{'temperature':0.0,'top_p':1.0,'top_k':0,'min_p':0.0,'repetition_penalty':1.0,'frequency_penalty':0.0,
                                'presence_penalty':0.0,'seed':0,'n':1,'max_tokens':2048,'min_tokens':0,'stop':[],
                                'stop_token_ids':[154820,154827,154829],'ignore_eos':False,'detokenize':False,'skip_special_tokens':False,
                                'truncate_prompt_tokens':None,'logit_bias':None,'allowed_token_ids':None,'bad_words':None,'structured_outputs':None,'repetition_detection':None},
             'frozen_control_map':{key:{'requested':value,'runtime_parameter':mapping[key][0],'runtime_value':mapping[key][1],
                                       'runtime_argument_type':mapping[key][2],'source_status':'SOURCE-SUPPORTED' if key not in ['retries','context_shifting','clipping','truncation'] else 'STATIC TRANSPORT DESIGN',
                                       'infrastructure_status':'INFRASTRUCTURE-UNVERIFIED'} for key,value in frozen.items()},
             'input':'Pre-render exact native default two-message template; backend encode(add_special_tokens=False); pass prompt_token_ids; no automatic BOS, chat API/history/tool/reasoning parser',
             'BOS_note':'Root/tokenizer metadata provides no bos token. Current Glm4MoeLiteConfig has library bos_token_id default0; do not inject it into nonempty precomputed native input.',
             'thinking_kwargs':'Absent/native default (equivalent measured rendering enable_thinking=True); never setFalse, /nothink, effort setting or no-thought constraint to fit reserve',
             'output':'All raw IDs and byte-preserving ByteLevel inverse, no parsed content-only/reasoning split; preserve unknown IDs in receipts and fail closed if text mapping undefined',
             'terminal_allowance':1,'native_terminal_ids':[154820,154827,154829],
             'cap_accounting':'All emitted reasoning/content/control/terminal IDs count toward2048. Verified length-capped event -> output_capacity_failure. EOS-at-cap requires observed finish/count/event evidence, not guessed from count alone; stop source checks native EOS before length.',
             'tool_handoff':'Stop on configured observation boundary and retain emitted tool-call body; never call a tool, append observation, resume or retry',
             'LoRA_support':'GLM class explicitly SupportsLoRA and fusion mappings; full projection and ParamWrapper direct serving parity unresolved. Primary route is independently reloaded adapter plus safe merge/export.',
             'source_urls':[vllm_url(n) for n in ['vllm/sampling_params.py','vllm/engine/arg_utils.py','vllm/entrypoints/llm.py','vllm/v1/core/sched/utils.py','vllm/model_executor/models/glm4_moe_lite.py','requirements/common.txt','requirements/cuda.txt','docker/Dockerfile']]}
    dump('runtime_profile.json',runtime)
    lifecycle={'repository':REPO,'revision':SHA,'status':'STATIC DESIGN; all model lifecycle execution NOT_RUN','credible_fresh_original_attention_path':True,
               'credible_expert_path':'Conditional source-supported eager ParamWrapper plus merge/export; not a demonstrated lifecycle',
               'original_representation':'BF16 weights, FP32 correction buffers; no dequantization or quantization needed',
               'lossless_load_conversion':'Individual routed experts -> numeric-order stack -> concatenate gate/up; preserve BF16 values and FP32 buffers',
               'MTP_policy':{'original_entries':212,'exact_excluded_keys':[r['checkpoint_tensor'] for r in mtp_rows],
                             'source':'TF explicitly ignores layer47; vLLM skips speculative layers; speculative_config=None',
                             'rule':'Allow only exact212 declared MTP entries as unused; zero missing or unexpected main weights. Retain all original bodies; MTP never adapted or used for speculation.'},
               'cycle':['authenticate original48 shards/config/tokenizer/index','fresh main-model load from exact original and lossless expert repacking',
                        'verify canonical pristine751-entry tensor/buffer manifest','fresh adapter initialization, optimizer/scheduler and RNG',
                        'authorized future adaptation','save adapter/config/provenance','destroy training process/model/optimizer/adapter state',
                        'fresh load SAME original again and verify pristine manifest','reload saved adapter into fresh base',
                        'safe BF16 merge to evaluation-only derivative','inverse original expert-layout export','raw-token vLLM evaluation','destroy evaluation state','next cycle begins original again'],
               'proof_records':{'original':['repo/SHA','48 sizes/body hashes','config/index/tokenizer/template hashes','metadata discrepancies'],
                                'pristine':['source/software/hardware/container identity','resolved config, eager expert dispatch and kernel flags','lossless converter recipe hash','sorted tensor/buffer name shape dtype nbytes SHA256','exact MTP exclusion receipt'],
                                'fresh_state':['unique cycle ID','adapter config and expanded targets','initial A/B tensor hashes','fresh optimizer/scheduler stepzero','Python/NumPy/Torch CPU/CUDA RNG states','no previous-state handles'],
                                'saved':['adapter_model.safetensors/config hashes','original and pristine roots','scope/rank/alpha/dropout/dtype','cycle/data/optimization provenance'],
                                'reset':['training process exit and GPU allocator inventory','fresh evaluation process','original-root verified BEFORE adapter applied','empty KV/prefix/history state'],
                                'evaluation':['reloaded adapter root','merge/export recipe and derivative body root','raw token/byte/terminal/finish/cap receipts']},
               'save_reload':{'format':'adapter_model.safetensors + adapter_config.json + external provenance','safe_serialization':True,'save_embedding_layers':False,
                              'reload':'PeftModel.from_pretrained(fresh authenticated original-main base, adapter, is_trainable=False); exact coverage of ordinary-module and parameter-wrapper saved keys'},
               'merge_export':{'primary':True,'merge':'merge_and_unload(safe_merge=True) on independently reloaded pristine BF16+adapter',
                               'precision':'BF16 base plus actual adapter dtype (oftenFP32); rounding documented; compare logits/decisions/outputs empirically',
                               'save_original_format':True,'safe_serialization':True,
                               'reason':'Inverse Concatenate/SplitModulelist recreates original individual expert gate/up/down names expected by pinned vLLM loader; no FP8 reverse operation in this unquantized model',
                               'stacked_export_direct_load':'UNRESOLVED; do not assume vLLM accepts current TF3D gate_up/down export',
                               'MTP_output':'Main47-layer export is evaluation derivative with MTP excluded; it never replaces the original48-shard store',
                               'identity_rule':'Only exact ORIGINAL48-shard manifest can parent fresh adaptation. PRISTINE_MAIN_LOAD is authenticated derived execution state; ADAPTER/MERGED_EVALUATION_DERIVATIVE cannot parent another cycle.'},
               'isolation':{'status':'DESIGN, NOT_CERTIFIED','network':'air-gapped namespace; deny sockets/egress; offline flags; USE_HUB_KERNELS=NO',
                            'mounts':'read-only authenticated model/runtime plus one immutable synthetic token request; scoped output and fresh tmpfs only; no project/candidate/benchmark/home/history/credential mounts',
                            'runtime':'non-root read-only OS/runtime image; allowlisted OS/driver reads; no external tools/retrieval/parser callbacks; no host path escape',
                            'request':'single fresh sequence, no history/tools/retries; prefix cache disabled and independent process/base/adapter state',
                            'verification':'later negative read/socket/tool/history/cache/reset probes and independent traces required'},
               'fallback_triggered':False,'protocol_modified':False,'inference_occurred':False,'model_instantiated':False,'adapter_instantiated':False}
    dump('original_base_lifecycle.json',lifecycle)
    gi=lambda n:round(n/2**30,6)
    compressed=47*32768*(512+64)*2;expanded=47*32768*20*(256+256)*2
    resources={'status':'TRANSPARENT SOURCE/ARITHMETIC ESTIMATES, NOT MEASURED','original_disk_bytes':declared_bytes,'original_disk_GiB':gi(declared_bytes),
               'full_original_payload_from_dtype_metadata_bytes':payload,'main_resident_payload_bytes':main_bytes,'main_resident_payload_GiB':gi(main_bytes),
               'unused_MTP_payload_bytes':payload-main_bytes,'residency_rule':'All64 routed experts and shared/dense/MLA/vocab main weights count; original storage includes unused MTP. No3B active-param shortcut.',
               'compressed_KV_32768_one_sequence':{'formula':'47*32768*(512+64)*2','bytes':compressed,'GiB':gi(compressed)},
               'expanded_KV_equivalent':{'formula':'47*32768*20*(K256+V256)*2','bytes':expanded,'GiB':gi(expanded),'note':'potential transient/alternative attention cost, NOT added automatically to compressed persistent cache'},
               'serving_main_BF16_subtotal_GiB':[gi(main_bytes+compressed)+3,gi(main_bytes+compressed)+10],
               'serving_subtotal_caution':'3–10GiB workspace planning allowance is not measured upper bound; absorb weights, prefill/expanded tensors, expert kernel buffers and allocator reserve may add more',
               'scopes':{},'expert_parametrization':{'one_layer_effective_BF16_gateup_down_bytes':64*(3072*2048+2048*1536)*2,
                                                    'all46_layers_effective_BF16_stack_bytes':46*64*(3072*2048+2048*1536)*2,
                                                    'note':'ParamWrapper baddbmm avoids a separate full delta but materializes effective expert weights; autograd may retain stacks. Whole-layer checkpointing/sharding and actual peak tests essential.'},
               'host_RAM_starting_GiB':[128,192],'host_RAM_basis':'full original62.443GB payload + main59.887GB state + packing/serializer/merge temporaries; streaming mmap may reduce, full copies may increase',
               'lossless_packing_one_layer_temporary_bytes':64*(3072*2048+2048*1536)*2,
               'merge_storage':{'original_plus_one_main_export_bytes':declared_bytes+main_bytes,
                                'original_plus_main_export_plus_atomic_second_main_bytes':declared_bytes+2*main_bytes,
                                'planning_free_disk_GB_decimal':[200,260]},
               'reset_burden':'Authenticate/read all48 original bodies each fresh cycle, fresh751-entry main manifest and reset state; packing time/hash/load/merge measured later, no reuse of prior adapted/merged base',
               'later_starting_points':'Serving: investigate one80GiB class device or two80GiB TP if required by measured workspace. Attention-only training:80GiB with separately authorized checkpointed microbatch starting point. Combined expert training: investigate multi-GPU/sharded checkpointing; uncheckpointed effective stacks alone can add51.75GiB. No GPU configuration verified or authorized.'}
    for name,scope in scopes.items():
        p=scope['rank16_trainable_parameters'];resources['scopes'][name]={'rank16_parameters':p,'BF16_adapter_bytes':2*p,'FP32_adapter_bytes':4*p,
                                                                     'optimizer_and_gradient_bytes':16*p,'formula':'BF16 weight2+grad2+FP32 master4+Adam8, or FP32 weight4+grad4+Adam8 without duplicated master',
                                                                     'base_plus_working_adapter_GiB':gi(main_bytes+16*p),'activation_workspace':'Additional; sequence length/training recipe not selected'}
    dump('resource_estimates.json',resources)
    tests=[
      ('A','Original body identity','Acquire48 authorized shards; verify exactLFS hashes/sizes and real dtype/shape/buffers; resolve incorrect index total_size','Authenticated original manifest'),
      ('B','Fresh original load/repack','Load exact original, numeric expert stack/concat; verify main751 tensors/buffers and only212 known MTP exclusions; no fresh missing weights','Pristine tensor root and complete load receipt'),
      ('C','32768 capacity load','Load pinned BF16 main with32768 and2048 reserve, MTP/speculation disabled','Effective config and measured load/prefill receipt'),
      ('D','Prompt/token parity','All51 exact default-thinking synthetic inputs vs runtime prompt IDs; no BOS0/history/tools/default injection','Matching byte/token hashes'),
      ('E','Entire suffix retention','Preserve every generated reasoning/content/role/tool marker in order; parser disabled; no content-only extraction','Full raw suffix receipt'),
      ('F','Thinking boundary','Input <think> counts as input; every emitted </think>/<think>/reasoning token counts as generated; no disabled-thinking accommodation','Boundary and total-count receipt'),
      ('G','Native EOS/tool stop','Test154820/154827/154829; distinguish turn EOS and observation handoff; remove only one verified final terminal, no tool execution','Native event/terminal and retained tool-body audit'),
      ('H','Natural termination','Observe authorized synthetic natural terminal before limit without retry','Actual finish/count/stop-event receipt'),
      ('I','Frozen controls','All15 unchanged controls/types, explicitneutral penalties/no stops/no processors, seed0','Independent effective controls certificate'),
      ('J','Forced2048 cap','Later synthetic request reaches verified LENGTH2048; retain stream; EOS-at-cap separately adjudicated with native event, no count-only inference','Capacity failure for actual length event; no clipping/retry'),
      ('K','Raw IDs/bytes','ByteLevel inverse and literal specials; strict UTF-8 with invalid-byte retention; unmapped154856..154879 IDs fail closed rather than vanish','Raw/normalized bytes and removal receipts'),
      ('L','Same-process greedy repeat','Repeat fixed authorized synthetic input/base/hardware/controls; compare IDs/bytes','Determinism or explicit failure record'),
      ('M','Fresh-process repeat','Cold process repeat with same original and immutable environment','Repeatability boundary certificate'),
      ('N','Isolation/no-read/no-tools','Negative sockets/files/tool/history/retrieval/cache probes; no candidate/product mounts','Independent isolation traces'),
      ('O','Resources/timing','Measure original-load/pack/prefill/decode/train/save/reload/merge/reset peaks and timings','RAM/VRAM/disk/timing table'),
      ('P','MLA forward/backward','Exact235 Linear targets/21,031,936 rank16 trainables; gradients finite/nonzero, base frozen, no MTP/router targets','Gradient/name/base-hash audit'),
      ('Q','Expert forward/backward','Eager92 3D ParamWrapper targets plusMLA; zero-dropout and no kernel/compile; exact431,025,152 trainables; routed gradient/restore checks','ParamWrapper gradient/state and peak audit'),
      ('R','Adapter save/destroy/reload','Save scope/config/dtype/hash; destroy; load SAME original again; reload exact adapter inclparameter wrappers','Adapter coverage and logit/parity receipt'),
      ('S','Direct serving or merge/export','FullMLA direct route optional test; primary safe BF16 merge and inverse individual expert export; compare loader coverage/logits/outputs','Authenticated evaluation derivative, no adapter bypass'),
      ('T','Second fresh original cycle','Fresh original load/repack again; canonical pristine hashes before fresh adapter/optimizer/RNG initialization','Same-original pristine root; stepzero receipt'),
      ('U','Contamination/reset','Prior adapter/optimizer/merged path/cache/history unavailable; derivative rejected as next-cycleparent','Destruction and fail-closed provenance audit'),
      ('V','MLA numerical/kernel parity','Compare TF/vLLM rope interleave/scaling, compressedKV and weight absorption; ensure merged q/kv changes applied','Logit/cache/key-layout parity'),
      ('W','Dependency/parser environment','Resolve immutable Linux package/kernel/container/driver lock; CPython3.11.9/Unicode14 parser; disabled parsers verified','Complete runnable lock and official completion certificate'),
      ('X','Inverse export/MTP exclusion','Verify stack gate/up split/order and expert indices0..63; exported main content inverse parity; no unused MTP execution','751-main/9491-raw coverage and212 exclusion receipt')]
    with (ROOT/'infrastructure_test_matrix.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['id','test','procedure','acceptance','status']);writer.writeheader()
        writer.writerows({'id':i,'test':t,'procedure':p,'acceptance':a,'status':'NOT_RUN'} for i,t,p,a in tests)
    source=read('source_manifest.json')
    project=[WORKSPACE/'experiments/model_preflight/landscape_closure'/n for n in ['REPORT.md','landscape.csv','source_manifest.json']]
    project += [WORKSPACE/'experiments/model_preflight/cross_model_audit'/n for n in ['REPORT.md','sources/draft2.txt','sources/draft3.txt']]
    project += [WORKSPACE/'benchmark_design/context_policy/current-repo-v1-draft3.json',WORKSPACE/'harness/context_policy/protocol.py',WORKSPACE/'harness/context_policy/core.py',WORKSPACE/'harness/context_policy/evidence.py',
                WORKSPACE/'experiments/model_preflight/devstral_small2_2512/check_tokenizer.py',WORKSPACE/'experiments/model_preflight/devstral_small2_2512/artifact_manifest.json']
    source['local_project_inputs']=[{'path':p.relative_to(WORKSPACE).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())} for p in project]
    d1=WORKSPACE/'experiments/model_preflight/devstral_small2_2512'
    previous=json.loads((d1/'artifact_manifest.json').read_text(encoding='utf-8'))
    source['reused_dependency_artifacts']=[{'path':(d1/r['path']).relative_to(WORKSPACE).as_posix(),'bytes':r['bytes'],'sha256':r['sha256']} for r in previous['files'] if r['path'].startswith(('dependencies_wheels/','tokenizer_dependencies/'))]
    source['reuse_scope']='Only tokenizer fixture construction methodology, authenticated dependency software and workflow/provenance conventions reused; GLM conclusions independently based on its exact artifacts and pinned model-specific implementations.'
    source['execution_scope']='Tokenizers/Jinja compiler and canonical synthetic framing/packing only; no Torch/Transformers/PEFT/vLLM model/source module imported or recipes executed'
    dump('source_manifest.json',source)
    print(json.dumps({'verdict':VERDICT,'original_elements':full,'main_elements':main,'mtp_elements':full-main,'payload_bytes':payload,'main_bytes':main_bytes,
                      'attention_trainables':attention_params,'expert_trainables':expert_params,'combined_trainables':attention_params+expert_params,'infrastructure_checks':len(tests)},indent=2))

if __name__=='__main__':main()
