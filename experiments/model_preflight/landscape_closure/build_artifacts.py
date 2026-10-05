"""Build the candidate-blind audit from public text snapshots and manual decisions.

No model libraries, model execution, project tasks, or weight-body access.
"""
import csv
import hashlib
import json
import pathlib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[2]
FIELDS = ['repository', 'lineage_group', 'eligibility', 'inference', 'adaptation',
          'product_relevance', 'disposition', 'static_preflight_state',
          'inference_resource_regime', 'adaptation_resource_regime',
          'license_evidence', 'product_evidence', 'serialization',
          'inference_reason', 'adaptation_reason', 'decision_reason']
manifest = json.loads((ROOT/'source_manifest.json').read_text(encoding='utf-8'))
decisions = json.loads((ROOT/'decisions.json').read_text(encoding='utf-8'))
assert all(len(r) == len(FIELDS) for r in decisions['rows'])
models = {r['repository']: r for r in manifest['models']}
rows = []

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}

def source_url(repo, revision, file):
    return f'https://huggingface.co/{repo}/blob/{revision}/{file}'

def specific_p_url(repo, fallback):
    if repo.startswith('openai/'):
        return 'https://deploymentsafety.openai.com/gpt-oss#evaluation'
    if repo.startswith('google/gemma-4-'):
        return 'https://huggingface.co/blog/gemma4#plug-in-your-local-agent'
    if repo == 'deepseek-ai/DeepSeek-V3.2':
        return 'https://arxiv.org/html/2512.02556v1#S4.SS1'
    if repo == 'deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct':
        s = next(s for s in manifest['support_repositories'] if s['repository']=='deepseek-ai/DeepSeek-Coder-V2')
        return f"https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/{s['revision']}/README.md#33-standard-code-benchmarks"
    if 'Nemotron-3-Ultra' in repo:
        return 'https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf'
    return fallback

for values in decisions['rows']:
    r = dict(zip(FIELDS, values))
    repo = r['repository']; s = models[repo]
    directory = ROOT/'sources'/repo.replace('/','__')
    metadata = read_json(directory/'hub_metadata.json')
    config = read_json(directory/'config.json')
    text = config.get('text_config', config)
    weights = [x for x in metadata.get('siblings', [])
               if '/' not in x['rfilename'] and x['rfilename'].endswith('.safetensors')]
    hf_shards = [x for x in weights if x['rfilename'].startswith('model-')]
    selected = hf_shards or weights
    assert selected, repo
    total = sum(x.get('size', x.get('lfs', {}).get('size', 0)) for x in selected)
    retrieved = [f for f in s['files'] if f['status']=='retrieved']
    license_urls = [f['url'].replace('/resolve/', '/blob/') for f in retrieved
                    if pathlib.PurePosixPath(f['url']).name.startswith('LICENSE')]
    if repo == 'deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct':
        support = next(x for x in manifest['support_repositories'] if x['repository']=='deepseek-ai/DeepSeek-Coder-V2')
        license_urls.append(f"https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/{support['revision']}/LICENSE-MODEL")
    card = source_url(repo,s['revision'],'README.md')
    r.update(revision=s['revision'], repository_created_at_utc=s.get('created_at'),
             repository_modified_at_utc=s.get('modified_at'),
             release_status='published weight artifact listed; bodies not fetched',
             weights_access='gated manual acceptance; not acquired' if s.get('gated') else 'ungated public weight entries; bodies not fetched',
             weights_gate='UNCERTAIN' if s.get('gated') else 'PASS',
             immutable_identity_gate='PASS', license_gate=r['eligibility'],
             proprietary_api_gate='PASS', documentation_gate='UNCERTAIN' if not config else 'PASS',
             gated=s.get('gated'), model_type=config.get('model_type','UNVERIFIED'),
             architecture='; '.join(config.get('architectures',[])) or 'UNVERIFIED',
             native_config_context=text.get('max_position_embeddings','UNVERIFIED'),
             hidden_size=text.get('hidden_size','UNVERIFIED'),
             layers=text.get('num_hidden_layers','UNVERIFIED'),
             selected_weight_packaging='model-* HF shards' if hf_shards else 'root safetensors',
             selected_weight_bytes_declared=total,
             selected_weight_files='; '.join(x['rfilename'] for x in selected),
             weight_lfs_hashes_declared='; '.join(str(x.get('lfs',{}).get('sha256','not declared')) for x in selected),
             weight_bodies_downloaded=False,
             quantization_config=json.dumps(config.get('quantization_config', {}),ensure_ascii=False,separators=(',',':')),
             terminal_config=json.dumps({'eos':text.get('eos_token_id',config.get('eos_token_id')),
                                         'bos':text.get('bos_token_id',config.get('bos_token_id'))},separators=(',',':')),
             card_url=card,config_url=source_url(repo,s['revision'],'config.json') if config else '',
             license_urls='; '.join(license_urls) or card+' (authoritative license declaration; follow linked terms)',
             product_evidence_url=specific_p_url(repo,card),
             evidence_level='public static evidence; project runtime unmeasured')
    rows.append(r)

assert set(models) == {r['repository'] for r in rows}
csv_fields = list(rows[0])
with (ROOT/'landscape.csv').open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=csv_fields);writer.writeheader();writer.writerows(rows)

def table(headers, content):
    def escape(x):
        return str(x).replace('|','\\|').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(escape(x) for x in line)+' |' for line in content])+'\n'

def name(r):
    return r['repository'].split('/',1)[1]

def cardlink(r):
    return f"[{name(r)}]({r['card_url']})"

def configlink(r):
    return f"[config]({r['config_url']})" if r['config_url'] else 'config not retrieved'

def support(repo, path):
    s=next(x for x in manifest['support_repositories'] if x['repository']==repo)
    return f'https://github.com/{repo}/blob/{s["revision"]}/{path}'

