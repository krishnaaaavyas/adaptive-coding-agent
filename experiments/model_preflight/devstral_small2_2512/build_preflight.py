"""Build static evidence artifacts only; never imports a model/adapter library."""
import sys
sys.dont_write_bytecode = True
import csv
import hashlib
import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[2]
REPO = 'mistralai/Devstral-Small-2-24B-Instruct-2512'
SHA = '55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128'
TF = '02d8fb9784e8f14a1251e4c992cd82a5762417c6'
PEFT = '532a05dd505c28993119b7715ee286f4234bf51b'
VLLM = 'ced6857afa0ea7b2e3f0846a62e1394e90f15607'
VERDICT = 'PROCEED TO INFRASTRUCTURE VERIFICATION'

def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))

def dump(path, data):
    (ROOT/path).write_text(json.dumps(data, ensure_ascii=True, indent=2)+'\n', encoding='utf-8')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def model_url(name):
    return f'https://huggingface.co/{REPO}/blob/{SHA}/{name}'

def tf_url(name):
    return f'https://github.com/huggingface/transformers/blob/{TF}/src/transformers/{name}'

def peft_url(name):
    return f'https://github.com/huggingface/peft/blob/{PEFT}/src/peft/{name}'

def vllm_url(name):
    return f'https://github.com/vllm-project/vllm/blob/{VLLM}/{name}'

