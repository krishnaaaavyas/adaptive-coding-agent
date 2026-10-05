# Development Subject common requirements v1

Requirements ID: `development-subject-common-requirements-v1`

Status: **FROZEN_DESIGN_LATER_EVIDENCE_PENDING**. REVIEW_FREEZE is CLOSED for the
candidate-independent design only, under DEVELOPMENT_SUBJECT_FREEZE_MANIFEST_V1.json.
No dataset, runtime, selection or upstream protocol is frozen/certified here.
Preparation date: 2026-10-04
(Asia/Calcutta).

This candidate-independent envelope supplements Development Subject Selection
v1. It specifies inherited constraints, derived bounds, candidate-independent invariants,
and prerequisites that cannot honestly be filled with numbers. Workload and Recipe
complete the frozen design; actual manifests, tokens, mapping and runtime evidence
remain pending. PRE_DISCOVERY_AUDIT_ENVELOPE is pending and uninstantiated.
No candidate, protected task, or historical output
was inspected to choose these requirements. There is no execution authorization.

## Source review and applicability

Only governance and generic harness source were inspected. Task requirements were
reviewed through the public-task schema, generic admission/output functions and
Protocol-v2 evaluator contract; no experiment task/config contents, product source,
private tests, scorer task implementations, or historical generated outputs were
read. Scorer governance was reviewed through `harness/scorers/fixtures/README.md`;
it distinguishes scorer fixtures from benchmark tasks and limits structural
convention scoring. No scorer fixtures were executed or treated as scientific data.

| Source and locator | What is inherited | What is not established |
| --- | --- | --- |
| `benchmark_design/context_policy/current-repo-v1-draft3.json`: `/budgets`, `/profile_schema`, `/public_task_schema`, `/H/BC_owned`, `/output`, `/normative_draft3` sections 7-11 | Exact proposed Study-1 P/K/H framing/byte limits, generation and admission controls, chronology and curated-evidence contract | Draft3 is itself `proposed-not-frozen`; adopting its values here does not freeze it or turn curated state into autonomously learned history. |
| `harness/context_policy/core.py`: limits and SYSTEM; `boundary.py:public_task`; `selector.py:select`; `evidence.py:pack_h` | Independent implementation confirmation that P/K/H packing counts serialized bytes | Byte limits are not tokenizer token limits; the H prompt budget is not a training corpus cap. |
| `harness/context_policy/protocol.py`: `CONTROL_VALUES`, `messages`, `output_preflight`, `treatments`, `common_admission`; `prepare.py:prepare_run` | Exact rendered input fit, reference-output preflight, all-condition admission before outcomes, fresh request isolation | Preparation does not execute generation; the legacy pilot runner cannot execute a draft3 request. |
| `harness/ADAPTATION_CONDITIONS.md`: Conditions, Information matching and budgets, Interpretation | A/B/M/C/BC meanings, within-model/task fairness, M/C information matching, target/regression/convention success | D/E remain reserved; no weight-training recipe, full training sequence size, epoch count or accumulated-history dataset is specified. |
| `harness/PROTOCOL_V2.md`: Configuration and privacy, Results, Integrity and failure attribution | Model/evaluator separation, complete artifact evaluation, independent target and regression tests, convention scoring and integrity | Existing pilot task contents and outcomes supply no requirements here. |
| `harness/PROVENANCE.md`: run manifest, Git and failure policy; `harness/DEFECT_POLICY.md`: rules | Exact-byte config and input hashes, runtime/run identity, immutable historical results, outcome-independent defect handling | A new completion/resume implementation still requires verification. |
| `harness/REPRODUCIBILITY.md`; `harness/inference.py`: module defaults | Record verified identity/controls and unknown metadata honestly | Legacy llama.cpp transport, unset seed and its output default are not the native Development Subject evaluation profile. Its unavailable template verification must be replaced by authoritative native pinning in a later implementation. |
| `DEVELOPMENT_SUBJECT_SELECTION_V1.md`: B, F-K, M-N | Common requirements before comparison, fresh-base stages, native authority, free compute, completion and storage boundaries | No candidate audit, recipe activation, or runtime feasibility is established. |

