# STEP 8K-B.1G1D — CROSS-MODEL FEASIBILITY AND HARMONY COMPLETION-BOUNDARY AUDIT

Date: 2026-10-03 (Asia/Calcutta). Workspace HEAD: `7fcdecbe26f4fd01138edf8f58c02ce4b947db0b`.

## 1. Verdict

**A — ENTIRE GENERATED STREAM REQUIRED**, understood as the complete emitted textual completion with only the expressly permitted native terminal removal and CRLF/CR normalization. The specifications do not authorize selecting one substantive assistant channel and discarding another.

**Final-only Harmony extraction that omits substantive analysis requires a protocol amendment. No amendment is made.** For Study 1 under `current-repo-v1-draft3`, classify the proposed gpt-oss-20b path **DROP — CURRENT PROTOCOL INCOMPATIBLE**. This is a verdict about the proposed analysis/final extraction path under this contract, not a claim that every possible sampled gpt-oss response contains analysis or that the architecture can never emit acceptable text.

**Qwen3-Coder-30B-A3B and Qwen3-Coder-Next: PROCEED TO INFRASTRUCTURE VERIFICATION.** Both have plausible source-supported inference and fresh-base adaptation paths, with no identified required protocol change. Neither is verified, admitted to the study, or frozen. Verify 30B first because its selected BF16 deployment has a materially smaller resident base and simpler attention state. This is engineering-resource ordering, not model-quality ranking.

## 2. Normative sources inspected

The precedence rule is draft3 §1, lines 7–11: draft2 applies except where draft3 explicitly replaces/adds requirements. Both documents describe a proposed, unfrozen specification. “Frozen intent” in the request does not establish external freeze or certification. [Draft3](sources/draft3.txt)

| ID | Source inspected | Role |
|---|---|---|
| D2 | Supplied Step 8K-B.1C, `current-repo-v1-draft2`, all 1,136 lines | Normative baseline |
| D3 | Supplied Step 8K-B.1C2, `current-repo-v1-draft3`, all 1,056 lines | Explicit normative replacements/additions |
| R30 | Supplied Step 8K-B.1G1A preflight, 180 lines | Static/model evidence, not normative authority |
| RN | Supplied Step 8K-B.1G1B preflight, 164 lines | Static/model evidence, not normative authority |
| RG | Supplied Step 8K-B.1G1C preflight, 274 lines | Static/model evidence, not normative authority |
| I | `harness/context_policy/protocol.py`, `core.py`, `artifact.py`, README | Existing implementation contract; no transport adapter is implemented here |

Exact source copies and original absolute paths, lengths and SHA-256 values are in [source_manifest.json](source_manifest.json). The audit also inspected R30's saved proposed-runtime and source manifest, RN's adapter-estimate JSON, and RG's four hand-authored channel fixtures. These are confined to the supplied preflight area. No upstream benchmark claims, new web sources, project tasks, discovery materials or evaluator artifacts were used.

The implementation records policy SHA-256 `d93f5136339153e65e35ef720333e21260292bc680f2cd3cfe608dfa46939a3b`, and implementation revision `current-repo-v1-draft3-implementation-r2` with SHA-256 `ccb9484cd342c00a3c8e49a9df5af745e9ab2a29fc24a26234e2fd24cc9d6bbb` (`core.py`, lines 12–15). These are recorded contract constants, not a new verification of the external policy artifact. No protected researcher directories were opened to re-establish them.

## 3. Existing completion contract