out=[]
def section(n,title,body):
    out.append(f'## {n}. {title}\n\n'+body.strip()+'\n')

out.append('# STEP 8K-B.1G1E — Open-weight model landscape closure\n\n'
           'Independent pre-outcome, candidate-blind audit. Evidence cutoff: **2026-10-03, Asia/Calcutta**. '
           'Historical project state: supplied 1G1D. No roster or protocol freeze.\n')
section(1,'Verdict', '''**The two Qwen checkpoints are non-redundant, but a Qwen-only primary adaptation roster leaves obvious dense, MLA, and Mamba adaptation mechanisms untested.** Recommend three additional static work items: a full Devstral Small 2 preflight, a targeted GLM-4.7-Flash preflight, and a targeted Nemotron 3.5 Lightning BF16 preflight. These are investigations that can change the roster, not admissions.

The census covers 36 exact checkpoint identities in 13 publisher families. It includes contemporary heads, significant architecture/resource transitions, and older obtainable alternatives where they establish an otherwise missing engineering path. It does not select a coding-quality winner. The current Qwen infrastructure order remains 30B first, Next second. The gpt-oss-20b proposed final-only Harmony path remains **DROP — CURRENT PROTOCOL INCOMPATIBLE**, without reopening that decision.

**STOP MODEL SHOPPING: conditional YES after the bounded work queue in section 15 resolves the three gaps or documents a source-based failure.** This closes the broad census, not every distinct architecture interaction. Known optional survivors remain visible. If an unresolved survivor demonstrates a distinct *feasible fresh-base adaptation* regime that the queue does not cover, closure must be withheld for that named gap; section 22 specifies this condition. There is no unconditional admission or unconditional closure today.''')
section(2,'Search cutoff and methodology', '''Fresh public-web searches and direct official repository checks were performed on the audit date. Searches covered each required publisher, architecture and context, license files, coding-agent/SWE positioning, current self-hosted serving, and PEFT/training support. Additional scope searches included MiniMax, NVIDIA Nemotron, Google Gemma, Meta Llama, Ai2 OLMo, IBM Granite, and Microsoft Phi. Official current heads were checked against repository metadata; current Qwen 3.8, DeepSeek V4.1, GLM 5.3, Kimi K3, Nemotron 3.5, and Granite 4.2 were included rather than assuming older remembered releases were current. OLMo 3.1 and Phi-4-reasoning-plus were checked separately from older representatives.

The cutoff is the requested calendar date, not a claim to know future releases later that day. Repository creation/modification timestamps are recorded as such; they are not substituted for official announcement dates. Exact model SHA identities were resolved through public Hub metadata; small files were fetched at that SHA. GitHub support files were similarly commit-pinned. Live documentation is timestamped and byte-hashed where archived. Search-index recency was used for discovery, not to override the direct snapshot.

Only public metadata, model cards, configs, templates, licenses, and selected upstream implementation/recipe text were acquired, with a 2,000,000-byte limit per direct response. No tokenizer vocabulary or weight body was downloaded. Weight sizes and LFS identities are publisher metadata declarations, not body-hash verification. Manual-gated access was not accepted or bypassed. Fetched source was read as text and never imported/executed.

Eligibility, I, A, and P were evaluated separately. I PASS retains the supplied historical static state for the two Qwens; it does not mean an infrastructure test passed. A PASS means a technically credible fresh-original-base PEFT route is documented or supported by explicit trainable projections and compatible adapter lifecycle; it does not mean an adapter was instantiated. I/A UNCERTAIN names the missing fact. P FAIL means qualifying evidence was not established in the inspected authoritative release/model documentation; it is not a universal claim that the model cannot do SWE.

Public benchmark evaluation **existence** was recorded only for P. No performance magnitude is present in decision fields, and no such number affected inclusion, exclusion, redundancy, the work queue, or tiebreak. Unfiltered public source snapshots may contain benchmark tables, but the audit does not extract or compare their values. No project task, result, output, candidate inventory, convention, evaluator, or scorer was consulted. Secondary search results supplied discovery leads only; decisions use primary evidence. Hardware regime descriptions are engineering estimates, not a purchased topology, a fixed ceiling, or a quality ordering.''')
source_rows=[]
for r in rows:
    source_rows.append([cardlink(r),f"`{r['revision']}`",configlink(r),f"[license evidence]({r['license_urls'].split('; ')[0].split(' (')[0]})"])
