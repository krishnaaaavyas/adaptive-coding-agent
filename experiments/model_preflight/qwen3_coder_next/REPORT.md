# STEP 8K-B.1G1B — QWEN3-CODER-NEXT MODEL PREFLIGHT

Date: 2026-10-03 (Asia/Calcutta). Static, candidate-blind preflight. Workspace HEAD verified as `7fcdecbe26f4fd01138edf8f58c02ce4b947db0b`. No full checkpoint, inference, training or official admission performed.

## 1. Verdict

**INCONCLUSIVE — INFRASTRUCTURE VERIFICATION REQUIRED**

Static identity, architecture, tokenizer, synthetic capacity and decoding-control evidence reveal no required change to current-repo-v1-draft3. Source-level adaptation is possible with explicit targets. Actual loading, terminal transport, adapter save/reload/merge and repeated fresh-base rebuilding remain unmeasured. This workstation cannot host the checkpoint. A source-supported route on larger infrastructure prevents declaring global deployment impractical, but does not establish study eligibility.

## 2. Exact model identity

Authoritative open-weight repository: `Qwen/Qwen3-Coder-Next`; immutable revision `a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb`. The Hub revision API was resolved before analysis, then all model files fetched by that revision; no moving branch used for analysis. `upstream_manifest.json` binds URLs, byte sizes and SHA-256 hashes. `weight_manifest.json` retains shard sizes and LFS identities without downloading bodies. 40 safetensors shards; 74,391 tensor names in the index. LFS identities are upstream metadata, not locally verified body hashes. Config/tokenizer/index were loaded; weight tensors were not.

## 3. License

SOURCE-SUPPORTED: pinned README front matter and pinned Hub card metadata declare `apache-2.0`. No separate LICENSE exists in the pinned file inventory; the card's moving LICENSE link returns 404. Thus the license declaration is verified, but a repository-specific standalone license text was not available to archive. Apache declaration permits the intended adaptation subject to its terms; archive license text and notices before distribution. This is a documentation limitation, not proof of an alternative license.

## 4. Architecture

SOURCE-SUPPORTED: `Qwen3NextForCausalLM`, `model_type=qwen3_next`, BF16; card labels 80B total and 3B activated. Do not interpret 3B active as resident footprint or throughput. 48 decoder layers, hidden width 2,048, untied embeddings/output head, model vocabulary rows 151,936. Every fourth layer uses gated full attention: 12 full-attention layers and 36 Gated DeltaNet linear-attention layers. Full attention has 16 query heads, 2 KV heads, head dimension 256, gated query projection width 8,192. Linear attention has 16 key heads and 32 value heads, 128-dimensional heads, depthwise convolution kernel 4. All 48 layers use MoE: 512 routed experts, top 10 per token, intermediate width 512; one shared width-512 expert with its own gate. Router probabilities normalized over selected experts. RoPE theta 5,000,000, partial rotary factor 0.25, no configured RoPE scaling/sliding window. Native context is 262,144, not tokenizer_config's 1,048,576 advisory maximum.

## 5. Tokenizer identity

MEASURED offline with Transformers 4.57.6/tokenizers 0.22.2, matching the prior preflight dependency versions. Declared `Qwen2Tokenizer`, instantiated `Qwen2TokenizerFast`; BPE with NFC normalization and all 256 byte symbols. Base vocabulary 151,643; tokenizer length 151,669 (model rows are larger). Canonical vocabulary hash `c96fa22dee2dd9c98c4f0c73ea423e21907bc96abda81fa5c6b2e24a670c66bf`. `tokenizer_identity.json` includes complete added-token flags, special IDs, backend details, padding example and hashes. Actual BOS is None, EOS 151645 (`<|im_end|>`), pad 151643 (`<|endoftext|>`), right padding/truncation defaults; truncation was explicitly disabled. No extra BOS/EOS added by raw encode, empty encode is empty. Exact tokenizer.json hash: `19564a48c4f71a2a1b937cce34c737a1e662b171c5f5d7edf641a15cd896f07d`.

## 6. Chat-template identity