| Term | Existing meaning and precise authority |
|---|---|
| Completion | The entire runtime-emitted textual result entering output handling. D2 §20 single-target, line 759: “The entire completion is the replacement content.” D3 §7.1 defines its acquisition and §7.2 reiterates the entire normalized result. There is no named analysis exception. |
| Raw completion | Exact returned text, after serving-interface removal of native terminal-control tokens; UTF-8 bytes and SHA-256 retained separately from finish reason, output count and terminal accounting. D3 §7.1, lines 433–440. “Raw” here is not the original generated token vector, and does not authorize arbitrary service-side content deletion. |
| Normalized completion | Raw text with CRLF and CR converted to LF, retaining every other character. Invalid Unicode/NUL fails. Preserve BOM, whitespace, fences, headers and terminal-newline state; append no newline. D3 §7.1, lines 442–448. |
| Model output | The specifications use output in two related senses: generated runtime facts and replacement artifacts. Generated tokens have a total 2,048 ceiling (D2 §17, lines 663–675; D3 §9, lines 749–755). Output artifacts are derived by §7 parsing. No third privileged “final answer only” output object is defined. Record finish/tokens/artifact hashes under D2 §27, lines 995–999. |
| Terminal token | A verified native EOS/terminal event; identifiers and effective behavior are profile facts, not guessed text. One terminal-token allowance is required for raw reference encoding. D3 §7.6, lines 526–541; §9, line 750. The specification does not supply universal IDs or treat every special token as a terminal. |
| Output artifact | Complete replacement content mapped to each public target; the sole single-target artifact is the entire normalized completion, while multi-target artifacts are exact section slices. D2 §20, lines 753–772; D3 §§7.2–7.3, lines 452–483. Current-target reference artifacts are capacity screens, not expected solutions (§7.5). |
| Complete replacement | Replace whole target contents, rather than apply a patch or extract a fragment. D2 §20, lines 753–755, and §18 system, lines 690–693. Newly generated unwanted explanation remains part of that replacement; no repair is permitted (D3 §7.2, lines 454–456). |
| Single-target output | Entire normalized text, including empty text, becomes the target. Header-looking lines and Markdown fences are literal content. No wrapper-removal heuristic. D3 §7.2, lines 452–456. Thus invalid Python can still be structurally `artifact_ready`; ordinary evaluation later judges it. |
| Multi-target output | Normalize once; first exact `=== FILE: <path> ===` header begins at offset zero, every header has LF, and the full header vector equals canonical P target order exactly. All exact header-shaped lines are reserved, even inside code/comments. Content extends from header LF to the next header or completion end. D3 §7.3, lines 460–483. |
| Transport framing | No general semantic-output transport projection is defined. D3 §7.1 expressly permits native terminal removal. D3 §7.5, lines 510–514, calls the conditional inter-section LF “protocol framing” for the reference artifact. D2 §§18/27 permit measuring input template/special tokens. None of these authorizes discarding a substantive generated channel. |
| Model-native serialization | A model-specific tokenizer, applied serving template, special-token/generation-prefix behavior and runtime identity are explicitly verified/profiled. D2 §18, lines 704–716; §26, line 971; D3 §9, lines 735–765. Input serialization latitude is not an output-content exclusion rule. |

Implementation trace: `protocol.TokenizerInterface` explicitly has “No completion transport.” `completion()` receives one text argument and externally verified integrity/token-limit facts; it stores exact raw bytes, calls `normalized_text(text, bom=False)`, and maps the entire normalized string to a single target (lines 182–211). For multiple targets, it validates and slices headers (lines 213–232). It does not inspect Harmony roles/channels or extract final content. `core.normalized_text`, lines 70–76, performs strict Unicode/NUL checking and newline conversion. `artifact_payload()['output']` likewise declares entire completion with only CRLF/CR normalization. [Implementation protocol](sources/protocol.py), [core](sources/core.py), [artifact contract](sources/artifact.py)

Runtime integrity failure takes precedence, then a verified length cap, then output format failure, then ordinary evaluation (D3 §7.7, lines 555–562; §13.2). A length-capped stream remains `output_capacity_failure` even if it also contains malformed headers. A count of 2,048 alone does not prove a length-cap event: the runtime may observe a native terminal at that token.

## 4. Harmony boundary determination

**Answer: A — ENTIRE GENERATED STREAM REQUIRED.** This is a textual-preservation obligation; it does not assert that raw numeric token IDs themselves are source-file characters. Native terminal removal is explicit. Any question about how nontext structural IDs are transported cannot authorize dropping substantive analysis text.

The decisive chain is:

1. D2 §20 requires the entire completion; D3 §7.1 identifies emitted textual completion and allows native terminal removal.
2. D3 §7.1, line 446, forbids stripping explanatory text and other wrappers/content.
3. D3 §7.2, line 452, requires the entire normalized result, and lines 454–456 disallow wrapper-removal heuristics or repairing incorrect generated content.
4. D3 §7.3 requires the first multi-target header at completion offset zero. A substantive preamble is not an authorized separate channel outside the artifact.
5. D2 §26, line 973, requires a new policy version for changed output handling.

Interpretation B's strongest argument is that D3 §7.1 starts from the serving interface's returned text and D2 §18 permits model-native templates. That does not grant the interface arbitrary authority to redefine what text belongs to completion. Otherwise any wrapper could omit explanations before the parser and defeat §7.2. The only express generated-content removal is native terminal-control handling, not removal of analysis/commentary bodies. The pre-existing documents define no final-message transport projection. RG's §11 explicitly labels that projection proposed and uncertified, and cannot create normative permission.

There is a narrower implementation detail still to verify for any new transport: how message/control IDs are represented and terminal events accounted for. That uncertainty does not make the substantive-channel question genuinely ambiguous. Removing channel labels alone cannot turn analysis into absent content. Even a typed parser that perfectly recognizes all messages still changes the artifact if it omits a nonempty analysis body.

The existing hand-authored RG `analysis_then_final` fixture contains 21 generated IDs: analysis text “Synthetic reasoning.” followed by `def synthetic():\n    return 1\n`, ending with native return ID 200002. This is an example of a possible stream, not measured model behavior or its frequency. Passing its full terminal-stripped rendered text to the frozen single-target parser preserves the analysis and channel syntax; passing only the final body produces a different artifact and hash. Retaining a sidecar documents deletion but does not make it authorized.

No inference is necessary to establish the normative difference. The accompanying [boundary_checks.json](boundary_checks.json) records a local deterministic parser demonstration using this existing invented fixture and small literal edge cases. Its integrity flags are synthetic test inputs, not deployment certifications. No Harmony runtime or weights were loaded for the demonstration.