The inherited envelope applies to the proposed draft3 information regime. Future
Study-2/3 weight treatments must satisfy its evaluation fairness and native
authority, but their dataset/treatment construction requires its own reviewed
specification. Do not claim that draft3 already defines all three studies.
The separate Qwen30 confirmation methodology remains unchanged and PENDING COMPUTE.
No Qwen30 context length, precision, LoRA rank or optimizer is imported as a
Development Subject-specific requirement.

## 1. Evaluation context envelope

**Frozen design adopts inherited byte limits and token reserve; absolute
rendered-token capacity remains pending verification.** Inherit draft3 exactly:
P <= 4,096 UTF-8 bytes, K <= 12,288 UTF-8 bytes, H <= 4,096 UTF-8 bytes. These are
serialized ceilings, not transformed token quotas or loose upper-bound advice.
K includes its outer framing and inventory; inventory is <= 2,048 bytes **within**
K. H includes its framing; BC owns two <= 2,048-byte portions **within** H, with
the original outer/lane ownership. Do not add those sub-budgets again.

The exact existing PUBLIC_TASK wrapper adds 30 UTF-8 bytes. Thus the maximum user
message content is 20,510 bytes. The exact inherited system content adds 553
UTF-8 bytes, yielding 21,063 bytes across system and user content, **before chat
template/BOS/generation-prompt overhead**. These are conservative ceilings; the
components need not simultaneously saturate them on a real task.

Reserved generation is exactly **2,048 tokens** including the inherited native
terminal accounting. Reference preflight remains `raw_reference_tokens + 1 <=
2048`, with no automatic BOS/EOS or template in that reference measurement. This
preflight screens baseline complete-replacement capacity, not solution length.
Generated token-limit failure remains an outcome, never permission for a retry,
partial-file answer, or post-treatment removal.

There is no justified universal numeric `evaluation_input_tokens` or
`evaluation_context_tokens`. For a verified tokenizer/template profile t define
`I_t = maximum len(render_t(system, canonical_P, exact_K, exact_H_condition))`
over the independently specified evaluation population and all required
conditions. Rendering includes actual special tokens and generation prompt.
Require **effective native sequence capacity >= I_t + 2048**. Byte-to-token
equivalence and a nominal advertised context size cannot establish this.

Before comparison, specify the evaluation population/envelope fixtures and their
coverage independently of candidate support. A later authorized no-generation
tokenization/profile check must establish a conservative bound covering that
population (or a proven bound covering every allowed byte-envelope message).
Do not inspect protected contents in this specification task. Do not use a
candidate's low capacity to select a smaller population. The generic draft3
admission machinery remains unchanged, but exclusions cannot be used to claim
that a candidate supports the entire fixed common envelope.

**Blockers EVAL_POPULATION and EVAL_TOKEN_BOUND:** independently reviewed population
and boundary coverage, followed by authenticated tokenizer/template/native
capacity receipts. The mathematical requirement is fixed here; token counts are
profile-dependent evidence, not candidate-specific relaxation.

Preserve identical K bytes/hash across conditions; identical context capacity,
output reserve, controls, tools and retry policy; no padding of A; no capacity
transfer to BC; whole-file/whole-record packing exactly as draft3. M/C matching
remains independently certified. Apply a common pre-outcome admitted population
across compared conditions, with missing infrastructure blocking finalization.

## 2. Adaptation/training sequence envelope

**DESIGN_FROZEN; TOKEN_ACCOUNTING_PENDING.** Workload section 2 specifies the
complete weight-training example and content envelope; actual token lengths remain
profile-dependent later evidence. Do not
reuse H's byte cap, the output reserve, or a confirmation model's context length
as that number.

Apply Workload section 2's frozen training-example contract:
authorized input/context, supervised target, template boundaries, terminal tokens,
loss mask, eligibility, and immutable lineage. Let `D_j` be the full eligible
stage dataset and `L_t = max tokenized_full_example_length_t` across every `D_j`.
The capacity requirement is native forward/backward/optimizer/save/reload support
for **every complete eligible example**, at least `L_t` tokens under the pinned
training renderer. The eventual dataset specification must justify a common
content bound and any scientifically necessary length ceiling before candidate
comparison; profile-specific token lengths then verify compliance.

