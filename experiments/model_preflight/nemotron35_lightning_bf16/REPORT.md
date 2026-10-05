# STEP 8K-B.1G1E-N1 — Nemotron 3.5 Lightning BF16 targeted static preflight

## 1. Verdict

**PROCEED TO INFRASTRUCTURE VERIFICATION**

Exact subject: **`nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16`**, revision **`a9904d24bcc1d289a1950fa9d2b978c47cf903b9`**.

The native default-thinking input admits an unchanged-Draft3 transport that captures **the entire raw generated suffix**, including reasoning, boundaries and tool text. No final-only extraction, reasoning suppression, effort adjustment, retry or larger allowance is needed. A fresh-original attention-LoRA lifecycle is source-supported; Mamba input-projection LoRA is also credible through the pinned trainable implementation. Routed-expert parameter LoRA is conditionally credible with explicit eager 3D parameter wrappers and merge/export.

This is a static mechanism/contract verdict. It does not establish a runnable installation, valid generated replacement, deterministic inference, numerical parity, successful adaptation or measured resource sufficiency. **All 24 infrastructure checks remain NOT_RUN.** No infrastructure work, roster freeze or GPU spending begins here.

## 2. Scope/prohibitions

The audit inspected permitted landscape/specification/cross-model artifacts, workflow precedents, exact immutable model text/metadata, and pinned official training/PEFT/serving source. Source acquisition was bounded to 2 MB per response, except the exact **17,077,484-byte tokenizer JSON**, explicitly bounded to 18 MB. This vocabulary exception contains text tokenizer data, not model weights. [Source manifest](source_manifest.json).

No weight bodies or tensor headers were downloaded. No model/adapter was instantiated, upstream recipe executed, GPU used, inference or model completion generated, A/B/M/C/BC experiment or Study1/2/3 run performed. No protected candidate inventory/task, project outcome or private scorer was inspected. Public documentation may contain evaluation tables; their numbers were not extracted into decisions or used for comparison.

Executable work consisted of standard-library acquisition/arithmetic/validation, canonical synthetic input packing, the exact tokenizer backend, and extracted immutable official Jinja compiler functions. No Torch, Transformers, PEFT, vLLM or downloaded model module was imported/executed. Tokenizer/Jinja dependency software was read-only reused from authenticated D1 files; fixture boilerplate and provenance conventions were reused, with independently derived Nemotron serialization/counts/maps. [Tokenizer environment](tokenizer_environment.json).

All new files are in `experiments/model_preflight/nemotron35_lightning_bf16/`. Existing specifications, landscape, completed preflights and product files are preserved. No substitution, final-only projection, clipping, retry, protocol edit, commit, roster selection or model shopping occurred.

## 3. Exact identity

Fresh exact-revision Hub metadata confirms the named SHA, public and ungated; created **2026-08-01T06:55:21.000Z**, modified **2026-08-24T23:46:27.000Z**. Model type is **`nemotron_h`**, architecture **`NemotronHForCausalLM`**. All recorded landscape identity/context/hidden/layer/shard/LFS fields match. The audited BF16 original is not the NVFP4, FP8, other-size or other-generation Nemotron release. [Identity](identity.json), [exact Hub metadata](upstream/hub_metadata.json), [config][config].

Packaging is **14** `model-00001-of-00014.safetensors` through `model-00014-of-00014.safetensors`, declared **65,827,374,264 bytes**. Every declared filename, size and LFS SHA256 is retained; names and hashes match 1G1E. These declarations are not body verification.

The index has **6513 original entries**: **6243 main entries** and **270 `mtp.*` entries**. Source/config-inferred coverage accounts for every key. The main load becomes **401 Transformers tensors/buffers** after individual expert stacking. [Full catalog](weight_layout_catalog.json), [index][index].

Metadata distinctions, preserved rather than silently repaired:

| Quantity | Meaning / finding |
|---|---|
| Hub `total` and index `total_parameters` = 31,577,937,344 | Matches inferred main parameters **excluding** 2944 correction-buffer elements and unused MTP |
| Inferred main elements including buffers = 31,577,940,288 | Main execution-state count |
| Hub BF16 = 32,913,263,168; F32 = 3072 | Includes all original main/MTP tensors and correction buffers |
| Full dtype sum = 32,913,266,240 | Main plus MTP, including buffers |
| Original MTP elements = 1,335,325,952 | Extra attention/MoE branch plus auxiliary projections/norms |
| Mixed-dtype payload = 65,826,538,624 bytes | Source arithmetic: BF16×2 + F32×4 |
| Declared shard bytes exceed inferred payload by 835,640 | Consistent with packaging overhead, unverified against headers |
| Index `total_size` = 65,842,365,568 bytes | Exceeds inferred payload by 15,826,944 and shard bytes by 14,991,304; unresolved public metadata inconsistency |

Do not use either the main-only Hub total or the inconsistent index byte field to reduce full original storage. Body acquisition later must reconcile actual shapes/dtypes/sizes. The official pinned Bridge guide also documents an import/export route for this release; it is upstream provenance/mechanism evidence, not project execution evidence. [Bridge guide][bridge].

## 4. License/product eligibility

The exact checkpoint LICENSE is **OpenMDW License Agreement 1.1**, with NVIDIA origin notices. It permits dealing in the model materials subject to its terms; redistribution retains the agreement and applicable origin notices. It includes a litigation-triggered termination provision, no restrictions on generated outputs, and assigns responsibility for other applicable rights. This supports the existing static product-use gate; it is not an Apache/MIT assumption imported from another checkpoint. [Exact LICENSE][license].

