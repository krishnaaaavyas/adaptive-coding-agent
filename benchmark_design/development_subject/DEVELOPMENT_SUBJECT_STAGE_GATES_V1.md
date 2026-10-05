# Development Subject stage gates v1

Status: **FROZEN_DESIGN**. Prepared: 2026-10-04 (Asia/Calcutta).
REVIEW_FREEZE: CLOSED (design only), under DEVELOPMENT_SUBJECT_FREEZE_MANIFEST_V1.json.

This is the frozen design's dependency classification, not a candidate audit,
eligibility decision, model selection or execution authorization. It preserves
Selection v1 and Common Requirements v1 science unchanged. The authorized ordering
repair separates design review from PRE_DISCOVERY_AUDIT_ENVELOPE. Design review is
closed; the envelope and all later-stage obligations remain pending, with no candidate PASS.
Candidate-dependent evidence need not exist before discovery; scientific choices
must not be made from candidate capabilities or desired adaptation outcomes.

## Interpretation and source basis

The reviewed sources are `DEVELOPMENT_SUBJECT_SELECTION_V1.md` (B-E, F-I, M-N),
`DEVELOPMENT_SUBJECT_COMMON_REQUIREMENTS_V1.md` (source review and sections 1-10),
and `development_subject_selection_v1.json` (common requirements, hard gates,
next-stage boundary, candidate/selection blocker descriptions). Generic governance
cross-checks used only `harness/context_policy/prepare.py`'s no-generation boundary,
`harness/ADAPTATION_CONDITIONS.md`'s reserved weight treatments, and
`harness/PROVENANCE.md`'s official-run integrity rules. No candidate source,
protected task/test content, product source or historical output was inspected.

Resolution stages mean:

| Stage | Resolution responsibility |
| --- | --- |
| PRE_LANDSCAPE | Candidate-independent scientific/comparison design and review/freeze prerequisites before discovery. |
| PRE_DISCOVERY | Independent approval/freeze of the complete candidate-audit envelope before any candidate information collection. Design freeze alone never opens discovery. |
| STATIC_CANDIDATE_AUDIT | Candidate-specific primary-source documentation and independently constructed manifest facts needed for admission/comparison; no model execution. |
| RUNTIME_CERTIFICATION | Separately authorized tokenization, effective-runtime or lifecycle/resource checks where source evidence is insufficient. No adaptation-benefit study. |
| POST_SELECTION_PRE_EXPERIMENT | Final experimental orchestration, persistence/completion implementation and run admission before experiments/results count. |
| LATER_DEPLOYMENT | Deployment-fidelity design and evidence after native subject selection; no retroactive change to native research results. |

Stages identify each blocker's resolution responsibility, not permission to act
or a guarantee that every blocker in one stage finishes before the next begins.
Static evidence can create a need for runtime certification and then return to
static eligibility review. No runtime check is authorized by a static audit.

**Discovery** means bounded identification and collection of public primary-source
candidate metadata after reviewed design freeze, PRE_DISCOVERY_AUDIT_ENVELOPE PASS
and separate audit authorization. The gate also precedes candidate/model-landscape
search and candidate inspection; no identity or candidate-derived evidence may be
collected before it closes.
It is not ranking. **Comparison** in the matrices means formal Selection v1
tiebreak/ranking, not recording descriptive facts or auditing gates. Selection v1
C-D requires all applicable hard gates PASS before ranking; a pending gate cannot
be bypassed by calling a ranking provisional. **Selection** means final assignment
of exactly one subject with accepted evidence/review. **Execution** means scientific
Study/weight-adaptation runs, not separately authorized engineering certification.
**Deployment claims** means affirmative feasibility/fidelity claims about the
adapted locally served representation, not merely existence of a proposed protocol.

In the matrices, Y means unresolved status blocks that action, directly or through
its prerequisites. N means that blocker alone does not block the action; other
blockers and explicit authorization still apply. C means Y only if the stated
certification trigger applies. A leaf is not closed or inactive merely because no
candidate has yet been discovered: conditional runtime obligations must be
accounted for explicitly by reviewer-accepted adequate source proof, or activated
and closed with certification evidence. Unknown evidence never means PASS.

## Findings and necessary distinctions