Silent truncation is prohibited for inputs **and labels**. No shortening of
examples or candidate-specific rejection is authorized. An example exceeding a
future reviewed ceiling is a dataset/envelope blocker, not a truncated example.
Either revise the dataset/envelope under explicit candidate-independent review
with new provenance, or reject the insufficient runtime/candidate. Splitting,
chunking, packing and loss-mask changes require an explicit prior scientific
specification preserving information/label semantics; none is silently enabled
here. Include padding/packing overhead in capacity accounting if later authorized.

The full-example format/content/length policy and recipe are frozen in Workload
and Recipe. Actual eligible dataset construction and separately authorized token
accounting/runtime verification remain prerequisites to burden comparison; do not
replace those facts with invented token counts or capacity claims.

## 3. H1/H2/H3 accumulated-history envelope

**DESIGN_FROZEN; HISTORY_DATASET_MANIFESTS_PENDING.**
H1/H2/H3 denote successive authorized accumulated-history stages, not three
arbitrary fixed-size batches. At a stage's authenticated cutoff, include the full
eligible authorized earlier history for that stage. Cutoffs are fixed before the
target becomes available; no current-target solution, private evaluator, future
outcome, benchmark selection judgment or unauthorized source is eligible.

Use draft3's chronology, source authorization, immutable revisions, certifications
and explicit supersession as a governance floor. A prior episode is a prior
public request, associated authorized attempts/changes and closing feedback.
Curated prompt evidence/rules remain curated, not a claim of autonomous learning.
Weight-supervision labels and source-to-example transformation follow frozen
Workload section 2; the curated-H contract alone does not authorize training.

With that contract, eligible stage sets are accumulated prefixes at ordered
cutoffs; revisions/withdrawals are resolved deterministically at each cutoff.
Earlier eligible information remains included unless an explicit eligibility
revision/withdrawal changes it, with immutable lineage. Full history does not
mean retaining obsolete superseded records or semantic duplication by default.
Any deduplication/transformation must be specified before candidate selection.

Capacity means processing the entire D_H1, D_H2 and D_H3 over as many resumable
sessions as necessary, not placing the entire corpus in a single context window.
No candidate-specific history subsampling, dropping long examples, choosing only
easy episodes, recency-only training, or adapter continuation between stages.
H prompt packing and its fixed budget never cap or sample the weight-training
corpus. Actual counts, bytes, token totals and steps must be measured from an
authorized independently constructed manifest, not historical model outcomes.

Prerequisite: stage cutoff schedule, source/label contract, construction and
revision policy, full stage manifests and coverage checks. Corpus counts remain
null until those exist; a final training resource comparison cannot be completed
before they do.

## 4. Minimum adaptation comparison lifecycle

**DESIGN_FROZEN; MODULE_MAPPING_AND_RUNTIME_PENDING.** Workload section 4 and Recipe
fix the common method/targets/parameters/seed policy; candidate instantiation is unverified.

`authenticated ORIGINAL base -> fresh native PEFT adapter -> train on full eligible stage history -> save -> destroy worker -> reload ORIGINAL plus saved adapter -> native evaluation -> repeat from ORIGINAL for next stage`

Verify base identity and immutability; new stages receive fresh adapter,
optimizer, scheduler and RNG initialization under a predeclared seed policy.
Verify save/reload adapter keys, shapes, dtypes and tensor hashes plus later
predeclared native reload checks. Save all provenance, stage coverage and required
artifacts under Selection v1's atomic completion contract. The baseline is the
same original base without the stage adapter, using comparable native controls.

No adapter-on-adapter, no merged derivative as parent, no foundation training.
Within-stage recovery may resume only an authenticated matching stage checkpoint
with optimizer/scheduler/RNG/sampler/step state; otherwise restart that stage from
ORIGINAL. This is distinct from building the next accumulated-history stage.
No training or synthetic lifecycle execution is authorized now.