The exact card describes English/coding use, customization/post-training, and coding-agent evaluations including SWE-bench and Terminal-Bench. Only evaluation existence/domain was used. Its BF16 positioning as a customization/reference release does not prove production serving readiness. [Exact card][card].

## 5. Architecture/topology

The main model has **52 ordered residual blocks**, hidden **2688**, untied embeddings/head, vocabulary **131072**: **23 Mamba2**, **6 attention**, **23 MoE**. Blocks are separately interleaved, rather than every block containing an attention+MLP pair. Every block has one pre-mixer RMSNorm; a final RMSNorm precedes the head. [Config][config], [training implementation][training].

Attention uses **32 query heads, 2 KV heads, head dimension 128**, with separate Q/K/V/O Linear modules. Pinned Transformers and vLLM attention forwards do **not apply rotary/position transforms**; `rope_theta` and `partial_rotary_factor` fields alone are not evidence that RoPE runs.

Mamba uses **64 heads×64 dimensions = 4096 intermediate**, state dimension 128, 8 B/C groups, depthwise convolution width 4, SiLU gating and grouped gated RMSNorm. Input projection width is **10304**, not `expand×hidden_size`: the implementation derives intermediate width from Mamba head count/dimension.

Each MoE block has **128 routed experts, top 6 per token and one shared expert**. Routed expert width 1856; shared width 3712. Experts use ReLU squared with **up/down only**, not gate/up/down. `moe_latent_size=null`; latent projections are Identity, not adaptation targets. Router selection uses FP32 sigmoid/correction scores, grouping 1/1, normalized top 6 weights and scale 2.5. All 128 experts are resident.

The card's approximately 30B-A3B label is topology marketing, not exact storage. Source arithmetic gives about **2.875 B decoder elements active per token excluding vocabulary tables**, with six of 128 routed experts counted; conventions for embeddings/head differ. No active-parameter residency shortcut or performance inference is used.

Native config and tokenizer declare **262144** context; the card documents extended **1 M** context. The study remains **32768 deployed target +2048 output reserve**. No extension or altered limit is proposed. The card describes NVFP4 pretraining ancestry, but the selected released original is BF16. [Card][card], [config][config].

Original MTP adds attention+MoE blocks under `mtp.layers.0/1`, fusion projection and norms. Transformers ignores `mtp.*`; vLLM's main weight mapper drops that prefix. Only the exact 270 declared entries may be unused; no missing main tensor is tolerated. Original storage retains all 14 shards; speculation/draft models remain disabled. [Training exclusion][training], [serving mapper][serving], [MTP source][mtp].

## 6. Native tokenizer/template

The exact `PreTrainedTokenizerFast` JSON is ByteLevel BPE with regex splitting, **normalizer null**, no prefix space/dropout/padding/truncation. Model `ignore_merges=True` also allows direct whole-piece vocabulary lookup. Backend and model vocabularies both have **131072 IDs**, with **1000 added special tokens**. Exact hashes, attributes and complete special-token map are retained. [Tokenizer][tokenizer], [tokenizer config][tokenizer-config], [serialization](serialization.json).

The selected two-message rendering is exactly:

```text
<|im_start|>system
{unchanged SYSTEM}<|im_end|>
<|im_start|>user
{unchanged user(P,K,H)}<|im_end|>
<|im_start|>assistant
<think>
```

The final line break after `<think>` is part of the input. Assistant generation-prefix IDs are **[10,1503,19464,1010,12,1010]**. No BOS is added. Template defaults `enable_thinking=True`; explicit True renders identically. False renders **`<|im_start|>assistant\n<think></think>`** instead. This is a native **input-mode choice**, not deletion of generated content, but its existence does not authorize study suppression. [Exact template][template].

Root BOS 1 is `<s>`; root EOS 2 is `</s>`; root/generation PAD 0 is `<unk>`. Tokenizer EOS and PAD are **`<|im_end|>` (ID 11)**. Native generation config stops on **[2,11]**. No padding is used, so the PAD metadata mismatch is disclosed without affecting these checks. `add_bos_token` and `add_eos_token` are False; backend encoding uses `add_special_tokens=False`. [Generation config][generation], [special token map][specials].

Tools/documents are None and no assistant history is supplied. If no system is supplied, the template inserts an empty ChatML system turn; with the frozen SYSTEM it inserts no extra system content. `truncate_history_thinking=True` is a default assistant-history cleanup branch, dormant in this selected system+user input. Never apply that branch to generated output.

## 7. Draft3 native-profile compatibility

| Profile | Classification | Decision |
|---|---|---|
| Native default thinking + raw offline token output, no parsers | **COMPATIBLE** | Selected |
| Explicit enable_thinking=True + same raw transport | **COMPATIBLE** | Measured identical input |
| Native enable_thinking=False branch | **UNRESOLVED** | Independent study authorization not established; not selected |
| nemotron_v3 reasoning parser with final/content-only output | **INCOMPATIBLE** | Changes/deletes generated reasoning and boundaries |
| Tool execution, resumed history/continuation/retry | **INCOMPATIBLE** | Violates frozen one-request/no-read/no-tools contract |

Selected profile: **`NATIVE_DEFAULT_THINKING_FULL_SUFFIX_RAW_TOKEN_IDS`**. The default mode retains effort, reasoning and the entire emitted suffix under the same 2048 total generated-token cap. It does not depend on turning thinking off, a final-answer extractor or cleaner output.

Draft3 §7.2 evaluates incorrectly included content as emitted. For a single target, reasoning/markers become literal replacement content; for multiple targets a reasoning preamble may cause output-format failure. That is a permitted unsuccessful outcome under the unchanged parser, not a reason to repair the stream. Static transport compatibility does not promise code-only output or compliance frequency. [Existing Draft3](../cross_model_audit/sources/draft3.txt), [existing parser](../../../harness/context_policy/protocol.py).