## 5. Amendment required? YES

**YES**, for the proposed final-only extraction of an analysis-bearing completion.

| Proposed operation | Classification |
|---|---|
| Apply verified model input template/tokenization and record exact IDs | Previously authorized model-specific serialization, subject to profile verification |
| Remove a verified native terminal-control token and normalize CRLF/CR | Existing explicitly authorized output handling |
| Preserve/record raw token vectors, channels, finish reasons and hashes | Audit detail; does not change the artifact |
| Select final and omit substantive analysis/commentary before `completion()` | Protocol amendment affecting output handling, not a neutral clarification or implementation detail |
| Increase reasoning allowance, suppress analysis, force final prefix, tune effort to pass, retry missing final | No accommodation authorized by this audit |

Under D2 §26, line 973, output-handling changes require a new policy version. D3 §17, lines 1023–1028, retains complete replacement/no-read/common admission and candidate blindness. No such change is made or recommended to retain gpt-oss. Record the proposed path as incompatible for current Study 1. A separately motivated future protocol would require its own deliberate pre-exposure design; this audit neither creates it nor treats it as an outstanding blocker to solve for draft3.

This distinction also prevents overclaiming: the frozen parser could mechanically retain all gpt-oss text and let ordinary evaluation fail or succeed on those bytes. That possibility is not certification of final-only extraction, and no model-generated compliance rate was measured. The admission recommendation is for the proposed preflight deployment/extraction path, without modifying generation to obtain a pass.

## 6. Three-model factual comparison

Evidence labels: **preflight-measured** means measured in the supplied earlier report, not rerun here; **source-supported** means archived/pinned source or Hub metadata; **estimated** means arithmetic/planning. No full weight body, loaded-model behavior or training lifecycle was measured in those reports or here. Exact checkpoint revisions identify artifacts to verify, not verified checkpoint-body hashes.

| Identity / serialization | Qwen3-Coder-30B-A3B | Qwen3-Coder-Next | gpt-oss-20b |
|---|---|---|---|
| Repository | `Qwen/Qwen3-Coder-30B-A3B-Instruct` | `Qwen/Qwen3-Coder-Next` | `openai/gpt-oss-20b` |
| Immutable model revision | `b2cff646eb4bb1d68355c01b18ae02e7cf42d120` | `a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb` | `6cee5e81ee83917806bbde320786a8fb61efebee` |
| License evidence | Apache-2.0 card and downloaded LICENSE; LICENSE hash `832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e` | Pinned card/Hub declare Apache-2.0; no standalone LICENSE in pinned inventory, linked text returned 404 | Downloaded Apache-2.0 LICENSE; hash `58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd` |
| Architecture | 48 full-attention MoE layers, 128 experts/top8, hidden 2,048 | 12 full/36 DeltaNet linear-attention layers; 512 routed experts/top10 plus shared expert per layer | 24 layers; 12 full/12 sliding attention with sinks; 32 experts/top4; hidden 2,880 |
| Base scale | Hub exact 30,532,122,624 parameters; rounded 3.3B active | Card rounded 80B total/3B active | Card ~21B/3.6B; source-shape total estimate 20,914,757,184 |
| Tokenizer | Qwen2TokenizerFast, BPE with NFC, base 151,643/loaded 151,669 | Same tokenizer.json/vocabulary identity; NFC | HF PreTrainedTokenizerFast plus official Harmony 0.0.8; 199,998 mergeable ranks match o200k_base; no normalization |
| tokenizer.json SHA-256 | `19564a48c4f71a2a1b937cce34c737a1e662b171c5f5d7edf641a15cd896f07d` | Same exact hash | `0614fe83cadab421296e664e1f48f4261fa8fef6e03e63bb75c20f38e37d07d3` |
| Applied template/renderer | Standalone Jinja, 6,211 bytes, hash `5a38bfa05833266240066aedc497decc9b00cc0d3e3b8cceea98cf530196ab06` | Standalone Jinja, 6,068 bytes, hash `c79a833039a43602150cce0902403d6e376c50930c1b2a139b2964e1f0c322a0`; embedded source differs by LF | Proposed typed Harmony, source `abd677f7ac962629c808197caa1feb9e3e95d2b0`; upstream Jinja hash `a4c9919cbbd4acdd51ccffe22da049264b1b73e59055fa58811a99efbd7c8146` is a separately measured alternative, not the same serializer |
| Generation prefix | `<|im_start|>assistant\n`, non-thinking | Same prefix, non-thinking | `<|start|>assistant`, leaves channel selection to model |
| Native input markers | Literal marker strings can become special IDs; no escape accommodation | Same issue | Typed TextContent encodes literal markers as ordinary data; flat Jinja path differs |

Sources: R30 §§2–6, RN §§2–6/14, RG §§2–6. [R30](sources/preflight_30b.txt), [RN](sources/preflight_next.txt), [RG](sources/preflight_gpt_oss.txt)