section(3,'Primary sources consulted', table(['Exact repository/card','Immutable checkpoint SHA','Architecture/context','Terms'],source_rows)+'''
All 36 Hub metadata responses and retrieved model text files are inventoried with URLs, bytes, SHA-256, status, and server retrieval dates in `source_manifest.json`. Every decision can be joined to its repository and exact revision in `landscape.csv`. A SHA identifies the published checkpoint tree; it does not certify every weight body has been obtained.

Additional primary implementation and adaptation sources:
'''+table(['Repository','Pinned support revision','Evidence read'],[[s['repository'],f"`{s['revision']}`",'; '.join(pathlib.PurePosixPath(f['url']).name for f in s['files'] if f['status']=='retrieved')] for s in manifest['support_repositories']])+'''
Official live sources include the [Mistral release](https://mistral.ai/news/devstral-2-vibe-cli), [Google Gemma license page](https://ai.google.dev/gemma/docs/gemma_4_license), [Hugging Face/Google Gemma release guide](https://huggingface.co/blog/gemma4), [OpenAI model card, section 2.6](https://deploymentsafety.openai.com/gpt-oss), [NVIDIA distributed Super adaptation guide](https://docs.nvidia.com/nemotron/latest/nemotron/super3/sft.html), [PEFT v0.21 LoRA parameter documentation](https://huggingface.co/docs/peft/v0.21.0/package_reference/lora), [DeepSeek V3.2 author report, section 4.1](https://arxiv.org/html/2512.02556v1#S4.SS1), and [NVIDIA Ultra author report, Table 10](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf). Web-only consultation records distinguish unarchived bytes from archived sources. Failed guessed documentation paths remain marked unavailable; they are not represented as inspected evidence.''')
family_notes=[
 ['Qwen','Coder 30B, Next, 480B; 3.8 dense 27B and Flash Next','Full-attention MoE, DeltaNet MoE, dense recurrence, and new QSA/conditional-memory architecture. API Qwen3.8-Flash is not silently equated to the obtainable Flash-Next checkpoint.'],
 ['Mistral/Devstral','Small 2 24B 2512; Small 2507 BF16; 123B 2512','SWE-specific dense family, Tekken serialization, native FP8 versus BF16, Apache versus revenue-conditioned modified MIT.'],
 ['OpenAI','gpt-oss 20b and 120b','Harmony and native MXFP4 experts; historical final-only projection remains closed.'],
 ['DeepSeek','V4.1 Flash; V4 Flash 0731; V3.2; Coder V2 Lite Instruct','Current CSA/Engram/mHC heads, DSA/MLA lineage, and a small BF16 MLA alternative. Not every legacy V3/R1 post-training variant is enumerated.'],
 ['Z.ai','GLM 4.7 Flash; 5.3 Flash; 5.3','Small MLA and new sparse/linear/mHC versus large DSA; do not inherit older MIT terms to the large 5.3 head.'],
 ['Moonshot','Kimi K3; K2.7 Code; Linear 48B; Dev 72B','KDA/latent expert head, K2 MLA coding checkpoint, experimental KDA+MLA, and Qwen2-derived dense SWE model. K2.5/2.6 are documented ancestors, not silently classified redundant.'],
 ['MiniMax','M3; M2.7; M2.5','Sparse-attention head and M2 full-attention line; explicit terms differ across releases.'],
 ['NVIDIA','Nemotron Lightning 3.5 30B, Super 120B, Ultra 550B BF16','Mamba2+MoE, latent expert transitions, explicit custom-kernel adaptation recipes, and three residency regimes. FP8/NVFP4 siblings are packaging alternatives, not extra subjects here.'],
 ['Google','Gemma4 dense 31B and MoE 26B-A4B','Native channel serialization and dense/expert BF16; official collaborative release guide establishes coding-agent positioning. Smaller 12B/E variants remain family scope, not a claim of identical regime.'],
 ['Meta','Llama4 Scout 17B-16E','Gated multimodal expert representative; access/terms uncertain and P unestablished.'],
 ['Ai2','OLMo3 Think 32B and current OLMo3.1 Instruct 32B','Fully open dense training lineage, but inspected current P documentation does not meet the mechanical SWE gate.'],
 ['IBM','Granite4.1 30B and current Granite4.2 8B','The newer head documents SWE evaluation and coding-agent integration; do not inherit that evidence backwards.'],
 ['Microsoft','Phi4 and Phi4-reasoning-plus','16k versus 32k nominal context; generic coding and benchmark decontamination are insufficient P evidence.']]