Before burden ranking, instantiate the frozen common scientific adaptation workload:
method, target-selection rule, rank policy, optimizer/loss, epochs or step/coverage
schedule, effective batch policy, train/evaluation precision policy and repeats.
Architecture-specific module names may instantiate a predeclared target rule;
they cannot silently create a lighter treatment for one candidate. Document
comparability limitations. No fixed rank or dtype is borrowed from Qwen30.

## 5. Free-compute resource accounting

**Measurement dimensions determined; numerical limits and measurements pending.**
Paid GPU compute is excluded. Observe actual assigned hardware and quotas; do not
assume a particular Colab GPU, session duration or availability. Record workload,
hardware, drivers, runtime, precision, adapter recipe and all history sizes so that
measurements or documented bounds have comparable assumptions.

Account separately for peak GPU memory; peak host RAM; local disk peak;
persistent storage peak and retained footprint; wall-clock training time for full
history coverage; inference/evaluation time; checkpoint save, upload/verification,
original reload, adapter reload, merge/export and conversion time where required;
and restart cost after interruption. Include caches, optimizer/activation states,
temporary copies, validation and I/O peaks rather than just parameter storage.
Separate native experimental costs from deployment transformation costs; export
is not automatically required for native evaluation. Account for non-GPU scorer
and test time when it affects full-run completion.

Restart cost includes lost work since the last verified durable checkpoint,
reacquisition/copy/cache rebuild, verification, reload and resume or full-stage
restart. Report interrupted attempts and incomplete planned workloads separately;
partial training cannot masquerade as a lower full-stage time. Compute quota and
wall-clock availability constrain operability but are not stable numeric gates.
Lower burden uses the Selection v1 evidence/dominance rules, not a weighted score
or a claim based solely on parameter count. Unmatched or overlapping bounds remain
incomparable. Use local working copies and verified durable Drive snapshots.

**RESOURCE_EVIDENCE pending:** full frozen workload and separately authorized
hardware/resource evidence; reject an insufficient runtime without changing the
workload. A new numerical time/memory threshold needs independent justification
and review before comparison; none is invented here.

## 6. Local deployment envelope

**Machine class determined; practical resource evidence pending.** Windows,
24 GB system RAM and RTX 2050 with 4 GB VRAM are user-specified physical capacities,
not budgets wholly available to model weights. Account for OS/application usage,
runtime/driver allocations, context/cache, offload, conversion peaks and disk.
CPU execution and CPU/GPU offload are permissible if documented and practical;
full GPU residency is not required. Do not select a quantization bit-width now.

There must be a documented same-original GGUF/llama.cpp route supporting the
architecture and exact tokenizer/template, local inference, required prototype
prompt/output workload, and a reproducible merge/export/quantization chain.
The prototype workload provisionally inherits the evaluation message and output
envelope; any additional product workload needs separate prior specification.
Numerical equality and deployment fidelity remain unproven. Local product serving
is separate from authoritative Study 1/2/3 native evaluation.

**LOCAL_DISK and LOCAL_RESOURCE_EVIDENCE pending:** actual usable disk/free RAM/VRAM,
conversion location, documented peak footprints and later runtime verification.
**LOCAL_USABILITY_RUNTIME pending when triggered:** Workload section 5 freezes
operational completion/resource-integrity criteria; latency is reported only,
without a numerical hard threshold. Actual usability remains unverified.
Quantization level is a later evidenced deployment configuration within this
envelope, not a reason to lower native scientific requirements.

## 7. Intended prototype license use

**Proposed use scope determined; checkpoint license audit pending.** The current
scope is research and a private/internal local prototype: obtaining/storing the
original, parameter-efficient fine-tuning, storing/reloading adapters and private
checkpoints (including private persistent Drive storage), local inference, native
evaluation, merge/export where required, quantization/conversion and prototype
integration. Each activity must be permitted or not prohibited under the actual
checkpoint license and applicable conditions; record attribution, access,
derivative-use and other obligations from source text.