MEASURED: standalone `chat_template.jinja` selected by AutoTokenizer, 6,068 UTF-8 bytes, SHA-256 `c79a833039a43602150cce0902403d6e376c50930c1b2a139b2964e1f0c322a0`. Embedded tokenizer_config template lacks the standalone source's final LF; both hashes recorded in `template_source_identity.json`, and identical rendering verified for all 51 fixtures. Native generation prefix is exactly `<|im_start|>assistant\n`. System/user content retained; no tools supplied, no thinking prefix. Card states non-thinking only. Native tool-capable branches are not invoked. Six template probes cover system/user, assistant history, multiline code, Unicode, literal protocol/special-token delimiters, empty H; 45 capacity probes cover all conditions. Four repeated render/encode checks per fixture were identical. Raw literal special-token strings may encode as special tokens: this is disclosed, not escaped or tuned away. Actual server rendering parity still requires verification.

## 7. Run-profile compatibility table

Frozen requests are unchanged. Table entries are SOURCE-SUPPORTED or wrapper obligations, not runtime measurements. Proposed arguments are in `proposed_runtime.json`, which is expressly not a verified official profile.

| Frozen requirement | Proposed vLLM 0.16.0 mapping | Static status |
|---|---|---|
| Greedy; temperature 0 | `temperature=0.0` invokes greedy | Source-supported |
| top_p 1; top_k disabled | `top_p=1.0`, `top_k=0` (native disabled value) | Source-supported; greedy normalizes neutral controls |
| repetition penalty 1 | `repetition_penalty=1.0` | Source-supported |
| frequency/presence penalty 0 | both `0.0` | Source-supported |
| seed 0 when supported | `seed=0` | Source-supported; no universal determinism claim |
| No text stops | `stop=[]` | Source-supported |
| 2,048 generation tokens | `max_tokens=2048`, `min_tokens=0` | Source-supported; reserve includes terminal allowance |
| One completion | `n=1` | Source-supported; greedy requires one |
| No retry | one transport request, retry count 0 | Wrapper obligation |
| No context shifting | fixed 32,768 capacity, reject overflow | Admission/wrapper obligation |
| No clipping/truncation | exact pre-rendered IDs; `truncate_prompt_tokens=None` | Source-supported plus exact-input parity verification |

Do not use upstream sampling defaults (`do_sample=true`, temperature 1, top_p .95, top_k 40) or recommended sampling values. Use native neutral generation config with explicit native terminal IDs to avoid hidden default overrides. Bool/int/decimal/array/string/native argument types must be frozen and verified before official profile validation. No claim that the harness's required exact profile schema was certified here.

## 8. Context/capacity verification

MEASURED: copied the same candidate-blind synthetic constructor, not earlier expected counts. Same protocol framing helpers and system message; independent Coder-Next tokenization. No certified histories or product snapshots used. Four families at exact ceilings and one byte below: ASCII punctuation, multilingual Unicode, NFC-expanding U+0344, code/literal delimiters. Each covers A/B/M/C/BC; five empty-registry cases give 45 capacity cases. A H is empty; other ceiling H is 4,096 bytes; BC divides the fixed H total into lanes no larger than 2,048. P is canonical J(P) bytes including JSON escaping. K is condition-independent with matching hashes across conditions. All 45 passed input + 2,048 <= 32,768 <= 262,144.

| Family | Maximum input tokens | + 2,048 reserve | Maximum raw rendered bytes | Result |
|---|---:|---:|---:|---|
| ASCII | 20,437 | 22,485 | 21,143 | PASS |
| Multilingual Unicode | 8,435 | 10,483 | 21,143 | PASS |
| NFC expansion | 27,855 | 29,903 | 21,143 | PASS |
| Code/delimiters | 4,747 | 6,795 | 21,143 | PASS |