section(4,'Landscape census', table(['Family','Checkpoint scope','Why investigated / grouping limit'],family_notes)+'''
This is a reasonable bounded census, not a proof that every public fine-tune was found. Managed API-only systems, embeddings, specialized modality models, and community derivatives without authoritative SWE positioning are outside the search target. No family was included merely to increase vendor diversity. Distinct contemporary mechanisms are visible even when their inference/adaptation path is only a reference or remains uncertain.''')
section(5,'Eligibility table', '''Five gates are shown separately: W = obtainable self-hosted weights; R = immutable checkpoint identity; L = intended research/product terms; API = core intelligence needs no proprietary API; D = enough published documentation for I/A/P. License PASS includes ordinary notice/use obligations and is scoped to the stated general SWE research/product use; undisclosed organizational/revenue/geographic facts are not invented. Terms-dependent models remain UNCERTAIN. W PASS is public artifact listing/access evidence, not a weight-download test. D PASS means the gate can be evaluated, not that it passes.

'''+table(['Checkpoint','W','R','L','API','D','Overall','Material license/access evidence'],[[name(r),r['weights_gate'],r['immutable_identity_gate'],r['license_gate'],r['proprietary_api_gate'],r['documentation_gate'],r['eligibility'],r['license_evidence']] for r in rows])+'''
For Llama4, ungated metadata/card/license are available but original config/tokenizer access is manual-gated; no acceptance was attempted. For MiniMax M2.7, the unqualified commercial product-development path fails; separately permitted personal/non-commercial research is not falsely described as prohibited or substituted for the user's combined scope. For Kimi Dev, the derivative MIT statement does not erase documented base obligations. M2.5's actual LICENSE-MODEL takes precedence over its card's Modified-MIT label.''')
section(6,'I — inference-feasibility table', '''The required deployed budget is **at least 32,768 tokens total, including the existing 2,048-token generation reserve**. Native maximum context is evidence, not proof of usable deployed capacity. Do not add the reserve again to require 34,816, and do not grant extensions merely to rescue a failure. Greedy controls, full emitted stream, terminal token identities, replacement output capacity, tools-disabled operation, and offline/no-read isolation must all be retained.

'''+table(['Checkpoint','I','Native pinned config context','Serialization / channels','Decision or unresolved fact'],[[name(r),r['inference'],r['native_config_context'],r['serialization'],r['inference_reason']+' '+configlink(r)] for r in rows])+'''
For every new plausible serving path, deployed greedy/sampling precedence, max-new-tokens=2048, EOS versus tool-handoff meanings, complete replacement emission, optional tool-loop removal, external-read isolation, and process/KV/recurrent-state reset remain unverified unless a row names a specific failure. Model-card sampled-agent recipes are not imported as study generation settings. An OpenAI-compatible local endpoint is transport, not a requirement for OpenAI's commercial API.

The historical gpt-oss exclusion concerns the proposed substantive analysis-to-final projection. The 120b row applies the same rejected projection to the family reference; it does not establish that all conceivable native Harmony paths are impossible, nor initiate a new Harmony audit. Source stop strings or special-token filtering cannot be used to delete substantive output. Native input-template controls are candidate facts to adjudicate against unchanged draft3, not approval to suppress reasoning. A valid profile must preserve the entire emitted textual completion apart from the already allowed native terminal removal and CRLF/CR normalization.''')
section(7,'A — adaptation-feasibility table', '''A is independent of I. Repeated adaptation must reload the exact ORIGINAL BASE each cycle, with new adapter and optimizer/scheduler/RNG state, then support saved-adapter reload and either original-base merge/export or compatible direct-adapter serving. A framework's general fine-tuning page is not an exact-checkpoint roundtrip certification. Fused expert Parameters need explicit parameter targeting or a declared attention-only scope; module names alone can miss them.

'''+table(['Checkpoint','A','Credible route / unresolved facts'],[[name(r),r['adaptation'],r['adaptation_reason']] for r in rows])+f'''
Support details were read at fixed commits: [GLM4 MoE Lite modeling]({support('huggingface/transformers','src/transformers/models/glm4_moe_lite/modeling_glm4_moe_lite.py')}) has attention Linears and tensor-stacked experts; [PEFT LoRA configuration]({support('huggingface/peft','src/peft/tuners/lora/config.py')}) exposes parameter targeting; [vLLM model support]({support('vllm-project/vllm','docs/models/supported_models.md')}) declares direct LoRA for several relevant architectures. A blank table cell is absence of that declaration, not a proof that merge/export adaptation cannot work.

The [pinned fine-grained FP8 quantizer]({support('huggingface/transformers','src/transformers/quantizers/quantizer_finegrained_fp8.py')}) reports `is_trainable=False`; supported dequantization is a separate path to verify. Native FP8/MXFP4/other compressed storage cannot be treated as ordinary trainable BF16 merely because weights can be served. Conversion must derive from the same original identity; a separately published BF16 sibling is not silently the same experimental original.

The exact [Lightning LoRA guide]({support('NVIDIA-NeMo/Nemotron','usage-cookbook/Nemotron-3.5-Lightning/dgx-station-recipes/lora.md')}) explains why Mamba `out_proj` wrappers can be bypassed by kernels. Its data-history truncation policy is not adopted here. The [Megatron-Bridge Lightning guide]({support('NVIDIA-NeMo/Megatron-Bridge','docs/models/nemotron/nemotron3.5-lightning.md')}) is upstream lifecycle support, not a project adaptation outcome. No claim that one model adapts better is made.''')
section(8,'P — product-relevance table with evidence', '''PASS evidence below is a precise location/description, rather than a copied benchmark score. Qualifying intended use establishes A-type evidence; repository/SWE evaluation existence establishes B-type evidence. A training-data or decontamination mention does not establish B. Generic code/function evaluations and community experiments are insufficient.

'''+table(['Checkpoint','P','Authoritative evidence / failed scope','Source'],[[name(r),r['product_relevance'],r['product_evidence'],f"[evidence]({r['product_evidence_url']})"] for r in rows])+'''
Gemma PASS uses the official Hugging Face release/integration guide co-developed with Google, especially “Llama.cpp” and “Plug in your local agent.” It is publisher-side release documentation, not a community anecdote or a copied quality result. The 26B coding-agent integration is explicit and the family guide applies to Gemma4's local deployment. The card alone would not establish this gate. Granite4.2's current card meets the gate; Granite4.1 does not inherit its successor's evidence.''')
section(9,'Resource-regime table', '''Selected checkpoint package sizes below are declared safetensor bytes, in decimal GB. They exclude tokenizer/runtime/activation/cache/optimizer overhead. Alternate consolidated versus HF shard packaging is not summed: Devstral Small2 has approximately 25.793GB of selected HF shards, Small2507 47.145GB, and 123B approximately 128.250GB. Counting both packaging paths would double those models. Native compressed size is not dense training residency. Labels describe plausible engineering classes; they are not measured fits or exclusion ceilings.

'''+table(['Checkpoint','Selected package GB','Inference regime','Adaptation regime'],[[name(r),f"{r['selected_weight_bytes_declared']/1e9:.3f}",r['inference_resource_regime'],r['adaptation_resource_regime']] for r in rows])+'''
Examples of source/card distinctions: Devstral Small2 advertises 256k while its pinned text config says 393216; V3.2/Coder-V2 advertise 128k while configs say 163840; Nemotron cards describe extended 1M while native configs say 262144; Granite4.2's extension claim is distinct from native 131072. None authorizes an extension or proves the study's usable budget.

Conditional memory deserves explicit accounting: Qwen Flash Next's active backbone count omits substantial lookup/PLE and MTP storage; DeepSeek V4.1's Engram has its own residency/offload; KimiK3's native compression does not make its logical multi-trillion base small to rebuild. Full context attention needs KV cache; DeltaNet/Mamba hybrids also need recurrent state and attention cache. Host offload, TP/CP/EP sharding, and quantization alter topology and repeated-cycle work. No accelerator price, spending estimate, throughput, or hard fit limit is asserted.''')
lineage=[]
for family,scope,note in family_notes:
    lineage.append([family,scope,note])