| Capacity / deployment | 30B-A3B | Next | gpt-oss-20b |
|---|---|---|---|
| Native context | 262,144 | 262,144 | 131,072 |
| Proposed deployed capacity | 32,768, one sequence | 32,768, one sequence | 32,768, one sequence |
| Prior protocol-capacity result | 45/45 synthetic checks pass; max input 27,855 + 2,048 = 29,903 | Same maximum, independently encoded; 45/45 pass | Typed 45/45 pass; max measured input 20,496 + 2,048 = 22,544 |
| Capacity caveat | NFC can expand bytes; synthetic coverage is not an exhaustive bound; actual per-input admission still required | Same caveat; hybrid runtime allocation unmeasured | Conditional fixed-metadata byte bound 21,417 + 2,048 = 23,465; does not prove emitted analysis/answer fit |
| Selected checkpoint storage | 16 BF16 shards, 61,066,575,656 bytes (~56.87 GiB); tensor payload 61,064,245,248 | 40 BF16 shards, 159,358,031,480 bytes (~148.41 GiB); payload 159,348,782,592 | Three MXFP4/BF16 HF shards, 13,761,316,904 bytes (~12.82 GiB); payload 13,761,264,768; alternative original package is not an extra logical model |
| Proposed runtime | Offline vLLM 0.11.2 V1, Linux/CUDA12.8, torch2.9.0, Transformers4.57.6; BF16 TP1 | Offline vLLM0.16.0 source `89a77b10846fd96273cce78d86d2556ea582d26e`, torch2.9.1, FlashInfer0.6.3; BF16 TP4 | Same pinned vLLM0.16.0; native MXFP4 weights, BF16 nonquantized compute, TP1 |
| Runtime pin limit | Saved source hashes bind examined 0.11.2 tag files; immutable runtime commit/container and full binary lock not established in R30 | Source SHA established; resolved container/binaries/driver/kernel lock not established | Same limit; native MXFP4 kernel/fallback behavior also unmeasured |
| Inference planning class | One 80GB GPU; ~65–75 GiB planned resident usage; 96–128GiB host safer, 150–250GB storage for copies | 4×80GB or 2×141GB; ~170–210 GiB aggregate planned; 192–256GiB host; 350–500GB storage | Native 24–48GB supported GPU planning; BF16 ~38.96GiB base needs ~80GB class; 64–128GiB host, 100–150GB storage |
| Local feasibility | Existing 4GiB GPU/~23.71GiB RAM/~23GiB disk insufficient | Same, with larger storage deficit | Native file may fit disk, but inference/BF16 rebuild cannot fit local GPU/RAM |
| Unresolved controls | Actual prompt parity, effective greedy/penalties/stops/cap, no clipping/retry, fresh state, terminal accounting and determinism | Same plus recurrent/hybrid state isolation and TP/kernel behavior | Same plus constant metadata/date/effort, native channels, reserved IDs, dequantization fallback and incompatible final projection |
| Native terminal evidence | Primary151645; native union [151645,151643]; source stop-before-length precedence | Same IDs; stop-before-length at newer runtime pin | [200002,199999,200012]; 200007 ends a message, not the response; 200012 is handoff, no tools allowed |
| Output issues | Natural terminal, raw decode, one-token allowance and 2048 boundary unmeasured | Same | Analysis/final/handoff can occur in one counted stream; final-only omission is incompatible; no retry to obtain final |

Sources: R30 §§7–11/19, RN §§7–11/20, RG §§7–13/15. Storage sizes are upstream declarations, not local body measurements. Planning configurations are starting environments, not measured fit or spending authorization.

| Adaptation / product | 30B-A3B | Next | gpt-oss-20b |
|---|---|---|---|
| Pinned training support | Transformers4.57.6 + PEFT0.18.0; explicit ordinary attention/expert Linear targets, avoid unsupported default mapping | Same versions; full/linear attention plus routed/shared expert Linear targets; hybrid backward needs testing | Same versions; attention Linear targets; experts are raw 3D parameters requiring experimental `target_parameters` |
| Attention-only rank16 estimate | ~13.37M parameters | 17,141,760 = 4,128,768 full + 13,012,992 linear | 7,962,624 |
| Routed expert rank16 estimate | ~830.47M extra; ~843.84M with attention | 3,019,898,880; shared expert extra5,898,240; attention+routed+shared derived total3,042,938,880 | 176,947,200; attention+experts184,909,824 |
| Broader state scale | ~10–14GiB at report's 12–16 bytes/parameter assumption, before base/activations | Routed adapter ~5.63GiB BF16; ~45GiB conventional16-byte training state, before base/activations | Combined adapter ~352.7MiB BF16/~2.76GiB state, before BF16 base/activations |
| Quantized training | Generic NF4 double-quantization route source-supported; compatible bnb/Accelerate lock and actual expert conversion not verified | Generic NF4 linears route, bnb0.49.1 pin; hybrid backward, expert conversion and distributed placement unverified; conv/recurrent parts remain outside generic linear conversion | Native MXFP4 training unsupported at pinned Transformers; BF16 dequantized LoRA supported; architecture-wide NF4 conversion not established for raw experts |
| Plausible training class | Attention BF16 LoRA starts with80GB + checkpointing; broad/long sequences may need multiple80GB; QLoRA only conditional | Attention BF16 starts4×80GB with actual training sharding; NF4 attention may start1–2×80GB, unverified | BF16 attention starts80GB H100 class; broad raw-parameter/dense fallback can require more |
| Save/reload/merge | PEFT source support; fresh BF16 merge/export plausible; no end-to-end serving parity | Same; direct expert-adapter vLLM loading not proven | Parameter-wrapper save/merge source support; quantized merge/export and direct expert adapters not proven |
| ORIGINAL BASE rebuild | Fresh original load/process, new adapter/optimizer/RNG, retrain allowed accumulated history; repeated lifecycle/cost unmeasured | Same, larger resident base, hybrid state and sharded loading complexity | Same with fresh verified dequantization, experimental expert wrappers and potential requantization identity changes |