The proposed distinction between pre-landscape design and later tokenizer facts
is supported. Freeze the common byte/population and complete-example/history
contracts, not a fabricated universal context-token count. Candidate profiles must
later prove they satisfy that same envelope. Mapping a frozen target-selection
rule to architecture module names is evidence collection, not permission to choose
a lighter recipe for a candidate.

Two limits prevent moving every construction or implementation concern after
selection:

- Common Requirements section 3 explicitly says final training-resource comparison
  cannot finish before actual full-stage manifests exist. Their candidate-independent
  construction is classified with STATIC_CANDIDATE_AUDIT, not postponed past
  selection. The audit worker receives only authorized manifest/count/coverage
  receipts; separate authorized custodians construct any protected material without
  exposing it to model discovery or this task. Candidate capability cannot determine
  which examples enter those manifests.
- Selection v1 G04/G05/G08/G09/G10/G11 requires affirmative feasibility evidence
  before ranking/selection. Static documentation may suffice for applicable gates;
  where it does not, certification must precede ranking. Post-selection completion
  implementation is not an exemption from these earlier stack/lifecycle gates.

FIDELITY_SPEC does not gate native subject discovery, ranking, selection or native
experiments. Earlier G10/G11 deployment-path/resource eligibility still does.
COMPLETION_IMPLEMENTATION does not block static discovery or selection merely
because the experiment orchestrator is unfinished, but it blocks scientific
execution/admission and counting results until verified. Candidate lifecycle support
is assessed earlier under resource/stack gates.

No scientific budgets, sample counts, training parameters or latency thresholds
are declared by this classification. Existing justified values and null unknowns
remain unchanged. A design may use a reproducible rule with justified inputs rather
than an unsupported scalar; it must yield a common comparable workload before
resource ranking. If an essential value lacks scientific justification, the next
candidate-independent design task must supply that justification or leave it blocked.

## Blocker lineage and exact coverage

The thirteen existing named roots remain historical identifiers. The additional
unsplit PRE_DISCOVERY_AUDIT_ENVELOPE gate is independent of REVIEW_FREEZE, not its
child; freezing the design leaves the new gate pending. Unsplit roots
are actionable leaves below; split roots are aggregate containers and receive no
additional resolution stage. A split root closes only when every child is closed
or its explicitly conditional obligation is accounted for as above. Each child
has exactly one stage and retains its root ID as the prefix. This avoids assigning
one mixed root to several stages or silently deleting any obligation.

| Existing root ID | Actionable leaf or complete child set |
| --- | --- |
| REVIEW_FREEZE | REVIEW_FREEZE (unsplit: design review/freeze prerequisite) |
| PRE_DISCOVERY_AUDIT_ENVELOPE | PRE_DISCOVERY_AUDIT_ENVELOPE (additional unsplit pre-discovery gate) |
| EVAL_POPULATION | EVAL_POPULATION_DESIGN; EVAL_POPULATION_MANIFEST |
| EVAL_TOKEN_BOUND | EVAL_TOKEN_BOUND_STATIC; EVAL_TOKEN_BOUND_RUNTIME |
| TRAINING_DATA_SPEC | TRAINING_DATA_SPEC_DESIGN; TRAINING_DATA_SPEC_TOKEN_ACCOUNTING |
| HISTORY_DATASET | HISTORY_DATASET_DESIGN; HISTORY_DATASET_MANIFESTS |
| TRAINING_RECIPE | TRAINING_RECIPE_DESIGN; TRAINING_RECIPE_MODULE_MAPPING; TRAINING_RECIPE_RUNTIME |
| RESOURCE_EVIDENCE | RESOURCE_EVIDENCE_STATIC; RESOURCE_EVIDENCE_RUNTIME |
| LOCAL_DISK | LOCAL_DISK (unsplit) |
| LOCAL_RESOURCE_EVIDENCE | LOCAL_RESOURCE_EVIDENCE_STATIC; LOCAL_RESOURCE_EVIDENCE_RUNTIME |
| LOCAL_USABILITY | LOCAL_USABILITY_DESIGN; LOCAL_USABILITY_RUNTIME |
| LICENSE_AUDIT | LICENSE_AUDIT (unsplit) |
| FIDELITY_SPEC | FIDELITY_SPEC_DESIGN; FIDELITY_SPEC_EVIDENCE |
| COMPLETION_IMPLEMENTATION | COMPLETION_IMPLEMENTATION (unsplit) |