section(10,'Lineage groups', '''Use all four dimensions together: architecture/base, documented checkpoint training ancestry, tokenizer/serialization, and runtime/adaptation. The family map in section 4 is a census grouping, not an equivalence partition that makes all its members redundant. The CSV gives finer mechanism groups and each exact config.

'''+table(['Comparison','Architecture / training lineage','Tokenizer / serialization','Runtime / adaptation consequence'],[
 ['Qwen30 / Next','Full-attention MoE versus DeltaNet/full-attention hybrid MoE; independent checkpoints','Shared Qwen BPE/ChatML does not erase architecture','Different recurrent state, target coverage, residency and export/serving paths'],
 ['Qwen30 / 480B','Related full-attention MoE family, separately trained size checkpoint','Same serialization family','Cluster original-base reload/sharding versus smaller-cycle regime; size alone is not the argument'],
 ['Qwen3.8 dense / Flash Next','Dense DeltaNet versus QSA/gated/conditional-memory MoE','New generation template/tokenizer details, exact identity required','Dense PEFT versus special conditional-memory targeting/offload; different terms'],
 ['Devstral2507 / Small2 /123B','Mistral dense SWE post-training; 2507 documented MistralSmall3.1 derivative; Small2 retains multimodal artifact','Tekken/Mistral instruction family, not necessarily identical exact template','BF16 versus FP8 same-original conversion; vision exclusions; large dense distributed state'],
 ['DeepSeekV2Lite /V3.2 /V4/V4.1','MLA→DSA/MLA→CSA/mHC→CSA2/Engram; not one same subject','V2 template versus revised protocol-aware encoding','Low-rank projections/expert targeting, sparse/compressed backward and quantization differ'],
 ['GLM4.7 /5.3Flash /5.3','MLA small versus sparse-linear/mHC and large DSA branches','Different native template/multimodal generations','BF16 attention PEFT versus new FP8/hybrid/export and cluster plan'],
 ['KimiDev /Qwen coding roster','Documented Qwen2.5-72B dense ancestor; not Qwen3 MoE','Qwen2 BPE/ChatML','Independent dense-large adaptation regime despite non-Qwen publisher'],
 ['KimiK2.7 /K3 /Linear','K2.5/2.6 MLA architecture reused versus KDA/latentMoE/AttnRes versus experimental KDA+MLA','Kimi channels; K3 always-thinking requirement differs','Compressed trillion-scale conversion versus KDA backward and mandatory-stream uncertainty'],
 ['MiniMaxM2.5 /M2.7 /M3','M2 full-attention expert family versus sparse-attention multimodal head','M2 versus M3 template and reasoning modes','Native FP8 versus large BF16 sparse path; license is checkpoint-specific'],
 ['NemotronLightning /Super /Ultra','Mamba2 expert family; larger heads add latent expert structures','Nemotron configurable-thinking templates','Fused-kernel target exclusions; different latent targets, distributed base state and terms'],
 ['Gemma4 dense /MoE','Same multimodal family, dense versus routed expert representation','Gemma native thought/final/turn channels','Different expert adaptation and resident package; multimodal training targets excluded explicitly'],
 ['Granite4.1 /4.2','Dense Granite models; exact public configs distinguish scale/post-training','Granite/default reasoning template details','30B versus modest 8B-cycle residency; successor has independent P evidence'],
 ['OLMo3 /3.1; Phi4 /reasoning-plus','Documented same base lineage with new post-training','Think versus instruction/reasoning templates','Different context/output behavior, not automatically equivalent subject']])+'''
Where an exact training ancestor is not documented, it remains unspecified. Similar model_type or common tokenizer is not substituted for known training lineage. No expected adaptation improvement is part of these comparisons.''')
section(11,'Redundancy decisions', '''**No census row is assigned REDUNDANT REPRESENTATIVE.** The strict four-dimension equivalence rule is not sufficiently established for the useful comparisons. In particular, the current Qwens are not redundant; Gemma dense/MoE, small/large Devstral, MLA/CSA DeepSeek, and Lightning/latent Nemotron materially change a mechanism or resource/serialization regime.

Avoiding dozens of trivial packaging/post-training variants is census grouping, not a scored exclusion or an assertion that those variants satisfy the frozen redundancy rule. Native BF16 versus separately quantized exports and alternative shard packaging are recorded as artifact distinctions; only one original checkpoint identity per listed subject is evaluated. Kimi K2.5/2.6 are ancestors represented in the current coding-lineage census, not individually rejected. Optional subjects are not called redundant merely because a minimum coverage set does not include them.''')
section(12,'Current-roster coverage analysis', '''Qwen3-Coder-30B-A3B covers full-attention routed MoE with ordinary attention/expert target paths and approximately 61GB BF16 original residency. Next covers a hybrid of full attention and DeltaNet recurrence with MoE, approximately 159GB BF16 residency, different state isolation, and different adaptation/serving integration. Their shared serialization gives limited protocol diversity, but their architecture and repeated-load resource regimes differ materially. These are historical static conclusions; their preflights were not rerun.

The most obvious independent missing primitive adaptation regimes are ordinary dense attention/MLP, MLA with low-rank attention projections and tensor-stacked experts, and Mamba2 with fused state-space kernels. Devstral Small2, GLM4.7Flash, and Lightning respectively expose those gaps while also adding Mistral, GLM, and Nemotron serialization. One cannot replace another: dense PEFT does not validate MLA projection/expert targeting; neither validates Mamba's wrapper-bypassing kernels. Next's DeltaNet path does not certify Mamba.

Gemma channels, Granite modest dense residency, dense DeltaNet, latent expert heads, CSA/QSA, and conditional-memory lookup remain independently useful sensitivity regimes. The minimum proposal samples the core mechanism gaps, not every mechanism×serialization×resource cross-product. Their omission limits breadth claims and is explicitly visible; no blanket claim of representation of all open models or every frontier architecture is justified. Models lacking an evidenced repeated original-base route remain engineering references; they are not excluded merely for being large.''')
section(13,'Final disposition table', '''Only the five requested disposition labels are used. “Historical completed” identifies a retained full-preflight path that needs no new static work. “Optional” and “reference” are work-state annotations, not additional dispositions. INFERENCE-ONLY REFERENCE is a provisional role outside the *currently evidenced* repeated-cycle plan: no exact project topology/reset/export plan has been supplied for those complex distributed or specialized originals. It is not an A FAIL, hardware-ceiling rejection, or proof they cannot be trained. A documented pre-outcome cycle plan can promote a reference without using outcomes.

'''+table(['Checkpoint','Disposition','Work state','Reason'],[[name(r),r['disposition'],r['static_preflight_state'],r['decision_reason']] for r in rows]))
section(14,'Tiebreak analysis', '''**NOT APPLIED.** No actual resource constraint requiring fewer surviving preflights was supplied. The three-item recommendation is a mechanism-gap work plan, not a ranking of survivors or a resource-elimination contest. Other dense/MLA representatives remain unresolved alternatives rather than invented losers. If a later concrete resource constraint requires choosing between non-redundant subjects, apply the requested lexicographic sequence: architecture/adaptation coverage → serialization coverage → adaptation-resource coverage → inference-resource coverage; then evidence of testable fresh-base adaptation; then unresolved verification burden; then documented resource burden. Retain both if still tied. Never add benchmark magnitude, expected adaptation quality, or a weighted score.''')
section(15,'Minimum additional preflight recommendation', '''**Three bounded static work items before GPU spending. Do not begin them as infrastructure tests in this audit.**

| Subject | Work | Coverage-changing fact | Required static deliverable |
| --- | --- | --- | --- |
| Devstral-Small-2-24B-Instruct-2512, pinned SHA in section 3 | FULL PREFLIGHT | Dense SWE original plus Tekken/Mistral serialization; native FP8 may prevent the required adaptation lifecycle | Exact text-only template/token/terminal accounting; deployed 32768/2048 and greedy-control mapping; pinned loader/serving stack; deterministic same-original-checkpoint dequantization route; explicit attention/MLP targets excluding modality components; adapter save/reload and original-base merge/export format; complete offline/no-read/no-tools profile; reset/load and package map |
| GLM-4.7-Flash, pinned SHA in section 3 | TARGETED PREFLIGHT | MLA projection and stacked expert representation, plus native GLM think-prefix behavior | Establish whether a documented native generation-input mode is allowed by unchanged draft3; enumerate the entire emitted suffix and real EOS/tool-handoff tokens without generation; map MLA q_a/q_b/kv_a/kv_b/o Linears and expert 3D parameters to PEFT/direct-serving formats; declare attention-only versus expert scope; certify the static original-base reset/save/reload/export plan |
| NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16, pinned SHA in section 3 | TARGETED PREFLIGHT | Mamba2 kernel-aware adaptation, recurrent state, and determinism independent of DeltaNet | Validate native input profile under draft3 without output reasoning extraction; identify all emitted native boundaries; map safe projections/expert targets and Mamba out_proj exclusions to actual kernel calls; preserve original identity through NeMo/Megatron adapter reload/export; document fresh SSM/KV state reset, MTP/speculation disabled or semantically controlled, and deterministic cache representation |

Use only small immutable public text/metadata for these deliverables. A static preflight may identify but cannot empirically certify long-context memory, repeatability, or replacement-output validity. Those remain later infrastructure admission checks, after the bounded static work. Do not execute upstream recipes, instantiate adapters, create synthetic model outputs, or inspect project tasks for this work.

For GLM/Nemotron/Gemma/Granite/Qwen-thinking templates, the fact that `enable_thinking=False` exists does not establish protocol permission. Examine input construction and the full emitted stream; do not choose a disabled-reasoning mode merely to fit the reserve. If the only usable path needs suppression, final-only projection, retries, different effort, clipping, or budget accommodation, mark that path incompatible under unchanged draft3. A refusal of that profile is not an architectural A failure.

The Lightning one-H100 example uses FP16 SSM cache with stochastic rounding. Greedy token selection alone does not settle bit-level repeatability. Determine whether a documented deterministic cache alternative exists without changing the study semantics; if it does not, retain I UNCERTAIN or fail the proposed path. The station LoRA recipe's history truncation and old-reasoning removal are not adopted. Kernel target exclusions must be reported as adaptation scope, not silently treated as all-module LoRA.

**Conditional replacements, not an expanding shopping list:** if Small2 has no technically credible conversion from its own original FP8 artifact, full-preflight the already enumerated Devstral-Small-2507 BF16 original as a distinct fallback, with its exact identity; do not silently switch originals. If GLM's only protocol path is impermissible, full-preflight the already enumerated BF16 DeepSeek-Coder-V2-Lite-Instruct as the MLA alternative, with its distinct license/template. There is no automatic Mamba fallback: an exact source-based block is recorded rather than moving indefinitely up the size ladder.

The three work items are necessary for three independent gaps; one or two cannot establish all three. This is a minimal covering work set under the stated core mechanism scope, not a theorem that these exact representatives uniquely dominate all other survivors. Gemma native channels are an optional targeted sensitivity check if the proposed non-Qwen serialization checks cannot support the intended protocol-breadth claim; Granite4.2 is an optional modest-dense resource sensitivity. A newly verified feasible conditional-memory or latent-expert route must be treated as a named additional scope decision before any claim of comprehensive regime coverage. No resource tiebreak is smuggled into these alternatives.''')
section(16,'Product adaptation-economics observations', '''Inference active parameters measure computation, not all resident original weights. Frozen PEFT still needs base weights and activation/backward propagation; a small routed active count does not shrink reload/export of all experts. Native quantized inference fit does not imply quantized training or same-original merge support.

| Burden | Dense BF16 / ordinary PEFT | MoE, recurrent, compressed, or conditional-memory route |
| --- | --- | --- |
| Inference residency | Full dense base plus KV and runtime workspace | All expert/base storage plus routing, KV/recurrent state, lookup memory or offload; active count is insufficient |
| Training residency | Frozen base plus activations and adapter gradients/optimizer | Frozen all-expert base plus sharded state and activation/routing/recurrent backward support; conversion may increase storage |
| Adapter state | Explicit target shapes and rank, not just total model count | Attention-only versus per-expert/parameter targets changes scale; fused tensor layout changes admissible targets |
| Reload each cycle | Verify exact original hash and discard prior adapted weights/state | Distributed reconstruction/offload and quantization provenance; fresh optimizer/RNG and base identity across workers |
| Merge/export | May allocate a full copy and write a whole dense checkpoint | Expert shards, custom kernels, latent/lookup components and quantized re-export may require special serialization |
| Operations | Simpler process/config/reset lifecycle is plausible, not measured | TP/CP/EP coordination, cache determinism, checkpoint I/O and compatible adapter serving add dependencies |

For a linear weight with dimensions m×n, ordinary LoRA contributes r(m+n) trainable parameters. For E independently adapted experts the corresponding contribution scales with E, unless the implementation explicitly shares adapters; do not assume active experts reduce saved adapter state. A stacked 3D expert tensor must be mapped to PEFT's actual parameter semantics before counting it.

Illustrative arithmetic only, not a selected adapter: Devstral-Small-2507's pinned dense config has 40 layers, hidden size 5120, 32 query heads, 8 KV heads, and head dimension 128. At hypothetical rank 16, q/k/v/o targets would have 19,660,800 adapter parameters: about 37.5 MiB for BF16 adapter weights. Adding gate/up/down targets with intermediate size 32768 would total 92,405,760 parameters, about 176.25 MiB BF16. If adapter weights, gradients, FP32 master copy and two FP32 Adam states total 16 bytes/parameter, these examples consume approximately 300 MiB and 1.377 GiB respectively, before activations, frozen base, workspace and distribution overhead. The rank/targets/optimizer are examples, not protocol decisions; no adapter was constructed.

For frozen BF16 weights, approximately 2N bytes of base residency is a lower-order starting estimate; package bytes include headers and may include modality/MTP tensors. Actual topology also depends on activations at the intended adaptation sequence length, sharding/offload, backward kernels, cache configuration and merge peaks. Do not silently impose the 32768 generation capacity as an adaptation truncation policy. Repeated-loop economics must include original reload, reconstruction, adapter-state reset, adapter reload and merge/export I/O, not only one forward pass. Without an actual topology and measurements, no cloud-price or cost ranking is warranted.''')
section(17,'Remaining uncertainties', '''1. Public listed weights are not body-verified local originals. Exact metadata SHA/LFS values are recorded, but no model was loaded; access acceptance remains unresolved for Llama4.
2. No new checkpoint has empirical deployed-capacity, deterministic-replay, full replacement, EOS/hand-off, or offline-isolation certification. Nominal context and a greedy flag are insufficient.
3. Native input modes and emitted reasoning/channel syntax require protocol adjudication without changing draft3. No blanket non-thinking exemption is granted. Mandatory-thinking KimiK3 remains an explicit unresolved boundary.
4. Native quantization conversion/backward, stacked/fused targets, exact safe module coverage, fresh-original loading, saved-adapter roundtrip and export support are static plausibility findings, not executed project facts.
5. Several community licenses depend on organizational/product revenue, geography, distribution and service scope. No undisclosed fact is assumed, no license authorization requested, and no model publisher contacted. Stated use restrictions remain obligations even where eligibility passes.
6. INFERENCE-ONLY REFERENCE reflects absence of an evidenced exact repeated-cycle plan for complex distributed/specialized originals; it must not become a permanent size exclusion. The audit cannot certify an undisclosed infrastructure budget. References with A PASS are technically plausible but outside the currently documented project cycle plan, not adaptation-incapable.
7. Some primary reports were consulted through the web tool without a locally archived body; the manifest explicitly records that limitation. Public live pages are date/hash snapshots rather than immutable publisher versions. Missing text files and failed documentation paths remain unavailable, not filled from memory.
8. Optional survivors and architecture interactions are not fully covered by the proposed minimum. The broad census supports stopping open-ended shopping under the bounded primitive-mechanism claim; comprehensive serialization, conditional-memory, latent-MoE or all-size claims require explicit further scope decisions. This uncertainty is not concealed by declaring those models redundant.
9. A PASS says testability, P PASS says authoritative SWE relevance, and I PASS says static admissibility. None is a prediction about coding quality, adaptation gain, economic viability, or generalization beyond the eventual measured roster.''')
section(18,'Candidate artifacts inspected?', '''**NO.** Neither Step8K candidate inventories/dispositions nor the 31 candidate conventions were opened. No benchmark/project task instances, Study1 outcomes, project model outputs, private evaluators or scorers were inspected. Project input was limited to the two supplied attachments, the historical cross-model audit report, and repository identity/status/instruction-path checks. Public vendor benchmark names/method descriptions were read only to establish P; project evaluations were not run.''')
section(19,'Model inference performed?', '''**NO.** No weights downloaded, no model/tokenizer loaded, no generation, no GPU infrastructure tests, no training, and no adapter instantiated. Selected upstream Python files were read as text, not executed. Only standard-library metadata acquisition/report generation and artifact-integrity checks ran.''')
section(20,'Protocol modified?', '''**NO.** Draft2, current-repo-v1-draft3, context-policy implementation, and the historical Harmony completion decision were not edited. No protocol or final roster was frozen. Qwen infrastructure order was preserved. No commit was made.''')
section(21,'Files created/modified', '''All audit writes are inside `experiments/model_preflight/landscape_closure/`:

- `REPORT.md`: all 23 requested sections.
- `landscape.csv`: 36 rows with exact identities, separate five eligibility subgates, I/A/P, resource/lineage/serialization, allowed disposition and evidence links; no benchmark-score field.
- `source_manifest.json`: primary-source retrieval/identity/hash/status records, historical input identity, acquisition constraints, and web-only consultation limitations.
- `artifact_manifest.json`: relative file paths, lengths and SHA-256 for every generated/archive file except itself; self-exclusion avoids a recursive hash definition.
- `decisions.json`: readable manual decisions underlying the CSV/report.
- `collect_sources.py`, `collect_support.py`, `build_artifacts.py`, `validate_artifacts.py`: bounded text acquisition, deterministic report construction and integrity checks; they do not import model code.
- `sources/`: archived small public model/support text and metadata, plus byte-identical supplied audit/request input copies.
- `validation.json`: row/schema/identity/cutoff/hash/package and tracked-repository integrity checks.

Existing preflight artifacts were retained. HEAD/tracked-file checks and exact source/body-size checks are recorded in validation. No application/private evaluation test was necessary or permitted for a documentation-only audit.''')
section(22,'STOP-MODEL-SHOPPING determination', '''**Conditional YES after the section15 bounded static queue; NO unconditional roster closure today.** Stop open-ended discovery/ranking once each of dense, MLA, and Mamba is either represented by a statically admissible fresh-base path or has a precise source-based failure with the named fallback checked where applicable. Record the optional/reference scope and limit conclusions to mechanisms actually retained and later admitted. A failed path is evidence about that path; it does not justify claiming the missing architecture was tested.

Before asserting the conditional stop has been reached, each work item must name its original SHA, eligibility/I/A/P classification, exact native-stream profile without unauthorized projection, safe adaptation targets and original-base lifecycle, descriptive topology, and remaining empirical infrastructure checks. If a conditional license or specialized training fact resolves in favor of an independently feasible conditional-memory, latent-expert or additional native-channel regime *and that regime is required for the project's breadth claim*, resolve that specific known scope gap before closure. The three preflights therefore do not guarantee unconditional closure regardless of what they discover.

No count of survivors is required. Optional Gemma/Granite/dense-DeltaNet sensitivities may remain outside the minimum with explicit claim limitations; that is not a redundancy determination. Reopen discovery only for a concrete factual blocker in an intended admission or an actually material new release/regime under a stated cutoff revision. Do not reopen because of benchmark magnitudes, anticipated adaptation results, or a desire for a more impressive roster. No future monitor/automation is created by this audit.''')
section(23,'Final recommendation', '''Complete the three additional **static** work items, using only public immutable text, before authorizing GPU spending. Keep Devstral BF16 and DeepSeek V2 Lite as named conditional substitutes, not silent checkpoint swaps. Preserve the two Qwen historical proceed states and 30B→Next infrastructure order; preserve the gpt-oss20b final-only Harmony DROP. Keep terms-sensitive and specialized families visible as unresolved/reference subjects, and optional Gemma/Granite coverage explicit.

The audit establishes a broad, source-grounded landscape and a bounded mechanism-gap plan. It does not admit a new model, certify infrastructure, select a quality winner, change the protocol, commit changes, or freeze the roster. Stop broad shopping after the bounded plan satisfies the conditional coverage criterion in section22; report any surviving distinct feasible gap rather than inventing closure.''')
(ROOT/'REPORT.md').write_text('\n'.join(out),encoding='utf-8')

