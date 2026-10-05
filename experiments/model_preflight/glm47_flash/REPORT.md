# STEP 8K-B.1G1E-G1 — GLM-4.7-Flash targeted static preflight

## 1. Verdict

**PROCEED TO INFRASTRUCTURE VERIFICATION**

Exact subject: **`zai-org/GLM-4.7-Flash`**, revision **`7dd20894a642a0aa287e9827cb1a1f7f91386b67`**. A credible unchanged-Draft3 path exists using the **native default-thinking input and the entire raw emitted suffix**, without a reasoning/content parser, effort change, output projection or larger allowance. MLA attention adaptation has an official-source fresh-original path. A second, conditional scope adds explicitly targeted routed-expert 3D parameters using PEFT parameter wrappers, eager expert execution and merge/export.

This is a **static compatibility/mechanism verdict**. It does not certify a runnable installation, valid generated replacement, deterministic generation, measured resource sufficiency or successful adaptation lifecycle. All **24 infrastructure checks are NOT_RUN**. No GPU spending or execution is authorized. The default-thinking profile may emit reasoning that becomes unwanted literal replacement content or causes multi-file format failure; that content must be evaluated as emitted, not extracted away.

## 2. Scope/prohibitions

The work inspected allowed landscape/specification/cross-model artifacts, the exact immutable GLM card/config/tokenizer/template/index/Hub metadata, and pinned official model/PEFT/runtime sources. The Devstral D1 precedent supplied only workflow/provenance conventions, synthetic input construction methodology and already authenticated tokenizer dependency software. Its model-specific conversion, targets, terminal rules and conclusions were not transferred.

No full weight bodies or tensor headers were acquired. No model or adapter was instantiated; no inference, generated model completion, GPU operation, upstream training/serving recipe, experimental A/B/M/C/BC or Study1/2/3 run occurred. No protected candidate inventory, task, benchmark outcome or private scorer was inspected. Public model-card benchmark numbers were not used as selection evidence.

Executable work was limited to bounded public acquisition, static arithmetic/maps, canonical synthetic input framing/packing, exact tokenizer encoding and the immutable official Jinja compiler functions. No Torch/Transformers/PEFT/vLLM module was imported or executed. Original model code was read as text. The exact tokenizer JSON is **20,217,442 bytes**, explicitly bounded to 21 MB after an initial 20 MB size-limit result; it is vocabulary text, not weights. No new binary dependency downloads were needed. [Source manifest](source_manifest.json), [tokenizer environment](tokenizer_environment.json).

All new files are under `experiments/model_preflight/glm47_flash/`. Existing landscape, Devstral, historical audits, policy and product repositories are preserved. No commit, infrastructure run, DeepSeek fallback, Nemotron work, roster freeze or protocol amendment occurred.

## 3. Exact identity