The card's normal serving examples use a reasoning parser. Pinned `nemotron_v3` source splits reasoning/content, strips trailing reasoning whitespace, and can swap channels under particular request controls. None is an evaluation transform here; use original raw IDs/bytes. These findings are independently based on Nemotron's template/parser, not borrowed GLM/Harmony behavior. [Native parser source][reasoning].

## 8. Full-stream/terminal accounting

| Token/boundary | Origin | Required handling |
|---|---|---|
| im_start 10, role text, input im_end 11 | Input template | Input accounting only |
| Assistant prefix including think 12 and following newline | Input generation prefix | Counts as input, not generated thought |
| Generated thought/text and think 12 / closing 13 | Model suffix | Retain/count every emitted ID and byte |
| Final-answer channel | No separate native final token | No extraction; closing think is retained |
| tool_call 14/closing 15, tool_response 16/closing 17 | Vocabulary/native tool syntax | Retain/count if emitted; do not invoke tools |
| `<function=...>`, `<parameter=...>` and closings | Ordinary tokenized XML text | Retain/count; not special terminal IDs |
| `</s>` (ID 2) / im_end 11 | Generation-config native terminals | Count terminal; at most one verified final terminal removal |
| BOS 1, unknown 0, legacy INST/tool specials 3–9, reserved SPECIAL tokens | Vocabulary specials | Not extra stops merely because special |

No separate tool-handoff terminal exists in this template: generated tool-call text can finish at im_end 11. Preserve its full body and stop once at the verified native terminal; never supply a tool response or continuation. Input tool-response framing uses a user turn, but it is disabled here.

All emitted IDs—including reasoning, ordinary text, special markers and terminal—share **2048**. Retain IDs, raw byte stream, actual total, native finish/stop event and removal/normalization receipts. Only at most one verified last configured terminal may be removed, followed by existing CRLF/CR→LF normalization. Closing think and internal role/tool markers are not terminal cleanup.

A verified **LENGTH** event yields `output_capacity_failure`. EOS at count 2048 requires actual event evidence; count alone does not identify a length cap, and pinned stop code checks native EOS before length. Natural termination and forced cap are separate NOT_RUN tests. [Native stop source][stop].

Raw byte transport inverts the complete ByteLevel alphabet and emits literal bytes for added tokens. Keep original bytes before strict UTF-8 admission; never use lossy replacement or `skip_special_tokens=True`. All fixture inputs round-trip losslessly. Actual generated-stream decode/event behavior and invalid-byte cases remain infrastructure-unverified.

## 9. Static capacity

Canonical unchanged limits: **P 4096, K 12288, H 4096 bytes**; BC lane ownership≤2048 bytes. Four pattern families—ASCII, Unicode, combining-character stress and code/delimiters—at maximum and maximum-1 across five serialized forms yield 40 capacity rows. Five empty-registry rows and six framing sanity inputs give **45 capacity checks /51 total synthetic inputs**. These are synthetic input encodings, not model experiments or generated completions.

Every render/encoding was repeated four times with exact equality and lossless input-byte roundtrip. The measured maximum is **20,465 tokens** (ASCII maximum B/M/C fixtures). **Maximum input+2048 = 22,513. Violations against 32768: 0.** [Capacity receipts](capacity_checks.json).

Fixed rendered UTF-8 overhead is **671 bytes**. Complete 256-byte alphabet, no normalization/prefix insertion, merge BPE and direct whole-piece lookup support the conservative source bound **671+20480+2048= 23,199**, also below 32768. This is input accounting, not loaded-model context certification.

Checks used Windows CPython 3.12.14, tokenizers 0.23.2 and Jinja 3.1.6 with authenticated dependency reuse. Only framing/packing and exact compiler/tokenizer ran. The frozen Python output parser still requires **CPython 3.11.9/Unicode 14.0.0** later; it was not executed here. [Tokenizer environment](tokenizer_environment.json).

## 10. Hybrid architecture map

Exact main order/index membership is retained in [architecture_map.json](architecture_map.json), with all original shapes in [weight_layout_catalog.json](weight_layout_catalog.json):

| Class | Zero-based block indices |
|---|---|
| Mamba2 |0,2,4,7,9,11,14,16,18,21,23,25,28,30,32,35,37,39,41,44,46,48,50 |
| Attention |5,12,19,26,33,42 |
| MoE |1,3,6,8,10,13,15,17,20,22,24,27,29,31,34,36,38,40,43,45,47,49,51 |

Original prefix is `backbone.layers.i`; pinned training prefix is `model.layers.i`. Every block is `NemotronHBlock` with `norm.weight(2688)` and type-specific mixer. Current config remaps legacy `mamba/attention` to `linear_attention/full_attention` and exposes the equivalent `hybrid_override_pattern`; the current vLLM resolver uses this native Transformers config. No ad-hoc model patch is needed. [Config implementation][training-config], [runtime config resolver][resolver].

