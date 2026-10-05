# STEP 8K-B.1G1A — QWEN3-CODER-30B-A3B MODEL PREFLIGHT

Date: 2026-10-03 (Asia/Calcutta). Candidate-blind metadata, tokenizer and source preflight only. This is not a frozen model, certified run profile, official admission, or adaptation experiment.

## 1. Verdict

**INCONCLUSIVE — INFRASTRUCTURE VERIFICATION REQUIRED**

The pinned checkpoint passes the performed tokenizer, template and synthetic capacity checks. Versioned first-party implementations provide a plausible inference and adaptation path. Full-checkpoint generation, deployed control enforcement, output accounting, adapter round trips and refresh cost have not been verified. Available local storage, RAM and GPU memory are insufficient for the proposed BF16 deployment; this is not evidence of general model incompatibility.

## 2. Exact model identity

- Repository: `Qwen/Qwen3-Coder-30B-A3B-Instruct`.
- Exact immutable revision: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- Workspace HEAD, verified before and after: `7fcdecbe26f4fd01138edf8f58c02ce4b947db0b`.
- Configuration SHA-256: `e2c8d8eea39471785cd93379d8b48241ad7dcda299013155dd02526e34a0de62`.
- Generation configuration SHA-256: `c99723ab3ba28630d26ae23def77603b540a46924895af5cf234740d3b27b51d`.
- Format/dtype: 16 Safetensors shards, BF16; Hub metadata reports exactly 30,532,122,624 parameters. The index reports 61,064,245,248 parameter bytes. Hub shard sizes sum to 61,066,575,656 bytes, including headers (61.067 GB / about 56.874 GiB).
- `upstream_manifest.json` records measured SHA-256 and byte length for each downloaded metadata/tokenizer file. `weight_manifest.json` records upstream-declared shard LFS SHA-256 values and sizes. Weight bodies were not downloaded, so their content hashes were not locally verified.
- [Pinned upstream model](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/tree/b2cff646eb4bb1d68355c01b18ae02e7cf42d120), [pinned configuration](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/blob/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/config.json).

## 3. License

Apache-2.0, confirmed by the pinned upstream card and LICENSE file. LICENSE SHA-256: `832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e`. Retain the license, notices and applicable modification notices when distributing derivatives. This is a recorded license identity, not a legal certification. [Pinned license](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/blob/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/LICENSE).

## 4. Architecture

`Qwen3MoeForCausalLM`, model type `qwen3_moe`: causal decoder MoE, 48 layers, hidden width 2,048, 128 experts per sparse layer, 8 selected experts per token, expert intermediate width 768, 32 query heads / 4 KV heads, head dimension 128, untied embeddings. Total parameters are exactly 30,532,122,624 per Hub metadata; active parameters are **3.3B as rounded by the authoritative card**, not an independently measured exact count. All experts remain resident in an ordinary GPU deployment despite sparse activation.

Native context is **262,144**, RoPE theta 10,000,000; `rope_scaling=null`, no sliding window. The tokenizer's `model_max_length=1048576` is not authority for native model capacity. This preflight adds no RoPE extension. Upstream says non-thinking mode only; `enable_thinking=False` is unnecessary. The card requires Transformers at least 4.51.0; config's `transformers_version=4.52.3` is serialization provenance rather than a strict runtime requirement. [Pinned card](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/blob/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/README.md).

## 5. Tokenizer identity

Loaded locally from the exact pinned file set with `trust_remote_code=False`, `local_files_only=True`, using Transformers **4.57.6**, Tokenizers **0.22.2**, Jinja2 **3.1.6**. Actual class: `Qwen2TokenizerFast`; declared class: `Qwen2Tokenizer`. Base vocabulary size 151,643; loaded length 151,669 including 26 added entries; model embedding vocabulary 151,936. No assumption that these three counts are interchangeable.

| File/identity | SHA-256 |
|---|---|
| tokenizer_config.json | `60f6e8cb15c98dd07300a3cc465ea662de245d2095e4245616af21b2324db3fc` |
| tokenizer.json | `19564a48c4f71a2a1b937cce34c737a1e662b171c5f5d7edf641a15cd896f07d` |
| vocab.json | `ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910` |
| merges.txt | `599bab54075088774b1733fde865d5bd747cbcc7a547c5bc12610e874e26f5e3` |
| Canonical sorted loaded vocabulary map | `c96fa22dee2dd9c98c4f0c73ea423e21907bc96abda81fa5c6b2e24a670c66bf` |

