# Development Subject recipe justification v1

Recipe ID: `development-subject-recipe-justification-v1`

Status: **FROZEN_DESIGN**. Evidence inspected: 2026-10-04
(Asia/Calcutta). This memo records methodology justification and project design
choices, now frozen for design only, not a feasibility certificate or experimental result.
Final-batch design revision: 2026-10-05 (Asia/Calcutta), under U02; no new web inspection.
REVIEW_FREEZE is CLOSED (design only), under DEVELOPMENT_SUBJECT_FREEZE_MANIFEST_V1.json.
PRE_DISCOVERY_AUDIT_ENVELOPE remains PENDING_EVIDENCE; no discovery/comparison/selection is authorized.

## Scope, evidence and source limitations

This task reviewed only the supplied methodology sources, existing Workload v1
and relevant existing Development Subject governance. Public methodology pages
were opened directly to verify the supplied facts; no model-landscape search or
candidate audit occurred. Generic documentation's illustrative model names are
not candidates or evidence about their eligibility. No documentation example was
executed. No model weights, datasets, runtime packages or repository source archives
were acquired. Paper pages were read through the web tool, not saved as extra files.

Sources below are primary methodology/documentation sources, not model selection
evidence. Papers use identified arXiv versions; documentation at `main`/unversioned
URLs is mutable. Retrieval date is not a runtime lock: later exact package/build
versions and effective behavior must be pinned and certified. The user-provided
research brief supplies the proposed reference choices; this memo independently
checks the cited methodological support and labels project departures.