| Exact suffix under `model.layers.i.mixer` | Shape / class | Status |
|---|---|---|
| Attention q_proj /k_proj /v_proj /o_proj |(4096,2688)/(256,2688)/(256,2688)/(2688,4096), nn.Linear |ORDINARY LINEAR MODULE |
| Mamba in_proj |(10304,2688), nn.Linear |ORDINARY LINEAR MODULE; admitted |
| Mamba out_proj |(2688,4096), nn.Linear |ORDINARY LINEAR MODULE; fused training may bypass forward, excluded |
| Mamba conv1d.weight /bias |(6144,1,4)/(6144), depthwise Conv1d |ORDINARY PARAMETER; frozen |
| Mamba A_log /D /dt_bias |Each (64), nn.Parameter |CUSTOM PARAMETER in architectural role; frozen, no Linear LoRA claim |
| Mamba norm.weight |(4096), grouped gated RMSNorm, group 512 |ORDINARY PARAMETER; frozen |
| MoE gate.weight |(128,2688), custom router parameter used with functional.linear |ORDINARY PARAMETER; frozen |
| MoE gate.e_score_correction_bias |(128), FP32 buffer |NON-TRAINABLE BUFFER |
| Routed experts.up_proj /down_proj |(128,1856,2688)/(128,2688,1856), nn.Parameters |ORDINARY PARAMETER, stacked 3D; parameter LoRA only |
| Shared experts.up_proj /down_proj |(3712,2688)/(2688,3712), nn.Linear |ORDINARY LINEAR MODULE; frozen |
| Latent projections |Identity for exact null latent size |No tensor/target |

“CUSTOM PARAMETER” distinguishes the architecture-specific vector role; these are ordinary PyTorch nn.Parameter objects, not an invented class. B/C and dt are input-dependent projected channels, not separate learned Linear modules. Input split is **z 4096 |x 4096 |B 1024 |C 1024 |dt 64**. A=-exp(A_log.float()); dt is softplus with bias and source-specific clamp; D is the skip term. [Training source][training], [gated norm][gated-norm].

Training cache shapes are conv(batch,6144,4) and recurrent(batch,64,64,128). Serving TP 1 minimal state shapes are conv(3,6144) in SD orientation and SSM(64,64,128), held per state slot. Runtime pages, checkpoint slots and TP replication can add memory. Derived recurrent/KV/cache arrays are non-trainable state, absent from original weights. [Cache implementation][training-cache], [state shapes/dtypes][state-utils].

Serving uses fused QKV, sharded Mamba projection segments, A_log→FP32 A, custom convolution/scan/selective-state kernels and non-gated FusedMoE packing. These are **FUSED RUNTIME REPRESENTATION**, not ordinary training-module LoRA coverage. [Serving source][serving], [Mamba runtime][mamba-runtime].

## 11. Adaptation mechanism analysis

The admitted scopes are explicit and bounded. Rank 16 is an arithmetic estimate, not a chosen training recipe/alpha/data schedule. Names/shapes and complete target lists are retained in [adaptation_targets.json](adaptation_targets.json).

| Scope | Targets | Rank 16 trainables | BF16 /FP32 adapter payload |
|---|---:|---:|---:|
| 1 Conservative attention |24 Linear modules |1,867,776 |3,735,552 /7,471,104 bytes |
| 2 Hybrid attention+Mamba input |Same 24 +23 in_proj modules |6,648,832 |13,297,664 /26,595,328 bytes |
| 3 Hybrid+routed expert parameters |Same 47 modules +46 stacked parameters |434,729,984 |869,459,968 /1,738,919,936 bytes |

Scope 1 anchored pattern:

```text
^model\.layers\.(?:5|12|19|26|33|42)\.mixer\.(?:q_proj|k_proj|v_proj|o_proj)$
```

Scope 2/3 anchored module pattern:

```text
^model\.layers\.(?:(?:5|12|19|26|33|42)\.mixer\.(?:q_proj|k_proj|v_proj|o_proj)|(?:0|2|4|7|9|11|14|16|18|21|23|25|28|30|32|35|37|39|41|44|46|48|50)\.mixer\.in_proj)$
```

Ordinary A/B shapes are (16,in)/(out,16), count 16×(in+out). Attention contributes 311,296 per attention block; each Mamba input contributes 207,872. **No Mamba out_proj is admitted** under the fused training route: the combined kernel receives `.out_proj.weight` and can return before calling module forward. NVIDIA's station recipe independently documents that exclusion. Reference torch source does eventually call out_proj.forward, but that alternative does not broaden this scope. `use_mamba_kernels=False` is deprecated/no-op at this pin; it is not a sufficient switch. [Training source][training], [NVIDIA LoRA guide][nvidia-lora].

The explicit reference training profile has `use_kernels=False`, `USE_HUB_KERNELS=NO`, no installed `mamba_ssm` or `causal_conv1d` package, eager expert execution, cache=False/None and no compile. Official dispatch selects bundled differentiable torch convolution/chunk-scan functions; the combined-kernel reference returns None, then follows ordinary torch operations. This avoids inventing custom-kernel backward support. Its speed/memory behavior is unverified. [Dispatch source][kernel-dispatch].

Scope 3 uses an explicit fully qualified **target_parameters list**, two parameters per main MoE block. It selects both routed up/down tensor types across 23 blocks and all 128 experts per stack; no expert-index slicing is claimed. Pinned PEFT ParamWrapper supports 3D expert-first tensors, the non-transposed (out,in) orientation, nested wrappers, and temporary parametrization inside the expert parent's forward. Exact eager Nemotron code reads the parameter slices inside that forward. Reads outside it are not adapted. [PEFT implementation][peft-layer], [expert dispatch][expert-dispatch].

| Parameter | Shape | Actual rank 16 A /B shape | Trainables per parameter |
|---|---|---|---:|
| experts.up_proj |(128,1856,2688)|(2048,2688)/(1856,2048)|9,306,112 |
| experts.down_proj |(128,2688,1856)|(2048,1856)/(2688,2048)|9,306,112 |

