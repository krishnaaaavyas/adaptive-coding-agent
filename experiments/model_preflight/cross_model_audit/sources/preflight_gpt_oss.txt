# STEP 8K-B.1G1C — GPT-OSS-20B MODEL PREFLIGHT

Candidate-blind static/model-protocol preflight, 2026-10-03 (Asia/Calcutta). Workspace HEAD: `7fcdecbe26f4fd01138edf8f58c02ce4b947db0b`, matching the requested HEAD. Frozen requirements were evaluated without changing them. MEASURED means an operation performed here; SOURCE-SUPPORTED means pinned source evidence; ESTIMATED means arithmetic or infrastructure planning. None of these substitutes for an externally certified serving/training run.

## 1. Verdict

**INCONCLUSIVE — INFRASTRUCTURE VERIFICATION REQUIRED**

Exact tokenizer and candidate-blind input serialization/capacity checks succeeded. The model is not certified eligible for Study-1. No weights were loaded, no serving implementation was executed, and no adapter lifecycle was tested. There is also an unresolved **protocol output-boundary question**, not just a GPU provisioning issue: draft3's single-target output is the entire completion, while normal Harmony output can contain substantive analysis followed by final content. Silently passing only final content to the frozen parser would not establish conformance. Sections 10–11 and 15 specify this blocker; accepting a limitation cannot waive a frozen requirement.

No static evidence establishes that Harmony necessarily adds different repository/task information across the five conditions. No conclusion that gpt-oss can never satisfy the protocol is justified from these serialization-only checks: actual channel behavior and the certified transport's definition of completion remain unverified.

## 2. Exact model identity