Sources: R30 §12, RN §12 and saved adapter estimates, RG §14. Rank16 is solely a comparison arithmetic assumption from the reports, not an adopted training setting. The Next combined count is addition of the three reported sets, not an instantiated adapter census. Different adapter counts do not imply different learning quality.

Methodological asymmetries: equal P/K/H byte ceilings do not equalize tokens, propositions, FLOPs or costs (D2 §§17/23/29; D3 §14). Qwen NFC changes token encoding without changing retained P/K/H bytes. Native templates have different overhead/authority; Harmony also carries constant reasoning/date/identity metadata. Native MXFP4 versus Qwen BF16 is a numerical-format difference, not free equivalence. All experts remain resident despite sparse routing; only routed branches may receive each token's gradient, and gpt-oss training fallback can perform dense expert work. Next linear/recurrent states differ from full attention. Different runtime versions/TP/kernels limit deterministic comparisons. One total 2,048 budget would include Harmony analysis/control tokens if that path were otherwise eligible; no extra answer allowance is licensed. No coding-quality, benchmark-score, throughput or price ranking follows from these facts.

## 7. Infrastructure-admission decision per model

| Model | Decision | Pre-outcome reason |
|---|---|---|
| Qwen3-Coder-30B-A3B | **PROCEED TO INFRASTRUCTURE VERIFICATION** | Synthetic capacity fits proposed32K; selected BF16 path is source-supported; attention/expert LoRA and fresh-base lifecycle are plausible on cloud hardware. Main gaps are empirical/runtime, not a known normative incompatibility. |
| Qwen3-Coder-Next | **PROCEED TO INFRASTRUCTURE VERIFICATION** | Same protocol plausibility; larger cloud/sharding requirement and hybrid state raise testing cost, but no supplied project resource ceiling establishes clear impracticality. Stage spending after the smaller model's checks. |
| gpt-oss-20b | **DROP — CURRENT PROTOCOL INCOMPATIBLE** | Proposed final-only extraction drops substantive generated analysis, which draft3 does not authorize. Hardware tests cannot supply normative permission. Native footprint and plausible BF16 LoRA do not remove this blocker. |

No model is classified clearly impractical solely because it requires cloud infrastructure. No “HOLD” remains for the substantive Harmony boundary: the supplied normative texts settle that question against the proposed projection. Qwen infrastructure admission is a recommendation for separately authorized future validation, not authorization to rent GPUs, fetch full weights or infer now.

## 8. Product adaptation-feasibility analysis

The product requires repeated fresh adaptation from **ORIGINAL BASE**, not continuation of a previous adapter or reuse of a merged derivative. Neither source support nor one successful optimizer step proves this lifecycle. D3's Study-1 H contract describes externally curated prompt evidence (§8.1); a training feasibility result must not relabel H as autonomous learning or silently add weight updates to the five-condition experiment.

For 30B, ~56.87GiB resident BF16 base plus a comparatively small attention-only adapter gives a credible80GB starting path. Explicit target auditing avoids PEFT's missing architecture default. All128 experts remain resident, and broader expert adapters increase trainable-state cost markedly. A fresh-process original-base load, newly initialized optimizer/adapter and a verified BF16 export offer a plausible repeated-rebuild workflow. Source support justifies testing, not an affordability or update-latency claim.

For Next, ~148.4GiB BF16 base makes load/merge/rebuild fundamentally a larger infrastructure operation. Attention-only projections across full and linear attention total17.14M rank16 parameters, but all routed expert projections exceed3B adapter parameters. Start by validating the source-supported attention path and actual hybrid backward/state cleanup, then the intended production target set if broader. Neither expert count nor “3B active” supports a throughput estimate. Sharded BF16 loading/merge and fresh recurrent state require explicit tests. Cloud requirement alone is insufficient to drop this model.