This document supplies the authoritative **frozen design classification** of the existing
aggregate blockers plus the authorized ordering gate. The JSON now records that
gate and its selection-record invariant; no candidate fact or candidate-gate PASS is added.

## PRE_LANDSCAPE resolution matrix

All rows in this matrix block discovery, comparison, selection, scientific
execution and affirmative adapted-deployment claims while unresolved.
At this checkpoint REVIEW_FREEZE is CLOSED (design only); the five scientific
design leaves are FROZEN_DESIGN. Later evidence and PRE_DISCOVERY remain pending.

| Blocker ID | Stage | Why here | Evidence that closes it | Downstream decision blocked | Discovery | Comparison | Selection | Execution | Deployment claims |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REVIEW_FREEZE | PRE_LANDSCAPE | Selection B/N requires reviewed/frozen design before examining candidates; future evidence cannot retroactively define requirements. | Authorized design approval/freeze with version/hash receipt and accepted stage classification. Upstream draft3 remains proposed; production authentication/native orchestration/official-run conformance retain later gates. CLOSED for design only; does not close PRE_DISCOVERY_AUDIT_ENVELOPE. | Design readiness only; no standalone candidate collection authority. | Y | Y | Y | Y | Y |
| EVAL_POPULATION_DESIGN | PRE_LANDSCAPE | Population, coverage and shared byte/output envelope must precede candidate capacity judgments. | Reviewed population/eligibility and boundary-coverage construction rules, inherited framing/fairness/admission controls and a candidate-independent content envelope. Population selection must not use candidate survival. | Fixed workload against which capacity is audited. | Y | Y | Y | Y | Y |
| TRAINING_DATA_SPEC_DESIGN | PRE_LANDSCAPE | Full-example semantics, labels/masks, content bounds and overlength policy are scientific treatment choices. | Reviewed source-to-example contract, input/label/template-boundary/loss-mask semantics, justified content bound and no-silent-truncation policy; explicit prior policy for any splitting/packing. Unsupported token ceilings remain pending later proof. | Common full-example capacity and scientific comparability. | Y | Y | Y | Y | Y |
| HISTORY_DATASET_DESIGN | PRE_LANDSCAPE | Eligibility, chronology and accumulated-stage construction cannot follow model fit. | Reviewed source/label eligibility, cutoff schedule/rule, certification, revision/withdrawal/dedup/transformation and complete stage coverage rules. No arbitrary H1/H2/H3 counts. | Independent construction of full stage manifests. | Y | Y | Y | Y | Y |
| TRAINING_RECIPE_DESIGN | PRE_LANDSCAPE | Method/target/rank/optimizer/coverage/batch/precision policy must define comparable adaptation work before inspecting candidates. | Candidate-independent design decision with rationale for essential parameters or deterministic policies, training seed/repeat policy and comparability rules. Where rank, coverage/epochs or another indispensable value is unjustified, a bounded scientific workload-design task must resolve it before discovery; this document does not choose it. | Fair resource envelope and target-rule mapping. | Y | Y | Y | Y | Y |
| LOCAL_USABILITY_DESIGN | PRE_LANDSCAPE | G10's practical local role must not be judged against a threshold chosen to favor a candidate. | Reviewed prototype workload and operational usability criteria, including which latency/session observations matter and independently justified acceptance rules. Inherited workload may be retained; no arbitrary speed threshold is required or invented here. | Meaning of practical local deployment and its later acceptance evidence. | Y | Y | Y | Y | Y |

Private/internal prototype activity scope and resource-accounting dimensions are
accepted in frozen Common Requirements with the scientific design.
This does not resolve the future candidate LICENSE_AUDIT result.
REVIEW_FREEZE reviews/freezes the candidate-independent design without requiring
an instantiated candidate-audit envelope. The latter has its own gate below.

## PRE_DISCOVERY resolution matrix

