# STEP 8K-B.1G1E-D1 — Devstral Small 2 full static preflight

## 1. Verdict

**PROCEED TO INFRASTRUCTURE VERIFICATION**

Exact subject: **`mistralai/Devstral-Small-2-24B-Instruct-2512`**, immutable revision **`55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128`**. This verdict means a credible static route exists from this original FP8 artifact to an authenticated BF16 representation, ordinary dense LoRA targets, adapter save/reload, and serving or merge/export. It does **not** mean that reconstruction, training, serving, numerical parity, isolation, resource sufficiency or deterministic inference has been demonstrated. Every infrastructure matrix item remains **NOT_RUN**. This report authorizes neither execution nor spending.

The main route is original FP8 shards → official explicit dequantization into ordinary BF16 layers → fresh adapter → save → destroy state → reconstruct the same original again → reload adapter → evaluation. A dense export must explicitly use `save_original_format=False`; the default reverse conversion can re-quantize. A recorded checkpoint-key mapping and attention-scaling configuration alias are required. See sections 11–15 and [reconstruction_analysis.json](reconstruction_analysis.json).

## 2. Scope and prohibitions

This work used the existing 1G1E landscape records, permitted historical static preflights, Draft2/Draft3 policy artifacts, exact-revision public model metadata/configuration/index/tokenizer/template files, and pinned official implementation source. It did not inspect protected tasks, the 31-candidate inventory, benchmark outcomes or private evaluators. No coding-quality comparisons or benchmark scores were used for the verdict.

No model weights or safetensors headers were downloaded. No model or adapter was instantiated; no inference, model completion, GPU use, training recipe, serving recipe, experimental A/B/M/C/BC run or Study1/2/3 run occurred. The only executable checks were source/metadata processing, canonical synthetic input packing, exact tokenizer encoding and the immutable Jinja template compiler. Its availability check was supplied by installed Jinja metadata; its rendering logic was unchanged. No upstream model/source module was imported or executed. `torch`, `transformers` and `peft` were not imported by the tokenizer check.

The two exact vocabulary JSON files are approximately 17 MB each, larger than ordinary metadata but needed for exact tokenization. Four bounded, hash-authenticated tokenizer/template dependency wheels were acquired and extracted locally; these contain tokenizer/template software, not model weights. All acquired artifacts and sizes are disclosed in [source_manifest.json](source_manifest.json). Most other downloads were bounded to 2 MB. Unavailable/size-limited discovery records remain visible and are not capability evidence.

No final model roster was frozen. No fallback, GLM or Nemotron work was started. Historical preflights, `landscape_closure`, product repositories and policy files were not edited. No commit was made.

## 3. Exact checkpoint identity