# Preserve only user-provided inputs and the allowed historical report as evidence.
input_paths = [
 pathlib.Path(r'C:\Users\admin\.codex\attachments\1db9acc3-d10e-495e-b964-2f0a7229eb12\Pasted text.txt'),
 pathlib.Path(r'C:\Users\admin\.codex\attachments\711734e4-d418-48ac-a289-2c72e140878c\Pasted text.txt'),
 ROOT.parent/'cross_model_audit'/'REPORT.md']
inputs=[]
for index,path in enumerate(input_paths):
    body=path.read_bytes(); destination=ROOT/'sources'/'project_inputs'/f'{index+1}_{path.name}'
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(body)
    inputs.append({'original_path':str(path),'archived_path':str(destination.relative_to(ROOT)),
                   'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'role':'supplied request' if index==1 else 'historical audit evidence'})
manifest['project_inputs']=inputs
manifest['methodology']={'requested_cutoff':'2026-10-03 Asia/Calcutta','decision_evidence':'primary only',
 'benchmark_magnitude_used':False,'candidate_artifacts_inspected':False,'project_tasks_or_outcomes_inspected':False,
 'model_inference_performed':False,'weight_bodies_downloaded':False,'adapters_instantiated':False,
 'protocol_modified':False,'roster_frozen':False,'commit_made':False,
 'weight_identity_evidence':'publisher metadata SHA and LFS declarations only',
 'direct_response_allowlist':'Hub metadata, README/config/template/license; selected upstream support text; official release/docs HTML',
 'known_unarchived_primary_consultations':'web tool only; no local byte hash asserted'}
manifest['web_only_primary_consultations']=[
 {'url':'https://arxiv.org/html/2512.02556v1','section':'4.1 SWE evaluation existence','local_body_archived':False},
 {'url':'https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf','section':'Table 10 SWE evaluation existence','local_body_archived':False},
 {'url':'https://huggingface.co/docs/peft/v0.21.0/package_reference/lora','section':'2D/3D parameter targets and LoRA lifecycle','local_body_archived':False},
 {'url':'https://developers.openai.com/api/docs/models/gpt-oss-20b','section':'official open-weight identity','local_body_archived':False},
 {'url':'https://developers.openai.com/api/docs/models/gpt-oss-120b','section':'official open-weight identity','local_body_archived':False},
 {'url':'https://www.microsoft.com/en-us/research/wp-content/uploads/2025/04/phi_4_reasoning.pdf','section':'SWE-bench decontamination mention is not a P evaluation','local_body_archived':False}]
manifest['selected_weight_packaging']=[{'repository':r['repository'],'packaging':r['selected_weight_packaging'],
 'bytes_declared':r['selected_weight_bytes_declared'],'files':r['selected_weight_files'].split('; '),
 'bodies_downloaded':False} for r in rows]
(ROOT/'source_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'rows':len(rows),'dispositions':dict(Counter(r['disposition'] for r in rows)),
                  'report_bytes':(ROOT/'REPORT.md').stat().st_size},indent=2))