| Blocker ID | Stage | Why here | Evidence that closes it | Downstream decision blocked | Discovery | Comparison | Selection | Execution | Deployment claims |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PRE_DISCOVERY_AUDIT_ENVELOPE | PRE_DISCOVERY | Candidate-shopping protection must precede every candidate information collection, while audit timing/scope is independent of design freeze. | Explicit complete cutoff, candidate scope, permitted source list/source classes and stopping rule, independently reviewed/approved and frozen under separate authorization before any candidate/model-landscape search, metadata collection, inspection, formal audit, comparison or selection. No candidate identity/evidence collection before PASS; no retroactive envelope. | Every candidate collection/audit action and downstream ranking/selection. | Y | Y | Y | Y | Y |

Status: **PENDING_EVIDENCE**; envelope uninstantiated. REVIEW_FREEZE closure alone
does not close this gate or authorize discovery. Existing user-designated incumbent
identity remains unassessed historical role metadata, not newly collected evidence.

## STATIC_CANDIDATE_AUDIT resolution matrix

These obligations can remain pending during discovery. Closing them requires
candidate identities or independently constructed facts, not candidate-informed
changes to the pre-landscape rules. Evidence collection is allowed only by a
later bounded static-audit authorization; this task performs none.

| Blocker ID | Stage | Why here | Evidence that closes it | Downstream decision blocked | Discovery | Comparison | Selection | Execution | Deployment claims |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EVAL_POPULATION_MANIFEST | STATIC_CANDIDATE_AUDIT | Actual population/boundary-coverage receipts instantiate the earlier fixed design, without requiring a selected subject. | Authorized immutable population/envelope manifests and coverage receipts, with candidate-independent construction and no private content given to discovery workers. Conservative proof must cover the fixed workload, not a smaller candidate-filtered subset. | Full-envelope G08 proof and common-population comparison. | N | Y | Y | Y | Y |
| EVAL_TOKEN_BOUND_STATIC | STATIC_CANDIDATE_AUDIT | Tokenizer/template identity, serialization rules and documented effective capacity depend on checkpoint/runtime identity. | Exact primary-source pins and justified tokenizer/rendering capacity analysis for the fixed evaluation envelope; explicitly adequate proof or a precise runtime-certification dependency. A dependency records audit progress but does not pass G08. | G06/G07/G08 evidence sufficiency and runtime scope. | N | Y | Y | Y | Y |
| HISTORY_DATASET_MANIFESTS | STATIC_CANDIDATE_AUDIT | Full manifests/counts instantiate independent stage rules; Common Requirements requires them before final training-resource comparison. | Authorized immutable full eligible stage manifests with cutoffs, lineage, content/count/coverage receipts and source/label certification. Counts are construction facts, not guessed requirements. Token totals remain profile-dependent. | Full-history workload accounting, G04/G09 and comparable full-stage burden. | N | Y | Y | Y | Y |
| TRAINING_RECIPE_MODULE_MAPPING | STATIC_CANDIDATE_AUDIT | Exact module names, architecture support and open-stack pins depend on candidate identity. | Source-backed exact target-rule-to-module mapping, supported native PEFT/quantizer/optimizer stack, base/tokenizer pins and faithful instantiation of common workload. Differences or unsupported coverage are explicit blockers, not lighter treatments. | G03/G05/G06/G07/G09 support and certification scope. | N | Y | Y | Y | Y |
| RESOURCE_EVIDENCE_STATIC | STATIC_CANDIDATE_AUDIT | Documented free-compute feasibility and comparable bounds are candidate-specific. | Source-backed complete-workload accounting for GPU/host/disk, full training/evaluation, save/reload/export when required and interruption/rebuild cost. Record whether documentation establishes each gate or requires runtime proof; a deferred proof leaves the gate pending. | G04/G05/G09 eligibility and first tiebreak evidence. | N | Y | Y | Y | Y |
| LOCAL_DISK | STATIC_CANDIDATE_AUDIT | Host/storage availability is an observational input, not a new scientific budget, and its sufficiency depends on candidate footprints. | Authorized observed usable disk/storage baseline, conversion location and source-backed required peak/retained footprint comparison. No candidate-specific budget reduction. Capture time/limitations and later recheck before use. | G10 local storage feasibility and deployment resource comparison. | N | Y | Y | Y | Y |
| LOCAL_RESOURCE_EVIDENCE_STATIC | STATIC_CANDIDATE_AUDIT | Exact Windows architecture/template/conversion/offload route and resource bounds require a checkpoint identity. | Documented same-original GGUF/llama.cpp path and complete RAM/VRAM/cache/OS/offload/conversion/storage accounting for the fixed prototype workload, with a clear sufficiency finding or runtime dependency. Conversion support is not fidelity. | G10/G11 and lower-local-serving-burden evidence. | N | Y | Y | Y | Y |
| LICENSE_AUDIT | STATIC_CANDIDATE_AUDIT | License terms require exact checkpoint/stack identities; they cannot be a pre-discovery fact. | Pinned primary license text and evidence for every declared private research/prototype activity, resolved conditions and reviewer assessment. Public redistribution is not required by current scope. No unsupported legal conclusion. | G02 and permission for later acquisition/adaptation/deployment activities. | N | Y | Y | Y | Y |