Expert addition is **428,081,152** parameters. Combined scope has 186 A/B tensors versus 48 conservative and 94 hybrid. ParamWrapper requires zero LoRA dropout, fan_in_fan_out=False, lora_bias=False, DoRA=False and no unsupported variants; one fresh adapter is admitted. Adapter autocast may yield FP32, so both payload estimates are conditional. [PEFT config][peft-config].

Routers/buffers, A_log/D/dt_bias, convolutions/norms, shared experts, embeddings/head, MTP and absent latent projections are excluded. Frozen base gradients remain disabled; gradients flow through source torch operations to admitted adapters. Zero B initialization may yield zero A gradients on the first step, and unused experts need not receive gradients. Later tests check finite meaningful selected-branch flow and wrapper restoration without demanding every A/expert be nonzero immediately.

## 12. Training vs serving representation

Pinned Transformers renames backbone→model and stacks 128 original expert up/down tensors into two 3D parameters. There is **no gate/up concatenation** and no quantization/calibration. Numeric ordering, dtype/value hashes and inverse slices require later verification. [Conversion mapping][conversion], [load/inverse operations][load], [training/serving map](training_serving_map.json).

Training invokes standard attention/Mamba in_proj module forwards and eager parameter-wrapped experts under the explicit reference profile. Serving fuses Q/K/V, applies TP Mamba slicing/conv transforms, computes A=-exp(A_log), and uses custom state kernels/FusedMoE. vLLM declares **SupportsLoRA**, QKV packing and MTP skip prefixes, but this does not establish coverage for every selected Mamba projection or PEFT 3D parameter adapter. Direct serving remains **UNRESOLVED**; do not map stacked parameters to ordinary expert LoRA by analogy. [Serving source][serving].

Primary alternative: independently reload saved adapter onto fresh original-main → `merge_and_unload(safe_merge=True)` → BF16 main evaluation export with `save_original_format=True, safe_serialization=True`. Original-format inverse restores individual indexed up/down.weight names and backbone prefix expected by serving. A stacked current-training export is not assumed to load directly. This unquantized model needs no dequantize/requantize cycle. [PEFT merge][peft-layer], [save source][save].

Known implementation difference: pinned training mixer uses **dt_limit=(0.001,∞)**, while serving Mamba scan calls use **(0.0,∞)**. Source inspection does not establish identical cross-runtime logits. Compare effective configuration and numerical/decision behavior; diagnose rather than silently patch or certify parity. BF16 merge rounding and runtime kernel reductions also require empirical tests. No deterministic merge/export execution is claimed.

## 13. Fresh original-base lifecycle

The original is the immutable **14-body BF16 release plus F32 buffers**. Lossless prefix/layout derivation produces authenticated pristine execution state, not a new released adaptation parent. Every cycle starts from that same original, including retained unused MTP bodies. [Lifecycle design](original_base_lifecycle.json).

1. Authenticate bodies, exact revision, small files and original manifest.
2. Fresh load/stack; verify 401 main tensor/buffer hashes and exact 270 MTP exclusions before adapters.
3. Fresh adapter, optimizer/scheduler/RNG; separately authorized future adaptation; safe adapter/config/provenance save.
4. Destroy training model, adapter, optimizer, caches and process.
5. Reload **SAME ORIGINAL**, verify pristine root before application, then reload exact adapter keys.
6. Separately verified direct serving or primary safe merge/original-layout evaluation derivative.
7. Fresh token 0 recurrent/conv/KV state; full raw output capture; destroy all evaluation state.
8. Next cycle again authenticates ORIGINAL. Adapter/merged derivative cannot parent it.

Adapter format is `adapter_model.safetensors` +`adapter_config.json` +external cycle/base/target/hash/dtype receipts; safe serialization, embedding save disabled. Standard PEFT reload must cover both module and parameter-wrapper keys. No save/reload occurred here.

Recurrent reset is separate from weight reset. Training uses cache=False/None and zero-initial reference scan; serving requires fresh initial-state flags, SSM/conv/KV slots, counters, prefix/replay/speculative state and RNG. Source cache reset/initial-state mechanisms are visible, but stale-slot isolation is not certified. Same-process tests must use a divergent prior synthetic request to expose leakage; independent cycles additionally destroy processes/state allocations. [Training cache][training-cache], [serving metadata][state-metadata], [conv kernel][conv-kernel].

Isolation design is non-root read-only authenticated runtime/model mounts, one immutable token input, scoped output and fresh tmpfs, denied sockets/egress and no candidate/product/benchmark/home/history/credential mounts. No tool/retrieval/parser callback, history or retry is allowed. OS/driver/package/kernel reads must be separately allowlisted and negative-probed. Environment flags alone are not an isolation certificate.

## 14. Runtime stack

Proposed pinned self-host stack: **vLLM 0.30.0**, commit **`ced6857afa0ea7b2e3f0846a62e1394e90f15607`**; CPython **3.11.9**; PyTorch **2.13.0**; Transformers **5.19.0.dev0**, commit **`02d8fb9784e8f14a1251e4c992cd82a5762417c6`**; PEFT **0.21.3.dev0**, commit **`532a05dd505c28993119b7715ee286f4234bf51b`**; tokenizers **0.23.2**, Jinja **3.1.6**, MarkupSafe **3.0.4**, packaging **26.3**. [Runtime profile](runtime_profile.json).

CUDA **13.0.3** is a pinned Dockerfile assumption for later Linux/x86_64 work. That Dockerfile defaults Python 3.12; it is not the proposed 3.11.9 lock. A custom build override or separate frozen parser process requires later verification. Exact transitive distributions, Triton/compiler/driver/kernel/container hashes and compatible wheels are **NOT_ESTABLISHED**. The pinned build metadata declares Python >=3.10,<3.15 and Torch 2.13.0, so CPython 3.11.9 satisfies its declared Python range; actual wheel/build compatibility remains unverified. No installation/image execution is claimed. [Build metadata][vllm-build]. [Dockerfile][docker], [CUDA requirements][cuda-requirements].