`capacity_checks.json` and CSV record every family's individual case: rendered and normalized bytes, token count, P/K/H bytes, K hash, reserve, total and capacity result. Fixtures retain messages, rendered strings and independently computed token IDs. Fixed raw framing overhead 663 bytes. NFC can expand raw bytes: maximum tested normalized bytes 37,323; its loose byte bound + reserve is 39,371, above 32,768 even though actual tokens fit. These synthetic measurements are not an exhaustive byte-ceiling proof. Frozen per-input admission must tokenize every condition and reference output; reject overflow without truncation and freeze the common population before inference. Native capacity is not measured allocated runtime capacity. Full normative parser was not run: tokenizer checks used Python 3.12.14; official parser still requires CPython 3.11.9/Unicode 14.0.

## 9. Terminal behavior

SOURCE-SUPPORTED: model config primary EOS 151645; generation_config native EOS set [151645,151643]; tokenizer pad 151643. vLLM sampling merges generation-config EOS IDs, and scheduler stops on primary EOS or explicit stop-token IDs before length-cap classification. Proposed profile explicitly retains both native terminals with no text stops, ignore_eos false. vLLM RequestOutput exposes token IDs, finish reason, stop reason; primary EOS may have no explicit stop_reason, so use final token plus finish reason. Native terminal is counted inside the 2,048 budget; reference-output admission reserves one terminal token, unchanged. Preserve raw token sequence and completion bytes; strip only a verified final native terminal token for file parsing, never blanket-strip internal special tokens. Runtime decode/count/2048-boundary parity is unmeasured. No terminal behavior inferred from generated text.

## 10. Proposed runtime