No documented hypothetical free-GPU type or advertised context window substitutes
for full-workload proof. If bounds are missing, overlapping or incomparable,
formal comparison remains blocked under Selection D. These rows neither require
model downloads nor authorize executing tokenizers or training libraries.

## RUNTIME_CERTIFICATION resolution matrix

The explicitly conditional rows apply when static source proof cannot establish
the required property. Training token accounting remains an explicit obligation
of the Common Requirements contract. Any adequate analytical token proof must be
accepted and authenticated in this certification stage rather than silently
assuming a tokenizer-independent number. Runtime certification is engineering
evidence only, under a separate bounded authorization; any computation/download
must be specifically authorized. It does not inspect protected tasks in this task
or use protected-task performance/adaptation gains to choose the subject.

| Blocker ID | Stage | Why here | Evidence that closes it | Downstream decision blocked | Discovery | Comparison | Selection | Execution | Deployment claims |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EVAL_TOKEN_BOUND_RUNTIME | RUNTIME_CERTIFICATION | Trigger: documented tokenizer/rendering/effective capacity proof is insufficient for G08. | Authorized authenticated no-generation rendering/tokenization and capacity receipts covering the fixed population/envelope and all conditions, exact controls/reference reserve and sufficient effective context. Use nonprotected coverage inputs or authorized isolated custodian receipts; no adaptation-benefit evaluation. | G08 PASS and final native capacity admission. | N | C | C | C | C |
| TRAINING_DATA_SPEC_TOKEN_ACCOUNTING | RUNTIME_CERTIFICATION | Full-example token lengths, label masks and terminal accounting depend on the pinned training renderer/profile. | Authenticated candidate-profile token/length/mask receipts or accepted conservative proof covering every full stage example, with complete-example capacity and no shortening. Actual forward/backward fit is certified under resource evidence when required. | Training sequence capacity, G08, full-history token/workload accounting. | N | Y | Y | Y | Y |
| TRAINING_RECIPE_RUNTIME | RUNTIME_CERTIFICATION | Trigger: architecture mapping/lifecycle behavior cannot be proven adequately from sources. | Separately authorized nonprotected synthetic lifecycle certification of original/fresh adapter, backward support, save/reload/native identity and repeat-from-original under the common recipe. No stage adapter continuation and no measured adaptation benefit as selection evidence. | G05/G09 PASS for the exact instantiated stack. | N | C | C | C | C |
| RESOURCE_EVIDENCE_RUNTIME | RUNTIME_CERTIFICATION | Trigger: free-compute feasibility, full capacity or restart cost cannot be established statically. | Authorized observed-hardware/resource traces and recovery/checkpoint receipts for the unchanged common envelope, with justified full-stage bounds and repeated rebuild feasibility. Reject insufficient assignments; no paid fallback or workload relaxation. | G04/G09 PASS and matched burden evidence. | N | C | C | C | C |
| LOCAL_RESOURCE_EVIDENCE_RUNTIME | RUNTIME_CERTIFICATION | Trigger: documented local route/resource fit is insufficient for G10/G11. | Authorized Windows route/conversion/resource verification for the fixed workload, recorded OS/free RAM/VRAM/disk/cache/offload and same-original artifact lineage. No inference or conversion is performed by this governance task. | G10/G11 practical feasibility and local burden comparison. | N | C | C | C | C |
| LOCAL_USABILITY_RUNTIME | RUNTIME_CERTIFICATION | Trigger: sources cannot establish the independently fixed usability criterion needed for practical G10 eligibility. | Authorized local timing/session/valid-output observations or accepted conservative usability proof against LOCAL_USABILITY_DESIGN, using nonprotected fixed prompts. This proves operability, not adapted-behavior fidelity. | G10 practical usability; no threshold may be chosen from measured candidate results. | N | C | C | C | C |