Serving source contains bundled Triton Mamba convolution/chunk-scan/selective-state kernels. Requirements pin flashinfer-python/cubin **0.6.18.post1**, apache-tvm-ffi **0.1.11**; selected SSU backend is Triton. Training is a separate dependency profile with no optional mamba_ssm/causal_conv1d package and no Hub kernel replacement, using pinned torch references and eager MoE. No upstream training/serving recipe runs here.

Use offline `LLM.generate` with precomputed `prompt_token_ids`, skip tokenizer init, no chat/reasoning/tool parser. Explicit proposals: 32768 max length, BF16/no quantization, one sequence, TP 1 starting point, eager execution, seed 0, prefix caching=False, generation_config="vllm", remote code=False, speculation=None, chunked prefill=False and max_num_batched_tokens 32768. [Entrypoint][llm], [engine arguments][engine].

Hybrid controls: **mamba_backend="triton"**, conv-cache bfloat16, SSM-cache float32, cache mode "none", stochastic rounding=False, Philox rounds 0, ReplaySSM=False, fine-grained Mamba prefix caching=False, FlashInfer autotune=False. FP32 SSM state follows exact config precision; do not import the card's FP16/stochastic-rounding throughput profile. Greedy/seed 0/no rounding still do not establish deterministic reductions.

Mamba runtime warmup itself uses random diagnostic tensors and Triton autotuning. Later warmup/reset/reseed/config receipts must be separated from the actual request; source availability is not a repeatability certificate. No warmup/model kernel ran here. [Mamba runtime][mamba-runtime], [Mamba controls][mamba-config], [cache controls][cache-config].

## 15. Frozen generation controls

All 15 requested values match unchanged Draft3 policy data; arguments/types are explicit in [runtime_profile.json](runtime_profile.json). Every row is **INFRASTRUCTURE-UNVERIFIED**. Native constructor/source mapping is SOURCE-SUPPORTED; retry/shift/clipping prohibitions are static transport design.

| Frozen control | Proposed mapping /type |
|---|---|
| greedy |temperature 0.0 /decimal |
| temperature 0 |temperature 0.0 /decimal |
| top_p 1 |top_p 1.0 /decimal |
| top_k disabled |top_k 0 /integer |
| repetition 1 |repetition_penalty 1.0 /decimal |
| frequency 0 |frequency_penalty 0.0 /decimal |
| presence 0 |presence_penalty 0.0 /decimal |
| seed 0 |seed 0 /integer |
| no text stops |stop = [] /array |
| max generation 2048 |max_tokens 2048 /integer |
| one completion |n 1 /integer |
| zero retries |single transport call, retry count 0 /integer |
| no clipping |all raw IDs/bytes retained /boolean false |
| no shifting |one fixed prompt sequence /boolean false |
| no prompt truncation |truncate_prompt_tokens=None; overflow rejection /boolean false |

Additional explicit neutral controls: min_tokens 0, min_p 0, stop_token_ids = [2,11], ignore_eos=False, detokenize=False, skip_special_tokens=False, no structured/logit-bias/allowed-token/bad-word/repetition-detection processor. Native generation config's sampled temperature 1/top_p 0.95 defaults are not inherited. Only verified final terminal handling is applied, with all generated IDs counted first. [Sampling source][sampling].

No authenticated run profile/control/capacity/isolation certificate was issued. No reasoning effort knob, forced empty thinking, history cleanup or tool handling is silently inherited into evaluation.

## 16. Resource regime

These are source arithmetic/planning estimates, **not measured bounds or hardware admission**. Full experts/base residency is counted.

| Component | Estimate |
|---|---|
| Original 14-shard disk |65,827,374,264 bytes = 61.307 GiB |
| Main execution payload |63,155,886,464 bytes = 58.819 GiB |
| Unused original MTP payload |2,670,652,160 bytes, retained in original storage |
| Attention KV,32768, one sequence |6×32768×2  KV heads×128×2(K,V)×2 BF16 bytes = 201,326,592 bytes = 0.1875 GiB |
| Mamba SSM, one state slot |23×64×64×128×4 FP32 bytes = 48,234,496 bytes = 0.044922 GiB |
| Mamba serving conv, one slot |23×6144×3×2 = 847,872 bytes; TF kernel-width 4 cache = 1,130,496 bytes |
| Main+minimum state+3–10 GiB workspace |62.052–69.052 GiB planning subtotal; not upper bound |
| Conservative adapter working state |29,884,416 bytes at 16 bytes/trainable; base+adapter 58.846 GiB before activations/workspace |
| Hybrid adapter working state |106,381,312 bytes; base+adapter 58.918 GiB before activations/workspace |
| Expert combined working state |6,955,679,744 bytes; base+adapter 65.296 GiB before effective stacks/activations |
| Effective expert stack, one layer |2,554,331,136 BF16 bytes |
| Effective expert stacks, all 23 layers |58,749,616,128 bytes = 54.715 GiB if retained |
| Host RAM starting regime |128–192 GiB; original~65.827 GB +main~63.156 GB +packing/serializer/merge temporaries; full copies can exceed it |
| Original+one main export |128,983,260,728 bytes |
| Original+main+atomic second-main temporary |192,139,147,192 bytes;210–280 GB free-disk planning starting point |