Authoritative checkpoint: [openai/gpt-oss-20b at immutable revision 6cee5e81ee83917806bbde320786a8fb61efebee](https://huggingface.co/openai/gpt-oss-20b/tree/6cee5e81ee83917806bbde320786a8fb61efebee). The Hub head was used only to discover this revision; acquisition URLs and the saved identity use the immutable SHA. A reproduction uses the saved revision rather than resolving a moving branch again.

MEASURED downloaded-file SHA-256 values:

| Artifact | SHA-256 |
|---|---|
| config.json | `3a2a26ded679375b7928ddeca59764df7cea83220c1961035f6d6e232659e9ce` |
| generation_config.json | `f9970ada892d2d1f72e3ed0a6535ccebadd11897318794ca671d8c7014c957da` |
| tokenizer.json | `0614fe83cadab421296e664e1f48f4261fa8fef6e03e63bb75c20f38e37d07d3` |
| tokenizer_config.json | `9279e942392b742d633c7adbb89ebe002c98399db8926a7af5125c726f404070` |
| special_tokens_map.json | `dd5e191d20c12d2fee1da5bae14ca1db0f5f4215300af691f23cdee97120a293` |
| chat_template.jinja | `a4c9919cbbd4acdd51ccffe22da049264b1b73e59055fa58811a99efbd7c8146` |
| model.safetensors.index.json | `0e085b977c4c9942f85938828e8c989ed7d5cdabf852e4da6a67c116cd502cd1` |
| LICENSE | `58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd` |
| README.md / architecture metadata | `03c2fcf292549176757b85c911e7dcf527aef3e4241d64b6caec94af3ecf3ac2` |

`upstream_manifest.json` binds URLs, sizes and hashes. `weight_manifest.json` records the three root HF shards and the alternative `original/model.safetensors` package, their upstream LFS SHA-256 identities and sizes. Root shard names are preserved literally, including the upstream zero-based numbering. No full weight bodies, header ranges, or tensor payloads were downloaded; upstream weight hashes are SOURCE-SUPPORTED, not locally verified hashes.

## 3. License

The pinned [LICENSE](https://huggingface.co/openai/gpt-oss-20b/blob/6cee5e81ee83917806bbde320786a8fb61efebee/LICENSE) is Apache License 2.0. The artifact was downloaded and hashed. Its identity is established; a future distribution must retain its applicable notices and attribution. This preflight did not redistribute model weights.

## 4. Architecture

SOURCE-SUPPORTED by the [checkpoint config](https://huggingface.co/openai/gpt-oss-20b/blob/6cee5e81ee83917806bbde320786a8fb61efebee/config.json), [model card](https://huggingface.co/openai/gpt-oss-20b/blob/6cee5e81ee83917806bbde320786a8fb61efebee/README.md), and [pinned Transformers implementation](https://github.com/huggingface/transformers/blob/753d61104116eefc8ffc977327b441ee0c8d599f/src/transformers/models/gpt_oss/modeling_gpt_oss.py):

| Property | Finding |
|---|---|
| Architecture / type | GptOssForCausalLM / gpt_oss, decoder-only causal MoE |
| Parameter scale | Card: approximately 21B total, 3.6B active; source-shape arithmetic: 20,914,757,184 total |
| Layers / width | 24 / 2,880 |
| Experts | 32 per layer, top 4 routed per token; fused gate/up and down projections, expert biases, biased router |
| Attention | 64 query heads, 8 KV heads, head dimension 64; GQA; attention sinks; biased q/k/v/o |
| Attention pattern | 12 full and 12 sliding layers, alternating; sliding window 128 |
| Positional encoding | YaRN, original 4,096 positions, factor 32; max_position_embeddings 131,072 |
| Native checkpoint format | MXFP4 expert projection blocks/scales; other tensors BF16 |
| Activation recommendation | BF16 in OpenAI's reference documentation |
| Vocabulary | Model output dimension 201,088; HF base BPE 199,998 entries plus 21 added token definitions |

The exact total above is ESTIMATED by enumerating complete source shapes, including untied input/output embeddings, attention biases/sinks, expert biases, routers and norms (`architecture_arithmetic.json`); it is not a loaded-tensor census. The rounded active count is reported separately rather than claiming an undocumented exact active-count convention. Neither active count nor number of routed experts was used to infer resident weights or throughput. [OpenAI's pinned reference](https://github.com/openai/gpt-oss/blob/7b583341fe16729127f6d5b94a7b09ccae97e1a1/README.md) explains the native MXFP4/BF16 representation and BF16 reference loading.

## 5. Tokenizer/Harmony identity

MEASURED: exact local HF artifacts loaded with Transformers 4.57.6 / tokenizers 0.22.2, PreTrainedTokenizerFast, trust_remote_code=False, offline. Official `openai-harmony==0.0.8`, `HarmonyEncodingName.HARMONY_GPT_OSS` / `HarmonyGptOss`, also loaded. Python was CPython 3.12.14 on Windows; the full normative CPython 3.11.9/Unicode 14.0 parser was not executed. `tokenizer-requirements.lock.txt` and `tokenizer_environment.json` list all actual dependencies. Harmony additionally used pydantic 2.13.5, pydantic-core 2.46.5, annotated-types 0.8.0 and typing-inspection 0.4.4. Existing Qwen preflight tokenizer dependencies were read-only; newly installed Harmony dependencies are confined here.

All 199,998 mergeable token byte sequences and their rank IDs were compared exhaustively with official o200k_base data: identical. Vocabulary data SHA-256: `446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d`; canonical HF vocabulary mapping hash: `c473d7dea3722ad7fe8f6abf41274a326ee1ad25d1aba9034a36a9c663145d0e`. The original encoding data is archived in `encoding_cache/` and bound by `encoding_data_manifest.json`. All 256 byte tokens are present. Backend normalization is null: decomposed/precomposed NFC-sensitive text produces different IDs; no NFC conversion was added.

BOS 199998 (`<|startoftext|>`), EOS 200002 (`<|return|>`), pad 199999 (`<|endoftext|>`). Encoding empty text gives no tokens; ordinary reference text has no inserted BOS/EOS. Padding and truncation were disabled in measurements. `tokenizer_identity.json` retains every HF added-token definition and official Harmony special-token mapping; model output dimension, HF tokenizer length and official reserved-token namespace are distinct identities. Reserved aliases are not assumed to be interchangeable rendered strings.

Harmony source is pinned at [abd677f7ac962629c808197caa1feb9e3e95d2b0](https://github.com/openai/harmony/tree/abd677f7ac962629c808197caa1feb9e3e95d2b0). Version 0.0.8 wheel/sdist are archived with PyPI SHA-256 verification. Installed Python source equals pinned GitHub/sdist after CRLF-to-LF conversion; raw hashes differ solely because of those line endings. Installed compiled extension SHA-256 is `c81b1885e1920c839e9f75eb0c1e7b60b359c4cf00491c98bc3b3d750b40c595`. This is a binary identity, not a reproducible-build attestation. Source/binary details are in the Harmony manifests.

## 6. Harmony compatibility

There is no separately numbered minimum Harmony wire-spec version established by the authoritative checkpoint artifacts. The required specification is gpt-oss Harmony with its encoding/control identities; this report pins checkpoint artifacts, official spec snapshot and implementation 0.0.8 rather than inventing a required version number. The [pinned OpenAI Harmony guide](https://github.com/openai/openai-cookbook/blob/0eac1447d4e24d06e47c459ca5e98f248b9413cf/articles/openai-harmony.md) establishes role/channel semantics.

Model-specific serialization: Harmony supports system, developer, user, assistant and tool roles. The upstream template maps the supplied conventional system instructions into developer instructions. User content is the frozen `[PUBLIC_TASK] + J(P) + K + H` message. Analysis is assistant reasoning; final is the user-facing answer; commentary is also a recognized channel. Channel names and roles are ordinary text between special structural tokens, not single special tokens themselves. Generation prefix is exactly `<|start|>assistant` (IDs `[200006,173781]`), leaving channel/header selection to the model. No forced final or analysis prefix was adopted.

| Structural token | ID | Meaning |
|---|---:|---|
| `<|start|>` | 200006 | Message start |
| `<|channel|>` | 200005 | Channel metadata separator |
| `<|message|>` | 200008 | Header/body separator |
| `<|end|>` | 200007 | End one message; continue the assistant turn if applicable |
| `<|return|>` | 200002 | Finish assistant response |
| `<|call|>` | 200012 | Handoff/action boundary |

The pinned Jinja template injects identity, knowledge cutoff 2024-06, current date, default medium reasoning and valid-channel instructions. They are real prompt content, not invisible model metadata. Tools/builtin_tools are absent/empty. The Jinja clock is nondeterministic across dates. Measurement locked the date to 2026-10-03 only for reproducible fixtures; no eventual study date/effort was frozen.

The proposed serializer is the official **typed Harmony renderer**, with explicit SystemContent metadata, unchanged SYSTEM text in DeveloperContent and unchanged user message as TextContent. The [pinned renderer](https://github.com/openai/harmony/blob/abd677f7ac962629c808197caa1feb9e3e95d2b0/src/encoding.rs) encodes TextContent as ordinary text. This preserves literal native delimiters in P/K/H as data. By comparison, flat Jinja-rendered-string tokenization promotes recognized delimiter spellings inside data into control IDs. Both paths were measured and retained; the typed path differs by two developer trailing LF bytes and by treatment of literal native delimiters. This is a disclosed model-specific serializer choice, not a rewrite of P/K/H. Display strings are not a sufficient round-trip format for literal delimiters: retain the typed conversation and exact IDs, and send IDs directly without re-encoding the display string with all special tokens allowed.

PROTOCOL SEMANTICS: `information_semantics_checks.json` proves A=P+K, B adds episodic H, M descriptive H, C confirmed-rule H, BC episodic+rule H. P/K hashes are identical across conditions; BC keeps its fixed total/lane budgets. All wrappers/default metadata are condition-independent. No condition labels, additional repository information, tool state or history are inserted into the five-condition requests. The historical-assistant template fixture is a separate serialization test, not a proposed experimental request. Empty registry produces empty H in all conditions.

## 7. Run-profile compatibility table

Classifications below distinguish pinned implementation support from actual deployment certification. SUPPORTED EXACTLY refers to exposed, source-verified behavior; no serving control was exercised against loaded weights. AMBIGUOUS means the end-to-end obligation remains unverified. No unsupported setting has been replaced with a changed treatment or budget.

| Frozen requirement | Classification | Proposed mapping / evidence and limit |
|---|---|---|
| Greedy decoding | SUPPORTED EXACTLY | vLLM temperature=0 selects greedy; bitwise determinism is separately AMBIGUOUS across hardware/kernels/TP |
| Deterministic generation | AMBIGUOUS | Greedy+seed does not prove repeated-token equality on the actual deployment |
| temperature 0 | SUPPORTED EXACTLY | `temperature=0.0` |
| top_p 1 | SUPPORTED EXACTLY | `top_p=1.0`; greedy source also normalizes to 1 |
| top_k disabled | SUPPORTED WITH VERIFIED EQUIVALENT | Native `top_k=0` means disabled; pinned source explicitly verifies this |
| repetition penalty 1 | SUPPORTED EXACTLY | `repetition_penalty=1.0` |
| frequency penalty 0 | SUPPORTED EXACTLY | `frequency_penalty=0.0` |
| presence penalty 0 | SUPPORTED EXACTLY | `presence_penalty=0.0` |
| seed 0 when supported | SUPPORTED EXACTLY | `seed=0`; it is not a bitwise-determinism guarantee |
| No text stops | SUPPORTED EXACTLY | `stop=[]`; native token terminals only |
| 2048 TOTAL generated tokens | SUPPORTED EXACTLY | One `max_tokens=2048`; analysis, final, generated headers and terminal all consume this one counter |
| One completion | SUPPORTED EXACTLY | `n=1`; greedy requires one |
| No retry | AMBIGUOUS | Single offline engine call and no application retry loop proposed; actual wrapper/isolation not certified |
| No context shifting | AMBIGUOUS | Fixed max_model_len=32768 and reject overflow; actual engine config/state must be attested |
| No clipping | AMBIGUOUS | Exact pre-rendered IDs supplied; prompt-ID parity must be checked in real runtime |
| No truncation | SUPPORTED EXACTLY | `truncate_prompt_tokens=None`, no tokenizer truncation; real transport parity remains unmeasured |
| No tools | SUPPORTED WITH VERIFIED EQUIVALENT | No definitions, executor or tool loop in proposed offline path; any emitted handoff is retained/rejected, never executed |

Source evidence: [vLLM SamplingParams](https://github.com/vllm-project/vllm/blob/89a77b10846fd96273cce78d86d2556ea582d26e/vllm/sampling_params.py), [input processor](https://github.com/vllm-project/vllm/blob/89a77b10846fd96273cce78d86d2556ea582d26e/vllm/v1/engine/input_processor.py), and [engine configuration](https://github.com/vllm-project/vllm/blob/89a77b10846fd96273cce78d86d2556ea582d26e/vllm/engine/arg_utils.py). Typed requested/effective arguments, native terminal handling and external profile certificate remain future verification. Do not inherit upstream `do_sample=true`. Disable generation-config sampling overrides, prefix reuse, speculative decoding and multi-request batching for initial certification. Source support is not an official run-profile certificate.

## 8. Reasoning-effort compatibility

SOURCE-SUPPORTED controls are low, medium and high, serialized as `Reasoning: <value>` in system metadata. Medium is the authoritative default. No mandatory nondefault value was found. **Medium is the single candidate-blind proposal for later certification**, because it retains the upstream default, not because of benchmark performance. This report does not adopt or freeze it; fixture use of default medium is a measurement convention.

This is prompt-encoded inference policy, not a separate sampler-only switch. It adds a reasoning instruction to the model's information content, but adds no repository/task/evidence information and must remain identical across all five conditions. Varying it by condition would add a treatment. Low/high selection based on final-answer fit or benchmark outcomes is not authorized. No extra analysis allowance, suppressed analysis, forced final prefix, or separate answer budget was adopted. [Pinned SystemContent controls](https://github.com/openai/harmony/blob/abd677f7ac962629c808197caa1feb9e3e95d2b0/python/openai_harmony/__init__.py).

## 9. Context/capacity verification

MEASURED: same candidate-blind semantic constructors as the Qwen preflights, independently encoded. Four families at exact byte ceilings and one byte below, each across five conditions, plus five empty-registry cases: **45/45 PASS**. P is canonical J(P) UTF-8 bytes, K is packed K bytes, H is packed H bytes; P<=4096, K<=12288, H<=4096. A H is empty; BC's two owned lanes remain <=2048 each. Full 2048 TOTAL generation reserve is included without clipping/truncation.

| Family | Largest input tokens | Input + 2048 | Largest serialized bytes | Result |
|---|---:|---:|---:|---|
| ASCII/punctuation | 20,496 | 22,544 | 21,417 | PASS |
| Multilingual Unicode | 7,686 | 9,734 | 21,417 | PASS |
| NFC-sensitive expansion input | 18,474 | 20,522 | 21,417 | PASS |
| Code/literal delimiters | 6,192 | 8,240 | 21,417 | PASS |

`capacity_checks.json` and CSV record every case's semantic byte counts, K/H hashes, serialized bytes, IDs/hash, input count, reserve, proposed 32768 capacity, native 131072 capacity, and result. `synthetic/` retains both typed Harmony and upstream Jinja representations/IDs. Four repeated typed renderings and HF tokenizations were identical. HF flat-rendered IDs matched official Harmony raw encoding on these template fixtures; that does not make flat and typed serializers interchangeable for literal control spellings.

Typed fixed framing overhead is 937 bytes. With the fixture metadata fixed, maximum raw serialized byte bound is 21417; byte BPE has no normalization expansion, so the conservative byte bound plus reserve is 23465, below 32768. This bound is conditional on exactly that serializer/metadata. Runtime allocation of 32768 is proposed, not measured. Common admission must still independently tokenize each real certified input and reference output before outcomes; no candidate population was read or admitted here. Reference file token budget alone does not prove that analysis+headers+answer will fit in 2048.

## 10. Terminal/channel behavior

SOURCE-SUPPORTED: config EOS 200002; [generation config](https://huggingface.co/openai/gpt-oss-20b/blob/6cee5e81ee83917806bbde320786a8fb61efebee/generation_config.json) terminal set `[200002,199999,200012]`. `<|end|>` 200007 terminates analysis messages without finishing the response: stopping there would wrongly omit final output. `<|return|>` ends the assistant response; `<|call|>` hands off. The official renderer's assistant-action stop set is `[200002,200012]`; the HF generation-config pad/endoftext terminal is separately disclosed. The proposed runtime explicitly preserves the upstream terminal union, rather than treating every special token as EOS.

Analysis is exposed in the generated stream; there is no separate invisible reasoning pool in the proposed local token-ID path. All generated tokens consume the same max_tokens counter, including channel metadata, analysis, final and terminal. A cap can occur during analysis or an incomplete final message; a handoff/endoftext can occur before any final. No retry or second generation is permitted to recover a missing final.

[Pinned vLLM stopping](https://github.com/vllm-project/vllm/blob/89a77b10846fd96273cce78d86d2556ea582d26e/vllm/v1/core/sched/utils.py) checks native EOS/explicit token stops before the length condition. Consequently a native terminal at token 2048 can yield stop rather than length. Record total count, last ID, finish_reason and stop_reason together; do not infer token-limit status from decoded text or length alone. A verified length cap maps to output_capacity_failure under draft3, including an analysis-only cap. Preserve its raw output facts even if no artifact can be extracted.

[CompletionOutput/RequestOutput](https://github.com/vllm-project/vllm/blob/89a77b10846fd96273cce78d86d2556ea582d26e/vllm/outputs.py) expose prompt/generated IDs, finish reason and stop reason. Primary EOS may have null stop_reason. Exact raw IDs can be retained; decode with strict UTF-8 or retain original decoded bytes, not replacement-character decoding. Unknown/reserved IDs remain auditable and must not be silently skipped. Actual terminal retention, cap-boundary behavior and decode parity were not measured. Four hand-authored token-stream parser checks were performed; these were not model generation.

## 11. Complete-replacement extraction

Candidate-blind conservative rule for later transport certification:

1. Retain the complete generated ID vector and hashes, typed parsed message spans, raw bytes where decodable, total generated count and finish/stop information before extraction.
2. Validate the full assistant stream structurally; distinguish the one terminal from message boundaries. Never use a regex on display text to find a final channel, and never apply blanket skip_special_tokens.
3. Reject handoff/tool output, malformed/ambiguous channels, multiple competing final artifacts and invalid UTF-8. A length-capped stream remains output_capacity_failure, regardless of apparent code fragments.
4. A single final body's bytes are only a **proposed** artifact projection. Remove only channel/header serialization and verified terminal framing; retain its exact content, whitespace and BOM, then apply frozen normalization/header parsing. No fence removal, explanatory-text removal, patch conversion, concatenation repair or retry.
5. If any analysis/commentary contains substantive content, preserve it and mark final-only extraction as **not certified under the frozen entire-completion rule**. This report supplies no permission to discard it. An empty/non-substantive structural message also needs a verified transport boundary before acceptance.

The frozen JSON output contract says single-target is the entire completion, with only CRLF/CR normalization; `harness/context_policy/protocol.py::completion` performs that handling. It has no analysis/final exception. Passing the whole decoded Harmony stream produces channel syntax/reasoning in the proposed source file; passing only final content excludes substantive generated text. Audit sidecars make exclusion explicit but do not by themselves make it conformant. The hand-authored analysis+final fixture demonstrates this distinction; it does not establish real model behavior frequency.

Before admission, certify that the existing frozen notion of completion already permits this transport-level final projection. If it does not, ordinary analysis-bearing output is incompatible with that extraction requirement. Do not amend draft3, force final-only generation or change effort/budget to obtain a pass. A GPU test alone cannot resolve a normative interpretation.

## 12. Proposed runtime

**ONE proposed official upstream runtime: Linux/CUDA vLLM 0.16.0**, source `89a77b10846fd96273cce78d86d2556ea582d26e`, using its offline LLM engine and pre-rendered prompt IDs. OpenAI's [pinned reference README](https://github.com/openai/gpt-oss/blob/7b583341fe16729127f6d5b94a7b09ccae97e1a1/README.md) includes vLLM integration. Choice is based on exposed IDs/controls and native gpt-oss support, not benchmark performance.

The [pinned gpt-oss implementation](https://github.com/vllm-project/vllm/blob/89a77b10846fd96273cce78d86d2556ea582d26e/vllm/model_executor/models/gpt_oss.py) includes MXFP4 loading, attention-sink/full/sliding implementation and SupportsLoRA with packed qkv mapping. Proposed capacity 32768, one sequence, TP=1 initially on a suitable GPU, dtype BF16 for nonquantized compute with native MXFP4 weights. Supply exact IDs; check returned prompt IDs. Use no chat server/agent loop that can re-template, strip reasoning or execute tools. No network model fetch during inference: use the verified local immutable snapshot.

Runtime source dependencies pin torch 2.9.1 and FlashInfer 0.6.3; Transformers range includes 4.57.6. Actual CUDA/driver, kernels, container/wheel hashes, topology and fully resolved runtime environment are unverified. vLLM was neither installed nor launched. Proposed arguments are archived in `proposed_runtime.json`; it is explicitly not a signed or validated run profile. No competing runtime was chosen. OpenAI torch/BF16 and Triton reference paths were evaluated from source as alternatives; convenience chat/Responses examples have tool/history layers that are unsuitable without separate isolation certification.

## 13. Resource requirements

SOURCE-SUPPORTED checkpoint storage: **13,761,316,904 bytes** for the three selected HF shards (~13.761 GB / 12.82 GiB); index tensor payload **13,761,264,768 bytes**. Alternative original-format file: 13,761,300,984 bytes. Downloading both packages would duplicate the logical checkpoint, not halve or expand the model's parameter count. Full local weight storage/verification was not measured. OpenAI reports native gpt-oss-20b inference within 16GB; that is not a measured guarantee for this 32768-capacity deployment.

ESTIMATED source-shape BF16 weight payload: **41,829,514,368 bytes / 38.96 GiB**, before runtime/cache/activation/loading overhead. Resident native memory must include all 32 experts, not only 4 active experts. Conservative 32768 KV arithmetic for full layers is 0.75 GiB, plus about 3 MiB for 128-token sliding layers if the implementation retains only the window; actual cache allocation/workspaces differ.

| Use | ESTIMATED starting infrastructure | Qualification |
|---|---|---|
| Native MXFP4 inference | 24–48GB supported GPU; 32/48GB provides more headroom than 16GB | Must verify selected kernels, exact 32768 allocation and overhead; native 16GB claim alone insufficient |
| BF16 inference | 1x80GB GPU, or verified sharding across 2x48GB | ~39 GiB weights plus cache/workspaces; 48GB is tight |
| BF16 attention LoRA | 1x80GB H100-class cloud GPU as a starting point | Short-sequence feasibility has official recipe support; study-length memory not measured |
| Broader expert LoRA | 1x80GB or multiple 80GB GPUs, depending on sequence/kernel/checkpointing | Dense fallback expert training can greatly increase activations; fit is unverified |
| Full-parameter training | Distributed multi-GPU cloud infrastructure; roughly 8x80GB starting planning class | Conventional states alone can approach 312 GiB at 16 bytes/parameter, before activations |
| Host / storage | 64–128GiB RAM; 100–150GB free for base, BF16 exports and working copies | Streaming may lower host peaks; merge/export/loading peaks must be measured |

Supported native quantization is MXFP4, with packed expert blocks and scales. Ordinary generic NF4 QLoRA is not established for the fused raw-parameter experts at the pinned training implementation; no additional quantized checkpoint was substituted. No throughput or rebuild-time estimate was inferred from active parameters.

MEASURED local inventory: RTX 2050 **4096 MiB**, driver 581.86; RAM **25,463,480,320 bytes (~23.71 GiB)**; free disk approximately **22.59 GiB** at final serialization check. The selected native checkpoint alone could fit available disk, but local GPU cannot hold advertised native weights and local RAM cannot hold the BF16 base. Loading, exporting and training are not currently feasible on this machine. Remote/cloud feasibility is a source-supported/estimated path, not a measured deployment result.

## 14. LoRA/QLoRA feasibility

Classification: **PRACTICAL WITH CLOUD GPU** for the source-supported BF16 LoRA route; actual study-length lifecycle is unverified. Native MXFP4 QLoRA/broad quantized expert training is **EXPERIMENTALLY DIFFICULT** at these pins and is not a certified route.

Pinned Transformers 4.57.6 and PEFT 0.18.0 (`77daa8d3b7decf2b40238ab47e2c1bd0f26c7749`) provide the following source evidence. Attention exposes nn.Linear q_proj/k_proj/v_proj/o_proj. Specify full matching paths `model.layers.<i>.self_attn.{q_proj,k_proj,v_proj,o_proj}` explicitly. Sinks, biases, router, norms, embeddings and lm_head remain frozen unless a separate adaptation design authorizes them. Rank 16 and these target sets are planning examples, not adopted training settings.

Experts are raw 3D nn.Parameter tensors: gate_up_proj `[32,2880,5760]`, down_proj `[32,2880,2880]`, with separate frozen biases. They require PEFT `target_parameters`, e.g. `model.layers.<i>.mlp.experts.gate_up_proj` and `.down_proj`; ordinary all-linear targeting does not include them. Router has its own raw weight/bias and is excluded. [PEFT parameter targeting](https://github.com/huggingface/peft/blob/77daa8d3b7decf2b40238ab47e2c1bd0f26c7749/docs/source/developer_guides/lora.md) is experimental: 2D/3D supported, expert dimension assumed first, multiple simultaneous parameter adapters unsupported. Pinned ParamWrapper also rejects nonzero lora_dropout, DoRA and lora_bias for these targets. Fresh sequential rebuilds must unload all preceding wrappers/adapters.

ESTIMATED adapter parameters from pinned source shapes, using r*(input+output) per attention matrix and experts*r*(input+output) for fused expert tensors:

| Rank-16 target set | Parameters |
|---|---:|
| All attention q/k/v/o only | 7,962,624 |
| All 24 layers' expert gate_up/down only | 176,947,200 |
| Attention plus all expert gate_up/down | 184,909,824 |

Broader adapter BF16 payload is about 352.7 MiB; conventional 16-byte/parameter training-state planning is about 2.76 GiB, in addition to the full base and activations. The count is not a measured adapter instantiation. Top-4 routing gives sparse expert coverage in normal execution; the pinned Transformers training fallback can materialize dense expert work, so inference sparsity does not establish training memory/performance.

The [pinned official fine-tuning notebook](https://github.com/openai/openai-cookbook/blob/0eac1447d4e24d06e47c459ca5e98f248b9413cf/articles/gpt-oss/fine-tune-transfomers.ipynb) uses BF16 dequantization and PEFT parameter targeting on an 80GB H100. That is feasibility evidence, not a recipe adopted here: its task, length, rank, targets and reported timing were not used as study settings or performance estimates. The [pinned MXFP4 quantizer](https://github.com/huggingface/transformers/blob/753d61104116eefc8ffc977327b441ee0c8d599f/src/transformers/quantizers/quantizer_mxfp4.py) declares native quantized training unsupported and directs dequantization; that path removes quantization config after loading. Unsupported kernels may trigger BF16 fallback, which must never be mistaken for a 16GB native load.

Generic bitsandbytes Linear4bit replacement targets modules, not these raw expert parameters: attention-only 4-bit conversion cannot justify a whole-base 4-bit memory assumption. No native MXFP4 backward or architecture-wide NF4 conversion was verified. BF16 dequantized LoRA is the supported proposed training route.

PEFT [save/reload](https://github.com/huggingface/peft/blob/77daa8d3b7decf2b40238ab47e2c1bd0f26c7749/src/peft/peft_model.py), [adapter serialization](https://github.com/huggingface/peft/blob/77daa8d3b7decf2b40238ab47e2c1bd0f26c7749/src/peft/utils/save_and_load.py) and [ParamWrapper merge](https://github.com/huggingface/peft/blob/77daa8d3b7decf2b40238ab47e2c1bd0f26c7749/src/peft/tuners/lora/layer.py) exist at the pin. Source support does not verify gradients, reload/merge parity or vLLM direct loading of trained expert-parameter adapters. Merge into a fresh verified BF16 dequantization of ORIGINAL BASE is a possible export path; requantizing a merged expert tensor introduces another numerical/identity step and is unverified. The notebook's illustrative reload code is not proof of native-quantized merge correctness.

ORIGINAL BASE rebuild feasibility is architectural: retain the immutable original snapshot; for every authorized rebuild start a fresh base load/process, adapter, RNG and optimizer; never chain prior adapters or use a previously merged base. Save independently, reload against the original identity, audit target names/shapes and verify output parity. Dequantization, loading costs, initialization, gradients, state isolation, save/reload, merge/export and two successive fresh rebuilds have not been measured. No adaptation was performed.

## 15. Protocol compatibility

Input/treatment semantics: no required modification identified for the typed Harmony path. P/K/H contents, canonical bytes/hashes, five conditions, fixed-total BC lanes, ceilings and common admission remain intact. Model wrappers and constant reasoning/channel metadata are serialization/inference-policy content, not condition-specific evidence. A differing or live-clock header across conditions would invalidate the run; exact metadata must be frozen later. Literal native markers are preserved as data through typed ordinary-text rendering, not escaped by changing P/K/H bytes.

Generated-token accounting: a single 2048 limit can include all Harmony output; no extra reasoning reserve is needed or authorized. Output conformance is **unresolved** for substantive analysis-bearing streams. Model-specific role/control serialization is permitted in principle, but declaring analysis non-completion is not automatically licensed by the frozen parser. Signed runtime profile, raw-output integrity and that completion boundary must be independently certified. The conservative preflight does not grant eligibility or a protocol amendment.

Artifact exclusion was verified from frozen `EXCLUDED_DIRS`, which includes experiments; no product tree was traversed to establish exclusion. No policy, harness or product file was modified. Full external certification/admission was not executed.

## 16. Cross-model methodological comparability

**UNRESOLVED.** Harmony does not intrinsically require different input treatments, and spending part of the common 2048 total budget on analysis is a disclosed model difference, not permission to allocate more tokens. The unresolved completion projection and its effect on output/reference admission prevent claiming a fully fair, certified comparison now. Under strict entire-generated-completion interpretation, selecting final while excluding substantive analysis is incompatible; if the existing protocol already allows a verified final-message transport boundary, it still needs source/transport certification. Do not alter admission populations based on observed reasoning/final fit.

Only earlier upstream config/tokenizer/weight metadata and candidate-blind constructors were used for factual comparison. No coding-quality rankings or benchmark outcomes were consulted.

| Dimension | Qwen3-Coder-30B-A3B | Qwen3-Coder-Next | gpt-oss-20b |
|---|---|---|---|
| Serialization | Qwen template, no Harmony channels in proposed path | Qwen template, no Harmony channels in proposed path | Typed Harmony with explicit reasoning/final boundaries |
| Native context | 262144 | 262144 | 131072 |
| Layer architecture | Full-attention MoE | Full/linear-attention hybrid MoE | Full/sliding GQA, attention sinks, MoE |
| Generated-token accounting | One total 2048 stream | One total 2048 stream | Same total, including analysis and channel/control tokens |
| Base footprint | ~30B-class BF16 checkpoint | ~80B-class BF16 checkpoint | ~21B logical parameters; native mixed MXFP4/BF16 ~13.761GB shards |
| Runtime complexity | MoE serving and exact template/control verification | Hybrid attention state plus MoE | Harmony parser/boundary verification plus native quantized MoE |
| Expert adaptation at pinned Transformers | Per-expert linear projections | Routed/shared expert linear projections | Fused raw 3D parameters, experimental parameter adapters |
| Training infrastructure | Prior preflight requires substantial cloud GPU memory | Larger base requires substantially more memory/sharding | BF16 cloud LoRA plausible; native quantized training unsupported at pin |

These are factual implementation/footprint differences; identical token counts, FLOPs, answer-token allowances or training costs are not claimed. `factual_comparison.json` records exact earlier artifact identities. No throughput was inferred from active parameters.

## 17. Synthetic generation performed?

**NO model generation.** Synthetic input construction/rendering/tokenization: YES, 58 saved input fixtures (8 general serialization tests, 5 distinct information-semantics tests, 45 capacity cases). Four hand-authored output-channel parser examples: YES. No sampled model completion or inference test occurred.

## 18. Model/project benchmark tasks inspected? NO

**NO.** Only frozen protocol framing and candidate-blind synthetic preflights were read locally. Upstream model cards and implementation/training documentation were acquired as authoritative artifacts; their performance claims were not used for compatibility selection. No model/project benchmark task instances were opened or executed. Step 8K-B was not rerun.

## 19. Candidate artifacts inspected? NO

**NO.** No candidate IDs, inventories, outcomes, dispositions, solutions or evaluators were inspected.

## 20. Adaptation experiment performed? NO

**NO.** No model was loaded, no training data was downloaded, no gradients/optimizer steps occurred, no adapter was instantiated or merged. Rank-16 counts are arithmetic only.

## 21. Files modified

Only new artifacts under `experiments/model_preflight/gpt_oss_20b/`: acquisition/check/finalization scripts; .gitignore; pinned upstream metadata/tokenizer/template/license/index; pinned implementation/specification sources and tokenizer distribution/encoding data; manifests; dependency/environment lock and isolated Harmony dependencies; synthetic fixtures and byte/token/hash checks; hardware/workspace audit; adapter/architecture estimates; comparison; proposed runtime; this report; final artifact inventory. `artifact_manifest.json` enumerates final paths, sizes and hashes, excluding installed dependencies/__pycache__ (Harmony installed source/extension hashes are retained separately).

Existing Qwen preflight artifacts remain unchanged. No tracked policy/harness/product modifications and no commit. All persistent preflight deliverables are here. Package-install temporary files and the initial library probe's default temporary encoding cache are runtime scratch, not study artifacts; subsequent operations use the archived directory-specific encoding cache.

## 22. Remaining verification

1. Resolve and certify the existing protocol's completion boundary for Harmony; substantive analysis must not disappear under an assumed final-only exception. If that exception is absent, record extraction incompatibility without changing draft3.
2. Provision suitable Linux/CUDA GPU/RAM/storage, pin the full runtime build/container/kernel identities and verify checkpoint bodies/LFS hashes when deployment verification is authorized.
3. Verify exact supplied/returned prompt IDs, untouched P/K/H, constant metadata/clock/effort and fresh sequence/no history/tool state. Freeze a single effort only during later certification, before any outcomes.
4. Perform authorized candidate-blind generation tests of analysis/final parsing, reserved IDs, UTF-8 integrity, raw token retention, native EOS/handoff/endoftext, and 2048 boundary precedence; prove the single total counter and no retries/truncation/shifting/clipping.
5. Verify greedy repeated-token behavior on pinned hardware/kernel/topology; document determinism limits and typed requested/effective controls in the externally authenticated profile.
6. Test a fresh ORIGINAL BASE BF16 LoRA lifecycle: actual target census, initialization, gradients, sequence-length memory, adapter save/reload and merge/export parity, then a second fully fresh rebuild. Separately certify any quantized export/training route; native MXFP4 training is unsupported at the chosen Transformers pin.
7. Run required parser/profile certification with CPython 3.11.9/Unicode 14.0 and independently freeze common pre-outcome input/reference admission across models. No candidate checks occurred here.

Reproduction: `fetch_evidence.py` uses saved immutable model/source pins; `supplement_sources.py` archives additional pinned source/distribution/encoding evidence; install the lock into directory-local dependencies; run `verify_synthetic.py` offline, `analyze_static.py`, then `finalize_artifacts.py`. Failed guessed source paths (404) are retained in source_manifest, with correct notebook/generate paths acquired; failed entries are not evidence. Python framing-only checks do not replace official parser validation.

## 23. Recommendation

Keep gpt-oss-20b outside the **verified** shortlist until the Harmony completion boundary, actual serving profile and fresh-base adaptation lifecycle are certified. Input serialization and capacity are feasible; BF16 cloud LoRA has a credible source-supported route. Local hardware cannot perform the required inference/training. Do not change treatments, budget, complete-replacement parsing or effort to obtain a pass, and do not run benchmark candidates or adaptation as part of this preflight.