Byte-level BPE with **NFC normalization** and all 256 byte symbols present. Normalization is native tokenizer behavior; original message/render bytes are retained separately. Unicode encoding can normalize the input, so decoding tokens is not an assertion of byte-for-byte preservation of unnormalized text. `add_prefix_space=false`, `clean_up_tokenization_spaces=false`, `split_special_tokens=false`, `errors=replace`, no unknown token. Protocol input remains strictly UTF-8; do not use replacement decoding to admit invalid input.

Tokenizer BOS is null; `add_bos_token=false`. Model config's BOS 151643 does not cause tokenizer insertion. Measured ordinary encoding with and without `add_special_tokens` is identical; empty input encodes to `[]`. EOS is `<|im_end|>` (151645), PAD is `<|endoftext|>` (151643), and `<|im_start|>` is 151644. Padding side and truncation side are right. A separate padding example verifies pad IDs with a zero attention mask; official single-request synthetic encoding uses **no padding and no truncation**. Complete added-token flags and special-token inventories are in `tokenizer_identity.json`; the configuration is preserved byte-for-byte upstream.

All six template cases and all 45 capacity cases were encoded four times with identical token IDs. Rendering then encoding with `add_special_tokens=False` matched `apply_chat_template(tokenize=True)`.

## 6. Chat-template identity

Authoritative `chat_template.jinja`, **6,211 exact UTF-8 bytes**, SHA-256 `5a38bfa05833266240066aedc497decc9b00cc0d3e3b8cceea98cf530196ab06`. The standalone bytes equal the decoded tokenizer-config template and loaded tokenizer template. [Pinned template](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/blob/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/chat_template.jinja).

Six synthetic cases: system+user; system+user+assistant; multiline Python code; Unicode including a decomposed accent; embedded protocol and native chat delimiters; empty H. Each produced deterministic bytes and tokens across four encodings. Full synthetic messages, renders and token vectors are saved in `synthetic/`, with hashes in `template_checks.json`. `add_generation_prompt=True` appends exactly `<|im_start|>assistant\n`; it does not append a generated EOS or a thinking block. No tools are supplied. Native chat delimiters embedded in content become special tokens; this is recorded rather than escaped or silently changed. Their semantic effect is untested.

## 7. Run-profile compatibility table

The classifications below describe **versioned source support** for the proposed offline vLLM 0.11.2 configuration. They are not deployment certification or measured logits-level equivalence. Explicit parameters are required; upstream recommends temperature 0.7 / top_p 0.8 / top_k 20 / repetition penalty 1.05 and much longer outputs, but these are recommendations, not architectural necessities. No protocol values were changed.

| Frozen setting | Classification | Proposed mapping / evidence |
|---|---|---|
| Greedy decoding | SUPPORTED EXACTLY | Temperature 0 selects `SamplingType.GREEDY` in pinned source. |
| Temperature 0 | SUPPORTED EXACTLY | `temperature=0.0`. |
| top_p 1 | SUPPORTED EXACTLY | `top_p=1.0`; retained by greedy initialization. |
| top_k disabled | SUPPORTED WITH VERIFIED EQUIVALENT | `top_k=0`; pinned source documents disabled and uses 0 in greedy mode. |
| Repetition penalty 1 | SUPPORTED EXACTLY | `repetition_penalty=1.0`. |
| Frequency penalty 0 | SUPPORTED EXACTLY | `frequency_penalty=0.0`. |
| Presence penalty 0 | SUPPORTED EXACTLY | `presence_penalty=0.0`. |
| Seed 0 when supported | SUPPORTED EXACTLY | Engine and SamplingParams `seed=0`; no cross-hardware determinism claim. |
| No text stops | SUPPORTED EXACTLY | `stop=[]`; native terminal IDs separately recorded. |
| Max generation 2048 | SUPPORTED EXACTLY | `max_tokens=2048`, explicit rather than inherited default. |
| One completion | SUPPORTED EXACTLY | `n=1`, `best_of=None`; greedy source rejects n>1. |
| No retry | AMBIGUOUS | Proposed one direct offline call; project transport/orchestration is absent and unverified. |
| No context shifting | SUPPORTED WITH VERIFIED EQUIVALENT | Config has no sliding window; fresh full-sequence input and length admission, no continuing conversation. End-to-end verification pending. |
| No clipping | AMBIGUOUS | No-read wrapper and complete output byte/token retention are proposed, not implemented. Must reject overflow without lowering 2048. |
| No truncation | SUPPORTED EXACTLY | Offline tokenizer `truncation=False`; vLLM `truncate_prompt_tokens=None`. Deployed prompt-ID equality remains pending. |