Linux/CUDA vLLM 0.16.0 at `89a77b10846fd96273cce78d86d2556ea582d26e`, Transformers 4.57.6 at `753d61104116eefc8ffc977327b441ee0c8d599f`. Model card requires vLLM >=0.15.0 (earlier model's 0.11.2 is below this requirement). Pinned registry/source supports Qwen3NextForCausalLM, hybrid inner state and SupportsLoRA with packed qkv/expert projection mappings. Its dependency source pins torch 2.9.1 and FlashInfer 0.6.3; Transformers range includes chosen 4.57.6. Start with BF16, 32,768 max sequence length, one concurrent sequence, TP=4 on 4x80GB class GPUs; TP=2 on 2x141GB is another plausible hardware configuration. Disable prefix reuse; fresh recurrent/KV state each request; no tools, speculative generation or read access. vLLM's hybrid prefix cache has implementation-specific restrictions; disabling it avoids needing any protocol alteration. No server installed or launched. vLLM LoRA marker does not prove all trained expert adapters can be served; attention-adapter import or merge/export needs actual checks. Versioned source evidence is archived, including a renamed input-processor path; unsuccessful 404 paths are retained in source_manifest and not treated as evidence.

## 11. Resource requirements

SOURCE-SUPPORTED: exact shard storage `159,358,031,480` bytes (159.358 GB / 148.41 GiB); tensor payload `159,348,782,592` bytes (148.405 GiB). BF16 resident weight payload is approximately this tensor size, conditional on declared BF16; no per-tensor dtype measurement. Config/card size is roughly 80B, not 3B resident.

ESTIMATED, single sequence, no throughput prediction:

| Use | Plausible configuration / memory budget | Qualification |
|---|---|---|
| BF16 inference | 4x80GB or 2x141GB GPUs; roughly 170–210 GiB aggregate including cache/workspaces | Must verify hybrid kernels/TP allocation; 2x80GB leaves little headroom |
| 8-bit inference | ~74.2 GiB ideal weight floor; ~85–115 GiB practical budget; 2x80GB | Requires compatible quantization path, not all kernels guaranteed |
| 4-bit inference | ~37.1 GiB ideal floor; ~45–65 GiB practical weight/runtime budget; 1x80GB or 2x48GB | Overhead/unquantized layers extra; 48GB single GPU marginal |
| BF16 attention LoRA | 4x80GB with explicit sharding, checkpointing, microbatch 1 as starting point | Frozen full base ~148.4 GiB plus training activations; fit unmeasured |
| NF4 attention QLoRA | 1x80GB or 2x80GB starting point; roughly 55–90+ GiB total depending on sequence | Not a promise of full 32K training on one GPU; no training-length tuning authorized |
| All-expert LoRA/QLoRA | rank-16 adapter alone ~5.63 GiB BF16; conventional training state ~45 GiB before activations/base | Requires substantially larger/sharded training; naive all-linear expensive |
| Host | 192–256 GiB RAM recommended for BF16 loading/merge; 64–128 GiB possible quantized streaming experiments | Loading method/quantization peaks unknown |
| Storage | ~350–500 GB free for immutable base, merged export, cache/workspace | ~160 GB minimum checkpoint alone; quantization/merge may need additional copies |

BF16 full-attention KV estimate at 32K: 12 layers * 2 K/V * 2 heads * 256 dim * 2 bytes * 32768 = 0.75 GiB per sequence; recurrent states/workspaces are additional. Quantized floors use tensor-payload ratios; mixed precision and scale metadata increase them.

MEASURED local inventory: RTX 2050 4,096 MiB, driver 581.86, host RAM 25,463,480,320 bytes (~23.71 GiB), free disk ~22.81 GiB at check time. Local full-checkpoint storage and GPU/RAM fit fail without any weight load. Larger remote infrastructure remains plausible but unverified. Repeated fresh-base rebuild costs cannot be inferred from active parameters; no timing or throughput measured.

## 12. LoRA/QLoRA feasibility

SOURCE-SUPPORTED for pinned Transformers 4.57.6 + PEFT 0.18.0 (`77daa8d3b7decf2b40238ab47e2c1bd0f26c7749`), not every newer implementation. PEFT default target mapping lacks qwen3_next, so explicitly specify targets. Full attention exposes q_proj/k_proj/v_proj/o_proj as nn.Linear; linear attention exposes in_proj_qkvz/in_proj_ba/out_proj as nn.Linear. Expert gate_proj/up_proj/down_proj are separate nn.Linear modules in ModuleList at this pin and correspond to indexed checkpoint keys. Shared experts are likewise linear. No raw expert target_parameters workaround is needed at this pin; newer fused-parameter architectures cannot inherit this claim.

Example non-executed regex target set for attention-only: `.*\.(self_attn\.(q_proj|k_proj|v_proj|o_proj)|linear_attn\.(in_proj_qkvz|in_proj_ba|out_proj))`. For routed experts use explicit paths `model.layers.<i>.mlp.experts.<e>.(gate_proj|up_proj|down_proj)`; shared expert paths are separate. Router `.mlp.gate`, shared_expert_gate, embedding, output head, convolution, norms and recurrence parameters remain frozen unless a separately frozen adaptation design explicitly targets them. MoE routing selects only some expert branches per token; sparse gradients and 24,576 experts affect coverage/overhead. `all-linear` is not equivalent to attention-only and can also wrap routers/shared gates. Enumerate and audit actual target list before training.

ESTIMATED adapter counts from `r*(input+output)` for each bias-free linear, verified source shapes; not instantiated parameter measurements:

| Target set | Rank 8 | Rank 16 |
|---|---:|---:|
| 12 full-attention layers (q,k,v,o) | 2,064,384 | 4,128,768 |
| 36 linear-attention layers (qkvz,ba,out) | 6,506,496 | 13,012,992 |
| All attention projections | 8,570,880 | 17,141,760 |
| Routed expert projections only | 1,509,949,440 | 3,019,898,880 |
| Shared expert projections only | 2,949,120 | 5,898,240 |

PEFT save_pretrained/from_pretrained and LoRA merge_and_unload are implemented in pinned sources. Pure linear LoRA merge to a freshly loaded BF16 original base is source-supported; save resulting full checkpoint and verify key/shape integrity, tokenizer/template persistence and output parity. vLLM mapping is source-supported but direct expert-LoRA loading is not proven. Quantized adapter merge can introduce rounding/quantization differences; prefer verified BF16 merge from ORIGINAL BASE then separately certify export/quantization. Do not claim quantized merge exactly restores a BF16 base.

QLoRA architecture route: pinned Transformers recursively replaces nn.Linear with bitsandbytes Linear4bit, including these ModuleList experts; PEFT has bnb Linear4bit adapters and prepare_model_for_kbit_training. NF4 + double quantization + BF16 compute is source-supported generic machinery with bitsandbytes 0.49.1 pinned. Conv/recurrence parameters are not automatically quantized linear modules. Qwen3Next hybrid kernel backward, full expert quantization, device placement and optimizer fit are not architecture-specific tested evidence. CPU-offload inference device_map is not a certified distributed-training strategy.

Repeated fresh adapters: retain immutable original checkpoint and quantization identity; initialize a new adapter/optimizer/RNG/training state for each authorized rebuild, train only on certified allowed history, save independently, reload against ORIGINAL BASE; never chain previous adapter weights or mutated/merged bases. For strict freshness use a fresh base process/load or verify immutable base identity and absence of state leakage. Generic save/reload makes this architecturally possible; repetitive setup cost, deterministic initialization, trainability, merge and lifecycle integrity are unmeasured. MEASURED adaptation results: NONE. No ranks/targets/training recipe were adopted as study settings by this report.

## 13. Protocol compatibility

No required protocol modification identified statically. Keep current-repo-v1-draft3, exact P/K/H construction and byte ceilings, A/B/M/C/BC, K reuse, common admission, 2,048 reserve, one native terminal allowance, complete replacement output, no-read generation and deterministic provenance unchanged. Tokenizer NFC is the native encoding behavior, not a change to canonical P/K/H bytes/hashes. Native special delimiters in supplied contents are disclosed; do not reconstruct K/H by delimiter search. Native tool template support does not grant tool/read access. Protocol already accepts model-specific tokenizer/template/runtime identities and pre-outcome capacity rejection. A new minimum runtime version is infrastructure work, not a normative amendment. Artifact directory is excluded because frozen EXCLUDED_DIRS includes experiments. No product/candidate reads were used to verify this exclusion.

Official status remains unverified: certify model/body hashes, runtime/profile arguments, actual native terminals/transport, no-read request isolation and common admission before study generation. Greedy does not prove bitwise determinism. No admission population was examined or changed here.

## 14. Comparison-relevant differences from Qwen3-Coder-30B-A3B

FACTUAL ONLY. Read only earlier constructor, dependency lock and pinned upstream config/tokenizer/template artifacts; no prior performance/report/results used. Next uses qwen3_next hybrid attention (12 full/36 linear) versus qwen3_moe full attention; both hidden width 2,048, 48 layers, native context 262,144. Next: 512 experts/top10/width512 plus shared expert; 30B:128/top8/width768. Next full attention heads16/KV2/head256 and gated q width8192; 30B heads32/KV4/head128. Native tokenizer.json, vocab.json and merges.txt are byte-identical between checkpoints, independently hashed; template sources differ. This does not reuse expected token counts. All counts here came from Next's tokenizer. Next minimum vLLM requirement is .15.0; prior acquisition script selected .11.2. Total base/storage footprint is substantially larger, even with the same advertised active-parameter order. No ranking, throughput, quality or adapter-performance comparison made.

## 15. Synthetic generation performed?

NO model generation. Synthetic input construction/rendering/tokenization only: YES, 51 fixtures.

## 16. Model/project benchmark tasks inspected?

NO. Model card downloaded as an authoritative metadata artifact; no benchmark task instances or product tests/candidates opened or executed, and model-card performance claims were not used to decide compatibility.

## 17. Candidate artifacts inspected?

NO.

## 18. Adaptation experiment performed?

NO.

## 19. Files modified

Only new files under `experiments/model_preflight/qwen3_coder_next/`: acquisition/reproduction/report scripts, .gitignore, pinned upstream metadata/tokenizer/template/index, implementation sources, manifests, synthetic fixtures, capacity/template/tokenizer checks, proposed_runtime.json, adapter estimates, factual comparison, workspace/hardware/environment audit, REPORT.md and artifact_manifest.json. Local dependencies are installed under this directory and ignored; lockfile records versions. `artifact_manifest.json` inventories exact paths/hashes excluding installed dependencies and __pycache__. No normative, harness, product or prior-preflight files modified. No commit. Existing prior preflight untracked artifacts preserved.

## 20. Remaining verification

1. Provision Linux/CUDA with sufficient checkpoint disk, RAM and GPU memory; do not infer performance from top-k expert count.
2. Verify full checkpoint shard hashes and dtype/key integrity only when infrastructure verification is explicitly authorized.
3. Freeze container/build dependency lock, CUDA/driver/kernel/TP identities and actual per-sequence capacity; test exact prompt ID parity and fresh recurrent state.
4. Candidate-blind generation transport tests must verify native EOS count/removal, 2,048-boundary classification, no text stops/no hidden truncation, raw-byte retention and all typed effective controls. These are future tests, not conducted here.
5. On fresh ORIGINAL BASE, verify explicit target audit, gradients, memory, save/reload and merge/export parity; repeat fresh adapter rebuild without optimizer/base contamination. Validate QLoRA separately if selected.
6. Bind complete model/tokenizer/template/system/generation-prompt/runtime/profile identities and attest determinism limits; use required Python parser environment for official harness validation.
7. Freeze common admission from certified pre-outcome input/reference checks later; no candidate checks were performed now. Resolve missing standalone license artifact/notice packaging before distribution.

## 21. Recommendation

Finish infrastructure verification on adequately sized hardware before adding this model to the verified shortlist. Start with source-supported BF16 serving and explicit attention-only adaptation feasibility checks; broader expert adaptation has materially different memory/coverage demands and requires its own frozen design. This recommendation does not tune the frozen protocol or choose an adaptation recipe. Keep the verdict provisional until actual runtime and fresh-adapter lifecycle evidence exists.

Evidence: [pinned model config](https://huggingface.co/Qwen/Qwen3-Coder-Next/blob/a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb/config.json), [pinned model card](https://huggingface.co/Qwen/Qwen3-Coder-Next/blob/a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb/README.md), [generation configuration](https://huggingface.co/Qwen/Qwen3-Coder-Next/blob/a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb/generation_config.json), [weight index](https://huggingface.co/Qwen/Qwen3-Coder-Next/blob/a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb/model.safetensors.index.json), [tokenizer configuration](https://huggingface.co/Qwen/Qwen3-Coder-Next/blob/a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb/tokenizer_config.json), [template](https://huggingface.co/Qwen/Qwen3-Coder-Next/blob/a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb/chat_template.jinja).

Implementation evidence: [Transformers Qwen3Next](https://github.com/huggingface/transformers/blob/753d61104116eefc8ffc977327b441ee0c8d599f/src/transformers/models/qwen3_next/modeling_qwen3_next.py), [bitsandbytes replacement](https://github.com/huggingface/transformers/blob/753d61104116eefc8ffc977327b441ee0c8d599f/src/transformers/integrations/bitsandbytes.py), [PEFT LoRA implementation](https://github.com/huggingface/peft/blob/77daa8d3b7decf2b40238ab47e2c1bd0f26c7749/src/peft/tuners/lora/model.py), [PEFT serialization](https://github.com/huggingface/peft/blob/77daa8d3b7decf2b40238ab47e2c1bd0f26c7749/src/peft/peft_model.py), [vLLM Qwen3Next](https://github.com/vllm-project/vllm/blob/89a77b10846fd96273cce78d86d2556ea582d26e/vllm/model_executor/models/qwen3_next.py), [sampling controls](https://github.com/vllm-project/vllm/blob/89a77b10846fd96273cce78d86d2556ea582d26e/vllm/sampling_params.py), [native stopping](https://github.com/vllm-project/vllm/blob/89a77b10846fd96273cce78d86d2556ea582d26e/vllm/v1/core/sched/utils.py).


Reproduction: acquire `fetch_evidence.py` (existing upstream/hub_metadata.json locks model revision), `supplement_sources.py`, install `tokenizer-requirements.lock.txt` into dependencies, run `verify_synthetic.py` offline, then `build_report.py`. Source tags are resolved to archived immutable SHAs; use implementation_pins/source_manifest SHAs for exact future re-fetches, rather than re-resolving tags. Installed packages are version-locked, not a wheel-hash/supply-chain attestation. The manifest does not claim downloaded checkpoint body verification.