| ID | Source and locator inspected | Supported use here; limitation |
| --- | --- | --- |
| S01 | [QLoRA, arXiv:2305.14314v1](https://arxiv.org/abs/2305.14314v1), [PDF](https://arxiv.org/pdf/2305.14314v1), section 3, Appendix B.2 and Table 9, printed page 23 | Frozen quantized-base/adapter method and the supplied reference settings. Appendix B.2 explicitly reports max gradient norm 0.3. Reference experiments are not a repository-adaptation study or universal optimum. |
| S02 | [LoRA, arXiv:2106.09685v2](https://arxiv.org/abs/2106.09685v2), [PDF](https://arxiv.org/pdf/2106.09685v2), sections 4.1-4.2 | Frozen base, low-rank residual and alpha/r scaling; attention-subset adaptation is a methodological possibility, not proof of this project's target rule's quality. |
| S03 | [PEFT quantization guide](https://huggingface.co/docs/peft/developer_guides/quantization), Quantize a model, LoraConfig | Explicit quantization/preparation and adapter configuration are supported interfaces. Illustrative defaults/ranks/dropout are not project justification or executable compatibility proof. |
| S04 | [Transformers bitsandbytes guide](https://huggingface.co/docs/transformers/en/quantization/bitsandbytes), QLoRA: Compute data type, NF4, Nested quantization | Documents explicit 4-bit/NF4/BF16/double-quantization settings. Hardware examples do not establish this project's free-Colab feasibility. |
| S05 | [PEFT LoRA reference](https://huggingface.co/docs/peft/main/package_reference/lora), LoraConfig parameters r, lora_alpha, bias, use_rslora, init_lora_weights | Standard versus rank-stabilized scaling, bias effects and no-op initial adapter behavior. Newer adapter methods remain excluded; this main-page interface is not a version pin. |
| S06 | [Transformers gradient accumulation](https://huggingface.co/docs/transformers/grad_accumulation), Loss scaling | Sum loss over prediction targets and normalize by their count across microbatches; count shifted causal labels. Mathematical normalization does not guarantee bitwise equivalence of runtime partitions. |
| S07 | [Transformers Trainer](https://huggingface.co/docs/transformers/en/main_classes/trainer), TrainingArguments optimizer, scheduler and reproducibility parameters | Explicit optimizer ancillary parameters, scheduling and seeding controls. Documented defaults are adopted only where expressly stated as a project choice below. |
| S08 | [PyTorch deterministic algorithms](https://docs.pytorch.org/docs/main/generated/torch.use_deterministic_algorithms.html), API notes | Deterministic algorithms can change execution or raise for unsupported operations; the switch alone does not establish reproducibility. |
| W01 | `DEVELOPMENT_SUBJECT_WORKLOAD_V1.md`, sections 2-4 and 6-8 | Pre-existing attention-only intervention, accepted-code/loss mask, chronological full coverage, no packing/truncation, endpoint checkpoint and leakage boundaries. This memo changes justification/readiness only where specified. |
| U01 | User research/proposed-recipe brief, `C:/Users/admin/.codex/attachments/d4ef95b5-12b2-4049-8c84-6609d01d111d/Pasted text.txt` | Direct authorization to propose the listed common values and three-seed policy. It is not empirical proof, a candidate fact or a freeze. |
| U02 | User independently reviewed FINAL-BATCH POLICY V1 authorization, `C:/Users/admin/.codex/attachments/964e84f3-a151-4e3d-a8ee-cf8c32a78b20/Pasted text.txt`, 2026-10-05 | Authorizes the common nominal-batch-16 policy with one actual-token-normalized underfull final update when needed. Project design decision, not numerical equivalence, execution authority or freeze. |

S01 verifies NF4/double quantization/BF16 and the rank/alpha/constant-schedule
precedent. Table 9 supports LR 2e-4 and batch 16 in its smaller experimental regime;
it does not establish applicability to every parameter size or architecture.
Those values are adopted uniformly as a **reference-informed project choice**,
not because an eventual candidate belongs to a favorable size category.
No paper benchmark magnitude, performance result or model identity is used to
choose the Development Subject or promise an adaptation effect.

## Source versus project-design table

Evidence types: `DIRECT_SOURCE` means the stated method/value is directly
documented, with its original scope; `SOURCE_INFORMED_PROJECT_CHOICE` means the
project explicitly adopts/translates precedent without an optimality claim;
`PROJECT_DESIGN_CHOICE` means an independently declared policy from U01/U02 or this
workload's scientific contract; `EXISTING_WORKLOAD_RULE` preserves W01. Scientific
choices are now frozen design with these evidence/claim limitations intact.
No library default silently defines the experiment. U02 resolves the tail-policy design gap.

| Field | Design value/rule | Evidence source | Evidence type | Rationale | Claim limitation |
| --- | --- | --- | --- | --- | --- |
| Adapter method | Uniform QLoRA | S01; W01; U01 | DIRECT_SOURCE | Quantized frozen base plus trainable low-rank residuals. | Method precedent, not project feasibility. |
| Original base | Exact pinned original; no base-weight training | S01/S02; W01 | DIRECT_SOURCE | Preserve checkpoint identity and isolate adapter updates. | Actual pins/authentication remain later evidence. |
| Base quantization | 4-bit NF4 | S01/S04; U01 | DIRECT_SOURCE | Explicit common base representation. | Not numerical equivalence to unquantized weights. |
| Double quantization | Enabled | S01/S04; U01 | DIRECT_SOURCE | Fix the same quantization policy for all subjects/conditions. | Exact implementation/storage behavior must be pinned. |
| Compute dtype | BF16 | S01/S04; U01 | DIRECT_SOURCE | Uniform quantized-linear/mixed-precision compute policy. | Unsupported runtime cannot switch to FP16/FP32; not a claim every operation uses BF16. |
| Trainable adapter storage/gradients | FP32, with BF16 mixed-precision forward arithmetic | U01 common precision requirement; S07 interface context | PROJECT_DESIGN_CHOICE | Explicitly retain stable trainable parameter/gradient storage and prevent implicit PEFT dtype drift. | A declared project precision choice, not alleged QLoRA adapter-storage precedent or proof of kernel support. |
| Optimizer state precision | FP32 moments under the selected 32-bit optimizer | U01; S01 paging principle | SOURCE_INFORMED_PROJECT_CHOICE | Consistent state precision and burden accounting. | Verify actual allocated state/dtypes, not only the optimizer name. |
| Nonquantized frozen modules | Common k-bit preparation: frozen FP32 normalization/stability modules, BF16 remaining floating forward profile; record exact module/dtype inventory | S03 preparation interface; U01 | PROJECT_DESIGN_CHOICE | Make preparation and stability casts explicit; no full-model dtype fallback. | Candidate mapping must prove the common policy; incompatible preparation requires review, not hidden changes. |
| Adapter targets | Preserve every text decoder layer's Q/K/V and attention-output-to-residual linear equivalents | W01; S02 supports subsets | EXISTING_WORKLOAD_RULE | Keep the independently designed bounded attention intervention. | Deviates from canonical QLoRA's all-linear coverage; does not inherit its effect size. |
| Target mapping | Source-backed equivalents/fused partitions/tied coverage; no architectural module-name list | W01 | EXISTING_WORKLOAD_RULE | Common mathematical rule before architecture mapping. | Missing mappings remain gate blockers. |
| Rank | 64 at every eligible transformation | S01 Appendix B.2; U01 | SOURCE_INFORMED_PROJECT_CHOICE | Fixed reference rank, not per-candidate capacity tuning. | All-layer precedent does not prove attention-only sufficiency. |
| Alpha | 16 throughout | S01 Appendix B.2; U01 | SOURCE_INFORMED_PROJECT_CHOICE | Adopt a common reference setting. | No optimality or learning-rate equivalence claim. |
| Scaling | Standard alpha/r | S02 section 4.1; S05 | DIRECT_SOURCE | Preserve original low-rank scaling definition. | Not claimed superior to alternatives. |
| use_rslora | false | U01; S05 | SOURCE_INFORMED_PROJECT_CHOICE | Avoid introducing a different scaling method in v1. | rsLoRA remains legitimate later methodology. |
| Dropout | 0.0 | W01; U01 | EXISTING_WORKLOAD_RULE | Preserve the disabled minimal-intervention rule. | Intentional deviation from reference regularization, not a literature-derived optimum. |
| Bias/extra trainable modules | bias=none; no extra trainable base modules | U01; S05; W01 | SOURCE_INFORMED_PROJECT_CHOICE | Keep adapter-OFF baseline unchanged by bias/base updates. | Mapping contradictions require explicit review; no silent bias training. |
| Initialization | Explicit PEFT reference no-op LoRA initialization, init_lora_weights=True; B starts zero | S05; W01 | SOURCE_INFORMED_PROJECT_CHOICE | Fresh initial adapter leaves the base behavior unchanged. | Pin exact A initialization/RNG implementation; no data-driven initialization. |
| Optimizer | paged_adamw_32bit | U01; S01 paged-optimizer principle; S07 optimizer interface | SOURCE_INFORMED_PROJECT_CHOICE | Specify the implementation family/state rather than import an optimizer default. | Exact string/support/version needs stack mapping; paper paging alone does not prove this interface. |
| Adam betas/epsilon | beta1=0.9, beta2=0.999, epsilon=1e-8 | S07 documented parameters; S01 beta2; U01 reproducible recipe | SOURCE_INFORMED_PROJECT_CHOICE | Explicitly adopt conventional documented ancillary settings to avoid hidden optimizer defaults. | Defaults are identified precedent, not scientific optimality; exact optimizer equations must be pinned. |
| Learning rate | 2e-4 | S01 Table 9; U01 | SOURCE_INFORMED_PROJECT_CHOICE | One common reference-informed rate. | No project tuning; no claim this rate suits all sizes/tasks. |
| Scheduler | Constant; one scheduler step per optimizer step, including the underfull final update | S01 Appendix B.2; W01; U02 stepping contract | SOURCE_INFORMED_PROJECT_CHOICE | Fixed rate without performance-adaptive schedule; explicit common step semantics. | Original schedule searches are not repeated here. |
| Warmup | None, warmup_steps=0 | W01; U01 | PROJECT_DESIGN_CHOICE | Preserve the constant minimal regimen. | Not inferred as a universal rule from the paper. |
| Weight decay | 0 | U01; S07 parameter interface | PROJECT_DESIGN_CHOICE | No added weight-decay intervention; no existing workload rule conflicts. | Not alleged to be a QLoRA paper value. |
| Gradient clipping | Global L2 norm cap 0.3 over trainable gradients, once per completed effective update after normalization | S01 Appendix B.2; U01 | SOURCE_INFORMED_PROJECT_CHOICE | Authenticate and adopt the reference max-gradient norm. | Source-derived engineering setting, not optimized for this project. |
| Effective batch | Nominal 16; exactly 16 actual eligible examples per ordinary optimizer update; final boundary under U02 | S01 Table 9; U01; U02 boundary | SOURCE_INFORMED_PROJECT_CHOICE | Common update workload across candidates using the same instantiated histories. | A final r-example update for r>0 is smaller and not numerically equivalent to a 16-example update. |
| Microbatch | Largest capacity-certified positive divisor of group size: 16 ordinarily, r for the tail | U01/U02; S06/S07 | PROJECT_DESIGN_CHOICE | Reduce instantaneous memory without changing group membership, order or objective. | Capacity alone may vary the partition; no fitting divisor means runtime certification fails, not a dataset/recipe change. |
| Gradient accumulation | Group size divided by microbatch size; deterministic partition preserving grouping/order and token-normalized gradient | U01/U02; S06 | SOURCE_INFORMED_PROJECT_CHOICE | One update per fixed ordinary or final group; no per-microbatch averaging artifact or cross-group carry. | Floating-point differences require receipts/certification, not equality assumptions. |
| Loss normalization | Sum completion-token CE across the effective batch divided by its total loss-bearing shifted target-token count | S06; U01; W01 mask | SOURCE_INFORMED_PROJECT_CHOICE | Target lengths differ; weight actual prediction tokens, not example means. | Verify exact masks/shift/denominator and no duplicated Trainer scaling. |
| Sequence packing | Disabled | W01; U01 | EXISTING_WORKLOAD_RULE | Preserve complete examples and boundaries. | No packing-based burden advantage. |
| Truncation | Prohibited for input and label | W01; U01 | EXISTING_WORKLOAD_RULE | Full eligible history and complete accepted labels. | Overlength examples block feasibility, not justify dropping them. |
| Coverage/order | Exactly one complete pass, existing chronological/hash/key order | W01; U01 | EXISTING_WORKLOAD_RULE | Minimal full-history exposure with no dosage search. | Does not guarantee learning or divisibility by batch size. |
| Early stopping | Disabled | W01; U01 | EXISTING_WORKLOAD_RULE | Finish only at the predetermined coverage endpoint. | Interruption/invalidity is not a successful short run. |
| Checkpoint selection | Final valid adapter at predetermined complete-coverage endpoint | W01; U01 | EXISTING_WORKLOAD_RULE | Avoid protected-target checkpoint selection. | No best-loss/best-evaluation intermediate selection. |
| Intermediate checkpoints | Authenticated recovery only at completed update boundaries | W01; U01 | EXISTING_WORKLOAD_RULE | Resume exact state, data position and coverage. | Cadence/resource behavior still requires implementation evidence. |
| H1/H2/H3 parent/reset | ORIGINAL, fresh adapter/optimizer/scheduler/RNG per stage and training seed | W01; U01 | EXISTING_WORKLOAD_RULE | Independent accumulated-history rebuilds. | Same-stage authenticated resume alone may restore stage state. |
| Training seeds | Three distinct integers from the candidate-independent protocol-hash algorithm below | U01 | PROJECT_DESIGN_CHOICE | Minimal resource-aware stochastic replication. | Not statistical optimality or sufficiency for broad inference. |
| Seed pairing | Same seed roster across comparable H stages and weight conditions | U01; W01 | PROJECT_DESIGN_CHOICE | Pair initialization policy; do not reroll favorable seeds. | Different histories consume different RNG streams; no guaranteed covariance reduction. |
| Evaluation seeds/controls | Existing inherited native generation profile | W01/common requirements | EXISTING_WORKLOAD_RULE | Hold evaluation budget/decoding fixed across paired conditions. | Training seeds do not override the evaluation seed. |
| Determinism | No automatic full_determinism; explicit fixed settings/environment and limitations | U01; S08/S07 | SOURCE_INFORMED_PROJECT_CHOICE | Avoid hidden algorithm substitutions and false reproducibility claims. | Seeds alone do not establish bitwise cross-device identity. |
| Native research evaluation | Same pinned native quantized original: adapter OFF baseline, adapter ON adapted; no merge | U01; W01 | EXISTING_WORKLOAD_RULE | Isolate adapter effect under a shared native profile. | Quantized native profile is not GGUF/deployment authority. |
| Deployment | Separate merge/export if required, quantization/GGUF/llama.cpp and fidelity track | W01; U01 | EXISTING_WORKLOAD_RULE | Keep numerical/behavioral transformation claims separate. | No local equivalence or fidelity assumed. |
| Final incomplete effective batch | FINAL-BATCH POLICY V1: q=floor(n/16) full groups; if r=n mod 16>0, one final group of r real examples, actual-token-normalized; otherwise none | U02; W01 full one-pass coverage | PROJECT_DESIGN_CHOICE | Preserve exactly one complete pass without dropping, repeating or manufacturing history. | Explicit nominal-batch boundary; report the smaller final batch, never equivalence to 16 or candidate-adaptive treatment. |

## Effective-batch and loss contract

For an ordinary group G of 16 consecutive full examples in the existing stage
order, define `N_G` as the count of actual loss-bearing shifted target labels
(including verified completion terminals), excluding masked input/template/padding.
Require N_G positive. The objective is `sum_G CE(target_tokens) / N_G`.
Do not average example means, average microbatch means, count padding as targets,
or divide this already normalized loss again by accumulation steps.

On a single-device Colab execution profile, choose the largest capacity-certified
positive divisor of 16 as the ordinary microbatch size, according to separately authorized
capacity verification under the unchanged recipe; accumulation is 16/microbatch.
Grouping, example order and optimizer-update boundary stay fixed. If no partition
fits, reject the runtime. A different distributed topology needs prior certification
of the same global group/denominator; it is not an automatic capacity fallback.

Each microbatch contributes its summed target-token loss divided by the same full
group N_G. Accumulate only within the group, then clip once using the global L2
norm cap 0.3 and take one optimizer step. Reset gradients between groups. Take
one scheduler step per optimizer step, including the underfull final update.
BF16 arithmetic, FP32 trainable storage/gradients/optimizer moments and numerical
limitations must be recorded. This math defines intended equivalence, not bitwise
identity across microbatch partitions. Later nonprotected conformance must check
full-group and accumulated gradients/update semantics with the pinned stack.
No such check occurs here.

### FINAL-BATCH POLICY V1 (authorized design)

**RECIPE_FINAL_BATCH_POLICY: DETERMINISTIC_RULE**, under U02. Let n be the number
of complete eligible training examples in an H stage, q=floor(n/16), and r=n mod 16.
Preserve the existing deterministic example order. Perform q ordinary optimizer
updates on exactly 16 consecutive real eligible examples each. If r>0, perform
exactly one final underfull optimizer update on the remaining r consecutive real
eligible examples; if r=0, no underfull update occurs. Total optimizer steps are
`q + indicator(r > 0)`. Every eligible example is visited exactly once. Empty
stages have zero updates and cannot establish adaptation; H0 semantics are unchanged.

For the tail, let N_tail be its actual loss-bearing shifted target-token count,
with the same completion mask/terminal rules as N_G and no input/template/padding
tokens counted. Require N_tail positive. Its objective is
`sum_tail CE(target_tokens) / N_tail`. Every microbatch contributes its summed CE
divided by that same N_tail; accumulate only within the tail group, clip once
after completing the group, and perform exactly one optimizer step followed by
one scheduler step. Use the same optimizer, LR, constant scheduler, precision,
adapter configuration, clipping cap and all other recipe controls as ordinary updates.
Do not scale tail loss to imitate a 16-example group or change LR for the tail.

For the single-device tail, choose the largest capacity-certified positive
divisor of r as microbatch size; `accumulation_steps = r / microbatch_size`.
Ordinary groups retain the largest capacity-certified positive divisor-of-16 rule.
Only capacity may change the runtime partition; scientific group membership,
order and token-normalized objective remain fixed. If no positive divisor execution
fits the certified runtime, runtime certification fails. Do not alter data or recipe.

Prohibit drop_last, dropping remainder examples, repetition, wrapping to the
beginning of history, gradient carry into a second pass, duplicates to reach 16,
synthetic/filler examples, counting padding as examples, changing history
construction for divisibility, skipping the tail optimizer step, and candidate-specific
tail behavior. No loss rescaling, second denominator or additional accumulation
division may manufacture a nominal 16-example tail.

Nominal effective batch is 16 examples. The underfull update is a predeclared
end-of-stage boundary preserving the more fundamental one-pass/full-history
intervention. It introduces a smaller final optimizer batch when n is not divisible
by 16; report that limitation. **The tail update is not numerically equivalent to
a 16-example update.** Compared candidates/conditions use the same instantiated
stage histories and n/q/r schedule, so the boundary is common, not candidate-adaptive.
Tail size is a stage-history fact, not a candidate property; no corpus is instantiated here.

All later training/resource manifests must separately report stage example count n,
q, r, number of ordinary updates, whether an underfull update occurred, its actual
example count, actual loss-bearing token count, microbatch/accumulation partition,
and total optimizer steps `q + indicator(r > 0)`. When no tail occurs, report zero
tail examples/tokens and a not-applicable tail partition rather than inventing one.
Actual counts and certified partitions remain later evidence, not assumed feasibility.

## Candidate-independent seed and reproducibility policy

Three independent training seeds per weight-adaptation condition is a **project
design decision** requested in U01. One seed supplies no stochastic replication;
three is a resource-aware minimum replication policy for this free-compute
development study. It is not claimed statistically optimal, a power calculation,
or sufficient for broad population inference. Statistical analysis and dependence/
replicate handling remain separate pre-experiment obligations.

Fixed deterministic seed algorithm, instantiated only after review/freeze:

1. Bind the exact-byte SHA-256 of the reviewed/frozen Workload document and this
   memo in a protocol seed receipt. These two protocol hashes are the namespace;
   neither contains the future seed receipt, preventing self-reference.
2. For ordered slots i=0,1,2, hash UTF-8 ASCII domain
   `development-subject-training-seeds-v1`, one NUL byte, the two 32-byte hashes
   in Workload-then-memo order, and unsigned big-endian 4-byte i and collision
   counter c. Start c=0 independently for each slot.
3. Interpret the digest's first 4 bytes as unsigned big-endian x and set
   `seed = 1 + (x modulo (2^31 - 1))`. If already used in an earlier slot,
   increment c and repeat; otherwise record the distinct integer and digest.
4. Publish/sign the ordered seed receipt with hashes, domain, counters and integer
   values before any training outcome. Actual values belong only in the separate
   seed receipt bound to final frozen Workload/Recipe hashes; neither hashed document
   contains those values or a receipt hash. The derivation is not performance-dependent.

The integer-range/mapping/collision rules are administrative project choices,
not scientific hyperparameter optima. No candidate/model identity, hardware, stage,
condition, corpus size, timestamp, measured score, random run UUID or desired
result enters the namespace. Run manifests reference that common protocol seed
receipt and their seed slot; fresh processes for comparable H stages and weight
conditions initialize from the same ordered roster. Unique run IDs cannot change
the seed set. A new reviewed protocol version requires a new explicit receipt;
no silent hash change/reroll is allowed after outcomes.

Set the recorded seed consistently for applicable Python/NumPy/Torch/accelerator
RNGs before fresh adapter initialization; preserve sampler order from Workload
rather than enabling random shuffling. Same-stage resume restores exact RNG,
optimizer/scheduler and dataset/update position instead of reinitializing halfway
through a run. Record dtype/module/initialization inventory, package/build/driver/
hardware identity, kernel/backends and deterministic flags, including any TF32/
algorithm settings. Require explicit requested/effective receipts and preserve
the same setting policy across compared conditions.

Do not enable Trainer full_determinism merely because the switch exists.
Unsupported nondeterminism is reported and its claim/analysis limits reviewed;
do not silently substitute algorithms, drop an unsupported operation, change
precision or pretend seeds guarantee identical outcomes. Runtime/build identities
and conformance remain later certification, not a permission to tune the recipe.

## Conflict check and preserved authority

| Required check | Finding and disposition |
| --- | --- |
| Attention-only versus canonical all-linear | Genuine methodological departure, not logical contradiction. Preserve W01's already designed Q/K/V/output-equivalent target rule. Reference all-linear rank/quality observations do not transfer automatically. |
| Dropout disabled | Preserve 0.0. The reference's nonzero dropout is not a mandatory definition of QLoRA and does not justify adding project regularization. |
| Bias and weight decay | No existing workload rule conflicts with bias=none or weight_decay=0. Explicitly declare both; architecture mapping contradictions would require review, never automatic bias training. |
| Native authority | Pinned original reconstructed under the same native quantization/runtime profile with adapter OFF versus ON. No authoritative merge; preserve base and adapter hashes/dtypes/configurations independently. |
| GGUF/llama.cpp | Later deployment-fidelity only; failures cannot rewrite native Study outcomes. |
| Hyperparameter/checkpoint selection | No protected-outcome tuning, protected-population recipe search, best-score checkpoint, seed reroll or candidate-specific method/dtype switch. Endpoint checkpoint and recovery semantics stay intact. |
| BF16 capability | An incompatible candidate/runtime remains pending or fails the relevant feasibility gate. No FP16/FP32 full-compute fallback. FP32 stability/parameter/state operations explicitly listed above do not redefine the common BF16 compute profile. |
| Nominal batch versus one pass | U02 explicitly authorizes the smaller final r-example boundary of nominal batch 16. Exactly one pass is preserved; report the limitation and make no numerical-equivalence claim. No dataset/divisibility or candidate-specific adjustment. |

The later authorized ordering repair changes only Selection/Common Requirements/
Stage Gates/JSON governance references to the independent pre-discovery gate.
Only this memo and Workload's affected recipe, justification, audit and readiness/
next-task statements are updated for U02. Scientific population,
training examples, history algorithm, attention targets, coverage, local usability,
study contrasts and leakage matrix remain unchanged. Aggregate later-stage evidence
obligations remain pending; this design checkpoint does not turn them into candidate-gate PASS.

## Readiness, remaining items and authorization boundary

**TRAINING_RECIPE_DESIGN: FROZEN_DESIGN**. U02 resolves
**RECIPE_FINAL_BATCH_POLICY** as a deterministic rule. Rank/scaling, optimizer and its explicit ancillary
parameters, LR/scheduler, regularization, precision/quantizer, ordinary batch/loss,
seed derivation and replication policy now have proposed source/design justifications.
Gradient clipping 0.3 is authenticated and not pending. No other scientific
recipe-design blocker remains; runtime compatibility/conformance is not established.

All five PRE_LANDSCAPE scientific designs are **FROZEN_DESIGN**:
EVAL_POPULATION_DESIGN, TRAINING_DATA_SPEC_DESIGN, HISTORY_DATASET_DESIGN,
TRAINING_RECIPE_DESIGN and LOCAL_USABILITY_DESIGN. No candidate gate is PASS;
**REVIEW_FREEZE is CLOSED (design only)**. The authorized review accepts the complete
design/justification package, Selection/Common Requirements/Stage Gates, unchanged
proposed upstream dependency status, private/internal prototype scope and resource-
accounting dimensions. Production authentication/native orchestration/official-run
conformance retain later prerequisites. REVIEW_FREEZE covers only the candidate-
independent design; an instantiated candidate-audit envelope is not required.
PRE_DISCOVERY_AUDIT_ENVELOPE is the separate mandatory gate: explicitly instantiate,
independently review/approve and freeze cutoff, candidate scope, permitted source
list/source classes and stopping rule before any candidate/model-landscape search,
metadata collection, inspection, formal audit, comparison or selection. No candidate
identity/evidence collection before PASS or retroactive envelope definition. Its
status is PENDING_EVIDENCE; no envelope is instantiated and discovery stays unauthorized.
Review/freeze and any later audit each require their applicable authorization.
After these documents reach final frozen bytes, instantiate the unchanged deterministic
policy in the separate seed receipt before outcomes, without mutating either document.
No seed values/receipt hash is embedded here. This is not an unresolved scientific seed policy. Runtime
pins, exact initialization/quantized-module inventory and capability, loss/mask
and accumulation conformance, resource/history manifests, statistical plan and
native runner/completion implementation retain their later-stage obligations.
No model-specific parameter choice or actual runtime setting is inferred here.

Candidate discovery remains unauthorized until independent design review/freeze,
PRE_DISCOVERY_AUDIT_ENVELOPE PASS and separate bounded audit authorization. Comparison and
selection also remain blocked; documentation does not establish free-Colab or
local feasibility, scientific efficacy, deployed fidelity or an optimal recipe.

The earlier methodology-page verification is recorded above. This final-batch
revision performs only documentation/static validation, with no web search or new
web inspection. No candidate/model-landscape search, candidate inspection,
weight/data/runtime download, candidate tokenization, inference, training,
runtime certification, protected-task/historical-output inspection, Study 1/2/3,
Qwen30/draft3/product modification or model selection occurs. Only the user-authorized
candidate-independent design freeze, separate seed receipt and checkpoint commit occur.