Public redistribution of weights, adapters or GGUF is **not required** for the
current prototype. Neither a public hosted service nor sale/external commercial
distribution is authorized or assumed. License restrictions on those activities
alone do not fail this current-use gate. If that scope is later intended, review
it explicitly before acting. Private cloud storage does not authorize publishing.
An unresolved restriction on a required activity blocks G02; do not infer license
permissions from the phrase open weights. This document defines intended actions
and makes no legal finding about a model; no legal/web research occurs here.

## 8. Runtime reproducibility and numeric provenance

Eventually pin exact original checkpoint revision/file hashes, tokenizer files and
encoding options, chat template bytes/rendering, system/generation prompt, native
runtime/package versions/builds and hardware/determinism limitations; QLoRA
quantizer/version/settings and compute dtype if used; adapter targets/rank and
initialization; optimizer/scheduler/loss/batch/coverage; seed and repeat policy;
generation controls; context/output and training capacities; dataset/history
manifests/cutoffs; scorer/test/protocol/configuration identities. Unsupported
controls must be explicit and compatible with the inherited contract. No pin is
invented now, and the legacy llama.cpp identity check alone cannot certify native
Hugging Face/PEFT authority.

Numbers below are frozen Development Subject design adoptions/arithmetic, without
freezing their upstream source or certifying capacity. JSON
records the same numeric provenance and inherited generation control values.

| Value | Source artifact and locator | Derivation | Classification |
| --- | --- | --- | --- |
| P 4,096 bytes; K 12,288 bytes; H 4,096 bytes | `current-repo-v1-draft3.json` `/budgets/{P,K,H}`; normative section 11; `core.py` limits | Exact serialized UTF-8 ceilings | Inherited exactly |
| Inventory 2,048 bytes; BC owned portions 2,048 bytes each | Same artifact `/budgets/inventory`, `/H/BC_owned`; `selector.py:select`, `evidence.py:pack_h` | Sub-budgets inside K/H, not additional capacity | Inherited exactly |
| Output reserve 2,048 tokens; terminal allowance 1 token | Same artifact `/budgets/generation`, `/output/terminal_allowance`, normative 7.6 | Exact reserve and reference check | Inherited exactly |
| Public wrapper 30 bytes; system 553 bytes | Same artifact `/system`; `protocol.py:messages` exact wrapper literals | UTF-8 lengths of those exact literals/content, excluding template | Deterministically derived |
| User maximum 20,510 bytes; system+user maximum 21,063 bytes | Above ceilings and literal lengths | 4096 + 12288 + 4096 + 30; then + 553 | Deterministically derived conservative ceilings |
| Generation temperature 0, top-p 1, repetition penalty 1, frequency/presence penalty 0, requested seed 0, completions 1, retries 0 | Same artifact `/profile_schema/controls`, normative section 9; `protocol.py:CONTROL_VALUES` | Copy controls exactly, with supported/effective status and disabled top-k, no text stops/clipping/truncation/context shifting | Inherited exactly; evaluation seed does not specify training seed policy |
| System RAM 24 GB; GPU VRAM 4 GB | User follow-up attachment, section 6 Local deployment envelope | Machine-class designation as supplied; no unsupported usable-memory or unit conversion | User supplied |
| Absolute context/input tokens, maximum training sequence, H1/H2/H3 counts and usable disk | Candidate/profile/manifest observations not yet established | Later evidence; remain null | PENDING, not newly invented |
| Adapter targets/rank, recipe, coverage, nominal batch/tail and three-seed replication policy | Workload section 4 and Recipe's source/design justification | Frozen common design; actual instantiated counts/steps/seed receipt separate | FROZEN_DESIGN, not empirical feasibility |
| Latency hard threshold | Workload section 5 | None; latency is reported only | FROZEN_DESIGN usability policy |

The policy source exact-byte SHA-256 is
`d93f5136339153e65e35ef720333e21260292bc680f2cd3cfe608dfa46939a3b`.
Identifiers such as v1/H1/H2/H3/Study 1/2/3 are labels, not new numeric workload
limits. No other numeric scientific budget is declared here.

## 9. Native authority and deployment transformation

