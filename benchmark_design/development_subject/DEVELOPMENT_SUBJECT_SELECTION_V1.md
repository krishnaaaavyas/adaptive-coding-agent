# Development Subject selection v1

Protocol ID: `development-subject-selection-v1`

Status: **FROZEN_DESIGN**. REVIEW_FREEZE: **CLOSED (design only)**.
Exact artifact identity and review are recorded in DEVELOPMENT_SUBJECT_FREEZE_MANIFEST_V1.json.
PRE_DISCOVERY_AUDIT_ENVELOPE remains PENDING_EVIDENCE; no discovery is authorized.

Prepared: 2026-10-04 (Asia/Calcutta)

Selection status: **NOT_SELECTED**; no candidate audit or runtime verification performed.

This is a researcher-only candidate-independent design. This checkpoint freezes
that design only, creates no execution authority and selects no model. Its companion,
`development_subject_selection_v1.json`, contains policy constants, an embedded
JSON Schema for future selection records, and an unassessed incumbent record.
Unknown facts are null or explicitly unresolved, never inferred from a model name.

## A. Roles and compatibility boundaries

After completed selection there is exactly **ONE active Development Subject**:
one small open-weight coding checkpoint for development and evaluation of the
adaptation mechanisms on free Google Colab-class compute. Candidate records are
audit alternatives, not concurrent experimental tracks. The incumbent is
`Qwen/Qwen2.5-Coder-7B-Instruct`, identified by the user's historical harness/pilot
context; its exact future revision and eligibility are not yet established.

Historical Qwen2.5-Coder-7B pilot work remains historical development evidence.
It creates no second track and must not be pooled, relabeled, or silently combined
with new experiments, even if the incumbent is retained. Future runs receive
distinct protocol/configuration, checkpoint, dataset and run provenance.

The existing large-model confirmation track remains separate and unchanged.
Qwen3-Coder-30B-A3B-Instruct remains first, **PENDING COMPUTE**. Its frozen BF16,
TP1, context, generation and LoRA methodology is not relaxed for Colab or inherited
as an automatically suitable small-model recipe. Development findings do not
establish confirmation results or generalization.

Relevant read-only governance references and potential conflicts:

| Existing artifact | Boundary for this proposal |
| --- | --- |
| `benchmark_design/README.md` | This entire directory is evaluator/researcher-only; do not expose this protocol or candidate audit to experimental model context or adaptation inputs. |
| `harness/ADAPTATION_CONDITIONS.md` | Frozen information treatments and equal within-model/task budgets remain intact. D/E are reserved for later weight adaptation; this proposal does not implement or activate them. |
| `harness/PROTOCOL_V2.md`, `harness/PROVENANCE.md`, `harness/DEFECT_POLICY.md` | Preserve test separation, target/regression/convention success, immutable historical evidence, source hashes, and outcome-independent defect handling. The proposed completion contract below adds future admission requirements; it does not change current runner behavior. |
| `harness/context_policy/README.md` and `benchmark_design/context_policy/current-repo-v1-draft3.json` | Preserve the draft3 identity and information protocol. No edit, reinterpretation, or automatic budget override is authorized. The draft3 JSON itself need not be inspected for this task. |
| `experiments/model_preflight/qwen30_infrastructure_governance/{execution_profile,generation_profile,adaptation_lifecycle_plan}.json` | Preserve Qwen30's separate frozen recipe and fresh-original-base principle; no small-model recipe substitutes for it. |
| `experiments/model_preflight/landscape_closure/REPORT.md`, sections 10 and 14 | Borrow explicit lineage/resource/serialization distinctions and evidence-based decisions only. Its multi-subject coverage order and retain-both-on-tie rule do not govern this single-subject track. No candidate findings are imported as development eligibility. |

Upstream methodology and product baselines are neither amended nor superseded.
The frozen common design is specified by Common Requirements, Workload, Recipe
and Stage Gates. Candidate-dependent facts and completion implementation remain
pending, not permission to change existing protocols.

## B. Pre-outcome selection and evidence rules

The candidate-independent protocol/common design is frozen before examining
candidates: evaluation and full-example capacity rules, output reserve, loss/recipe,
full-history construction, resource-accounting scope and private prototype use.
Workload/Recipe supply the justified parameters and deterministic policies; actual
token lengths, history counts and candidate/runtime facts retain their later gates.
PRE_DISCOVERY_AUDIT_ENVELOPE must additionally PASS before any candidate collection.
Reuse applicable existing scientific requirements without
weakening them. If requirements conflict or are infeasible, record a blocker for
explicit review rather than reducing them to admit a preferred candidate.