The fresh exact-revision Hub response independently confirms the repository and revision above; created **2025-11-28T11:27:11.000Z**, modified **2026-07-15T12:20:36.000Z**, public and ungated. These timestamps are repository metadata, not a release-date assertion. Root model type is `mistral3`, architecture `REDACTED_SECRET`; the text submodel type is `ministral3`. [Exact Hub metadata](https://huggingface.co/api/models/mistralai/Devstral-Small-2-24B-Instruct-2512/revision/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128?blobs=true), [pinned config][config].

Selected packaging is exactly six `model-00001-of-00006.safetensors` through `model-00006-of-00006.safetensors` bodies, declared total **25,793,059,408 bytes**. The alternate two consolidated bodies total **25,793,035,888 bytes** and are not added to the selected total. The HF index contains **1,145 tensor entries**, declared payload **25,792,912,480 bytes**, and declared `total_parameters=24,011,361,840`. Public per-shard LFS identities, sizes and blob IDs are in [identity.json](identity.json); no bodies were fetched. [Pinned index][index].

Independent source/config arithmetic resolves **24,011,361,280 non-scale model parameters**, plus **560 inferred scalar scale elements**. Actual body dtype, shape, scalar layout, scale values and finiteness remain unverified. Agreement with index totals is an arithmetic consistency check, not safetensors inspection.

Comparison against 1G1E finds **no discrepancy** in repository, revision, creation/modification metadata, architecture/model type, layer count, hidden dimension, native config context, selected six shards, byte count, LFS identities or FP8 configuration. The landscape's root terminal summary `bos=null/eos=null` reflects absence from root config; this audit refines it using generation/tokenizer files to BOS **1**, EOS **2**, PAD **11**. The existing 256k-card/393216-config distinction remains. None of the old artifacts was rewritten. [Landscape input](../landscape_closure/landscape.csv), [generation config][generation].

## 4. License/product eligibility

The exact authoritative model card and Hub card metadata declare **Apache-2.0**; the repository listing has no standalone `LICENSE`. The card describes an agentic model for software engineering, codebase exploration and multi-file editing. This supports the existing static product-use eligibility gate; the license declaration is not a measured product capability or quality result. Apache license/attribution/NOTICE requirements still apply to eventual redistribution. This audit does not reinterpret the absent standalone license as a restrictive replacement license. [Exact model card][card], [Apache-2.0 text](https://www.apache.org/licenses/LICENSE-2.0).

## 5. Architecture/topology

The text network is dense: **40 layers**, hidden **5120**, intermediate **32768**, **32 query heads / 8 KV heads**, head dimension **128**. Q output is 4096; K/V output is 1024; O maps 4096→5120. All four attention projections and all three SiLU-gated MLP projections are separate bias-free `nn.Linear` modules. Attention dropout is zero and sliding window is null. There are two RMSNorm weights per text layer, a final RMSNorm, 131072×5120 embeddings and an untied head of the same shape. This is ordinary dense attention/MLP adaptation, not MoE expert adaptation. [Pinned config][config], [Ministral3 implementation][text-source].

The original also contains a Pixtral vision tower: **24 layers**, hidden1024, intermediate4096, 16 heads, head64, patch14, image1540, 3 channels; and a norm/patch-merger/two-linear multimodal projector with spatial merge2 and GELU activation. These remain part of the authenticated original/reconstructed artifact, are frozen, and receive no image/pixel inputs. They are excluded from both adaptation scopes. Text-only operation is supported by the model's optional-image forward path; this is not a claim that modality tensors have been deleted. [Mistral3 implementation][wrapper-source], [Pixtral implementation][vision-source].

Inferred subtotals: text **23,572,403,200**, vision **403,305,472**, projector **35,652,608**, sum **24,011,361,280**. The complete 585-weight catalog matches all `.weight` entries in the index. Shapes are inferred from exact config and constructors. [adaptation_targets.json](adaptation_targets.json).

Text native `max_position_embeddings=393216`, YaRN factor48/original8192, with Llama4 attention scaling beta0.1. The card advertises 256k and generation config `max_length=262144`. Neither is substituted for the deployed **32,768 total tokens** and **2,048-token reserve**. The huge tokenizer `model_max_length` sentinel is not an independent capacity claim. [Config][config], [params][params], [tokenizer config][tokenizer-config].

## 6. Tokenizer/template/serialization

Exact pinned `tokenizer.json`, `tekken.json` v13, `tokenizer_config.json` and `chat_template.jinja` were acquired and hashed. The backend is `TokenizersBackend` / tokenizers **0.23.2**: regex splitting followed by ByteLevel BPE; **normalizer null**, no BPE dropout, vocabulary **131072**, with **1000 added special tokens**. All 256 byte-alphabet symbols exist. Native special IDs include UNK0, BOS1, EOS2, INST3, closing INST4, tool framing5–9, image10, PAD11, image break/end12–13, and system framing17–18. All exact special token definitions/attributes are retained in [serialization.json](serialization.json). [Pinned tokenizer][tokenizer], [Tekken][tekken], [tokenizer config][tokenizer-config].

The canonical two-turn path renders:

```text
<s>[SYSTEM_PROMPT]{unchanged Draft3 SYSTEM}[/SYSTEM_PROMPT][INST]{unchanged user(P,K,H)}[/INST]
```

The template inserts BOS exactly once; raw backend encoding uses `add_special_tokens=False`, no padding/truncation. There is **no appended assistant prefix**: the last prompt marker is `[/INST]`. `add_generation_prompt=True/False` renders identically in the checked path. Assistant text in the sanity fixture uses the native assistant content plus EOS. The default Mistral Vibe system message is injected only if a supplied system turn is absent; Draft3 always supplies its exact system turn, so that default does not enter study input. No date function or reasoning/thinking channel is inserted on this path. [Pinned template][template], [official immutable Jinja compiler][template-source].

Tools and documents are `None`, all content is plain text, no processor/image arguments are supplied. Tool markers, FIM markers and modality markers remain native vocabulary tokens; none is treated as a tool execution request or special output projection. Literal native marker strings in admitted text can encode as special tokens: preserve the exact canonical input, and never discover policy machine structure by searching content delimiters.

## 7. Draft3 completion-contract compatibility

There is a credible **full-stream** text path. The template does not require final-only extraction, alternate effort settings, reasoning suppression, retries or projection. Any reasoning, tool-looking content or modality marker emitted later remains in the stream and is subject to the unchanged strict output contract. Static serialization does not establish that the model will produce a valid completion.

Collect all output token IDs including an observed EOS, actual generated count, finish reason, stop reason, raw bytes and normalization/removal receipts. Permit only removal of **one verified final EOS ID2**, then existing CR/LF normalization. PAD11, internal EOS, tool markers and other special tokens are not blanket-stripped. No clipping is allowed. ByteLevel vocabulary inversion plus literal added-token bytes provides a lossless byte transport; a string-only decoder that replaces invalid UTF-8 cannot alone prove raw-byte retention. Lossless **input** byte round-trips were checked on all 51 fixtures. Output transport and invalid-byte handling remain infrastructure tests. [Policy protocol](../../../harness/context_policy/protocol.py), [serialization.json](serialization.json).

The **2048 cap includes any terminal token**. vLLM's pinned stop code tests EOS before length; an EOS at position2048 may therefore report `stop`. The study must independently classify actual count≥2048 as `output_capacity_failure`, retain the stream and avoid a retry. A stop label never overrides the frozen cap. Natural termination before cap must be tested separately. [Pinned stop implementation][stop-source].

No authenticated official runtime profile was created: the current policy validator requires independently authenticated verified controls. [runtime_profile.json](runtime_profile.json) is a source-supported proposal, intentionally not a certificate claiming those checks have passed.

## 8. Static capacity accounting

The existing Qwen fixture methodology was reproduced with the canonical `messages`, `pack_h`, record framing and canonical JSON helpers. Synthetic P/K/H maxima remain **4096/12288/4096 UTF-8 bytes**; BC lane ownership remains≤2048 each. Four patterns (ASCII, Unicode, combining-character NFC expansion stress, code/delimiters), two boundaries (maximum and maximum−1) and five input forms yield40 capacity fixtures; five empty registries add5. Six framing/template sanity fixtures bring the total to51. These are input serialization/tokenization fixtures, not experimental A/B/M/C/BC runs. No protected tasks were used.

Every encoding was repeated four times with equality assertions. **Maximum observed input:20,454 tokens. Maximum input+reserve:22,502. Violations:0.** Exact rows, input/token hashes and fixture content are saved in [capacity_checks.json](capacity_checks.json) and `synthetic/`.

The fixed rendered UTF-8 overhead is630 bytes. Complete byte alphabet + no normalization + no prefix insertion in the ByteLevel pretokenizer + merge-only BPE supports a conservative source-inferred bound of **630+20480+2048=23,158** tokens including reserve. This supplements sampled fixtures; it is not a measured deployed-context certificate. Literal specials reduce token counts relative to their bytes. No NFC tokenizer expansion occurs; the Unicode stress family is retained for comparability.

Local checks ran on **CPython3.12.14 / Windows**, tokenizers0.23.2, Jinja3.1.6, MarkupSafe3.0.4 and packaging26.3. Only policy packing/framing helpers ran; the official parser's **CPython3.11.9 / Unicode14.0.0** environment must still be used and certified later. [tokenizer_environment.json](tokenizer_environment.json).

## 9. Runtime/control mapping

Proposed self-hosted stack: **vLLM0.30.0**, commit **`ced6857afa0ea7b2e3f0846a62e1394e90f15607`**, offline V1 `LLM`, CPython**3.11.9**, PyTorch**2.13.0**, Transformers**5.19.0.dev0** at **`02d8fb9784e8f14a1251e4c992cd82a5762417c6`**, PEFT**0.21.3.dev0** at **`532a05dd505c28993119b7715ee286f4234bf51b`**, tokenizers**0.23.2**, Jinja**3.1.6**. Ancillary proposed pins are in the runtime JSON. The pinned Dockerfile's CUDA **13.0.3** is a later Linux/x86_64 build assumption, not a tested driver/container identity. [vLLM requirements][requirements], [CUDA requirements][cuda-requirements], [Dockerfile][docker].

The first acquired vLLM development snapshot is explicitly rejected for this stack because its Transformers bound `<5.18` conflicts with the chosen5.19 source. Released0.30.0 requires Transformers≥5.10.4 and tokenizers≥0.21.1, which admit the proposed versions. A complete resolved lock, optional media dependency compatibility, wheel hashes, kernels, driver and container digest remain **unestablished**. Source requirement compatibility is not installation certification.

The primary inference base is the **same authenticated pristine BF16 reconstruction** used for adaptation. Do not compare native-FP8 pristine execution against BF16 adaptation as if representation were unchanged. Engine proposal: `max_model_len=32768`, BF16, no quantization, TP1, one sequence, seed0, eager execution, prefix caching disabled, `generation_config="vllm"`, tokenizer initialization skipped, image limit0, remote code disabled, no speculative configuration. Supply precomputed `prompt_token_ids` directly; no chat endpoint or server template injection. [Engine arguments][engine-source], [offline entrypoint][llm-source].

| Frozen control | Exact runtime mapping | Status |
|---|---|---|
| greedy / temperature0 | `temperature=0.0` | Source-supported; infrastructure-unverified |
| top_p1 | `top_p=1.0` | Source-supported; infrastructure-unverified |
| disabled top_k | `top_k=0` (greedy code also resets to0) | Source-supported; infrastructure-unverified |
| repetition1 / frequency0 / presence0 | corresponding penalty arguments1.0/0.0/0.0 | Source-supported; infrastructure-unverified |
| seed0 | `seed=0` | Source-supported; determinism unverified |
| no text stops | `stop=[]` | Source-supported; infrastructure-unverified |
| max generation2048 | `max_tokens=2048`, `min_tokens=0` | Source-supported; actual cap unverified |
| one completion | `n=1` | Source-supported; infrastructure-unverified |
| retries0 | one orchestrator request, no retry handler | Static transport design; unverified |
| no shifting/clipping/truncation | one fixed token sequence, retain all output, truncation unset, overflow fails | Static transport design; unverified |

Explicit EOS2/`ignore_eos=False`, `detokenize=False`, `skip_special_tokens=False`, `min_p=0`, no logit bias, allowed-token restriction, bad words, structured decoding or repetition detector prevent hidden defaults. The frozen policy's15 controls are all mapped with argument types in [runtime_profile.json](runtime_profile.json). [Sampling source][sampling-source].

The serving config must carry the authenticated legacy alias `text_config.llama_4_scaling={original_max_position_embeddings:8192,beta:0.1}` from original `params.json` and `rope_parameters`. Transformers applies this scale through `rope_parameters`; the pinned vLLM Mistral attention reads the legacy field. Preserve the original values and record the derived config hash; test logits/attention parity at positions above8192. This is an explicit configuration translation, not an unrecorded change to model constants. [Ministral3 attention][text-source], [vLLM Mistral attention][mistral-source], [original params][params].

## 10. Native FP8 representation

Root `dtype=bfloat16` does not mean the stored original is BF16. Exact quantization metadata declares `quant_method=fp8`, **static** activation scheme, `dequantize=False`, **`weight_block_size=null`**, excluding vision tower, multimodal projector and LM head. `params.json` declares **`fp8_e4m3`** weight format and per-tensor activation scheme. [Config][config], [params][params].

Each of the280 text projection weights has `weight_scale_inv` and `activation_scale` entries. Inferred quantized projection parameters total **22,229,811,200**. Remaining non-scale parameters total **1,781,550,080**. The equation

```text
22,229,811,200×1 + 1,781,550,080×2 + 560×2 = 25,792,912,480 bytes
```

matches the index payload exactly. This supports FP8 text matrices/BF16 remainder/BF16 scalar scales as a **source-and-arithmetic inference**. Bodies are still needed to confirm the particular dtype variants and layouts. Null block size must not be silently replaced by128×128. [Index][index].

The independently inspected **`FineGrainedFP8HfQuantizer.is_trainable` returns False**. Direct native-FP8 PEFT training is **UNSUPPORTED for this inspected intended path**; do not bypass the flag or infer backward support from generic LoRA claims. [Pinned quantizer][quantizer-source].

## 11. Same-original reconstruction/dequantization analysis

The official config accepts `activation_scheme="static"` and null block size. Loading attributes can explicitly request `dequantize=True`. For prequantized originals, the quantizer creates/augments `Fp8Dequantize` conversions. `replace_with_fp8_linear` leaves ordinary layers in place on this route. Conversion promotes FP8 weights and their stored scales toFP32, derives the grid from scale shape (scalar/one-element fallback1×1), multiplies, then casts to the destination parameter dtypeBF16. `activation_scale` is consumed; reconstructed inference uses dense BF16 computation rather than original activation quantization. Unscaled norms/embeddings/head/vision/projector pass through. [Quantization config][quant-config-source], [quantizer][quantizer-source], [conversion implementation][fp8-source].

Official postprocessing **removes `hf_quantizer`, `quantization_config`, `quantization_method` and sets `is_quantized=False`** after prequantized dequantized load. This supplies an ordinary trainable representation without an ad hoc flag bypass. The absence of these flags must be verified before adaptation and export. [Quantizer base postprocessing][quantizer-base].

Old checkpoint keys differ from current module names. The declared source-supported `key_mapping` is:

```text
^language_model\.model\.  -> model.language_model.
^language_model\.lm_head\. -> lm_head.
^vision_tower\.           -> model.vision_tower.
^multi_modal_projector\.  -> model.multi_modal_projector.
```

Static mapping covers all1145 entries bijectively and all585 weight names match the constructor-derived catalog. Mapping retains projection scale pairing. The current automatic `mistral3`→`llava` rename logic does not alone establish that these older checkpoint prefixes will load correctly; the explicit mapping is part of the reconstruction recipe. Actual loader completeness must reject any missing, unexpected, mismatched or newly initialized weights. [Model loading/key_mapping][modeling-utils], [conversion mappings][mapping-source], [target catalog](adaptation_targets.json).

| Central question | Answer and evidence level |
|---|---|
| 1. Directly train exact FP8 original? | **UNSUPPORTED** by inspected FP8 quantizer (`is_trainable=False`). |
| 2. Reconstruct a trainable base? | **SOURCE-CODE INFERENCE:** official explicit dequantized BF16 path exists for the declared per-tensor representation. |
| 3. Preserve same-original relationship? | **SOURCE-CODE INFERENCE:** every value derives from exact original bodies/scales; no substitute checkpoint. |
| 4. Official conversion? | **DOCUMENTED / source-visible:** FineGrainedFP8Config→quantizer conversions→Fp8Dequantize→quantizer-base cleanup. |
| 5. Deterministic? | **EMPIRICALLY UNVERIFIED:** no RNG/calibration in mapping; pin software/CPU/dtype/thread settings and compare independent tensor roots. |
| 6. Transformed tensors? | **SOURCE-CODE INFERENCE:**280 projection matrices;560 scales consumed;305 other weights retained. Actual layouts unverified. |
| 7. Regeneration/calibration/approximation/requantization? | No new initialization or calibration required. Existing FP8 precision loss is irreversible; BF16 output includes declared rounding. Requantization must be prevented by explicit export option. |
| 8. Hash/manifest every cycle? | **SOURCE-CODE INFERENCE:** feasible per-tensor and original/software/recipe manifest chain; dense tensor hashes not yet obtained. |
| 9. Expansion? | **SOURCE-CODE INFERENCE:**25.793 GB original→48.023 GB dense BF16 payload; memory/storage estimates in section17. |
| 10. Fresh reconstruction each cycle? | **EMPIRICALLY UNVERIFIED:** repeat source-supported path from original only; repetition/peaks/timing must pass later. |

**Statically established means a credible official-code route, not a verified reconstruction lifecycle.** It reconstructs a dense representation of the **stored quantized original**. It does not recover a lost prequantization BF16 release, nor guarantee equality with native FP8 kernel computation. The effective scale semantics and actual tensors must be validated from authorized original bodies later.

`Fp8Dequantize.reverse_op` returns `Fp8Quantize`. Thus dense and merged exports must explicitly use **`save_original_format=False`** with safe serialization, full tensor coverage, no scales/quantization metadata and BF16 body verification. Preserve original config/tokenizer bytes separately from authenticated derived export config. [FP8 reverse operation][fp8-source], [save_pretrained][modeling-utils].

## 12. Adaptation target map

Current Transformers module prefix is `model.language_model.layers.{0..39}`; raw checkpoint prefix is `language_model.model.layers.{0..39}`. Full anchored patterns prevent accidental vision adaptation:

```text
ATTENTION-ONLY:
^model\.language_model\.layers\.(?:[0-9]|[1-3][0-9])\.self_attn\.(?:q_proj|k_proj|v_proj|o_proj)$

ATTENTION + MLP:
^model\.language_model\.layers\.(?:[0-9]|[1-3][0-9])\.(?:self_attn\.(?:q_proj|k_proj|v_proj|o_proj)|mlp\.(?:gate_proj|up_proj|down_proj))$
```

| Projection | Weight shape (out,in) | LoRA rank16 A / B shapes |
|---|---|---|
| q_proj | (4096,5120) | (16,5120)/(4096,16) |
| k_proj, v_proj | (1024,5120) each | (16,5120)/(1024,16) |
| o_proj | (5120,4096) | (16,4096)/(5120,16) |
| gate_proj, up_proj | (32768,5120) each | (16,5120)/(32768,16) |
| down_proj | (5120,32768) | (16,32768)/(5120,16) |

| Scope | Modules/base tensors | Adapter A/B tensors | Rank16 trainables | BF16 payload | FP32 payload |
|---|---:|---:|---:|---:|---:|
| Attention-only |160|320|19,660,800|39,321,600 bytes (37.5 MiB)|78,643,200 bytes (75 MiB)|
| Attention+MLP |280|560|92,405,760|184,811,520 bytes (176.25 MiB)|369,623,040 bytes (352.5 MiB)|

Formula is `r×(in+out)` per projection, summed over40 layers. The extra MLP scope contributes72,744,960 parameters. All names, shapes and counts are expanded in [adaptation_targets.json](adaptation_targets.json). No adapters were instantiated.

Deliberate exclusions: embeddings/vocabulary unchanged; untied head and text norms frozen because requested scopes cover projection adaptation; entire vision/projector frozen because invocation is text-only. These exclusions are scope choices, not claims that standard dense heads or vision linears are inherently unsupported. Bias none, no `modules_to_save`, no automatic embedding save. Rank16 is an estimate/scoping proposal; alpha, dropout, loss/data, optimizer hyperparameters and schedule were not selected. [Text constructors][text-source], [PEFT LoRA implementation][lora-source].

## 13. PEFT/backward support

Pinned PEFT source dispatches ordinary `nn.Linear` to LoRA Linear, inserts A/B matrices, freezes base parameters, computes the base forward plus scaled `B(A(dropout(x)))`, and supports safe adapter serialization/reload. This gives a **source-supported** standard-autograd route after explicit dequantization, with no native-FP8 backward claim. Generic causal-LM PEFT wrapping of the multimodal conditional model's text `input_ids`/`labels` forward remains subject to actual integration tests. [LoRA layer][lora-source], [LoRA model][lora-model], [PEFT wrapper/save/reload][peft-model], [Mistral3 text forward][wrapper-source].

Frozen base parameters do not mean the entire network can run under `no_grad` during training: gradients must pass through subsequent frozen layers to earlier adapters. Verify `requires_grad` names, finite nonzero adapter gradients and unchanged base tensor hashes. Training should disable inference KV caching and use a separately authorized checkpointing/backend recipe; this audit executes none. Gradient checkpointing is declared in model source, but successful backward and memory behavior are **GPU-unverified**.

BF16 base plus FP32 adapter arithmetic/optimizer state is a plausible mixed-precision route. PEFT's default `autocast_adapter_dtype=True` may promote BF16/FP16 adapters toFP32. Consequently BF16 adapter payload estimates are conditional, not guaranteed actual save sizes. Optimizer/master/gradient assumptions must be recorded, and optimizers may only own declared adapter parameters. Numerical finiteness, actual gradient flow, kernel compatibility, trainable counts and optimizer reset are testsO/P/T. [PEFT dtype behavior][peft-model], [dtype/utility implementation][peft-other].

## 14. Fresh original-base lifecycle

Each fresh cycle starts from the six authenticated immutable original bodies, in a new destination/process. Reconstruct and validate the canonical pristine tensor root; create a fresh training model, adapter, optimizer, scheduler and RNG initialization. Save only adapter/config/provenance. Destroy the training process/state; reconstruct the **same original again**, verify its pristine root, and reload the adapter for evaluation. Destroy evaluation state afterward. The next cycle repeats from original rather than continuing any adapted state.

Required records include original repository/revision/body/config/index/tokenizer hashes; conversion/source/package/hardware/container identity; exact key mapping, BF16 dtype and attention-scaling alias; sorted reconstructed tensor name/shape/dtype/bytes/hash and manifest root; adapter initialization config/seed/initial tensor root; step-zero optimizer/scheduler; Python/NumPy/Torch CPU/CUDA RNG states; training process termination and GPU/state destruction receipts; saved adapter root and originating cycle; pristine root authenticated **before** application of adapter; and evaluation/merge derivative provenance. [original_base_lifecycle.json](original_base_lifecycle.json).

Type enforcement is fail-closed: only exact `ORIGINAL` artifacts enter reconstruction, and only authenticated `PRISTINE_RECONSTRUCTION` creates a fresh adapter. `ADAPTER` and `MERGED_EVALUATION_DERIVATIVE` are output-only and cannot become adaptation parents. Separate directories/read-only original mounts enforce that lineage; filename, model-name metadata or a claimed `base_model_name_or_path` is insufficient proof. Actual destruction, reset and repeat reconstruction remain NOT_RUN.

## 15. Adapter save/reload/export

Adapter output is **`adapter_model.safetensors` + `adapter_config.json` + external provenance manifest**, with safe serialization and `save_embedding_layers=False`. Record exact target expansion, wrapper prefix/key map, rank/alpha/dropout/bias, actual dtype, tensor hashes, original/reconstruction roots and cycle identity. Reload uses the standard PEFT route onto a fresh authenticated BF16 reconstruction with `is_trainable=False` for evaluation, rejecting key mismatches. [PEFT save/reload][peft-model], [adapter state handling][peft-save].

Pinned vLLM Mistral3 declares `SupportsLoRA`, packed QKV and gate/up mappings and HF→runtime weight-name mapping. A direct adapter serving route is therefore **source-supported but unverified** for these exact saved adapter names/dtypes/rank. It is not assumed merely from architecture similarity. [Serving model][serving-model].

If direct serving does not pass, an independently reloaded adapter may be merged into the full reconstructed BF16 base through `merge_and_unload(safe_merge=True)` and exported as dense sharded safetensors using **`save_original_format=False`**. Safe merge's finite check is not a determinism certificate. BF16 base update and adapter compute dtype produce declared floating-point rounding; direct and merged routes can differ numerically. Freeze and test acceptable numerical/decision parity before relying on the route; never change completion parsing to accommodate differences. Full dense weights are needed for merge/export; no original-weight download/merge happened here. [PEFT merge][lora-model], [LoRA merge arithmetic][lora-source], [dense export][modeling-utils].

Merged exports include all retained original components, tokenizer/template identity and the authenticated configuration alias, but no FP8 quantization metadata or scale tensors. They are labeled evaluation derivatives and blocked as future adaptation bases. A failed direct route does not authorize another original checkpoint or automatic fallback.

## 16. Isolation profile

Later execution design: air-gapped host/namespace with blocked egress/socket probes, Hub/Transformers offline flags, non-root user and a minimal read-only runtime image; mount only authenticated read-only model/runtime assets, one immutable token-input request, scoped output and fresh temporary storage. No project, home, candidate, benchmark, private evaluator, credential, tool, retrieval or history directories are mounted. Necessary OS/driver/package reads belong to the authenticated runtime allowlist; arbitrary host reads are forbidden.

No tool executor/registry, agent framework, retrieval, conversation history, chat/reasoning parser or server template path is active. Emitted tool markers are retained text. One fresh sequence/request, one completion, zero retries, no shifting/truncation and complete byte capture apply. Prefix caching is explicitly disabled. Fresh processes and separate pristine/adapted state boundaries prevent KV/adapter contamination.

This is **static design**, not certification. Later synthetic negative tests must demonstrate denied sockets, files, symlink/reparse escape, tool access, session history and cache sharing; mount/process/read traces and destruction receipts are required. Candidate execution cannot begin on mere offline environment variables. [Lifecycle isolation design](original_base_lifecycle.json), [engine options][engine-source].

## 17. Resource envelope

All figures below are arithmetic or planning estimates, **not measurements**, prices or spending authorization. GB is decimal; GiB/MiB are binary. All full-artifact parameters are counted; vision retention and dense resident parameters are not discounted as “active parameters.”

| Item | Estimate / basis |
|---|---|
| Original disk |25,793,059,408 bytes, approximately24.022 GiB; six selected shards only |
| Reconstructed BF16 disk |24,011,361,280×2 = **48,022,722,560 bytes**, approximately44.724 GiB, plus headers/config/tokenizer |
| Original+one pristine dense payload |73,815,781,968 bytes, approximately73.816 GB |
| 32768-token BF16 KV, one sequence |40×2×8×128×2×32768 = **5,368,709,120 bytes =5 GiB** |
| BF16 serving subtotal |44.724 GiB base+5 GiB KV+2–8 GiB planning workspace = approximately51.724–57.724 GiB; allocator/prefill/logits can add more |
| Attention-only training base+adapter/gradient/optimizer |44.724 GiB base+19,660,800×16 bytes = approximately45.017 GiB, **before activations/workspace** |
| Attention+MLP training base+adapter/gradient/optimizer |44.724 GiB base+92,405,760×16 bytes = approximately46.101 GiB, **before activations/workspace** |
| Host RAM starting envelope |96–128 GiB streaming reconstruction;128–192 GiB load/merge planning; full-copy loaders may exceed these |
| Largest per-matrix conversion intermediates |167,772,160 elements: two FP32 copies plus BF16 destination≈1.5625 GiB; serial conversion assumed |
| Adapter files |37.5/176.25 MiB BF16 or75/352.5 MiB FP32; metadata/headers extra |
| Original+pristine+one merged payload |121,838,504,528 bytes≈121.839 GB |
| Above plus a second dense atomic temporary |169,861,227,088 bytes≈169.861 GB;180–220 GB free-storage planning starting point |
| Fresh reset per reconstruction |Read at least25.793 GB original; write48.023 GB dense; hash all tensors; repeat for fresh train/evaluation as specified; duration unmeasured |

The16-byte trainable-state formula is BF16 weight2+gradient2+FP32 master4+Adam moments8, or FP32 adapter4+gradient4+moments8 without a duplicate master. Actual optimizer and dtype govern costs.

Long-sequence training remains a major empirical constraint. One BF16 hidden tensor per layer at32768×5120 costs12.5 GiB; one32768×32768 BF16 MLP intermediate costs2 GiB; full32768×131072 logits cost8 GiB BF16 or16 GiB FP32. These are sensitivity components, not a complete training peak. Multiple saved tensors, checkpoint recomputation, fused loss, attention implementation and allocator behavior matter. No training sequence length or recipe is selected here. [resource_estimates.json](resource_estimates.json).

A later starting point is one80 GiB-class accelerator for BF16 serving, TP1. For training, investigate one80 GiB-class device with an authorized checkpointed microbatch recipe, and an authenticated two-device sharding route only if necessary. **Neither configuration is verified.** No wall-clock throughput/reset estimate is supplied without measurement.

## 18. Infrastructure test matrix

[infrastructure_test_matrix.csv](infrastructure_test_matrix.csv) has **24 items A–X, all NOT_RUN**:

| IDs | Later verification |
|---|---|
| A–D |Original body acquisition/hash/shape, official reconstruction,32768 load, exact prompt parity |
| E–I |Frozen controls, native terminals, natural stop, forced2048 cap, raw token/byte retention |
| J–N |Same-process/fresh-process greedy repeats, isolation, resource peaks, timing |
| O–P |Attention-only and attention+MLP exact-scope forward/backward |
| Q–T |Adapter save/destroy/reconstruct/reload, direct serve or merge/export, independent reconstruction, contamination reset |
| U–X |Attention-scale/YaRN parity above8192, official parser/full stream, complete dependency/container lock, reset cost/derivative guard |

Each row has a concrete procedure and acceptance record. No infrastructure tests were started. Tokenizer fixture checks are reported separately and are not counted as a passed infrastructure matrix.

## 19. Remaining blockers

There is **no unresolved static blocker eliminating the credible same-original path**. Admission to actual study execution is nevertheless blocked pending original body integrity/layout checks, official reconstruction/load completeness, two independent pristine tensor-root matches, runnable environment resolution, attention-scale parity, exact prompt/control/terminal/cap/raw-byte certification, full parser environment, isolation, both scope backward tests, adapter lifecycle/export and measured resources/repeatability.

In particular, a source-supported scalar conversion is not a measured scale/layout check; a mapped module catalog is not a successful model load; standard LoRA arithmetic is not a demonstrated gradient; and a serving class declaration is not an adapter reload result. Any failure remains an explicit bounded infrastructure issue rather than permission for protocol repair, candidate use or checkpoint substitution.

## 20. Fallback decision

**Fallback triggered: No.** The exact original has a credible same-original reconstruction/adaptation path. Therefore the condition for a separate Devstral-Small-2507 BF16 full static preflight is not met. No fallback was executed or selected; it would be a distinct original if separately authorized under the stipulated no-path condition. Existing Qwen ordering and gpt-oss Harmony conclusions remain untouched.

## 21. Protocol modified?

**No.** `current-repo-v1-draft3`, Draft2/Draft3 source/specification, completion contract, input budgets, deployment target32768 and reserve2048 are unchanged. Full textual output remains required. No final-only extraction, suppression, retries, clipping, alternate effort mode or post-hoc projection was introduced. The proposed runtime profile is an unauthenticated implementation mapping, not a protocol amendment.

## 22. Files created/modified

All new work is under **`experiments/model_preflight/devstral_small2_2512/`**:

- Required `REPORT.md`, source/artifact manifests, `identity.json`, `serialization.json`, `capacity_checks.json`, `runtime_profile.json`, `adaptation_targets.json`, `original_base_lifecycle.json`, `resource_estimates.json`, `infrastructure_test_matrix.csv`, `validation.json`.
- Additional `reconstruction_analysis.json`, `tokenizer_environment.json`, `baseline_integrity.json`, `collect_static.py`, `check_tokenizer.py`, `build_preflight.py`, `validate_preflight.py`.
- Exact public text/metadata/vocabulary snapshots under `upstream/` and `sources/`; four pinned dependency wheels/extracted tokenizer libraries;51 synthetic **input** fixtures.

The manifest inventories files with sizes and SHA256. It excludes itself to avoid circular hashing. The validation file is finalized before manifest hashing; validation recomputes and checks that manifest. No historical or landscape file was modified. The baseline preservation set covers667 permitted existing files, including policy and previous preflight sources, without inspecting protected outcomes.

Final validation details and git state are in [validation.json](validation.json). Expected unchanged HEAD: **`7fcdecbe26f4fd01138edf8f58c02ce4b947db0b`**. Worktree status: **`?? experiments/model_preflight/`**, already present before this step and still containing uncommitted preflight artifacts. No tracked/staged diff or commit is introduced.

## 23. Final recommendation

Record **PROCEED TO INFRASTRUCTURE VERIFICATION** for this exact original as a **static** conclusion only. Same-original trainable reconstruction is statically established at official-code/inference level; empirical reconstruction/lifecycle/determinism are unverified. Both proposed dense rank16 scopes are statically admissible. Synthetic maximum20,454+2048=22,502 fits unchanged32768. All24 infrastructure checks remain NOT_RUN. Fallback is not triggered. Protocol changed:no; inference:no; protected candidates accessed:no; commit:no.

**Stop after this report.** Do not begin infrastructure verification, spend on GPUs, proceed to GLM/Nemotron, run the fallback, freeze a roster or use candidate/benchmark results.

[card]: https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/README.md
[config]: https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/config.json
[params]: https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/params.json
[index]: https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/model.safetensors.index.json
[generation]: https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/generation_config.json
[tokenizer]: https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/tokenizer.json
[tekken]: https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/tekken.json
[tokenizer-config]: https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/tokenizer_config.json
[template]: https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/chat_template.jinja
[text-source]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/models/ministral3/modeling_ministral3.py
[wrapper-source]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/models/mistral3/modeling_mistral3.py
[vision-source]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/models/pixtral/modeling_pixtral.py
[template-source]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/utils/chat_template_utils.py
[quantizer-source]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/quantizers/quantizer_finegrained_fp8.py
[quant-config-source]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/utils/quantization_config.py
[fp8-source]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/integrations/finegrained_fp8.py
[quantizer-base]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/quantizers/base.py
[modeling-utils]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/modeling_utils.py
[mapping-source]: https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/conversion_mapping.py
[lora-source]: https://github.com/huggingface/peft/blob/532a05dd505c28993119b7715ee286f4234bf51b/src/peft/tuners/lora/layer.py
[lora-model]: https://github.com/huggingface/peft/blob/532a05dd505c28993119b7715ee286f4234bf51b/src/peft/tuners/lora/model.py
[peft-model]: https://github.com/huggingface/peft/blob/532a05dd505c28993119b7715ee286f4234bf51b/src/peft/peft_model.py
[peft-save]: https://github.com/huggingface/peft/blob/532a05dd505c28993119b7715ee286f4234bf51b/src/peft/utils/save_and_load.py
[peft-other]: https://github.com/huggingface/peft/blob/532a05dd505c28993119b7715ee286f4234bf51b/src/peft/utils/other.py
[requirements]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/requirements/common.txt
[cuda-requirements]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/requirements/cuda.txt
[docker]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/docker/Dockerfile
[sampling-source]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/sampling_params.py
[stop-source]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/v1/core/sched/utils.py
[engine-source]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/engine/arg_utils.py
[llm-source]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/entrypoints/llm.py
[serving-model]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/model_executor/models/mistral3.py
[mistral-source]: https://github.com/vllm-project/vllm/blob/ced6857afa0ea7b2e3f0846a62e1394e90f15607/vllm/model_executor/models/mistral.py