Fresh exact-revision metadata confirms the repository/revision above, public and ungated, created **2026-01-19T06:28:10.000Z**, modified **2026-01-29T08:06:19.000Z**. Root model type is **`glm4_moe_lite`**, class **`Glm4MoeLiteForCausalLM`**. It is the landscape-pinned GLM-4.7-Flash, not another GLM checkpoint. [Exact Hub response](https://huggingface.co/api/models/zai-org/GLM-4.7-Flash/revision/7dd20894a642a0aa287e9827cb1a1f7f91386b67?blobs=true), [config][config].

Selected original packaging is **48** `model-00001-of-00048.safetensors` through `model-00048-of-00048.safetensors` shards, declared **62,444,175,504 bytes**. All filenames and public LFS identities agree with 1G1E; their full sizes/blob IDs/SHA256 declarations are saved in [identity.json](identity.json). They have not been verified against bodies.

The exact index contains **9703 entries**, including **212 unused MTP-layer entries** at `model.layers.47`. Public Hub tensor metadata declares **31,221,485,568 BF16 elements** plus **3008 F32 elements**, total **31,221,488,576**. The config/card identify an approximately 30B-A3B main model; full artifact totals additionally include the MTP branch. [Index][index], [Hub metadata](upstream/hub_metadata.json).

**Source inconsistency:** index `metadata.total_size=31,221,488,576` equals that element count, not the declared mixed-dtype byte payload. BF16/F32 arithmetic gives **62,442,983,168 payload bytes**; selected shard bytes are 1,192,336 bytes higher, consistent with headers but not body-confirmed. Use actual public LFS byte totals for original disk, retain both conflicting declarations, and require body/header verification later. Do not silently halve residency using the index field.

All 9703 names match the source/config-inferred catalog. Main execution state has **9491 raw entries**, represented as **751 current Transformers tensors/buffers** after expert stacking; total main elements including 2944 FP32 correction-buffer elements are **29,943,393,920**. MTP has **1,278,094,656 elements**, including 64 correction-buffer elements. Shapes/counts are inferred from constructors and checked against public metadata, not measured from weights. [Weight-layout catalog](weight_layout_catalog.json).

## 4. License/product eligibility

The exact card and Hub card metadata declare **MIT**, supporting the existing static product-use gate. The card documents software-engineering evaluation/use, including SWE-bench and terminal workflows; no score magnitude or relative quality is used. [Exact card][card].

The exact repository listing contains **no standalone LICENSE**, and its resolve URL returned 404. This corrects the landscape wording `MIT; LICENSE`; the existing license URL already pointed to the authoritative card. The official deployment repository's pinned LICENSE is MIT as supplementary evidence, not a substitute checkpoint license. Preserve applicable license/copyright notices for eventual redistribution. Eligibility is supported by the model's own MIT declaration, not by assuming other GLM releases share terms. [Official deployment repository](https://github.com/zai-org/GLM-4.5/tree/170f20b2c10659008fdbc909d478bc2a75bc3627), [its LICENSE](https://github.com/zai-org/GLM-4.5/blob/170f20b2c10659008fdbc909d478bc2a75bc3627/LICENSE).

## 5. Architecture/topology

The main decoder has **47 layers**, hidden **2048**, vocabulary **154880**, untied embeddings/head. Layer 0 is a dense SiLU-gated MLP, intermediate 10240. Layers 1–46 have **64 routed experts, top 4 per token and one shared expert**, expert intermediate 1536; the router uses sigmoid scores, correction bias, topk grouping 1/1, normalized selected weights and scale 1.8. All routed experts remain resident even though only 4 are selected for each token. [Config][config], [GLM implementation][glm-source].

Attention is MLA: **20 heads**, query low rank 768, KV low rank 512, Q/K non-positional head 192 plus rotary 64, value head 256. Q/K total head 256. The module uses Q_a→RMSNorm→Q_b and KV_a→latent RMSNorm→KV_b, plus O. These are separate ordinary bias-free Linear modules in Transformers, not the low-rank adapter itself. The architectural compression ranks 768/512 are distinct from proposed adapter rank 16. [GLM attention source][glm-source].

Native config context is **202752**; tokenizer config declares **128000**. Neither replaces the study target **32768** or reserve **2048**. Current pinned config defaults `rope_interleave=True`, positional dimension 64 and theta 1e6; resolved runtime values/ordering require later parity checks. [Config][config], [configuration implementation][glm-config], [tokenizer config][tokenizer-config].

One extra original MTP layer 47 has its own attention/MoE, embedding/head and auxiliary norms/projection. Transformers explicitly ignores `model.layers.47.*`; vLLM main loader skips speculative layers. We disable speculation/MTP and exclude exactly the declared 212 keys, retaining every original shard for provenance. This is a documented unused-original branch, not silent original replacement or missing-main-weight initialization. [Main loader][serving-source], [Transformers exclusion][glm-source], [MTP implementation][mtp-source].

The “3B active” card label is approximate. Transparent decoder-only arithmetic, counting 4/64 routed weights while excluding full vocabulary tables, gives approximately 3.262B elements accessed per token; conventions differ for head/embedding treatment. It is a topology description, never a residency estimate or performance assertion.

## 6. Native tokenizer/template

Pinned files: `tokenizer.json`, `tokenizer_config.json`, `chat_template.jinja`, all independently acquired/hashed. Tokenizer config names generic `PreTrainedTokenizer`; the supplied JSON defines the exact Rust backend used here: regex splitting, ByteLevel BPE, **normalizer null**, no BPE dropout, complete 256-byte alphabet. Backend vocabulary is **154856** versus padded model vocabulary 154880. The unassigned model IDs 154856–154879 must not silently disappear in output decoding; retain IDs and fail infrastructure if no authenticated text mapping exists. [Tokenizer][tokenizer], [tokenizer config][tokenizer-config], [serialization](serialization.json).

Native prompt prefix is `[gMASK]<sop>` IDs **154822/154824**. Roles: system 154826, user 154827, assistant 154828, observation 154829. Endoftext/PAD is 154820. Root/tokenizer metadata specifies no BOS token; current model configuration class has library default BOS0. That default is **not** an instruction to insert 0 into a nonempty precomputed native prompt. No padding, truncation or automatic special insertion is used.

Canonical chosen rendering is:

```text
[gMASK]<sop><|system|>{unchanged SYSTEM}<|user|>{unchanged user(P,K,H)}<|assistant|><think>
```

Default or `enable_thinking=True` appends the identical assistant/`<think>` generation prefix. `enable_thinking=False` instead appends **`<|assistant|></think>`** to the **input**. This is a native template input choice, not deletion of already generated output; it still changes the requested thinking mode and is not automatically authorized by the study. [Exact template][template], [compiler][template-source].

Tools are None, no documents/history/images are supplied, and no default system text is injected. The template has an assistant-history branch that extracts/clears prior reasoning according to `clear_thinking`/turn position. That branch is dormant for the selected system+user request; the template is never applied to generated output. Its existence grants no output-cleanup permission. Native vocabulary contains modality tokens, but the audited model is a text causal LM; no modality input path is enabled.

## 7. Draft3 native-profile compatibility

| Native/proposed profile | Classification | Decision |
|---|---|---|
| Default thinking + offline raw token output, no reasoning parser | **COMPATIBLE** | Selected |
| Explicit enable_thinking=True + same raw path | **COMPATIBLE** | Same measured input; redundant |
| enable_thinking=False template input branch | **UNRESOLVED** | Not selected; a documented mode does not establish independently authorized study use |
| Reasoning parser followed by content/final-only extraction | **INCOMPATIBLE** | Deletes part of emitted suffix |
| Agent tool execution, resumed conversation/history/retries | **INCOMPATIBLE** | Violates frozen one-request/no-read/no-tools design |

The selected default path neither alters effort to fit the reserve nor suppresses reasoning. All reasoning remains generated output under the same 2048 cap; `<think>` already in the prompt belongs to input. No enlarged answer-only allowance, timeout retry, additional turn or extraction is proposed. The publisher's thinking documentation is consistent with default thinking; its separate API `reasoning_content` examples are not adopted as the study output interface. [Template][template], [publisher thinking documentation](https://docs.z.ai/guides/capabilities/thinking-mode).

**Compatibility is about preserving the contract, not guaranteeing usable code.** Draft3 §7.2 says incorrectly included content is evaluated as emitted. For a single target the entire normalized suffix becomes replacement content, including reasoning/markers; for multiple targets a preamble can violate the first-header-at-zero requirement and produce output-format failure. Those are allowed outcomes under the unchanged parser, not permission to repair output. No compliance frequency or quality was measured. [Existing Draft3](../cross_model_audit/sources/draft3.txt), [existing output parser](../../../harness/context_policy/protocol.py).

This resolves the GLM serialization gate by selecting a complete raw-suffix path, rather than relying on the landscape's tentative non-thinking branch. It transfers no Harmony final-only exemption or Devstral output behavior. The prior gpt-oss conclusion concerned a proposed extraction path; this GLM profile explicitly excludes extraction.

## 8. Full emitted-stream/terminal accounting

| Marker/event | Source/status | Accounting |
|---|---|---|
| `[gMASK]<sop>`, system/user roles | Template input | Input tokens |
| `<|assistant|><think>` | Template generation prefix | Input tokens, not generated reasoning |
| Generated reasoning text | Possible model suffix | Every emitted token retained/counted |
| `<think>`154841 / `</think>`154842 | Native vocabulary; closing marker may delimit answer | Retain/count whenever emitted; not terminal removal |
| Final answer text | Later possible suffix | Retain/count; no separate final channel marker |
| `<tool_call>`154843 and closing 154844, arg delimiters 154847–154850 | Native tool syntax | Retain/count all emitted body/markers |
| `<tool_response>`154845/154846, observation 154829 | Tool-return/handoff syntax | No actual tool return or second request is supplied |
| Endoftext 154820, user 154827, observation 154829 | Exact config/generation EOS list | Count emitted terminal; at most one verified final terminal may be removed from text |
| `<eop>`154825, PAD/internal roles/other specials | Vocabulary entries | Not additional stops merely because special |

Source metadata distinguishes tool handoff from normal endoftext; observation is nevertheless a configured stop. If emitted, stop once, retain any tool-call body, record the observed native event and execute no tool/continuation. A stop does not make the remaining text valid replacement content. [Generation config][generation], [tokenizer][tokenizer], [runtime stop implementation][stop-source].

All emitted IDs—reasoning, answer, boundaries and a final terminal—share the total 2048 ceiling. Record complete IDs, actual count, finish/stop reasons, native event, decoded raw bytes and removal/normalization receipts. A verified LENGTH-capped event yields `output_capacity_failure`. EOS exactly at count 2048 must be adjudicated from actual termination evidence; count alone does not prove a length event, and pinned stop code checks EOS before length. Natural termination and forced cap remain separate tests. No reason-only sidecar can justify discarding reasoning from the replacement.

Byte-preserving decode inverts the exact ByteLevel alphabet for ordinary tokens and emits literal UTF-8 bytes for added tokens. Keep raw bytes before strict UTF-8 admission; do not use lossy replacement or `skip_special_tokens=True`. At most one verified final native terminal ID is removed, then existing CRLF/CR→LF normalization. Input byte round-trip was checked on every fixture. Output decoding, invalid bytes/unmapped IDs and event timing remain unverified.

## 9. Static capacity accounting

The selected **default-thinking** profile was used for every capacity fixture. Canonical P/K/H byte maxima remain 4096/12288/4096; BC ownership remains≤2048 per lane. Four patterns (ASCII, Unicode, combining-character expansion stress, code/delimiters) × two boundaries × five serialized forms produce 40 rows; five empty registries give 45. Six framing/template sanity fixtures give 51 total inputs. No candidate task or experimental condition run was used.

Each encoding was repeated four times with exact equality. **Maximum synthetic input:20,427 tokens. Maximum input+2048:22,475. Capacity violations:0.** All fixture input/token hashes and counts are retained in [capacity_checks.json](capacity_checks.json), with synthetic input JSON under `synthetic/`.

Fixed rendered UTF-8 overhead is 633 bytes. Complete byte alphabet/no normalization/no pretokenizer prefix insertion/merge-only BPE supports a conservative bound **633+20480+2048=23,161**, below 32768. This is source-inferred byte accounting, not loaded-context certification. Tokenizer 128000/config202752 native declarations are both above the target; neither is treated as measured capacity.

Local checks used CPython 3.12.14/Windows, tokenizers 0.23.2 and Jinja 3.1.6, with read-only authenticated dependency reuse. Only canonical framing/packing helpers and the extracted official template compiler functions ran; the full official parser still requires CPython 3.11.9/Unicode14.0.0 later. [Tokenizer environment](tokenizer_environment.json).

## 10. MLA structure

Exact targets for each main layer 0–46 are `model.layers.i.self_attn.*`:

| Module | Weight shape (out,in) | Role |
|---|---|---|
| q_a_proj |768×2048|Query compression |
| q_b_proj |5120×768|20×256 expanded query |
| kv_a_proj_with_mqa |576×2048|512 latent+64 shared positional key |
| kv_b_proj |8960×512|20×(192 nonpositional K+256 V) |
| o_proj |2048×5120|20×256 value output→hidden |
| q_a_layernorm |768|RMSNorm between query stages, excluded |
| kv_a_layernorm |512|RMSNorm of latent KV, excluded |

Full `q_proj` isNone for this exact q_lora_rank768 config. Architectural MLA ranks are not PEFT ranks. Positional rotation uses the 64-dimensional component and current native interleave configuration. [GLM implementation][glm-source], [MLA map](mla_map.json).

Pinned Transformers caches 512 latent and 64 positional values per token/layer **before** expanding K/V for the attention call. Expanded K/V can be transient workspace even though persistent cache is compressed. vLLM native MLA uses custom/absorbed-weight execution; Q_a/KV_a may be fused, and KV_b is supplied to an MLA helper. Those serving kernels are not a backward-support claim and may bypass ordinary adapter forward calls. We use the standard Linear/eager-expert training path and a merged evaluation export unless full direct-adapter parity is separately verified. [Runtime GLM model][serving-source], [MLA implementation][deepseek-source], [runtime helper][mla-runtime].

## 11. Expert representation

The original index stores individual routed expert weights:

```text
model.layers.{1..46}.mlp.experts.{0..63}.gate_proj.weight  (1536,2048)
model.layers.{1..46}.mlp.experts.{0..63}.up_proj.weight    (1536,2048)
model.layers.{1..46}.mlp.experts.{0..63}.down_proj.weight  (2048,1536)
```

The pinned Transformers implementation represents each layer as **two 3D `nn.Parameter` objects**:

```text
model.layers.i.mlp.experts.gate_up_proj  (64,3072,2048), [gate;up]
model.layers.i.mlp.experts.down_proj     (64,2048,1536)
```

These are **not ordinary expert Linear modules**. Official `glm4_moe_lite` aliases the `qwen2_moe` conversion: numeric-order `MergeModulelist(dim=0)`, then gate/up `Concatenate(dim=1)`; down is stacked. This is lossless layout conversion, with no quantization/calibration/new weights. Source natural key ordering avoids lexicographic expert 10-before 2 errors. [Conversion mapping][conversion-source], [conversion operations][load-source], [expert map](expert_map.json).

Router parameter is 64×2048; correction buffer is 64 FP32 elements. Shared expert is one 1536-intermediate ordinary gated MLP, with three Linear modules. Router, correction, shared experts, dense layer 0, norms/vocabulary/head and MTP are frozen/excluded. vLLM uses fused expert parameter mappings and may fuse shared experts, so a Transformers parameter adapter is not assumed to be a directly loadable vLLM LoRA adapter. [GLM experts][glm-source], [runtime loader][serving-source].

## 12. Adaptation target scopes

Scope 1 is **MLA attention-only**, exact anchored `target_modules`:

```text
^model\.layers\.(?:[0-9]|[1-3][0-9]|4[0-6])\.self_attn\.(?:q_a_proj|q_b_proj|kv_a_proj_with_mqa|kv_b_proj|o_proj)$
```

It targets **235 Linear modules**,470 A/B tensors. Rank 16 trainables are **21,031,936**: sum `16×(in+out)` across five projections and 47 layers. A shape is 16×in; B isout×16. BF16 payload **42,063,872 bytes**; FP32 **84,127,744 bytes**. [Adaptation map](adaptation_targets.json).

Scope 2 is **MLA plus routed gate_up/down parameter adaptation**: same 235 module targets plus an explicit fully qualified `target_parameters` **list** of 92 parameters, two per sparse layer 1–46. Each targeted stack includes all 64 routed experts. This selects parameter types/layers, not individual expert-index subsets; no unsupported selective-slice claim is made.

| Parameter | Rank 16 A / B actual flattened shape | Trainables/layer |
|---|---|---:|
| gate_up_proj (64,3072,2048) |(1024,2048)/(3072,1024)|5,242,880 |
| down_proj (64,2048,1536) |(1024,1536)/(2048,1024)|3,670,016 |

Expert-only addition is **409,993,216** parameters. Combined total is **431,025,152**,654 A/B tensors. BF16 payload **862,050,304 bytes**; FP32 **1,724,100,608 bytes**, plus format/config/provenance. Formula is `64×16×(in+out)` per stacked parameter; it is not ordinary two-dimensional Linear LoRA.

This second scope is **conditionally source-supported**, using pinned PEFT `ParamWrapper`, which supports 2D/3D parameters, expert-axis orientation, nested wrappers and temporary parametrization during the parent forward. The exact GLM eager expert forward indexes the targeted parameters inside that parent call. Reads outside the wrapped forward are not adapted. Required restrictions: **zero LoRA dropout**, no fan-in/fan-out, LoRA bias, DoRA or unsupported variant; one fresh adapter; `experts_implementation="eager"`, `USE_HUB_KERNELS=NO`, no Torch compile or fused expert-forward substitution. These are implementation-admissibility constraints; no training recipe was executed. [PEFT config][peft-config], [parameter wrapper][peft-layer], [expert dispatch][experts-dispatch].

Ordinary Linear LoRA uses standard autograd with a frozen base. Parameter LoRA creates effective expert weights through parametrization; its backward/reload/merge path is source-visible but empirically unverified. The no-grad routing-mask construction does not wrap expert matrix arithmetic in no-grad. Only selected expert branches receive token gradients; default zero B initialization can produce zero A gradients on the first backward. Later tests must check meaningful gradient flow without demanding every expert/A tensor be nonzero immediately. PEFT may promote adapters to FP32; storage estimates are conditional. [PEFT layer][peft-layer], [wrapper/save/reload][peft-model].

No all-module adaptation is claimed. Dense/shared MLPs, routers, correction buffers, norms, embeddings/head and every MTP tensor remain excluded.

## 13. Fresh original-base lifecycle

Native original is BF16 weights plus FP32 correction buffers, with **no quantization configuration**. No dequantization is required. Individual-expert stacking is a lossless execution-layout derivation authenticated against the original; it does not introduce a separate released base.

Every cycle: authenticate original 48 bodies/config/index/tokenizer/template → fresh main-model load/repack → verify pristine 751-entry tensor/buffer root and exact 212 MTP exclusions → fresh adapter/optimizer/scheduler/RNG → separately authorized future adaptation → save adapter/config/provenance → destroy all training state → load the **same original again** → verify pristine root **before adapter application** → reload adapter → merge/export/evaluate → destroy evaluation state. The next cycle again begins with original, not a previous adapter or merged derivative.

Required proof records cover original repo/SHA/body hashes, lossless converter/source/software/hardware/container identity, resolved config and eager/kernel flags, sorted tensor/buffer name/shape/dtype/bytes/hash, adapter initialization/expanded targets/config/initial tensor hash, step-zero optimizer/scheduler, Python/NumPy/Torch CPU/CUDA RNG identities, training process exit/GPU state destruction, saved adapter root, reloaded pristine root and evaluation derivative/output receipts. [Lifecycle design](original_base_lifecycle.json).

Adapter serialization is `adapter_model.safetensors` plus `adapter_config.json` and external original/pristine/cycle provenance, with safe serialization and embedding save disabled. Standard PEFT reload onto a fresh original-main base must cover both ordinary module and parameter-wrapper keys exactly. No actual save/reload happened.

Primary serving route is fresh-original+reloaded adapter→**`merge_and_unload(safe_merge=True)`**→BF16 evaluation derivative→**`save_pretrained(save_original_format=True, safe_serialization=True)`**. Here the original-format option reverses lossless gate/up concatenation and expert stacking into the **individual expert names expected by vLLM**. There is no FP8 reverse conversion in this unquantized model. A stacked export is not assumed to be directly accepted by the runtime. Preserve/integrate loader conversion metadata and verify inverse tensor/index ordering before using export. [Merge source][peft-layer], [inverse operations][load-source], [save behavior][modeling-utils], [runtime loader][serving-source].

Merge precision depends on actual adapter dtype and BF16 base rounding; safe-merge finite checks are not determinism/parity certificates. Require independent unmerged/merged reload and numerical/decision parity tests. The main 47-layer export is an evaluation derivative with unused MTP excluded, never the next original. Only the exact 48-body **ORIGINAL** manifest can parent fresh adaptation; `ADAPTER` and `MERGED_EVALUATION_DERIVATIVE` are output-only. No adapter-on-adapter continuation or derivative-base contamination is allowed.

## 14. Runtime/serving mapping

Proposed self-host stack: **vLLM 0.30.0**, commit **`ced6857afa0ea7b2e3f0846a62e1394e90f15607`**; CPython**3.11.9**; PyTorch**2.13.0**; Transformers**5.19.0.dev0**, commit **`02d8fb9784e8f14a1251e4c992cd82a5762417c6`**; PEFT**0.21.3.dev0**, commit **`532a05dd505c28993119b7715ee286f4234bf51b`**; tokenizers**0.23.2**, Jinja**3.1.6**, MarkupSafe**3.0.4**, packaging**26.3**. CUDA **13.0.3** is the pinned Dockerfile assumption for later Linux/x86_64 execution. Complete transitive lock, compatible driver/kernels/wheels and container digest are **not established**. [Runtime profile](runtime_profile.json), [requirements][requirements], [CUDA requirements][cuda-requirements], [Dockerfile][docker].

The exact runtime registry includes `Glm4MoeLiteForCausalLM`; source declares `SupportsLoRA` and Q_a/KV_a fusion mapping. That establishes a declared support route, not proof that all five projection adapters or PEFT 3D wrappers are applied by MLA/expert kernels. Direct adapter serving remains unresolved; merged BF16 individual-expert export is the primary proposed route for both scopes. [Registry][registry], [GLM runtime][serving-source]. The frozen card's historical nightly instructions are read as documentation, not executed or treated as proof that only a contemporary nightly can support the model.

Use offline `LLM.generate` with precomputed native `prompt_token_ids`; skip runtime tokenizer initialization and every chat/reasoning/tool parser. Engine proposals:32768 max length, BF16/no quantization, TP1 starting point, one sequence, seed 0, eager execution, prefix cache disabled, `generation_config="vllm"`, remote code disabled, speculationNone. Native default thinking is preserved; no `/nothink`, extra effort knob or final-only content transport is used. [Entrypoint][llm-source], [engine arguments][engine-source].

| Frozen control | Runtime mapping | Evidence status |
|---|---|---|
| greedy/temperature 0 |temperature 0.0|SOURCE-SUPPORTED; INFRASTRUCTURE-UNVERIFIED |
| top_p1, top_k disabled |top_p1.0, top_k0|Same |
| repetition 1, frequency 0, presence 0 |corresponding 1.0/0.0/0.0 penalties|Same |
| seed 0 |seed 0|Source-supported; repeated inference unverified |
| no text stops |stop[]|Source-supported; unverified |
| max generation 2048 |max_tokens2048, min_tokens0|Source-supported; actual limit behavior unverified |
| one completion |n 1|Source-supported; unverified |
| retries 0 |single orchestrator request, no retry handler|Static design; unverified |
| no shifting/clipping/truncation |fixed prompt; full capture; truncationNone; overflow rejection|Static design; unverified |

All 15 controls and exact types are mapped. Additional explicit settings: stop IDs 154820/154827/154829, ignore_eosFalse, detokenizeFalse, skip_special_tokensFalse, min_p0, no structured/logit-bias/allowed-token/bad-word/repetition-detection processor. Do not mask padded IDs to improve output; fail closed on unmapped emitted IDs without altering logits. [Sampling source][sampling-source]. No authenticated deployment certificate/profile was issued.

Isolation design: non-root read-only runtime/OS image, network namespace/egress denied, offline flags and Hub kernels disabled; allow only authenticated read-only model/runtime, one immutable token input, scoped output and fresh tmpfs. No candidate/product/benchmark/home/history/credential mounts, no external tools/retrieval/parser callbacks, one fresh sequence and process/base boundaries, no prefix cache or previous adapter state. OS/driver/package reads belong to an explicit runtime allowlist. These conditions require independent negative probes/traces; environment flags alone are not certification. [Lifecycle isolation](original_base_lifecycle.json).

## 15. Resource regime

All figures are descriptive/source arithmetic or planning starting points, **not measured bounds or hardware admission**. Sparse active parameters do not reduce full expert residency.

| Item | Estimate |
|---|---|
| Original disk |62,444,175,504 bytes =58.156 GiB, including original MTP |
| Main execution payload |59,886,793,728 bytes =55.774 GiB, including FP32 correction buffers |
| Original unused MTP payload |2,556,189,440 bytes, retained in authenticated original storage |
| Persistent compressed KV 32768, one sequence |47×32768×(512+64)×2 =1,774,190,592 bytes =1.652 GiB |
| Expanded K/V equivalent |47×32768×20×(256+256)×2 =31,541,166,080 bytes =29.375 GiB; transient/alternative representation, not automatically added to compressed cache |
| BF16 serving planning subtotal |55.774+1.652+3–10 GiB workspace =60.426–67.426 GiB; prefill/absorption/kernel/allocator peaks can exceed it |
| Attention adapter |42,063,872 bytes BF16 or 84,127,744 FP32 |
| Combined adapter |862,050,304 bytes BF16 or 1,724,100,608 FP32 |
| Attention base+trainable working state |55.774 GiB+21,031,936×16 bytes =56.087 GiB before activations/workspace |
| Combined base+trainable working state |55.774 GiB+431,025,152×16 bytes =62.197 GiB before activations/effective stacks/workspace |
| Host RAM planning |128–192 GiB; original 62.443 GB payload + main 59.887 GB + packing/merge/serializer temporaries; full copies may exceed this |
| One-layer expert packing/effective-stack payload |1,207,959,552 bytes =1.125 GiB |
| All 46 materialized effective expert stacks |55,566,139,392 bytes =51.75 GiB if retained; not a trivial rank-only adapter overhead |
| Original+one main export |122,330,969,232 bytes≈122.331 GB |
| Original+main export+atomic second main temporary |182,217,762,960 bytes≈182.218 GB;200–260 GB free disk planning starting point |

The 16-byte trainable-state formula is BF16 weights 2+gradients 2+FP32 master 4+Adam moments 8, or FP32 weights 4+gradients 4+moments 8 without duplicated masters. PEFT actual dtype/optimizer governs costs.

`ParamWrapper`'s single-adapter `baddbmm` path avoids a separate full delta tensor but still creates effective expert weights; autograd may retain them across layers. Whole-layer checkpointing/sharding and empirical peak measurements are essential for combined scope. Training sequence length, loss/logit implementation, microbatch and recipe are not selected here. MLA compression does not eliminate expanded/transient attention workspace. [Parameter implementation][peft-layer], [resource estimates](resource_estimates.json).

Later starting points: investigate one 80 GiB-class device for serving and checkpointed attention-only adaptation, or two devices if measured workspace requires it. Combined expert training warrants investigating multi-GPU/sharded checkpointing; no device count is verified or excluded arbitrarily. Each fresh cycle authenticates original bodies and reloads/repacks pristine state; reset/save/reload/merge timings remain unmeasured. No GPU spending is authorized.

## 16. Infrastructure test matrix

[infrastructure_test_matrix.csv](infrastructure_test_matrix.csv) contains **24 items A–X, all NOT_RUN**:

| IDs | Later checks |
|---|---|
| A–D |48-body identity/layout discrepancy, fresh load/repack,32768 load, exact prompt/token parity |
| E–K |Full suffix, thinking boundary, EOS/tool stops, natural termination, controls, forced 2048 cap, raw bytes/unknown IDs |
| L–O |Same/fresh-process greedy repetition, isolation, resource peaks/timing |
| P–Q |Exact-scope MLA and conditional expert forward/backward |
| R–U |Adapter save/destroy/reload, direct serve or merge/export, second ORIGINAL cycle, contamination/reset |
| V–X |MLA rope/cache/absorption parity, runnable dependency/parser lock, inverse export/exact MTP exclusions |

Every row specifies procedure and acceptance records. Tokenizer fixture checks are not counted as executed model infrastructure checks.

## 17. Remaining blockers

No static blocker eliminates the selected full-stream/default-thinking transport or attention fresh-original mechanism. Actual study execution remains blocked on body integrity/layout/size reconciliation; pristine loading/exclusion coverage; runnable software/container identity; exact input/full-output/control/native-event parity; cap accounting; parser environment; isolation; repeated greedy behavior; resource peaks; backward and adapter save/destroy/reload; inverse expert export/merge and a second pristine-original cycle.

Expert scope is conditional on the exact eager ParamWrapper restrictions, actual gradient/restoration behavior and sufficient memory. Direct adapter serving is **unresolved**, not silently certified from `SupportsLoRA`. Merge/export supplies a credible static alternative; it must still pass numerical/loader/output tests. The generic non-thinking profile's independent study admissibility is unresolved and unnecessary for the selected default path.

Reasoning may lead to format/evaluator failures under full retention; there is no static promise of code-only output. Such failures cannot authorize mode changes, extraction, retries, clipping or an increased reserve.

## 18. Fallback decision

**Fallback triggered: No.** A usable full-stream native profile and credible MLA fresh-original path are statically established. The stipulated condition for the next distinct DeepSeek-Coder-V2-Lite-Instruct BF16 full preflight is therefore not met. No fallback was acquired, evaluated or executed. Direct expert-serving uncertainty is not silently converted into a new-original substitution.

## 19. Protocol modified?

**No.** Draft2/Draft3, `current-repo-v1-draft3`, SYSTEM, canonical P/K/H budgets 4096/12288/4096, BC lane ownership, context 32768, reserve 2048, full completion contract and existing failure taxonomy remain unchanged. Thinking defaults are retained; no suppression/final-only/alternate effort/retry/clipping/projection is introduced. The runtime proposal is not a protocol amendment or authenticated run profile.

## 20. Files created/modified

New dedicated directory: **`experiments/model_preflight/glm47_flash/`**.

- All required artifacts: `REPORT.md`, `source_manifest.json`, `artifact_manifest.json`, `identity.json`, `serialization.json`, `capacity_checks.json`, `mla_map.json`, `expert_map.json`, `adaptation_targets.json`, `original_base_lifecycle.json`, `runtime_profile.json`, `resource_estimates.json`, `infrastructure_test_matrix.csv`, `validation.json`.
- Additional `weight_layout_catalog.json`, `tokenizer_environment.json`, `baseline_integrity.json`, acquisition/tokenizer/build/validation scripts.
- Small pinned public source/config/index/document snapshots plus exact tokenizer JSON;51 synthetic **input** fixtures. Existing dependency files are referenced by hash and read-only reused, not copied or modified.

The artifact manifest inventories every file with size/SHA256, excluding itself to avoid circular hashing. Validation is written before final manifest hashing, then hashes are recomputed/asserted. **939 allowed pre-existing policy/historical/landscape/Devstral files** are covered by the preservation baseline, without protected task/outcome inspection. [Validation](validation.json).

Final unchanged HEAD: **`7fcdecbe26f4fd01138edf8f58c02ce4b947db0b`**. Worktree status: **`?? experiments/model_preflight/`**, present before this step; no tracked/staged diff or commit.

## 21. Comparison with 1G1E classification

Identity, SHA, architecture,47-layer/2048-hidden topology,202752 context,48 shards,62.444 GB declared bytes and all LFS declarations match 1G1E. The standalone-LICENSE wording is corrected; the model's MIT declaration remains. New refinements include unused original MTP 212 entries, the incorrect index byte-size field, actual tokenizer 154856 versus model 154880, and exact native terminals/think prefix.

1G1E inference was **UNCERTAIN—PREFLIGHT REQUIRED** because non-thinking-input permission/full suffix was unresolved. This audit establishes **source-supported default-thinking full-suffix compatibility**, with no non-thinking exemption. Its adaptation PASS is refined into **attention-only source-supported** and **conditional stacked-parameter expert adaptation**, with explicit serving/export limitations. The result is a recommendation for later infrastructure verification, not roster admission or an update to the landscape files.

## 22. Claim limitations

Source support does not establish installation, model load, backward, deterministic generation, compliant replacements, expert coverage, isolation or measured resource feasibility. Public dtype/shape/count inference is not body verification. Native template choice is not authorization to change effort. Full-stream preservation is not final-answer extraction. Greedy/seed 0 is not a repeatability certificate. No relative model quality, adaptation gains, coding-performance prediction, MLA superiority, benchmark preference or product-adaptation demonstration is claimed.

## 23. Final recommendation

Record **PROCEED TO INFRASTRUCTURE VERIFICATION** for the exact pinned GLM original. Select native default thinking and retain the entire emitted suffix; full-stream compatibility is statically established as contract-preserving transport. MLA attention adaptation is source-supported; routed-expert parameter adaptation is conditionally credible with eager wrappers and merge/export. Synthetic maximum **20,427+2048=22,475** fits unchanged 32768. All 24 infrastructure tests remain **NOT_RUN**. Fallback:no; protocol changed:no; inference:no; protected candidates:no; commit:no.

**STOP after this report.** No Devstral/GLM infrastructure work, DeepSeek fallback, Nemotron, GPU spending or roster freeze begins.

[card]: https://huggingface.co/zai-org/GLM-4.7-Flash/blob/7dd20894a642a0aa287e9827cb1a1f7f91386b67/README.md
[config]: https://huggingface.co/zai-org/GLM-4.7-Flash/blob/7dd20894a642a0aa287e9827cb1a1f7f91386b67/config.json
[index]: https://huggingface.co/zai-org/GLM-4.7-Flash/blob/7dd20894a642a0aa287e9827cb1a1f7f91386b67/model.safetensors.index.json
[generation]: https://huggingface.co/zai-org/GLM-4.7-Flash/blob/7dd20894a642a0aa287e9827cb1a1f7f91386b67/generation_config.json
[tokenizer]: https://huggingface.co/zai-org/GLM-4.7-Flash/blob/7dd20894a642a0aa287e9827cb1a1f7f91386b67/tokenizer.json
[tokenizer-config]: https://huggingface.co/zai-org/GLM-4.7-Flash/blob/7dd20894a642a0aa287e9827cb1a1f7f91386b67/tokenizer_config.json
[template]: https://huggingface.co/zai-org/GLM-4.7-Flash/blob/7dd20894a642a0aa287e9827cb1a1f7f91386b67/chat_template.jinja
[glm-source]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/models/glm4_moe_lite/modeling_glm4_moe_lite.py
[glm-config]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/models/glm4_moe_lite/configuration_glm4_moe_lite.py
[template-source]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/utils/chat_template_utils.py
[conversion-source]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/conversion_mapping.py
[load-source]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/core_model_loading.py
[modeling-utils]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/modeling_utils.py
[experts-dispatch]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/integrations/moe.py
[peft-config]: https://github.com/huggingface/peft/blob/532a05dd505c28993119b7715ee286f4234bf51b/src/peft/tuners/lora/config.py
[peft-layer]: https://github.com/huggingface/peft/blob/532a05dd505c28993119b7715ee286f4234bf51b/src/peft/tuners/lora/layer.py
[peft-model]: https://github.com/huggingface/peft/blob/532a05dd505c28993119b7715ee286f4234bf51b/src/peft/peft_model.py
[serving-source]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/model_executor/models/glm4_moe_lite.py
[mtp-source]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/model_executor/models/glm4_moe_lite_mtp.py
[deepseek-source]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/model_executor/models/deepseek_v2.py
[mla-runtime]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/model_executor/layers/mla.py
[registry]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/model_executor/models/registry.py
[requirements]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/requirements/common.txt
[cuda-requirements]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/requirements/cuda.txt
[docker]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/docker/Dockerfile
[sampling-source]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/sampling_params.py
[stop-source]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/v1/core/sched/utils.py
[engine-source]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/engine/arg_utils.py
[llm-source]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/entrypoints/llm.py