The 16-byte adapter formula is BF16 weight 2+gradient 2+FP32 master 4+Adam 8, or FP32 weight 4+gradient 4+Adam 8 without a duplicate master; actual optimizer/dtype governs costs. Adapter payload alone does not include gradients/optimizer/container overhead. [Resource estimates](resource_estimates.json).

Persistent SSM/conv state is per slot, not automatically multiplied by 32768. Hybrid cache-manager page balancing/padding and extra checkpoint slots can exceed minimum arithmetic. Serving A=-exp(A_log) is FP32 and packed/kernel buffers can differ from original tensor payload.

Reference Mamba scan uses FP32, expands B/C groups and creates chunk/interchunk matrices/state intermediates; cache=False does not remove autograd activations. ParamWrapper baddbmm avoids a separate full delta but materializes effective 3D expert weights, potentially retained across layers. No sequence length/microbatch/loss recipe is selected; whole-block checkpointing/sharding and measured peaks are required. [Training source][training], [PEFT source][peft-layer].

Later starting points may investigate 80 GiB-class serving/conservative/hybrid training, subject to authorized measured checkpointing/workspace, or multi-GPU where needed. Expert scope warrants sharding/checkpointing investigation. No device count is verified or excluded by a hard ceiling. Every fresh cycle repeats original authentication/load/stack/pristine root plus recurrent/KV/RNG reset; throughput/reset timing is unmeasured.

## 17. Infrastructure test matrix

[infrastructure_test_matrix.csv](infrastructure_test_matrix.csv) contains exactly **24 checks A–X, all NOT_RUN**:

| IDs | Required later checks |
|---|---|
| A–D |Exact bodies/layout discrepancies; pristine load;32768 capacity;51 prompt/token fixtures |
| E–J |Full suffix; terminals; natural termination; forced 2048; raw bytes; all frozen controls |
| K–P |Same/fresh-process repeats; recurrent/cache reset; isolation; resource peaks; throughput/reset timing |
| Q–S |Conservative, hybrid and conditional expert forward/backward/coverage |
| T–X |Adapter save/reload; direct serving or merge/export/config/time-step parity; second ORIGINAL cycle; contamination/state reset; immutable dependency/container lock |

Each row includes a procedure and acceptance record. Tokenizer fixture checks are not executed model infrastructure checks.

## 18. Remaining blockers

No static blocker eliminates default-thinking full-stream transport or the conservative fresh-original adapter mechanism. Actual execution remains blocked on original body/hash/layout reconciliation; 401-entry pristine load and 270 exclusions; complete runnable dependency lock; context/prompt/output/terminal/control/cap certificates; state reset/isolation; repeats/resource peaks/timings; backward/save/reload/export and second-original cycle.

Hybrid admission requires verified reference dispatch and gradients to Mamba in_proj. Fused out_proj adaptation stays unresolved/excluded. Expert admission requires exact eager ParamWrapper restrictions, gradient/restoration/reload/merge behavior and measured memory. Direct adapter serving coverage is unresolved for full scopes; merged original-layout export is the credible alternative, still unverified.

Native TF/vLLM time-step-clamp, packing/state/kernel/config/precision differences require explicit parity assessment. No identical logits/output is asserted. Reasoning can make replacement formatting/content invalid; failures grant no permission for suppression, extraction, retry, clipping or reserve changes.

## 19. Static experimental-regime contribution

This checkpoint represents **Mamba2 selective state-space + sparse non-gated ReLU2 experts + occasional GQA attention**, with recurrent-state isolation, wrapper-bypassing training kernels, explicit projection coverage and Nemotron default-thinking/ChatML serialization.

That exact regime is not represented by the other surviving preflights. Qwen Next's Gated DeltaNet is recurrence evidence for a different mechanism; it does not certify Mamba's A/dt/conv/state kernels. Devstral supplies ordinary dense projections, GLM supplies MLA, and Qwen 30B supplies ordinary attention/MoE; none substitutes for this state-space path. These are descriptive architecture distinctions, not performance comparisons. [Frozen landscape rule](../landscape_closure/REPORT.md), [existing Next architecture record](../qwen3_coder_next/REPORT.md).

Under the frozen four-dimension rule—architecture/base, documented training ancestry, tokenizer/serialization, runtime/adaptation—**non-redundant** survives. The card documents Nemotron-Lightning/MTP ancestry and post-training; an exact equivalence to another surviving checkpoint is not established. Common reasoning markers or sparse activation labels do not establish lineage equivalence.

N1 changes this exact model from a pending targeted static work item into a **static-qualified candidate for later infrastructure/roster closure**, conditional on all external verification. It adds eligibility for that later closure consideration; it admits no model to a frozen roster, selects no winner and rejects no other survivor. No roster is frozen.

## 20. Protocol modified?

**No.** Draft2/Draft3/`current-repo-v1-draft3`, frozen SYSTEM, P/K/H 4096/12288/4096 bytes, BC ownership, 32768 context, 2048 reserve, full replacement/stream semantics and failure taxonomy are unchanged. Default thinking remains enabled. No special cleaner mode, reasoning deletion, final-only output, retry, continuation, shifting/clipping/truncation or projection is introduced.

The runtime and adaptation descriptions are static proposals, not protocol amendments, executed recipes or authenticated run profiles.

## 21. Files created/modified

New directory: **`experiments/model_preflight/nemotron35_lightning_bf16/`**.

- Required: `REPORT.md`, `source_manifest.json`, `artifact_manifest.json`, `identity.json`, `serialization.json`, `capacity_checks.json`, `architecture_map.json`, `adaptation_targets.json`, `training_serving_map.json`, `original_base_lifecycle.json`, `runtime_profile.json`, `resource_estimates.json`, `infrastructure_test_matrix.csv`, `validation.json`.
- Additional full inferred weight catalog, tokenizer environment, baseline preservation manifest, bounded acquisition/tokenizer/build/validation scripts, immutable public text snapshots and 51 synthetic input fixtures.
- Existing dependency files were read-only referenced by authenticated hashes, not copied or changed.