Sources: [vLLM 0.11.2 SamplingParams](https://raw.githubusercontent.com/vllm-project/vllm/v0.11.2/vllm/sampling_params.py), [input processing](https://raw.githubusercontent.com/vllm-project/vllm/v0.11.2/vllm/v1/engine/processor.py). Archived source bytes/hashes are in `source_manifest.json`.

## 8. Context/capacity verification

Used the repository's existing `messages()` and `pack_h()` helpers with synthetic objects only: actual fixed SYSTEM; canonical J(P); complete K wrappers, inventory and synthetic file block; no H for A; episodic/descriptive/rule lanes for B/M/C; separate episodic/rule lane ownership for BC. Fake records were used only for serialization, without certification or eligibility claims. Neither treatment admission nor benchmark execution was run.

Test families: ASCII punctuation, Unicode, Unicode NFC expansion (U+0344), and multiline code with delimiters. Each used **P=4096/K=12288/H=4096 bytes** and near-boundary **P=4095/K=12287/H=4095**. A always has H=0. BC lanes satisfy each owned <=2048-byte allowance. K hashes are identical across the five forms for each family/boundary. Five additional empty-registry cases verified H is zero bytes for every form. No max_length, clipping, truncation, or generation was used.

| Form | Maximum measured input tokens | Plus 2048 reserve | Native capacity |
|---|---:|---:|---:|
| A | 21,777 | 23,825 | 262,144 |
| B | 27,855 | 29,903 | 262,144 |
| M | 27,855 | 29,903 | 262,144 |
| C | 27,855 | 29,903 | 262,144 |
| BC | 27,819 | 29,867 | 262,144 |

**All 45 synthetic checks pass**, including the proposed deployment capacity 32,768. Fixed raw rendered overhead is 663 bytes; raw maximum is 21,143 bytes. NFC expansion makes a raw-byte token bound invalid: the largest tested normalized render is 37,323 bytes, while its actual token count is below 32,768 minus reserve. These measurements do not prove an exhaustive maximum over all valid Unicode/content. Later official admission must count actual rendered tokens for every treatment against the deployed capacity and retain the complete common 2048 reserve. If any treatment fails, apply the unchanged common-admission rule; do not truncate or substitute a smaller reserve. `capacity_checks.json` and `capacity_bound.json` preserve the measurements and their scope.

## 9. Terminal behavior

Model/tokenizer primary EOS: **151645 `<|im_end|>`**. Upstream generation configuration declares native terminal set **[151645,151643]**, the latter also being PAD/endoftext. Proposed `generation_config="vllm"` prevents upstream sampling defaults from leaking in; explicitly retaining stop-token ID 151643 preserves the second authoritative terminal. No text stops or additional user-invented terminal IDs are introduced.

Pinned vLLM sampling code can add secondary EOS IDs from generation config to its token stop set; this is token termination, not hidden textual stopping. Proposed controls make the set explicit. The scheduler distinguishes terminal stop from length cap, checks EOS/token stops before the length cap, and the output processor exposes token IDs, `finish_reason` and `stop_reason`. An EOS at the 2048th token therefore has terminal precedence in the examined source. [Stop logic](https://raw.githubusercontent.com/vllm-project/vllm/v0.11.2/vllm/v1/core/sched/utils.py), [output processor](https://raw.githubusercontent.com/vllm-project/vllm/v0.11.2/vllm/v1/engine/output_processor.py).

Later retain raw output token IDs and raw decoded bytes, removing only an observed final native terminal from the replacement artifact with explicit accounting. Do not indiscriminately strip every special token. Verify natural-stop versus forced-length behavior on the exact checkpoint, including terminal retention, output token count and one-token terminal allowance. No generation was available here, so these are source findings, not observed model behavior.

## 10. Proposed runtime

**One proposed official inference runtime: offline vLLM 0.11.2 V1**, Linux x86_64/CUDA 12.8, PyTorch **2.9.0**, Transformers **4.57.6**, Tokenizers **0.22.2**, Jinja2 **3.1.6**. Tokenize with the pinned local snapshot; submit those exact prompt token IDs to offline generation. BF16 original checkpoint, `quantization=None`, `trust_remote_code=False`, `max_model_len=32768`, TP=1, one sequence, seed 0, eager execution, prefix caching off, no speculative decoding, no tool parser or constrained decoding. This is a proposal rather than an installed or fully locked cloud environment.

Set `VLLM_ENABLE_V1_MULTIPROCESSING=0` and serialize requests. Do not use the online server for the official deterministic proposal. Upstream restricts reproducibility to the same hardware and vLLM version even with controlled scheduling; pin driver, CUDA build, kernels, complete dependency lock and image digest, then measure repeatability. [vLLM reproducibility](https://docs.vllm.ai/en/v0.11.2/usage/reproducibility/), [GPU installation](https://docs.vllm.ai/en/v0.11.2/getting_started/installation/gpu/).

Runtime comparison: Transformers 4.57.6 directly implements this architecture and gives tokenizer/template fidelity plus the clearest training path, but generation finish classification needs a wrapper. vLLM 0.11.2 directly implements `Qwen3MoeForCausalLM` with structured completion facts and bounded inputs, motivating the choice. SGLang is listed by the official Hub integration and remains a plausible alternative; its exact deployment/version was not verified or selected. No choice used benchmark performance. [vLLM supported models](https://docs.vllm.ai/en/v0.11.2/models/supported_models/), [versioned architecture implementation](https://raw.githubusercontent.com/huggingface/transformers/v4.57.6/src/transformers/models/qwen3_moe/modeling_qwen3_moe.py).

## 11. Resource requirements

**MEASURED locally:** RTX 2050, 4,096 MiB VRAM, driver 581.86; host RAM 25,463,480,320 bytes (23.714 GiB); available RAM about 11.637 GiB at measurement; free C: storage 24,853,585,920 bytes (23.147 GiB). Metadata/tokenizer download was 13,218,006 bytes; no weight body was downloaded. The upstream-declared checkpoint storage is 61,066,575,656 bytes. Local inference load time, prompt latency, throughput and training memory are **NOT MEASURED**.

**ESTIMATED planning ranges, not observed measurements:**

- BF16 inference: about 56.87 GiB weights, plus KV cache, kernels and workspace. One A100/H100 80 GB is a plausible starting environment at 32,768 capacity, batch one; budget roughly 65–75 GiB resident GPU memory. Exact kernel allocation/OOM behavior must be measured. An alternative is two 48 GB GPUs with tensor parallelism, requiring a separate reproducibility check.
- BF16 KV cache formula: `2 * 48 * 4 * 128 * 2 = 98,304 bytes/token` (~3 GiB at 32,768; ~24 GiB at full 262,144). Native sequence capacity alone does not establish full-context hardware feasibility.
- Inference host RAM: 64 GiB with low-memory/sharded loading may suffice; 96–128 GiB is a safer planning provision. Storage: at least 80–100 GB for base and environment; 150–250 GB if retaining base, merged derivative and multiple artifacts.
- Raw int8 and 4-bit parameter payload floors are about 28.44 and 14.22 GiB; practical quantized footprints are larger due to scales, unquantized tensors and KV/workspace. A 24–48 GB GPU may support quantized inference depending on implementation. Quantization is a derived numerical model requiring its own identity and preflight; it is not the selected BF16 official proposal.
- Ideal checkpoint network transfer lower bounds: about 8.1 minutes at sustained 1 Gbit/s or 81 minutes at 100 Mbit/s, ignoring overhead. Ideal read lower bound is about 61 seconds at 1 GB/s disk throughput. These are conditional arithmetic bounds, not measured load times.
- Prompt latency and generation throughput are unresolved. No defensible exact-checkpoint rate is inferred from active parameter count. Measure batch-one synthetic TTFT and output tokens/s on the proposed GPU before accepting deployment cost.

## 12. LoRA/QLoRA feasibility

**PRACTICAL WITH CLOUD GPU — source-supported, exact-checkpoint validation pending.** Proposed training stack: Transformers **4.57.6**, PEFT **0.18.0**, PyTorch **2.9.0**; add a separately pinned compatible bitsandbytes/Accelerate environment for QLoRA. The latter binary stack has not been resolved or tested, so QLoRA deployment readiness remains provisional.

The pinned Transformers source and checkpoint index expose `self_attn.q_proj`, `k_proj`, `v_proj`, `o_proj` plus per-expert `mlp.experts.<index>.gate_proj`, `up_proj`, `down_proj` as ordinary linear projections. Explicit `target_modules` names avoid reliance on a model-type default mapping: PEFT 0.18.0's inspected default LoRA map has `qwen3` but no `qwen3_moe` entry. Attention-only LoRA is feasible in source; attention plus expert MLP projections provides broader adaptation. This is a candidate target inventory, not a tuned or frozen adapter design. Exclude router `mlp.gate` unless separately justified. [Architecture source](https://raw.githubusercontent.com/huggingface/transformers/v4.57.6/src/transformers/models/qwen3_moe/modeling_qwen3_moe.py), [PEFT mapping](https://raw.githubusercontent.com/huggingface/peft/v0.18.0/src/peft/utils/constants.py).

MoE-specific costs: all 128 expert sets consume storage; only routed experts receive each token's updates; sparse coverage and load balancing require care. At illustrative rank 16, four attention projections across 48 layers have about **13.37M adapter parameters**. Adding all three projections across all 128 experts adds about **830.47M**, bringing the illustrative total to **843.84M**; roughly 10–14 GiB of training state may result at 12–16 bytes per adapter parameter, before activations. Rank 16 is an estimation assumption, not a chosen experimental hyperparameter. The inspected version uses ModuleList experts; fused-parameter examples in newer stacks require `target_parameters` and cannot be applied blindly. PEFT 0.18.0 documents limitations for multiple parameter-target adapters. [Versioned LoRA guidance](https://raw.githubusercontent.com/huggingface/peft/v0.18.0/docs/source/developer_guides/lora.md).

QLoRA path: frozen base quantized to NF4 with double quantization, BF16 compute on an appropriate GPU, `prepare_model_for_kbit_training`, explicit targets, gradient checkpointing and disabled training KV cache. Verify that expert linears actually convert to the expected 4-bit modules. Estimate 24–48 GB for shorter sequences and attention-only QLoRA; **48–80 GB or more** for longer sequences/all-expert adapters. BF16 attention-only LoRA may start on one 80 GB GPU with checkpointing; all-expert/long-context BF16 training may require two 80 GB GPUs or sharded/offloaded training. These are conditional ranges; full 20k–30k-token training examples can materially exceed short-sequence estimates. Inference TP support is not proof of training sharding support. [PEFT quantization guidance](https://raw.githubusercontent.com/huggingface/peft/v0.18.0/docs/source/developer_guides/quantization.md).

PEFT supports adapter `save_pretrained` and loading onto a specified base; `merge_and_unload` is available for ordinary LoRA, with quantization-dependent limitations. Proposed robust export route: retain adapter separately, reload the original pinned BF16 base, merge into a new derivative, hash it, verify synthetic equivalence within declared numerical limits, then use the selected inference runtime. Avoid claiming direct all-expert vLLM adapter compatibility from its architecture support alone. No save/load or merge was exercised here. [PEFT checkpoint guidance](https://raw.githubusercontent.com/huggingface/peft/v0.18.0/docs/source/developer_guides/checkpoint.md).

Full accumulated-history refresh from **ORIGINAL BASE** is technically possible with this workflow: reload original revision, initialize a fresh adapter/optimizer, retrain over the entire permitted accumulated history, and never continue from a previously adapted/merged base. Practical cost is unverified because history length, update frequency and GPU throughput are unknown and project evidence was not read. Estimate refresh cost later from total training tokens / measured training tokens per second, adding loading and validation. Cloud availability alone does not establish an affordable refresh schedule.

## 13. Protocol compatibility

Read only normative policy/framing helpers, not candidate inventories. Policy SHA-256 remains `d93f5136339153e65e35ef720333e21260292bc680f2cd3cfe608dfa46939a3b`. P/K/H message construction and exact K reuse are demonstrated synthetically. H=0 is truly omitted; lane framing and BC ownership follow existing code. Generation reserve remains 2048. No protocol tuning occurred.

No-read generation is achievable by sending only prepared token IDs to a model worker without tools or product mounts, but that isolation is not implemented/certified here. Complete replacement output is the existing SYSTEM instruction and parser contract; model compliance is not demonstrated without generation. Deterministic provenance needs the final weight/adapter content hashes, worker/container identity and runtime certificate. Actual tokenizer normalization and template identity are recorded. No silent truncation occurred in performed tests. Common admission and reference-output preflight remain required under the unchanged protocol; synthetic checks do not admit actual tasks or establish semantic context sufficiency.

This tokenizer-only check ran Python **3.12.14**. Official policy parsing requires **CPython 3.11.9 / Unicode 14.0**; its full validation was not executed or bypassed. Use the required parser environment separately from the inference worker and certify the boundary.

## 14. Synthetic generation performed?

**NO.** Tokenizer/template/capacity checks only. No checkpoint weights loaded.

## 15. Model/project benchmark tasks inspected?

**NO.** Upstream architectural/usage/license metadata and runtime sources were inspected; model-card performance graphics/tasks were not analyzed. No A/B/M/C/BC benchmark execution and no Step 8K-B rerun.

## 16. Candidate artifacts inspected?

**NO.** No candidate inventory, dispositions, selected candidates or product snapshots were opened. The synthetic names and records were invented for this preflight.

## 17. Adaptation experiment performed?

**NO.** No project-data training or synthetic adapter training. Architecture support was assessed from versioned first-party sources and tensor-name metadata.

## 18. Files modified

Only a new `experiments/model_preflight/qwen3_coder_30b_a3b/` area was created: this report; fetch/verification scripts; exact upstream metadata/tokenizer snapshots; upstream/source/weight/artifact manifests; synthetic message/token fixtures; checks/identity/environment/hardware JSON; tokenizer dependency lock; proposed-runtime JSON; local ignore file; isolated dependency directory. `artifact_manifest.json` inventories every persistent non-dependency file and hash, excluding itself. Dependencies are locally ignored and documented in the lock; the project virtualenv was not modified.

`experiments` is already excluded by the frozen policy; no normative artifact, product repository, root ignore rule, candidate artifact or tracked file was changed. No commit was made; no model or run profile was frozen.

## 19. Remaining verification

1. Provision sufficiently large Linux GPU/RAM/storage infrastructure; retrieve exact shards and verify upstream-declared hashes. Resolve a complete compatible binary dependency lock/image digest.
2. Load the exact BF16 checkpoint with the proposed offline runtime; verify all effective sampling controls, exact prompt IDs, explicit native terminal set, no truncation/clipping/context shift, no tools/reads/retries and fresh-sequence isolation.
3. Run candidate-blind natural-terminal and forced-length generation probes; retain token IDs, output bytes, finish/stop reasons and terminal accounting. Test repeated requests and fresh processes on fixed hardware; record numerical determinism limits.
4. Repeat tokenizer/reference/admission verification with the required policy parser environment and certify model/tokenizer/template/profile identities. No actual benchmark admission occurs at this stage.
5. Run a tiny synthetic adapter forward/backward/save/reload cycle on the exact model; test targeted expert coverage, BF16 merge/export and serving round trip. Validate NF4 conversion separately if QLoRA is selected.
6. Measure load time, synthetic prompt latency, inference/training throughput, peak RAM/VRAM and refresh cost. Establish practical full-history refresh feasibility from ORIGINAL BASE before adaptation eligibility is accepted.

## 20. Recommendation

Keep this model as a provisional candidate for infrastructure validation. Its observed tokenization and synthetic capacities do not require protocol changes. Do not freeze it or declare Study-1 shortlist eligibility until the deployment and adaptation checks above resolve the remaining uncertainties. The local 4 GB GPU environment cannot establish those facts.