For gpt-oss, the compact native13.761GB checkpoint does not describe BF16 training residency: estimated dequantized base is38.96GiB. An80GB BF16 attention route is technically credible; expert parameter adapters add experimental constraints, and dense training fallback may erase inference sparsity advantages. Native MXFP4 backward is unsupported at the chosen pin; generic whole-base NF4 assumptions are unjustified. Repeated fresh dequantization/export would add operational steps. These facts would justify feasibility work in an independently appropriate study, but the current output incompatibility prevents spending on this model for draft3 Study1.

Before accepting product feasibility, specify the intended update frequency, allowed history lengths, adapter targets/rank, training sequence envelope, supported export route and resource/cost envelope independently of model outcomes. Those requirements were not supplied here and are not invented. Later measure load, train, save/reload, export and validation separately; full-history refresh time depends on observed training throughput and accumulated training tokens. A short smoke test cannot establish study-length or accumulated-history fit.

## 9. Minimum infrastructure test matrix

Run this matrix separately for both admitted Qwen models with exact pinned checkpoints, batch/sequence count one and invented code tasks only. An explicit CSV is provided in [infrastructure_test_matrix.csv](infrastructure_test_matrix.csv). Each row is a required gate or explicitly conditional export/quantization branch. Freeze fixtures, repeat roster, numerical tolerances and failure criteria before measurement. Record failures; do not tune the frozen protocol to recover a pass.

| ID | Test and minimum observation | Acceptance/evidence required |
|---|---|---|
| A | Download exact selected shard set outside inference; verify every body against recorded LFS SHA-256/length; census actual tensors/dtypes/keys | All exact identities match; original read-only snapshot retained; no substitution of another quantized checkpoint |
| B | Fully resolve runtime/container and training dependency identities; record GPU/topology/driver/CUDA/kernels, wheel/build hashes and policy parser | Container/build digest and dependency lock; 30B0.11.2 source commit resolved to archived file hashes; Next0.16.0 exact SHA; CPython3.11.9/Unicode14.0 for policy operations |
| C | Load checkpoint in selected dtype/TP with32,768 capacity and one sequence; log actual residency and full valid near-capacity synthetic prefill | No silent offload/quantization/fallback; actual capacity supports prompt+2,048; an overlength synthetic input is rejected without clipping |
| D | For fixed invented P/K/H, all A/B/M/C/BC and empty H, retain messages/render bytes, token vectors and hashes | Offline authoritative encoding equals engine returned prompt IDs exactly; K unchanged; literal special markers/Unicode/newline cases retain original payload identities |
| E | Inspect requested typed and effective greedy controls and actual arguments, including inherited defaults | Temperature0, top_p1/top_k disabled, neutral penalties, seed0 or explicit unsupported status, no text stops, max2048, n1, min_tokens0, no retries or reserve reduction; verified profile behavior |
| F | Instrument primary and secondary native terminal IDs, decode/count/removal and terminal-at2048 boundary | Preserve entire emitted vector; remove only verified final terminal; internal special IDs remain; native stop/length precedence reflects actual finish facts; reference allowance exactly one |
| G | One small invented complete-file task, then invented multi-file task, to observe natural termination | All emitted text reaches frozen parser; no fences/explanation cleanup; original raw/normalized bytes/finish and artifact results retained even on failure |
| H | Invented long-output task under unchanged controls; add deterministic token-scheduler/transport fixtures if a real length cap is not elicited | Real cap shows2048 total and output_capacity_failure; no ignore_eos/min-token forcing or continuation; a scripted fixture alone does not establish loaded-runtime cap behavior; incomplete test remains pending |
| I | Retain token IDs, exact decoded byte/text identities, raw/normalized hashes, output counts, finish/stop facts and terminal provenance | No blanket skip_special_tokens, unknown-ID skipping or Unicode replacement; distinguish valid literal U+FFFD from decoder repair; lossless accounting/certified decode |
| J | Repeat identical synthetic requests three times in the same pinned process, frozen order | Compare complete token vectors/artifact hashes; log differences, deterministic scope and causes; seed/greedy alone is not proof |
| K | Repeat same roster in a second fresh serving process on identical hardware/build | Reset all request/KV state; exact parity or explicitly documented verified determinism limits; no silent selection of the best repeat |
| L | Audit worker mounts/capabilities, request log and failure injection | No product/evaluator mounts, tools, shell/read callbacks, network model fetch, feedback, prior conversation, auto retry or fallback; failure makes exactly one attempt |
| M | Measure peak GPU memory per device, aggregate host RAM and storage at load, near-capacity generation, training and export | Actual32K inference and intended training envelope fit chosen resources; separately log startup/loading/optimizer/export peaks and failures |
| N | Measure batch-one load time, cold/warm TTFT, output-token throughput and training tokens/s | Report prompt/output lengths, timers, synchronization, repeats, generated vs terminal counts and hardware; measured engineering costs only, no coding-quality claims |
| O | Fresh ORIGINAL BASE + new explicit attention adapter; fixed tiny invented code sequence, forward/backward and optimizer step | Actual targets/shapes/trainable census; finite loss/gradients and intended nonzero gradients; frozen base/router unchanged; Next full/linear branches checked; repeat intended-length envelope before product eligibility |
| P | Save adapter, destroy model/optimizer process, reload adapter onto independently verified ORIGINAL BASE | Serialized identity/key/shape checks; frozen synthetic logits/output parity within predeclared numerical tolerances; no restoration of unwanted optimizer/base state |
| Q | Test the selected serving route; merge/export if required, otherwise direct-adapter serving | Fresh original BF16 base + adapter, hash derivative, preserve tokenizer/template, compare unmerged/reloaded/served outputs; direct attention loading must be verified, not inferred from SupportsLoRA; quantify any requantization difference |
| R | Second entirely fresh original-base process + independently initialized adapter/RNG/optimizer; retrain fixed accumulated invented history | Same ORIGINAL BASE identity; no warm-start from first adapter or derivative; deterministic initialization/checkpoint identities and rebuild timings recorded |
| S | Contamination check: after first cycle, new pristine worker and second cycle; compare base hashes/state and control probes | Fresh pristine outputs match original control; prior adapter/wrapper/optimizer/RNG/KV/history/merged base absent; Next recurrent/conv state cleared; repeat export cannot mutate original |