The artifact manifest covers every new file with size/SHA256 except itself, avoiding circular hashing. Validation is written first, then the manifest and recomputed hash checks. **1069 permitted pre-existing policy/historical/landscape/preflight files** are preservation-checked. No protected inventory is enumerated to perform those checks. [Validation](validation.json).

Final unchanged HEAD: **`7fcdecbe26f4fd01138edf8f58c02ce4b947db0b`**. Final status: **`?? experiments/model_preflight/`**, already present initially. Tracked/staged diffs are empty; no commit.

## 22. Claim limitations

Source support is not infrastructure success, determinism, isolation, code compliance, adaptation improvement or production readiness. Inferred shapes/dtypes/counts are not header/body/value measurements. No benchmark magnitude, ranking, expected adaptation gain, state-space superiority or hardware spending is used. Prior models supplied workflow evidence and descriptive regime context; their serialization/adapter/count/terminal conclusions were not applied to Nemotron.

Declared LoRA support does not prove kernel coverage. Native mode availability does not authorize study effort changes. Default-thinking full-suffix capture can preserve invalid code. Merge finite checks do not prove numerical parity. Explicit FP32 SSM/no stochastic rounding does not certify repeatability. All model lifecycle and infrastructure checks remain NOT_RUN.

## 23. Final recommendation

Record **PROCEED TO INFRASTRUCTURE VERIFICATION** for the exact pinned Nemotron BF16 original. Select native default thinking with the **entire raw suffix**. Full-stream Draft3 compatibility is statically established; conservative attention adaptation is source-supported, hybrid Mamba input adaptation is credible under the explicit reference path, and expert parameter adaptation is conditional. Fused Mamba out_proj and direct full-scope serving remain unresolved.

Maximum synthetic input **20,465**, maximum input+2048 **22,513**, violations **0**. Proposed pinned runtime vLLM 0.30.0; **24 NOT_RUN** infrastructure checks. Regime: Mamba2+MoE/GQA; redundancy: non-redundant under frozen rule. Protocol changed: no; inference: no; protected candidates: no; commit: no.

**STOP after this static preflight.** No infrastructure verification, roster freeze or further model shopping begins.

[card]: https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/blob/a9904d24bcc1d289a1950fa9d2b978c47cf903b9/README.md
[license]: https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/blob/a9904d24bcc1d289a1950fa9d2b978c47cf903b9/LICENSE
[config]: https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/blob/a9904d24bcc1d289a1950fa9d2b978c47cf903b9/config.json
[index]: https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/blob/a9904d24bcc1d289a1950fa9d2b978c47cf903b9/model.safetensors.index.json
[tokenizer]: https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/blob/a9904d24bcc1d289a1950fa9d2b978c47cf903b9/tokenizer.json
[tokenizer-config]: https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/blob/a9904d24bcc1d289a1950fa9d2b978c47cf903b9/tokenizer_config.json
[specials]: https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/blob/a9904d24bcc1d289a1950fa9d2b978c47cf903b9/special_tokens_map.json
[template]: https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/blob/a9904d24bcc1d289a1950fa9d2b978c47cf903b9/chat_template.jinja
[generation]: https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/blob/a9904d24bcc1d289a1950fa9d2b978c47cf903b9/generation_config.json
[training]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/models/nemotron_h/modeling_nemotron_h.py
[training-config]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/models/nemotron_h/configuration_nemotron_h.py
[training-cache]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/cache_utils.py
[gated-norm]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/models/zamba2/modeling_zamba2.py
[conversion]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/conversion_mapping.py
[load]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/core_model_loading.py
[save]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/modeling_utils.py
[kernel-dispatch]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/integrations/hub_kernels.py
[expert-dispatch]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/integrations/moe.py
[peft-config]: https://github.com/huggingface/peft/blob/532a05dd505c28993119b7715ee286f4234bf51b/src/peft/tuners/lora/config.py
[peft-layer]: https://github.com/huggingface/peft/blob/532a05dd505c28993119b7715ee286f4234bf51b/src/peft/tuners/lora/layer.py
[serving]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/model_executor/models/nemotron_h.py
[mtp]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/model_executor/models/nemotron_h_mtp.py
[mamba-runtime]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/model_executor/layers/mamba/mamba_mixer2.py
[state-utils]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/model_executor/layers/mamba/mamba_utils.py
[state-metadata]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/v1/attention/backends/mamba2_attn.py
[conv-kernel]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/model_executor/layers/mamba/ops/causal_conv1d.py
[mamba-config]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/config/mamba.py
[cache-config]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/config/cache.py
[resolver]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/transformers_utils/config.py
[reasoning]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/parser/nemotron_v3.py
[stop]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/v1/core/sched/utils.py
[sampling]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/sampling_params.py
[engine]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/engine/arg_utils.py
[llm]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/entrypoints/llm.py
[docker]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/docker/Dockerfile
[cuda-requirements]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/requirements/cuda.txt
[nvidia-lora]: https://github.com/NVIDIA-NeMo/Nemotron/blob/8749344f8ccefd50181c56b013ddc5c8a6154a8c/usage-cookbook/Nemotron-3.5-Lightning/dgx-station-recipes/lora.md
[bridge]: https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/721356847b79c4bf78e5b8e9ceb6ed87835d3872/docs/models/nemotron/nemotron3.5-lightning.md

[vllm-build]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/pyproject.toml