Authoritative evaluation is **pinned ORIGINAL base + native PEFT adapter (where
applicable) + frozen native Hugging Face/PEFT runtime/tokenizer/template/controls**.
QLoRA quantization is part of the pinned native representation when authorized.
Future Study 1/2/3 results must use that authority and the unmodified evaluator
integrity contract. Count only authenticated COMPLETE runs, including valid
negative results, and preserve interrupted/invalid receipts.

Merge/export -> quantization -> GGUF -> llama.cpp is a separate deployment chain.
A later fixed-prompt/task paired fidelity comparison must predeclare acceptance,
repeats and scoring without token-equality assumptions. Its failure is a deployment
finding, not permission to rewrite native outcomes or choose another subject based
on adaptation effect. **FIDELITY_SPEC pending**, separately authorized later.

## 10. Failure rule and remaining blockers

If no candidate satisfies the eventually frozen envelope on free compute, record
**BLOCKED_NO_ELIGIBLE_SUBJECT / requirements review**. Do not lower budgets,
truncate examples, subsample history, relax lifecycle/precision requirements,
silently spend money, or alter confirmation protocols to admit a model. Any review
creates an explicit candidate-independent version/rationale before comparison and
before adaptation outcomes; all original findings remain immutable.

Remaining prerequisites, with their resolution boundaries:

- **REVIEW_FREEZE: CLOSED (design only).** The frozen package accepts the common
  design and applicable upstream dependency status. Production authentication,
  native orchestration and official-run conformance remain later prerequisites;
  upstream draft3 is not frozen by this checkpoint. The audit envelope is independent.
- **PRE_DISCOVERY_AUDIT_ENVELOPE:** separate mandatory PRE_DISCOVERY gate. Explicitly
  instantiate, independently review/approve and freeze cutoff, candidate scope,
  permitted source list/source classes and stopping rule before any candidate/model-
  landscape search, metadata collection, inspection, formal audit, comparison or
  selection. No candidate identity/evidence collection before PASS; no retroactive
  envelope. This envelope is uninstantiated and pending; discovery remains unauthorized.
- **EVAL_POPULATION:** construction design frozen in Workload section 1; actual
  authorized population/coverage manifest remains pending, without capacity filtering.
- **EVAL_TOKEN_BOUND:** later authorized tokenizer/template and effective-capacity
  receipts establish the input/context token requirement; no universal number yet.
- **TRAINING_DATA_SPEC:** example/label/mask/content/length policy frozen; actual
  profile-specific full-example token/mask receipts remain pending.
- **HISTORY_DATASET:** eligibility/cutoff construction rules frozen; instantiate
  authorized immutable full-stage manifests/counts/sizes later, never guess them.
- **TRAINING_RECIPE:** common recipe/seed/replication design frozen; exact target
  mapping, open-stack pins and applicable runtime conformance remain pending.
- **RESOURCE_EVIDENCE:** document or separately verify full-workload Colab resource
  and interruption/recovery feasibility; no fixed GPU assumption.
- **LOCAL_DISK, LOCAL_RESOURCE_EVIDENCE, LOCAL_USABILITY_RUNTIME:** usable local
  capacity, conversion/storage route and verification of the frozen usability policy.
- **LICENSE_AUDIT:** source-based checkpoint/stack terms for the declared private
  research/prototype activities; no candidate facts or legal conclusion now.
- **FIDELITY_SPEC:** later paired deployment comparison and acceptance policy.
- **COMPLETION_IMPLEMENTATION:** later implement/verify atomic publication,
  authenticated resume and native save/reload provenance before experiments count.

The candidate-independent invariants and supported numeric derivations now exist;
the candidate-independent design is frozen. Unresolved later-stage evidence prevents
eligibility/ranking/execution claims; design freeze does not imply any such readiness.
No web/landscape search, model download, inference, training, protected candidate
or task inspection, historical output inspection, Study execution, frozen Qwen30
or draft3 modification, product change or model selection is authorized/performed.
The user-authorized design checkpoint/commit alone is permitted. Selection's gates remain
in force; this document authorizes no landscape audit or runtime activity.