Model-specific additions are part of these gates: 30B has full-attention KV allocations and explicit ModuleList expert conversion/gradient census if expert or NF4 targets are selected; Next needs fresh full/linear recurrent state, hybrid backward kernels, actual TP/training-shard topology and shared-expert separation. No broad expert training is mandatory merely because it exists. If the product's frozen design selects experts, extend O/P/Q/R/S to that exact set, including gradient coverage under predeclared synthetic routing probes. Attention-only success cannot certify expert adaptation.

The proposed BF16 serving/attention-adaptation path can be tested without choosing QLoRA. If a quantized training/export path is selected later, additionally freeze its derived identity and numerical tolerances; verify every intended Linear4bit conversion, frozen/unquantized exceptions, kernels/backward, base and adapter round trips. Do not inherit BF16 certification. Inference tensor parallelism is not evidence that training sharding works.

Natural-stop/cap/terminal-boundary tests do not require weakening controls: the loaded model must be tested as configured, and deterministic transport fault fixtures are supplementary. Boundary fixtures may simulate EOS at2047/2048, no EOS at2048, malformed partial headers, invalid text and integrity failure. Report unobserved loaded-model cases as pending, not as verified by a mock.

## 10. Cost-conscious verification order

1. **Resolve nonhardware gates first.** Complete this normative boundary audit; drop the proposed Harmony projection. Review source pins/license packaging, runtime/profile schema, literal synthetic fixtures, no-read worker design and intended product adaptation/export requirements. No GPU spend is needed for this stage. Resolve30B runtime immutable source/build pin against archived hashes; keep its proposed0.11.2 unless deliberately adopting and recertifying another profile. Do not silently impose0.16.0 on both Qwens.
2. **30B checkpoint and serving gates A–N.** Verify~61GB bodies, lock the80GB starting environment, then load and shortest natural-terminal/prompt-parity/control checks before near-capacity/cap/repeat/isolation tests. Any identity/control/output-integrity failure halts spending on that configuration. Observe memory/timing as each test runs; no separate timing-only expensive deployment.
3. **30B fresh attention-adapter gates O–S.** Run short forward/backward, then save/reload and verified serving route, then second original-base rebuild and contamination check. Finally validate intended training-length/history envelope and practical rebuild resources. This tests the product hypothesis before committing to the larger base.
4. **Next gates A–N, then O–S.** Reuse synthetic fixture definitions and audit requirements, but independently verify its~159GB bodies,0.16.0 runtime, TP4/hybrid state and sharded training/export. Its4×80GB starting topology is materially larger than30B's1×80GB. No inherited capacity, terminal, gradient or lifecycle pass is allowed.
5. **Conditional broader/quantized paths.** Spend on these only when selected by an independently defined product design. Test exact targets/conversions/lifecycle; short attention LoRA does not certify them.

30B failure need not automatically reject Next: an architecture/runtime-specific failure can leave Next plausible. A shared no-read/profile/output-contract blocker or failure of the project's defined fresh-rebuild requirements should be resolved before allocating larger resources. Similarly, no observed model performance may change admission rules or the engineering order. Exact money, throughput and refresh time are unavailable; the order follows selected resident/storage/topology requirements, not assumed price or speed.

## 11. Remaining model-shortlist blockers

For each Qwen, complete and externally attest A–S with actual bodies/builds, per-sequence capacity, prompt parity, controls, terminals/raw retention, isolation, repeatability limits, resource measurements and a second ORIGINAL BASE rebuild. Choose/freeze the intended adapter and serving/export route independently of benchmark outcomes; validate the relevant sequence/history envelope. Resolve Next's distribution notice/license text packaging before redistribution. Freeze the validation repeat roster and numerical tolerances before testing.

Keep gpt-oss outside the draft3 Study1 roster for the proposed incompatible output path. Its drop does not create a requirement to revise draft3. No fixed survivor count is required. A reviewed model-shortlist decision after candidate-blind infrastructure evidence must precede common benchmark admission; unverified models must not silently create an empty intersection (D2 §19, line745).