Selection may use static metadata, exact-checkpoint licenses, architecture,
documented runtime support, published coding evidence, resource requirements,
tokenizer/template information, and reproducibility evidence. A later separately
authorized runtime check may establish infrastructure feasibility on fixed
synthetic/nonprotected inputs; it must not measure adaptation benefit or candidate
performance on protected tasks. This document authorizes no such check.

Never use Study 1/2/3 adaptation outcomes, protected-task performance, favorable
adaptation effects, or desired research conclusions. Do not inspect protected
experimental candidates, private tasks, historical pilot outcomes, or private
scorer/output records for selection. Reviewers record an outcome-blind declaration.

Every factual assessment cites an evidence ID with a primary-source URL or
repository path, exact revision/version, retrieval date, locator, supported claim,
and limitations. Preserve immutable text/snapshot hashes when available. Published
independent coding evidence should be cited at its original evaluator/report;
vendor-reported evidence is labeled as such and is not independent. Compare only
compatible checkpoint, task, harness, prompt/tool, sampling and budget settings.
Incomparable scores remain incomparable; use no weighted score or invented
benchmark margin. This proposal conducts no current landscape audit.

## C. Hard gates and unresolved feasibility

Each gate has `PASS`, `FAIL`, `PENDING_EVIDENCE`, or `PENDING_RUNTIME`, with evidence
IDs and a reason. All eleven gates apply to every candidate; none may be waived.
`PASS` requires affirmative evidence for the common requirements. Any `FAIL`
eliminates the candidate before ranking. Any pending gate prevents ranking and
final selection; pending does not mean pass, failure, or provisional winner.
Use `PENDING_RUNTIME` when documentation cannot establish free-Colab feasibility
or a required lifecycle property without actual verification. Runtime evidence
must come from separate authorization, not from this proposal or the static audit.

| ID | Required gate | Evidence needed for PASS |
| --- | --- | --- |
| G01 | Openly obtainable weights | Identifiable original checkpoint and documented acquisition/access terms; no weights acquired in this stage. |
| G02 | Suitable license | Exact checkpoint license permits research and the declared prototype use, including adapters/export/quantized distribution where intended; conditions resolved explicitly. |
| G03 | No commercial/proprietary AI API dependency | All required adaptation, evaluation and serving steps have an open local stack; Colab/Drive infrastructure is not an AI inference API. |
| G04 | Realistic free-Colab LoRA/QLoRA | Documented or separately verified topology supports the full required workload, including base residency, activations, gradients, optimizer, reload/export peaks, RAM/disk and session recovery; inference-only fit is insufficient. |
| G05 | Reproducible open training stack | Pinned open stack supports this exact architecture and adapter targets, backward pass, save/reload and reproducible fresh-base construction; custom code and dependencies are recorded. |
| G06 | Pinnable tokenizer/template | Exact tokenizer files, special tokens, template bytes and rendering implementation can be versioned/hashed; no mutable default template. |
| G07 | Pinnable checkpoint/revision | Immutable original repository/revision and file inventory can be fixed and later authenticated by hashes; mutable tags alone do not pass. |
| G08 | Required context/output budget | Effective runtime supports frozen input plus output capacity and training sequence needs without clipping, silent truncation, extension or context shifting. Advertised maximum context alone is insufficient. |
| G09 | Practical original-base rebuilds | Every stage can reconstruct the original plus a fresh adapter with independent optimizer/RNG state and full stage history, accounting for repeated I/O and session interruptions. |
| G10 | Practical machine-class deployment | Documented Windows route for 24 GB system RAM and RTX 2050 4 GB VRAM, accounting for host/GPU residency, CPU/offload fallback, context/cache, conversion peaks and storage; full GPU residency is not required. Disk capacity is unresolved until declared. |
| G11 | Quantized local serving | Same-original derivative can be exported/quantized for GGUF/llama.cpp with documented architecture/tokenizer support and lineage. No numerical-equivalence or behavioral-fidelity claim follows from conversion support. |

Parameter count includes total resident parameters and, where relevant, active
parameters separately. Native storage estimates specify dtype, bytes, assumptions
and source; they are not training peak-memory estimates. No incumbent exemption
applies: historical use does not establish a current PASS.

## D. Exact tiebreak order and incumbent advantage

Only all-PASS candidates enter ranking. Use this exact lexicographic priority:

1. Lower free-compute burden.
2. Simpler/more reproducible adaptation stack.
3. Lower local-serving burden.
4. Stronger independent coding-capability evidence.
5. Newer model/checkpoint, only as the final substantive tiebreak.