def main():
    config=read('upstream/config.json');meta=read('upstream/hub_metadata.json')
    index=read('upstream/model.safetensors.index.json');params=read('upstream/params.json')
    generation=read('upstream/generation_config.json');capacity=read('capacity_checks.json')
    assert meta['sha']==SHA and meta['id']==REPO
    with (WORKSPACE/'experiments/model_preflight/landscape_closure/landscape.csv').open(encoding='utf-8',newline='') as stream:
        landscape=next(r for r in csv.DictReader(stream) if r['repository']==REPO)
    assert landscape['revision']==SHA
    shards=[s for s in meta['siblings'] if re.fullmatch(r'model-\d{5}-of-00006\.safetensors',s['rfilename'])]
    alternate=[s for s in meta['siblings'] if re.fullmatch(r'consolidated.*\.safetensors',s['rfilename'])]
    selected_bytes=sum(s['size'] for s in shards)
    assert selected_bytes==25_793_059_408 and len(shards)==6
    assert landscape['selected_weight_files'].split('; ')==[s['rfilename'] for s in shards]
    assert landscape['weight_lfs_hashes_declared'].split('; ')==[s['lfs']['sha256'] for s in shards]
    assert json.loads(landscape['quantization_config'])==config['quantization_config']

    key_mapping={r'^language_model\.model\.':'model.language_model.',r'^language_model\.lm_head\.':'lm_head.',
                 r'^vision_tower\.':'model.vision_tower.',r'^multi_modal_projector\.':'model.multi_modal_projector.'}
    def mapped(name):
        for pattern,target in key_mapping.items():
            if re.search(pattern,name):return re.sub(pattern,target,name)
        raise AssertionError('Unmapped checkpoint key: '+name)

    catalog=[]
    def add(raw,shape,group,quantized=False):
        assert raw in index['weight_map'],raw
        catalog.append({'checkpoint_tensor':raw,'transformers_tensor':mapped(raw),'shape_inferred':shape,
                        'parameters':math.prod(shape),'group':group,'shape_evidence':'config and pinned constructors; NOT weight-body measurement',
                        'original_dtype_declared_or_inferred':'FP8 E4M3' if quantized else 'BF16 (payload arithmetic inference)',
                        'reconstructed_dtype_proposed':'BF16','quantized':quantized,
                        'source_shard':index['weight_map'][raw]})
    dims={'q_proj':[4096,5120],'k_proj':[1024,5120],'v_proj':[1024,5120],'o_proj':[5120,4096],
          'gate_proj':[32768,5120],'up_proj':[32768,5120],'down_proj':[5120,32768]}
    modules=[]
    for layer in range(40):
        for name,shape in dims.items():
            group='attention' if name in ('q_proj','k_proj','v_proj','o_proj') else 'mlp'
            middle='self_attn' if group=='attention' else 'mlp'
            raw=f'language_model.model.layers.{layer}.{middle}.{name}.weight'
            add(raw,shape,group,True)
            module=mapped(raw).removesuffix('.weight')
            scale=raw.removesuffix('.weight')+'.weight_scale_inv'
            activation=raw.removesuffix('.weight')+'.activation_scale'
            assert scale in index['weight_map'] and activation in index['weight_map']
            modules.append({'module':module,'checkpoint_weight':raw,'weight_shape':shape,
                            'scope':group,'weight_scale_inv':scale,'activation_scale':activation,
                            'lora_A_shape':[16,shape[1]],'lora_B_shape':[shape[0],16],
                            'rank16_parameters':16*sum(shape)})
        for norm in ('input_layernorm','post_attention_layernorm'):
            add(f'language_model.model.layers.{layer}.{norm}.weight',[5120],'text_norm')
    add('language_model.model.embed_tokens.weight',[131072,5120],'embedding')
    add('language_model.lm_head.weight',[131072,5120],'lm_head')
    add('language_model.model.norm.weight',[5120],'text_norm')
    for layer in range(24):
        prefix=f'vision_tower.transformer.layers.{layer}.'
        for name in ('q_proj','k_proj','v_proj','o_proj'):
            add(prefix+'attention.'+name+'.weight',[1024,1024],'vision')
        for name in ('gate_proj','up_proj','down_proj'):
            add(prefix+'feed_forward.'+name+'.weight',[1024,4096] if name=='down_proj' else [4096,1024],'vision')
        for norm in ('attention_norm','ffn_norm'):
            add(prefix+norm+'.weight',[1024],'vision')
    add('vision_tower.patch_conv.weight',[1024,3,14,14],'vision')
    add('vision_tower.ln_pre.weight',[1024],'vision')
    for name,shape in [('linear_1',[5120,1024]),('linear_2',[5120,5120]),('norm',[1024]),('patch_merger.merging_layer',[1024,4096])]:
        add('multi_modal_projector.'+name+'.weight',shape,'projector')
    weight_names={r['checkpoint_tensor'] for r in catalog}
    assert weight_names=={k for k in index['weight_map'] if k.endswith('.weight')}
    scales={k for k in index['weight_map'] if not k.endswith('.weight')}
    assert len(catalog)==585 and len(scales)==560 and len({mapped(k) for k in index['weight_map']})==1145
    assert scales=={m[k] for m in modules for k in ('weight_scale_inv','activation_scale')}
    count=sum(r['parameters'] for r in catalog);quantized=sum(r['parameters'] for r in catalog if r['quantized'])
    assert count==24_011_361_280 and quantized==22_229_811_200
    assert count+560==index['metadata']['total_parameters']
    expected_payload=quantized+2*(count-quantized)+2*560
    assert expected_payload==index['metadata']['total_size']
    dense_bytes=2*count
    discrepancies=[]
    checks={'repository_created_at_utc':meta['createdAt'],'repository_modified_at_utc':meta['lastModified'],
            'model_type':config['model_type'],'architecture':config['architectures'][0],
            'native_config_context':str(config['text_config']['max_position_embeddings']),
            'hidden_size':str(config['text_config']['hidden_size']),'layers':'40',
            'selected_weight_bytes_declared':str(selected_bytes)}
    for key,value in checks.items():
        if landscape[key]!=value:discrepancies.append({'field':key,'landscape':landscape[key],'independent':value})
    assert not discrepancies
    identity={'repository':REPO,'revision':SHA,'independently_verified':True,'created_at_utc':meta['createdAt'],
              'last_modified_at_utc':meta['lastModified'],'gated':meta['gated'],'private':meta['private'],
              'license':'apache-2.0','license_evidence':model_url('README.md'),
              'standalone_license_present':any(x['rfilename']=='LICENSE' for x in meta['siblings']),
              'product_eligibility':'PASS_STATIC: software-engineering use and Apache-2.0 declaration; retain license/NOTICE obligations',
              'model_type':config['model_type'],'architecture':config['architectures'][0],
              'text_config':config['text_config'],'vision_config':config['vision_config'],
              'spatial_merge_size':2,'modality_components_retained_but_excluded':['model.vision_tower','model.multi_modal_projector'],
              'parameter_count_non_scale_inferred':count,'index_total_parameters_including_560_scales':index['metadata']['total_parameters'],
              'group_parameters':{g:sum(r['parameters'] for r in catalog if r['group']==g) for g in sorted({r['group'] for r in catalog})},
              'dense_ordinary_text':True,'attention':'40 layers; GQA 32 Q / 8 KV heads; head_dim 128; full attention',
              'mlp':'SiLU gated dense MLP, 5120 -> 32768 -> 5120; separate bias-free gate/up/down',
              'native_context_config':393216,'card_advertised_context':'256k','generation_config_max_length':262144,
              'deployed_context':32768,'tokenizer_class':read('upstream/tokenizer_config.json')['tokenizer_class'],
              'tokenizer_normalizer':None,'quantization_config':config['quantization_config'],
              'original_quantization_declared':params['quantization'],'config_dtype_is_not_storage_dtype':'bfloat16 compute declaration with native mixed FP8/BF16 weight packaging',
              'selected_packaging':'six model-* HF safetensors shards','selected_shard_count':6,
              'selected_declared_bytes':selected_bytes,'index_payload_declared_bytes':expected_payload,
              'selected_lfs_identities':shards,'alternate_packaging':alternate,'alternate_bytes_not_added_to_selected':sum(s['size'] for s in alternate),
              'weight_bodies_downloaded':False,'tensor_headers_downloaded':False,'body_dtype_shape_scale_values_verified':False,
              'landscape_discrepancies':discrepancies,
              'landscape_refinements':['landscape terminal_config null/null is absence in root config, not missing native BOS/EOS; generation/tokenizer files establish 1/2/11',
                                      '24B rounded marketing label resolved to exact inferred non-scale count',
                                      'scale dtype/scalar shape inferred by payload arithmetic; must inspect bodies later'],
              'source_urls':[model_url(n) for n in ('config.json','params.json','generation_config.json','model.safetensors.index.json','tokenizer_config.json')]}
    dump('identity.json',identity)

    attn=[m for m in modules if m['scope']=='attention'];a=sum(m['rank16_parameters'] for m in attn)
    all_params=sum(m['rank16_parameters'] for m in modules)
    assert a==19_660_800 and all_params==92_405_760
    pattern_prefix=r'^model\.language_model\.layers\.(?:[0-9]|[1-3][0-9])\.'
    patterns={'attention_only':pattern_prefix+r'self_attn\.(?:q_proj|k_proj|v_proj|o_proj)$',
              'attention_plus_mlp':pattern_prefix+r'(?:self_attn\.(?:q_proj|k_proj|v_proj|o_proj)|mlp\.(?:gate_proj|up_proj|down_proj))$'}
    scopes={}
    for name,targets,p in [('attention_only',attn,a),('attention_plus_mlp',modules,all_params)]:
        scopes[name]={'status':'SOURCE_SUPPORTED / GPU_UNVERIFIED','rank_for_estimate':16,'target_regex':patterns[name],
                      'target_modules':[m['module'] for m in targets],'base_weight_tensors':len(targets),
                      'adapter_A_B_tensors':2*len(targets),'trainable_parameters_rank16':p,
                      'adapter_payload_BF16_bytes':2*p,'adapter_payload_FP32_bytes':4*p,
                      'optimizer_state_working_estimate_bytes':16*p}
        assert all(re.fullmatch(patterns[name],m['module']) for m in targets)
    targets={'repository':REPO,'revision':SHA,'checkpoint_to_transformers_key_mapping':key_mapping,
             'catalog':catalog,'catalog_complete_against_index':True,'catalog_shapes_body_verified':False,
             'modules':modules,'scopes':scopes,'excluded':{
                 'embedding':'Frozen; no vocabulary resize or embedding adaptation authorized',
                 'lm_head':'Frozen untied dense head; projection scopes only',
                 'text_norm':'Frozen normalization scales; projection scopes only',
                 'vision':'Frozen and never invoked with images; same q_proj suffix is NOT safe to target globally',
                 'projector':'Frozen; text-only invocation'},
             'lora_constraints':{'bias':'none','modules_to_save':None,'save_embedding_layers':False,
                                 'alpha_dropout_schedule':'Not selected by static preflight; must be separately frozen before training'},
             'unusual_modules':'Text projections are separate ordinary nn.Linear. Mistral3 multimodal wrapper/RMSNorm/patch merger excluded. vLLM packs QKV and gate/up at serving time.',
             'adapter_tensor_prefix_note':'PEFT wraps paths with base_model.model; verify exact saved-key translation in later reload tests',
             'source_urls':[tf_url('models/ministral3/modeling_ministral3.py'),tf_url('models/mistral3/modeling_mistral3.py'),peft_url('tuners/lora/layer.py')]}
    dump('adaptation_targets.json',targets)

    answers=[
      ('Direct FP8 PEFT training?','UNSUPPORTED','The inspected FineGrainedFP8HfQuantizer.is_trainable is False. No native-FP8 bypass or undocumented training route is admitted.'),
      ('Reconstruct trainable representation?','SOURCE-CODE INFERENCE','Yes: pre_quantized plus explicit dequantize=True on the SAME original, preserving static activation scheme/null block size, FP32 scale multiplication then BF16 destination. Ordinary nn.Linear remains.'),
      ('Same original provenance?','SOURCE-CODE INFERENCE','All tensors derive only from exact original shards; no separately released BF16 checkpoint. Original hashes plus conversion recipe plus reconstructed tensor hashes form the identity chain.'),
      ('Official conversion path?','DOCUMENTED','FineGrainedFP8Config -> FineGrainedFP8HfQuantizer.get_weight_conversions/augment_weight_conversions -> Fp8Dequantize.convert/_dequantize_one; postprocess_model removes quantization configuration.'),
      ('Deterministic conversion?','EMPIRICALLY UNVERIFIED','Path has no RNG/calibration and deterministic elementwise mathematical mapping under a pinned implementation. Pin CPU architecture/PyTorch/thread settings and compare two independent tensor manifests; bitwise repeatability has not been tested.'),
      ('Transformed tensors?','SOURCE-CODE INFERENCE','280 text projection matrices use weight_scale_inv; 560 scale entries are consumed (activation_scale not reproduced as BF16 runtime quantization). 305 nonquantized weights pass through; actual dtype/shape/scales remain body-unverified.'),
      ('Regenerated/calibrated/requantized?','SOURCE-CODE INFERENCE','No regeneration/calibration is needed. Existing FP8 rounding is irreversible; FP32 multiplication -> BF16 adds declared rounding. Use save_original_format=False to avoid inverse Fp8Quantize during dense export. Reject missing or newly initialized weights.'),
      ('Hashable every cycle?','SOURCE-CODE INFERENCE','Yes: original LFS/body hash, source/environment hash, sorted per-tensor name/shape/dtype/byte hash and canonical manifest root; no such dense tensor hashes have yet been measured.'),
      ('Expansion?','SOURCE-CODE INFERENCE',f'Original {selected_bytes:,} bytes; reconstructed BF16 payload {dense_bytes:,} bytes. Full artifact retained; RAM/VRAM/workspace costs are separately estimated.'),
      ('Repeat fresh reconstruction?','EMPIRICALLY UNVERIFIED','Conceptually supported: original read-only shards -> new empty destination -> exact recipe -> matching tensor root. Repeat for every fresh cycle; never reload prior adapted/merged derivative. Time and peak memory unmeasured.')]
    reconstruction={'original_repository':REPO,'original_revision':SHA,'static_path_established':True,
                    'verified_lifecycle':False,'direct_native_fp8_training_supported':False,
                    'destination':'BF16 full dense representation of the stored quantized original',
                    'prequantization_BF16_recovered':False,'native_fp8_execution_bitwise_equivalent':False,
                    'key_mapping':key_mapping,'loading_attributes':{'dequantize':True,'dtype':'bfloat16','device_map':'cpu','trust_remote_code':False,'local_files_only':True},
                    'preserve_quantization_metadata_on_input':config['quantization_config'],
                    'dense_export_required':{'save_original_format':False,'safe_serialization':True,'quantization_config_absent':True,'is_quantized':False},
                    'serving_config_alias':{'text_config.llama_4_scaling':{'original_max_position_embeddings':8192,'beta':0.1},
                                            'origin':'unchanged exact params.json constants and text_config.rope_parameters values',
                                            'purpose':'vLLM MistralAttention reads legacy alias; Transformers reads rope_parameters; preserve both'},
                    'questions':[{'number':i+1,'question':q,'evidence_level':level,'answer':ans} for i,(q,level,ans) in enumerate(answers)],
                    'required_fail_closed_checks':['All six original body hashes/sizes match declared LFS','All 1145 raw entries accounted; 280 scale pairs complete',
                                                 'Actual dtype/shape agrees with topology; finite scales and outputs','Zero missing/unexpected/mismatched or newly initialized weights',
                                                 '585 reconstructed non-scale parameters; complete named tensor catalog','BF16 export has no quantization flags/scales/requantized tensors',
                                                 'Repeat reconstruction per-tensor hash equality','Serving config alias is authenticated; logits parity including positions >8192'],
                    'source_urls':[tf_url('quantizers/quantizer_finegrained_fp8.py'),tf_url('integrations/finegrained_fp8.py'),
                                   tf_url('quantizers/base.py'),tf_url('modeling_utils.py'),tf_url('conversion_mapping.py'),
                                   vllm_url('vllm/model_executor/models/mistral.py'),model_url('params.json')]}
    dump('reconstruction_analysis.json',reconstruction)

    # Read frozen control values only from permitted policy code, without importing model libraries.
    import ast
    tree=ast.parse((WORKSPACE/'harness/context_policy/protocol.py').read_text(encoding='utf-8'))
    frozen=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CONTROL_VALUES' for t in n.targets)))
    mappings={'decoding':('temperature',0.0,'decimal'),'temperature':('temperature',0.0,'decimal'),
              'top_p':('top_p',1.0,'decimal'),'top_k':('top_k',0,'integer'),
              'repetition_penalty':('repetition_penalty',1.0,'decimal'),'frequency_penalty':('frequency_penalty',0.0,'decimal'),
              'presence_penalty':('presence_penalty',0.0,'decimal'),'seed':('seed',0,'integer'),
              'text_stops':('stop',[],'array'),'max_generation':('max_tokens',2048,'integer'),
              'completions':('n',1,'integer'),'retries':('orchestrator retry count',0,'integer'),
              'context_shifting':('one fixed prompt_token_ids sequence, no shifting',False,'boolean'),
              'clipping':('lossless capture; no slice/clipping',False,'boolean'),
              'truncation':('truncate_prompt_tokens=None; overflow fail, never truncate',False,'boolean')}
    assert set(mappings)==set(frozen)
    sampling={'temperature':0.0,'top_p':1.0,'top_k':0,'min_p':0.0,'repetition_penalty':1.0,
              'frequency_penalty':0.0,'presence_penalty':0.0,'seed':0,'n':1,'max_tokens':2048,'min_tokens':0,
              'stop':[],'stop_token_ids':[2],'ignore_eos':False,'detokenize':False,'skip_special_tokens':False,
              'truncate_prompt_tokens':None,'logit_bias':None,'allowed_token_ids':None,'bad_words':None,
              'structured_outputs':None,'repetition_detection':None}
    runtime={'status':'STATIC_PROPOSAL / NOT AN AUTHENTICATED RUN PROFILE','verdict':VERDICT,
             'same_original_inference_representation':'authenticated pristine BF16 reconstruction, and independently reloaded adapter or merged evaluation derivative',
             'stack':{'vllm':{'version':'0.30.0','commit':VLLM,'backend':'V1 offline LLM'},
                      'python':'3.11.9','pytorch':'2.13.0','transformers':{'version':'5.19.0.dev0','commit':TF},
                      'peft':{'version':'0.21.3.dev0','commit':PEFT},'tokenizers':'0.23.2','jinja2':'3.1.6',
                      'markupsafe':'3.0.4','packaging':'26.3','accelerate':'1.15.0','safetensors':'0.6.2',
                      'mistral_common':'1.12.0','cuda_assumption':'13.0.3 from pinned vLLM Dockerfile; compatible actual wheel/driver/container/kernels must be resolved and authenticated later',
                      'os_architecture_assumption':'Linux x86_64 CUDA; local Windows tokenizer check is separate'},
             'installation_certified':False,'transitive_lock_container_digest':'NOT_ESTABLISHED; mandatory before later execution',
             'dependency_source_check':'vLLM 0.30.0 Transformers>=5.10.4 and Tokenizers>=0.21.1 admit proposed versions; no installed-build ABI or complete dependency-resolution claim',
             'rejected_runtime_snapshot':{'commit':'5f30fc7031cae49bf51073fc953d419b08f8887c','reason':'its Transformers upper bound <5.18 conflicts with selected 5.19.0.dev0 snapshot'},
             'engine_args':{'max_model_len':32768,'dtype':'bfloat16','quantization':None,'tensor_parallel_size':1,
                            'max_num_seqs':1,'seed':0,'enforce_eager':True,'enable_prefix_caching':False,
                            'generation_config':'vllm','skip_tokenizer_init':True,'limit_mm_per_prompt':{'image':0},
                            'trust_remote_code':False,'speculative_config':None},
             'input_transport':'explicit precomputed prompt_token_ids; no chat server template or history/tool/reasoning parser',
             'configuration_alias':reconstruction['serving_config_alias'],'sampling_params':sampling,
             'frozen_control_map':{k:{'requested':v,'runtime_parameter':mappings[k][0],'runtime_value':mappings[k][1],
                                      'runtime_argument_type':mappings[k][2],'source_status':'SOURCE-SUPPORTED',
                                      'infrastructure_status':'INFRASTRUCTURE-UNVERIFIED',
                                      'evidence':vllm_url('vllm/sampling_params.py') if k not in ('retries','context_shifting','clipping','truncation') else 'static transport/isolation design; wrapper must be certified'} for k,v in frozen.items()},
             'terminal_ids':[2],'terminal_allowance':1,'raw_capture':['all generated token IDs INCLUDING EOS','actual count','finish_reason','stop_reason','decoded raw bytes','only-one-final-EOS removal receipt','CR/LF normalization receipt'],
             'cap_rule':'2048 includes terminal; independent actual count >=2048 is capacity failure even if vLLM checks EOS before LENGTH and reports stop',
             'decode_rule':'exact ByteLevel inverse alphabet to bytes plus added-token literal UTF-8 bytes, retain all special markers; do not silently replace invalid UTF-8 via a string-only decoder. Remove at most one verified final observed EOS ID, then strict full-stream text admission and allowed CR/LF normalization only',
             'no_final_only_projection':True,'determinism':'greedy/seed source support does not establish repeated-process or cross-hardware deterministic inference',
             'source_urls':[vllm_url(n) for n in ('vllm/sampling_params.py','vllm/engine/arg_utils.py','vllm/v1/core/sched/utils.py','vllm/outputs.py','vllm/entrypoints/llm.py','requirements/cuda.txt','requirements/common.txt','docker/Dockerfile')]}
    dump('runtime_profile.json',runtime)

    lifecycle={'repository':REPO,'revision':SHA,'status':'STATIC DESIGN / ALL MODEL LIFECYCLE STEPS NOT_RUN',
               'inference_comparison':'pristine reconstructed BF16 original vs same-original BF16+adapter/merge; do not mix native FP8 baseline and BF16 adaptation without a separately justified representation design',
               'cycle':['authenticate immutable original','fresh output directory and fresh CPU reconstruction from original','check reconstructed tensor root against canonical pristine root',
                        'fresh training model load','fresh adapter initialization','fresh optimizer and scheduler','authenticated RNG initialization',
                        'authorized future train','save adapter and metadata','destroy ALL training model/optimizer/adapter states',
                        'reconstruct SAME original again and verify pristine root','reload adapter for evaluation','direct serving or isolated merge/export',
                        'destroy evaluation state; next cycle starts from original again'],
               'required_provenance':{
                   'original':['repo','immutable revision','six body byte counts/SHA256','all config/tokenizer/template hashes','index hash'],
                   'reconstruction':['original manifest root','software source/package/container hashes','CPU/hardware identity','conversion/key mapping/alias/dtype recipe hash',
                                     'sorted tensor name shape dtype nbytes SHA256','canonical tensor root','export shard hashes'],
                   'adapter_initialization':['unique cycle ID','scope exact regex/expanded names','rank/alpha/dropout/bias configuration','initial adapter state hashes','initialization seed and RNG state hashes'],
                   'optimizer':['new instance receipt','no restored state','initial optimizer/scheduler manifest','step zero','allowed parameters only'],
                   'rng':['Python/NumPy/Torch CPU and all CUDA state hashes','deterministic settings','fixed hardware and kernel identities'],
                   'destruction':['training process exit','GPU allocator/process inventory','fresh evaluation process and empty caches','no optimizer/previous adapter handle accessible'],
                   'adapter_saved':['adapter .safetensors and adapter_config hashes','original root','pristine reconstruction root','cycle ID','scope and training provenance'],
                   'evaluation':['reconstructed pristine base root verified BEFORE adapter application','loaded adapter root','merge/export recipe root if used','output raw token/byte hashes']},
               'derivative_contamination_rule':'Only artifacts typed ORIGINAL with exact repo/revision/body manifest may enter reconstruction; only matching authenticated PRISTINE_RECONSTRUCTION may create a fresh adapter. ADAPTER and MERGED_EVALUATION_DERIVATIVE are output-only and never adaptation parents.',
               'derivative_storage':'Separate read-only original store, fresh reconstruction store, adapter store and evaluation-only derivative store; merged base_model_name_or_path metadata alone is insufficient proof',
               'save_reload_export':{'adapter_format':'adapter_model.safetensors + adapter_config.json + external provenance manifest',
                                     'save_embedding_layers':False,'safe_serialization':True,
                                     'reload':'PeftModel.from_pretrained(fresh authenticated reconstructed model, saved adapter, is_trainable=False); match all saved keys',
                                     'direct_serving':'vLLM Mistral3 SupportsLoRA and packed QKV/gate_up mapping source-supported; actual adapter key/dtype/rank translation NOT_RUN',
                                     'merge_route':'reload adapter onto pristine full BF16 base -> merge_and_unload(safe_merge=True) -> save_pretrained(save_original_format=False, safe_serialization=True)',
                                     'merge_precision':'BF16 base update with adapter compute dtype (often FP32); final BF16 rounding; direct-adapter and merged numerical/decision parity unverified',
                                     'export':'full dense BF16 sharded safetensors/config/tokenizer/template, no quantization_config or FP8 scale entries; authenticated legacy attention-scaling alias',
                                     'requires_dense_weights':True,'may_be_next_base':False},
               'isolation':{'status':'DESIGN / NOT_CERTIFIED','network':'air-gapped host/namespace network disabled; offline Hub/Transformers flags plus blocked sockets/egress; loopback-only IPC if indispensable',
                            'mounts':'Read-only immutable model and runtime package store + authenticated single-request token input; write-only scoped output; fresh tmpfs. Mount no project/candidate/benchmark/home/history/tool directories.',
                            'tools':'No tool registry/execution, retrieval/chat/reasoning parsers or plugins in serving process; treat any emitted marker as ordinary retained text',
                            'filesystem':'Non-root UID; read-only root filesystem; explicit mounts only; block host filesystem, symlink/reparse escape, process inspection and credentials; audit allowed OS/driver/runtime reads separately',
                            'history':'Single fresh token sequence per request; no conversation/session state',
                            'cache':'enable_prefix_caching=False; max_num_seqs=1; fresh process per cycle/adapted vs pristine partition; no cross-base/adapter cached KV',
                            'retries':'zero; fail on infrastructure error without regeneration','audits':'negative socket/read/tool probes on synthetic denied locations, mount/process traces and output receipts before candidate execution'},
               'fallback_triggered':False,'protocol_modified':False,'model_instantiated':False,'adapter_instantiated':False,'inference_occurred':False}
    dump('original_base_lifecycle.json',lifecycle)

    gib=lambda n:round(n/2**30,6)
    kv=40*2*8*128*2*32768
    resources={'status':'ARITHMETIC AND PLANNING ESTIMATES / NOT MEASURED','resident_parameters':count,
               'active_vs_resident':'dense: all full artifact resident unless explicitly staged/offloaded; no active-parameter discount',
               'original_disk':{'bytes':selected_bytes,'GiB':gib(selected_bytes),'basis':'declared six LFS bodies only, no duplicated consolidated shards'},
               'reconstructed_dense_disk':{'payload_bytes':dense_bytes,'GiB':gib(dense_bytes),'headers_and_metadata_extra':True},
               'original_plus_reconstructed_bytes':selected_bytes+dense_bytes,
               'reconstruction_expansion_ratio':round(dense_bytes/selected_bytes,6),
               'kv_cache_32768_one_sequence':{'formula':'40 layers * 2(K,V) * 8 KV heads * 128 head_dim * 2 BF16 bytes * 32768 tokens','bytes':kv,'GiB':gib(kv)},
               'serving_vram_BF16':{'base_GiB':gib(dense_bytes),'KV_GiB':5,'workspace_planning_GiB':[2,8],
                                    'subtotal_range_GiB':[gib(dense_bytes)+7,gib(dense_bytes)+13],
                                    'additional':'allocator reserve, temporary prefill/logits and vision initialization require measurement; subtotal is not a hard upper bound'},
               'native_fp8_serving_reference_only':{'weight_GiB':gib(selected_bytes),'KV_GiB':5,'workspace_GiB':[2,8],
                                                    'excluded_from_primary_same_representation_comparison':True},
               'training_rank16':{},
               'training_activation_sensitivity':[{'sequence_length':t,'one_saved_BF16_hidden_tensor_per_layer_GiB':gib(40*t*5120*2),
                                                   'one_BF16_intermediate_MLP_GiB':gib(t*32768*2),
                                                   'full_BF16_logits_GiB':gib(t*131072*2),
                                                   'full_FP32_logits_GiB':gib(t*131072*4)} for t in (2048,8192,32768)],
               'activation_caution':'Sensitivity components only: checkpointing recomputes activations; kernels/loss/logits may retain multiple copies. No training sequence length or recipe selected. SDPA/FlashAttention avoids full attention score matrices; must certify actual backend.',
               'host_RAM':{'streaming_conversion_start_GiB':[96,128],'load_merge_start_GiB':[128,192],
                           'basis':'44.725 GiB BF16 + up to 24.022 GiB original mapped pages + largest conversion intermediates/metadata; loader retaining full copies can exceed estimates'},
               'largest_matrix_conversion':{'elements':167772160,'FP32_cast_bytes':671088640,'FP32_product_bytes':671088640,'BF16_destination_bytes':335544320,
                                            'total_intermediate_planning_bytes':1677721600,'GiB':gib(1677721600)},
               'temporary_conversion_disk':'Atomic fresh export adds up to one dense payload beyond original+canonical dense if both retained',
               'merge_export_disk':{'original_plus_pristine_plus_one_merged_payload_bytes':selected_bytes+2*dense_bytes,
                                    'with_second_dense_atomic_temporary_bytes':selected_bytes+3*dense_bytes,
                                    'planning_free_storage_GB_decimal':[180,220]},
               'fresh_reset_cost':{'minimum_original_read_bytes':selected_bytes,'fresh_dense_write_bytes':dense_bytes,
                                    'plus_eval_reconstruction':'Repeat if training state destroyed before evaluation; cost charged separately',
                                    'seconds':'NOT_MEASURED; storage bandwidth, scalar conversion and hash throughput required'},
               'later_starting_points':'BF16 serving: one 80 GiB class GPU, TP=1. Training: start one 80 GiB class GPU with authorized checkpointed small-microbatch recipe; investigate two 80 GiB GPUs with authenticated sharding only if needed. None verified or spending-authorized.'}
    for name,p in [('attention_only',a),('attention_plus_mlp',all_params)]:
        resources['training_rank16'][name]={'trainable_parameters':p,'BF16_adapter_bytes':2*p,'FP32_adapter_bytes':4*p,
                                          'gradient_optimizer_master_formula':'16 bytes/parameter: BF16 weight2+gradient2+FP32 master4+Adam moments8; or FP32 adapter4+gradient4+moments8 without separate master',
                                          'adapter_plus_gradient_optimizer_bytes':16*p,
                                          'base_plus_adapter_optimizer_GiB':gib(dense_bytes+16*p),
                                          'activation_and_workspace':'add sequence/backend-dependent activations/logits/workspace and allocator reserve; no empirical or hard peak claim',
                                          'PEFT_adapter_autocast':'defaults may promote adapters to FP32; manifest actual dtype, no guaranteed BF16 adapter file size'}
    dump('resource_estimates.json',resources)

    tests=[
      ('A','Exact acquisition and body identity','Acquire only authorized original six shards; verify LFS sizes/SHA256 and immutable metadata; inspect real dtype/shape/scale headers','Original body manifest; reject mismatch'),
      ('B','Official reconstruction','Execute explicit dequantize=True and key mapping on CPU; account for every weight/scale; reject missing/new weights; verify finite BF16 and flags stripped','585 tensor manifest and conversion trace'),
      ('C','32,768 context load','Load authenticated full BF16 reconstruction with max_model_len=32768 and reserve2048; no native-maximum inference','Effective config and memory receipt'),
      ('D','Prompt token parity','Exact pinned renderer/backend vs input server receipt on all synthetic fixtures; no hidden BOS/default system/history/tool/template','Byte and token hashes identical'),
      ('E','Frozen controls','All 15 requested controls effective; source profile typed parameters; seed/greedy/reserve; no generation_config overrides','Authenticated control receipt, negative override tests'),
      ('F','Native terminals','Establish actual native EOS2 behavior; PAD11/internal tools/modality markers retained; no blanket special stripping','Raw IDs and termination receipt'),
      ('G','Natural termination','Allow synthetic authorized input to terminate before cap; actual count and finish_reason recorded','Natural termination with no retry'),
      ('H','Forced 2,048 cap','Synthetic later generation reaching2048: count terminal within cap; EOS-at-cap classified capacity failure despite runtime stop precedence','output_capacity_failure; no clipping/regeneration'),
      ('I','Raw token/byte retention','Capture all IDs; invert ByteLevel alphabet to raw bytes including literal special markers; retain invalid UTF-8 without replacement; only verified final EOS removal and CR/LF normalization','Raw/normalized byte hashes and receipts'),
      ('J','Same-process greedy repeat','Authorized synthetic inference repeats fixed request/controls; compare IDs/bytes','Exact repetition or explicit failure'),
      ('K','Fresh-process greedy repeat','Cold process repeats pinned hardware/runtime/base/request; compare IDs/bytes','Repeatability boundary certificate'),
      ('L','Isolation/no-read/no-tools','Negative egress/tool/filesystem/history/retrieval probes; no candidate mounts or server prefix cache','Independent sandbox audit'),
      ('M','Peak RAM/VRAM/storage','Measure acquire/reconstruct/load/prefill/generation/train/save/reload/merge/reset peaks for both scopes','Peak table versus estimates'),
      ('N','Timing/throughput','Measure cold reconstruction/hash/load, full prompt prefill, decode, save/reload/merge/reset timing','Resource timings only; no model-quality selection'),
      ('O','Attention-only forward/backward','Fresh base and rank16 attention adapter; exact160 targets/19,660,800 trainables; finite nonzero gradients; base frozen','Gradient, trainable-name and base-hash audit'),
      ('P','Attention+MLP forward/backward','Fresh base and rank16 combined adapter; exact280 targets/92,405,760 trainables; finite nonzero gradients; vision/head frozen','Gradient and scope audit'),
      ('Q','Adapter save/destroy/reload','Save safetensors/config/provenance; terminate training; reconstruct original again; reload saved adapter exactly','Adapter hashes, key coverage and output/logit agreement'),
      ('R','Direct serving or merge/export','Verify vLLM packed-target adapter route; alternatively safe BF16 merge/export with save_original_format=False, no quant metadata; compare declared numerical/decision parity','Evaluation derivative manifest; no new adaptation parent'),
      ('S','Second independent reconstruction','Reconstruct same original in fresh directory/process under pinned CPU/software twice; compare per-tensor hashes','Equal canonical pristine tensor roots; shard byte determinism separately checked'),
      ('T','Contamination/reset audit','Cycle2 starts original only; fresh adapter/optimizer/RNG; no merged derivative/history/cache state; destruction receipts','Original lineage and zero optimizer-step audit'),
      ('U','Architecture/attention-scale parity','Authenticate legacy llama_4_scaling alias from original constants; compare Transformers and vLLM logits including >8192 positions and YaRN','No omitted/doubled attention scaling'),
      ('V','Parser environment/full stream','CPython3.11.9 Unicode14.0.0 official completion parser; retain reasoning/tool markers if emitted, no final-only extraction','Protocol-compatible raw full-stream certification'),
      ('W','Dependency/container/kernel lock','Resolve complete Linux package versions/wheel hashes, CUDA driver, Torch/vLLM extensions, model class and container digest; reject incompatible optional media dependencies','Complete runnable immutable environment identity'),
      ('X','Fresh cycle cost and derivative guard','Measure repeat original reconstruction per train/evaluation cycle; prove merged export rejects as original input','Reset cost receipt and fail-closed provenance tests')]
    with (ROOT/'infrastructure_test_matrix.csv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['id','test','procedure','acceptance','status'])
        writer.writeheader();writer.writerows({'id':i,'test':t,'procedure':p,'acceptance':acceptance,'status':'NOT_RUN'} for i,t,p,acceptance in tests)
    source_manifest=read('source_manifest.json')
    source_manifest['selected_runtime_pin']={'vllm':VLLM,'transformers':TF,'peft':PEFT}
    source_manifest['local_project_inputs']=[{'path':str(p.relative_to(WORKSPACE)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())}
        for p in [WORKSPACE/'experiments/model_preflight/landscape_closure'/n for n in ('REPORT.md','landscape.csv','source_manifest.json')]
        +[WORKSPACE/'benchmark_design/context_policy/current-repo-v1-draft3.json',WORKSPACE/'harness/context_policy/core.py',WORKSPACE/'harness/context_policy/protocol.py',WORKSPACE/'harness/context_policy/evidence.py']]
    source_manifest['execution_scope']='Only tokenizer backend/template compiler and canonical synthetic policy framing/packing helpers executed. No upstream training/serving recipe or model/adapter library executed.'
    dump('source_manifest.json',source_manifest)
    print(json.dumps({'catalog':len(catalog),'scales':len(scales),'non_scale_parameters':count,'rank16_attention':a,
                      'rank16_combined':all_params,'infrastructure_items':len(tests),'verdict':VERDICT},indent=2))

if __name__=='__main__':main()