This audit recommends who to test; it does not perform **MODEL SHORTLIST FREEZE** or certify any model. Capacity/reference checks on actual study tasks belong to the later authorized common-admission process, not this candidate-blind audit.

## 12. Remaining current-repo-v1 freeze blockers

The model shortlist is only one prerequisite. D2 §§26–30 and D3 §§8/9/13/15/18 require:

1. Independent final normative/policy/configuration review and exact behavior/source-build identities, including implementation-r2; all budgets/caps/one-hop/packing/output handling remain as specified.
2. Independently certified immutable product/deny manifests, complete existence acquisition, snapshot bytes and authenticated receipt; reviewed verification algorithms, signer/key roles and external verifier code. This audit did not inspect or certify those artifacts.
3. Public-task certification and pre-outcome task/target admission, performed only in its authorized later phase.
4. Historical ledger/cutoff/registry chronology, exact-body lineage, distinct constructor/certifier, human rule confirmation and active revisions certified under `study1-curated-evidence-v1`. Retrospective record construction cannot be backdated.
5. Independently authored/reviewed literal conformance expectations, including D3's seven fixture families; actual CPython3.11.9/Unicode14.0 conformance and deployment certification. This audit's few boundary demonstrations are not full conformance or authentication evidence.
6. Verified model/tokenizer/template/system/generation-prefix/runtime profiles, actual capacity/controls/native terminals, exact K reuse and no-read/no-retry request isolation for the fixed roster.
7. Candidate-blind no-generation input/reference validation with untouched P<=4,096/K<=12,288/H<=4,096, inventory<=2,048, one total2,048 generation reserve, BC two owned<=2,048 lanes, all five conditions and one reference terminal allowance. Preserve empty H and unused capacity; no clipping or model-specific K reduction.
8. Later independently freeze and hash the common population intersection across every fixed model/condition before outcomes, along with any replicate roster/execution order. No retrospective removal of truncation/failure cases.
9. Certify emitted information-matching manifests before representation-effect claims; preserve context-sufficient information, K/H overlap, BC fixed-total interpretation, curated-state attribution and existing claim limits. Preserve full-access sensitivity analysis as historical sensitivity evidence.

No external trust input, study population or final policy was frozen here. Existing implementation and earlier synthetic reports do not themselves satisfy these external governance/runtime prerequisites.

## 13. Candidate artifacts inspected? NO

**NO.** No Step8K candidate inventory/dispositions, benchmark/project task instances, model/adaptation outcomes, solutions, evaluators or protected discovery files were opened. Directory/file-name discovery was limited to locating repository instructions and the permitted implementation/preflight area; no product content was traversed. No candidate relevance, classification or evidence-role assignment occurred.

## 14. Model inference performed? NO

**NO.** No model weights downloaded or loaded, no model generation, no GPU/runtime launch, no training, no adapter instantiation or optimizer step. Local deterministic output-parser demonstrations used invented text and the existing hand-authored preflight fixture. Earlier reports' tokenizer measurements were summarized without rerunning their acquisition/generation paths.

## 15. Protocol modified? NO

**NO.** Normative sources, harness, existing preflights and product content remain unchanged. No change to treatments, model effort, allowance, output parser, common admission, claim ladder or full-access sensitivity analysis. No shortlist or external policy freeze, no commit.

## 16. Files modified

Only new artifacts under `experiments/model_preflight/cross_model_audit/`:

- `REPORT.md`: this17-section audit.
- `source_manifest.json`: exact original/archive source identities and supplementary evidence identities.
- `infrastructure_test_matrix.csv`: A–S gates separately for both admitted Qwen models; definitions only, no execution.
- `verify_audit.py`: bounded offline parser/source/report/matrix checks.
- `boundary_checks.json`: hand-authored parser demonstration results and recorded scope/runtime.
- `artifact_manifest.json`: final audit-file identities, excluding itself to avoid recursive hashing.
- `sources/`: ten byte-identical copies of the six supplied inputs and four implementation-contract files listed in §2. These are archival copies, not edited normative sources.

`experiments` is excluded by D2 §16, line625, and `core.EXCLUDED_DIRS`; no product read was needed to establish exclusion. Existing untracked `experiments/model_preflight/` artifacts were present before this audit and remain preserved. Final manifest/checks record source equality and unchanged inspected originals; they are local integrity evidence, not independent signed certification.

## 17. Final recommendation

Proceed to separately authorized candidate-blind infrastructure verification for **Qwen3-Coder-30B-A3B first, Qwen3-Coder-Next second**, using the staged A–S matrix and testing repeated ORIGINAL BASE rebuilding before accepting product feasibility. **Drop the proposed gpt-oss final-only Harmony path from draft3 Study1** because excluding substantive analysis changes the completion artifact. Keep draft3 unchanged. Freeze neither roster nor policy until the stated empirical and external certification gates are satisfied.