Before comparison, freeze candidate evidence and the comparison envelope. Record
each pairwise comparison as `BETTER`, `EQUAL`, `WORSE`, or `INCOMPARABLE`, with
citations and uncertainty. Move to the next priority only on established equality;
missing data, overlapping estimates and tradeoffs are not equality. Incomparable
survivors block a final comparison until bounded evidence resolution or explicit
pre-outcome protocol review; do not invent a hidden scalar score.

Resource comparisons use a common history/context/adapter recipe and comparable
hardware/software assumptions: peak VRAM and host RAM, required disk, full-stage
compute time, original reload/export I/O and restart work. A resource improvement
requires no worsening on the relevant dimensions and at least one strictly better
dimension supported by nonoverlapping bounds or matched evidence. Parameter count
or active MoE count alone does not establish lower burden. Stack simplicity uses
set inclusion of required custom patches, custom kernels, conversions, manual
steps and unpinned dependencies; a strict subset with the same supported lifecycle
is better. Local burden uses the same documented machine and frozen prompt/output
envelope, including host/GPU/cache/offload and conversion requirements.

**Incumbent advantage:** if a challenger does not materially beat the eligible
incumbent under these predeclared criteria, retain the incumbent. Operationally,
replacement requires a strict dominance improvement at priority 1, 2 or 3 with
equality at every earlier priority, no demonstrated regression in the other burden
dimensions, and no demonstrated loss of coding capability under comparable
independent evidence. An improvement can be a verified removal of a required
custom patch/conversion, or a documented lower resource envelope with disjoint
bounds and no new burden. Unsupported estimates or an unverified compatibility
claim cannot establish it. A newer date or higher published score alone is not
material replacement evidence. Missing evidence needed to establish dominance
does not favor a challenger; unresolved hard gates still block everyone.

Priorities 4 and 5 rank challengers with otherwise equal burdens, but do not
override incumbent advantage. No arbitrary benchmark percentage threshold is
introduced. If the incumbent fails a gate, it is eliminated and has no advantage;
choose among eligible challengers using the same five priorities. If the incumbent
is pending, do not silently replace it or declare it retained. No eligible subject
means `BLOCKED_NO_ELIGIBLE_SUBJECT`, not a relaxed gate.

## E. Redundancy and deterministic single-subject procedure

First deduplicate identical original repository/revision identities; aliases,
sharding and quantized exports are not extra candidate subjects. Keep their
evidence/representation distinctions under one record. For distinct checkpoints,
record architecture/base, documented training ancestry, tokenizer/serialization,
and adaptation/runtime/resource regime. Mark equivalent-role redundancy only
when all four are evidenced equivalent for this track; common publisher, good
coding results, or small active parameter count alone do not establish redundancy.

Within an evidenced redundant group, apply gates, then the exact order in D and
incumbent advantage. Retain one representative; record other records as
`REDUNDANT_NOT_SELECTED` with representative and evidence IDs. Unknown equivalence
remains unresolved rather than becoming an exclusion. Distinct nonredundant
survivors are still alternatives for the single role, not an expanding roster.

Apply D across group representatives. If substantive comparisons are all equal,
retain the eligible incumbent. If the incumbent is eliminated and multiple
challengers remain exactly tied through priority 5, use UTF-8 bytewise ascending
`repository@immutable_revision` as an administrative tie resolution; this makes
no quality claim. Record it after the five priorities, never as a sixth research
criterion. Incomparability is not an administrative tie.

Finalization requires every included candidate's disposition and blockers to be
accounted for, reviewer acceptance, exactly one `SELECTED` record, and exactly one
matching active-subject identity. Alternatives remain audit history and never run
as simultaneous Development Subjects. During this proposal there are zero newly
selected subjects; the exactly-one invariant applies to completed selection.

## F. Authoritative native representation

The research authority is the **original pinned base checkpoint + native PEFT
LoRA/QLoRA adapter + frozen tokenizer/template/runtime/generation configuration**.
Freeze base dtype, any QLoRA quantizer and compute dtype, adapter targets/rank,
optimizer, seeds, package versions, precision, decoding, stops, context/output
budgets and template hashes. QLoRA's native base quantization is part of that
representation, not an unspecified deployment conversion. Native fresh-baseline
and adapted evaluations use comparable frozen configurations across conditions.

Future Study 1/2/3 results for this subject must come from that native Hugging
Face/PEFT representation. Exported/merged results cannot replace it by default.
The deployment transformation is separately tracked:

`native adapted model -> merge/export if required -> quantization -> GGUF -> llama.cpp/local serving`

Record original and adapter hashes, conversion commands/configurations/tool
versions, intermediate artifacts, quantization type and final artifact hashes.
Never overwrite the original or adapter. Do not assume numerical or experimental
equivalence between native and GGUF/local results.

## G. Later deployment-fidelity track

Separately authorize and predeclare a paired comparison of native authority and
the locally served derivative on the same fixed prompts/tasks. Freeze the prompt
set and scorers before seeing either output; retain identical source prompt bytes,
rendering/serialization receipts, nominal budgets and task/test harness. Record
any unavoidable runtime/tokenization differences and restrict claims accordingly.
Do not expose protected tasks during selection or reuse them without authorization.

Compare task/test success, output validity, convention adherence and behavioral
regressions, reporting paired per-task disagreements and aggregate counts. Freeze
acceptance rules, repeat/seed policy and exclusions before execution; they remain
unresolved here. Token-for-token equality is not assumed after quantization.
Deployment-fidelity failure is a deployment finding. Preserve it with its own
manifest; it cannot rewrite native Study 1/2/3 results, justify outcome-based model
replacement, or establish that native adaptation failed.

## H. Free-compute contract

The user will not pay for GPU compute. Free Colab GPU availability, assigned type,
session lifetime and quotas are not assumed stable. These are planning constraints,
not current service guarantees. Every future session must observe and record GPU
identity/VRAM, RAM, disk, CUDA/driver/runtime and available capacity. Check the
frozen workload envelope before work; reject an insufficient runtime explicitly.
Do not weaken scientific/model requirements to fit the assigned GPU, silently
switch precision/targets/budgets, or use paid compute as an automatic fallback.

Execution must be resumable and checkpointed to persistent storage. Persist
verified checkpoints with base/config/history identity, adapter/optimizer/scheduler,
RNG/sampler state, step position and lineage. Resume only the same stage/recipe
from an authenticated complete checkpoint under compatible frozen runtime
conditions. If exact resume cannot be supported, restart that stage from the
original base and record the interruption. A resumed H2 is not H1-to-H2 adapter
continuation. Partial outputs are never completed experiments.

## I. Atomic experiment completion contract

Proposed future lifecycle:

`PLANNED -> STARTED -> STAGING -> VALIDATING -> MANIFESTED -> FINALIZING -> COMPLETE`

1. PLANNED fixes a unique run ID, authorization, protocol/configuration hashes,
   subject/native representation, history cutoff, expected artifact inventory,
   scorer/test versions and completion criteria.
2. STARTED records observed hardware, start time and original-base verification.
   STAGING writes only to run-specific temporary paths; checkpoint success is not
   experiment success. Persist interruption/restart receipts.
3. VALIDATING verifies required outputs, expected workload coverage, native
   identity, evaluator integrity, finite/valid artifacts and successful authorized
   execution. A completed evaluation with failed task tests is a valid negative
   result, not an infrastructure failure or a reason to omit the run.
4. MANIFESTED seals a versioned manifest of all required byte counts/SHA-256 hashes,
   stage lineage, hardware/runtime and completion checks. Verify persisted copies
   after upload; a local hash alone does not prove a complete Drive copy.
5. FINALIZING publishes an immutable complete bundle. On a filesystem with suitable
   semantics, use an atomic same-filesystem rename. For Drive/sync storage without
   that guarantee, publish versioned immutable blobs first, verify them all, then
   publish a single final completion receipt referencing the sealed manifest.
   Consumers admit only a verifiable receipt and complete referenced bundle;
   folder existence or a mutable status flag is insufficient.
6. COMPLETE is assigned only after finalization validation. Do not overwrite prior
   runs. Aggregation reads only authenticated COMPLETE runs satisfying the native
   representation and protocol requirements; track missing planned runs explicitly.

`INTERRUPTED`, `FAILED_VALIDATION`, and `REJECTED_RUNTIME` remain non-counting
states with audit receipts. Reconcile interrupted finalization idempotently:
verify existing hashes/receipt before adoption, never promote missing files.
Recovery cannot silently turn partial work into an experimental result. This
contract is a future implementation requirement, not a claim about the current
runner's save semantics or a change to Qwen30's frozen lifecycle.

## J. Storage and execution roles