Runtime scheduling after a static shortlist is not a provisional selection.
All-PASS candidates alone may enter formal ranking; a PENDING_RUNTIME incumbent
or challenger remains unranked. Nothing here requires unnecessary runtime checks
when adequate documented evidence already satisfies an applicable hard gate.

## POST_SELECTION_PRE_EXPERIMENT resolution matrix

| Blocker ID | Stage | Why here | Evidence that closes it | Downstream decision blocked | Discovery | Comparison | Selection | Execution | Deployment claims |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| COMPLETION_IMPLEMENTATION | POST_SELECTION_PRE_EXPERIMENT | Full experiment orchestration can use the selected pinned subject, but partial runs must never become scientific results. Earlier candidate save/reload/rebuild capability still gates eligibility separately. | Reviewed/versioned native runner, frozen run/config/manifest/scorer identities, staging/hash/persistent-copy checks, atomic final receipt, interrupted/resume reconciliation and negative-result handling verified on nonprotected fixtures; official-run provenance/isolation/conformance ready. Exact native profile is frozen before scientific runs. | Authorized scientific execution, COMPLETE result admission and any claims relying on adapted experimental artifacts. | N | N | N | Y | Y |

This placement does not activate D/E or implement training through the legacy
runner. Scientific execution requires separate study/treatment authorization,
verified isolation, all selected-subject eligibility conditions and applicable
upstream conformance. Same-stage engineering certification may test primitive
checkpoint operations earlier; it is not permission to count scientific results.

## LATER_DEPLOYMENT resolution matrix

| Blocker ID | Stage | Why here | Evidence that closes it | Downstream decision blocked | Discovery | Comparison | Selection | Execution | Deployment claims |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FIDELITY_SPEC_DESIGN | LATER_DEPLOYMENT | Fidelity concerns a particular authoritative native adapted artifact and a derivative deployment configuration after subject selection. G10/G11 establish a path earlier, not behavioral equivalence. | Reviewed fixed paired prompt/task set, rendering/budget/scorer controls, transformation lineage, repeat/exclusion/acceptance rules fixed before either compared output is observed. Any protected-task reuse requires separate authorization. | Authorization/readiness for deployment-fidelity test and fidelity claims. | N | N | N | N | Y |
| FIDELITY_SPEC_EVIDENCE | LATER_DEPLOYMENT | Design existence cannot establish that the served quantized derivative preserves behavior. | Separately authorized authenticated paired native/local outputs and task/test, validity, convention and regression comparisons under the fixed fidelity design; report disagreements and failures without assuming token equality. | Affirmative deployment-fidelity claims; never native subject eligibility or retrospective editing of Study results. | N | N | N | N | Y |

A completed failing fidelity test resolves the evidence obligation as a deployment
finding but does not license a preservation claim. Native results remain immutable.
Deployment-path failure at G10/G11 is independently an earlier selection blocker.

## Reconciliation of other existing blocker descriptions

These are aliases/aggregates already present in Selection M and the JSON record,
not additional unassigned leaves. Their obligations resolve through the matrix:

| Existing description/status | Matrix coverage |
| --- | --- |
| PENDING_REQUIREMENTS_FREEZE; numeric common requirements; protocol reviewer approval/freeze | REVIEW_FREEZE and the PRE_LANDSCAPE design leaves. Candidate-dependent token facts are not inputs to scientific design freeze; unsupported essential scientific parameters still block that freeze. |
| Bounded current primary-source candidate landscape audit; candidate/license/architecture/parameter/storage source audit | STATIC_CANDIDATE_AUDIT leaves, plus ordinary G01-G11 evidence records under Selection C/M. Architecture/parameter facts needed for resource accounting belong to RESOURCE_EVIDENCE_STATIC; acquisition/pins/open-stack facts to EVAL_TOKEN_BOUND_STATIC and TRAINING_RECIPE_MODULE_MAPPING; license to LICENSE_AUDIT. The audit remains incomplete until every gate/disposition and evidence reference is accounted for. |
| Immutable checkpoint and tokenizer/template pins | EVAL_TOKEN_BOUND_STATIC and TRAINING_RECIPE_MODULE_MAPPING, followed by applicable runtime authentication receipts. Pinnability is not a model download. |
| Full-workload Colab and stack feasibility; separately authorized runtime verification where static evidence is insufficient | RESOURCE_EVIDENCE_STATIC/RUNTIME, TRAINING_RECIPE_MODULE_MAPPING/RUNTIME and TRAINING_DATA_SPEC_TOKEN_ACCOUNTING. |
| Local disk and deployment envelope | LOCAL_DISK, LOCAL_RESOURCE_EVIDENCE_STATIC/RUNTIME and LOCAL_USABILITY_DESIGN/RUNTIME. |
| Later fidelity acceptance criteria and separate authorization | FIDELITY_SPEC_DESIGN/EVIDENCE. |
| Future atomic completion/recovery implementation and verification | COMPLETION_IMPLEMENTATION. |