| Location | Role |
| --- | --- |
| Git/repository | Source code, configs, protocol, scorers, manifests/schemas, notebooks/launchers; no large model artifacts or secrets. |
| Persistent external storage, initially Google Drive | Adapters, checkpoints, large generated outputs, experiment snapshots, required persistent caches and sealed bundles/receipts. |
| Colab local disk | Disposable runtime workspace, training/inference cache, temporary model copies, high-churn working files and staging artifacts. |

Use local working copies for high-churn training I/O; periodically package, hash,
upload and verify snapshots/checkpoints rather than writing many small Drive files
in a training loop. Loss of Colab local disk must not destroy the latest verified
persistent checkpoint. Persist enough inputs/manifests to rebuild from the original;
no durable result may rely solely on ephemeral cache contents.

## K. Future training rule

Do not train a foundation model from scratch. Weight adaptation means LoRA/QLoRA
or another explicitly authorized parameter-efficient method. No training is
authorized here, including synthetic feasibility training.

Each authorized H1/H2/H3 stage starts from the **ORIGINAL frozen base**, fresh
adapter initialization and fresh optimizer state, and trains on the **full eligible
accumulated history for that stage**. Freeze history inclusion/cutoff, order,
deduplication, tokenization and any scientifically authorized transformation in
stage provenance. No silent history subsampling to fit a session. Do not train
adapter-on-adapter or use a merged derivative as a new parent. Within-stage resume
may restore that stage's authenticated checkpoint; a new accumulated-history
stage must rebuild independently from the original.

## L. Claims before evidence

At this stage we may claim only that reviewed/frozen design artifacts exist. Runtime
infrastructure, feasibility and completion guarantees remain unverified. We may
not claim successful adaptation, accumulated-history improvement on unseen tasks,
LoRA superiority over memory/rules, local GGUF behavioral preservation, or
generalization to Qwen30 or other confirmation subjects. Later claims require
authorized COMPLETE evidence and remain scoped to measured subjects/configurations.

## M. Machine-readable record and review

The companion embeds a draft-2020-12 `selection_record_schema`, with a record
instance under `selection_record`. This requires no third supporting schema file.
Policy constants mirror the sections above. The record supports protocol/status,
incumbent and candidate checkpoint identity/revision, license, parameter counts,
architecture, native storage estimate, Colab and adaptation-stack evidence,
tokenizer/template pinning, local deployment, eleven hard gates, redundancy,
ordered tiebreak evidence, dispositions, evidence sources, blockers and review.

Unknown facts are null; unassessed gates are pending. Evidence references must
resolve to source IDs. Future review must additionally enforce semantic invariants
that JSON Schema alone does not prove: all gates PASS before ranking, evidence
adequacy, outcome blindness, pairwise comparisons in the exact order, incumbent
advantage, and exactly one matching selected identity after completed selection.
Freeze records with reviewer identity, decision/rationale, timestamp, and hashes.
The separate design-freeze manifest records this checkpoint; candidate-selection
review/hashes remain unpopulated and no subject is selected.

Open blockers: PRE_DISCOVERY_AUDIT_ENVELOPE; actual population/history/token receipts;
candidate/license/stack/storage audit;
immutable base/tokenizer/template pins; free-Colab runtime evidence where needed;
local disk and deployment envelope; future fidelity acceptance rules; executable
completion/recovery implementation and verification; candidate-selection review.
These are explicit pending work, not evidence against or for the incumbent.

## N. Next-stage authorization boundary

`REVIEW_FREEZE` covers only reviewed/frozen candidate-independent Development Subject
design. It does not require an instantiated candidate-audit envelope and does not
authorize candidate discovery.

After design freeze, **PRE_DISCOVERY_AUDIT_ENVELOPE must PASS**, under separate
authorization, before any candidate/model-landscape search, metadata collection,
candidate inspection, formal audit, comparison or selection. PASS requires the
complete cutoff, candidate scope, permitted source list/source classes and stopping
rule to be explicitly instantiated, independently reviewed/approved and frozen
before any candidate identity or candidate-derived evidence is collected. No
retroactive definition is permitted. This gate is pending and its envelope is not
instantiated here; the existing unassessed user-designated incumbent is not new
candidate evidence or an exemption.

Only then may the separately authorized **bounded, current, primary-source candidate
landscape audit** record eligibility, comparisons and blockers; unresolved runtime gates
require a later separate authorization and cannot be guessed into PASS.

**No model download, inference, training, protected-task evaluation, protected
candidate inspection, or adaptation experiment is authorized by this document.**
It does not authorize Study 1/2/3, modification of frozen protocols or product
repositories or selection of a winning model. The separately user-authorized design
freeze/checkpoint commit creates no candidate collection or execution authority.