Aggregate open-blocker lists in earlier documents are not a claim that every item
must be resolved before discovery. Selection B's common context/sequence/history
requirements are the independently chosen contracts and capacity rules; candidate
token counts demonstrate compliance later. Common Requirements is frozen design
with pending construction/evidence obligations. Its statement that manifests are
needed before final resource comparison remains enforced. Selection C's pending
gate restriction is also unchanged. No blocker classification closes a gate,
sets a frozen hash, creates a selected subject or changes native/deployment authority.

## Closing decisions and next-task boundary

### 1. Closed candidate-independent design obligations

REVIEW_FREEZE is CLOSED for the candidate-independent design. EVAL_POPULATION_DESIGN,
TRAINING_DATA_SPEC_DESIGN, HISTORY_DATASET_DESIGN, TRAINING_RECIPE_DESIGN and
LOCAL_USABILITY_DESIGN are FROZEN_DESIGN under the authorized manifest. Workload
and Recipe contain the justified policies; this classification adds no scientific
numbers. No actual H-stage counts, token capacities or runtime facts are assumed.
PRE_DISCOVERY_AUDIT_ENVELOPE remains PENDING_EVIDENCE and uninstantiated.

### 2. Blockers allowed to remain pending during candidate discovery

All STATIC_CANDIDATE_AUDIT, RUNTIME_CERTIFICATION, POST_SELECTION_PRE_EXPERIMENT
and LATER_DEPLOYMENT leaves may remain pending during bounded discovery. In root
terms this includes EVAL_TOKEN_BOUND, RESOURCE_EVIDENCE, LOCAL_DISK,
LOCAL_RESOURCE_EVIDENCE, LICENSE_AUDIT, FIDELITY_SPEC and COMPLETION_IMPLEMENTATION;
the manifest/token-accounting/module-mapping/runtime children of EVAL_POPULATION,
TRAINING_DATA_SPEC, HISTORY_DATASET, TRAINING_RECIPE and LOCAL_USABILITY may also
remain pending once their PRE_LANDSCAPE design children close.

This removes no formal comparison or selection obligation: missing static workload
manifests, profile token proof, required resource/license/local evidence or an
activated runtime certificate still blocks ranking/selection. Fidelity and the full
experiment-completion implementation alone do not. Discovery is currently blocked
by open PRE_LANDSCAPE design/review obligations, PRE_DISCOVERY_AUDIT_ENVELOPE and
lack of separate audit authority;
comparison and selection are also currently blocked.

### 3. Exact authorization boundary after this checkpoint

The next candidate-related prerequisite is separately authorized instantiation,
independent approval and freeze of PRE_DISCOVERY_AUDIT_ENVELOPE. No model-landscape
search, candidate inspection/metadata collection or formal audit is permitted before
its PASS. No protected task/historical output inspection, model/data acquisition,
candidate tokenization, inference/training/certification, Studies, Qwen30/draft3/
product-baseline modification or subject selection is authorized by this checkpoint.

This document does not start or authorize that future task. After the required
design review/freeze and PRE_DISCOVERY_AUDIT_ENVELOPE PASS, a separately authorized
bounded current primary-source landscape audit may collect candidate facts while the later-stage leaves above
remain pending. Runtime verification, scientific experiments and deployment
fidelity each require their own explicit authorization. No such activity, model
selection occurs in this checkpoint. Only the user-authorized candidate-independent
design freeze and checkpoint commit are performed.
