# STEP 8K-B.1G2A-0 — Qwen30 infrastructure governance and environment lock

## 1. Verdict

**NOT READY — RUNTIME_BUILD, TARGET_CAPACITY, RUNNER_ATTESTATION.** Preparation policies, the historical A–S dependency graph, literal fixture inputs, generation profile, repetition counts and external-run schema are frozen. The remaining vLLM **source-commit** blocker is resolved. The full executable environment is not locked or certified, and no acquisition or execution is authorized by this report.

## 2. Scope/prohibitions

This is preparation only. Public retrieval consisted of 45 bounded source/package/container metadata responses, with a 2,000,000-byte response ceiling and rejection of package/archive/weight bodies. Registry digest and PyPI wheel hashes are declarations, not downloaded-body verification. No packages, container layers or weights were fetched or installed. No upstream code was executed.

No model/adapters were instantiated; no completion, inference, training, GPU use/rental, protected candidate/task/scorer/outcome access, A/B/M/C/BC experiment or Study1/2/3 occurred. No model search, checkpoint/roster refresh, product repository change, protocol change or commit occurred. The only writes are within this dedicated governance directory. Existing context-policy source/test files were read as allowed conformance evidence or hashed; no tests, harness or scorer were run.

## 3. Frozen Qwen30 identity

- Repository: `Qwen/Qwen3-Coder-30B-A3B-Instruct`.
- Revision: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- Native original BF16, offline vLLM0.11.2 V1, TP1, capacity32,768, generated reserve/cap2,048.
- Sixteen declared safetensors bodies total **61,066,575,656 bytes**. Expected body SHA256/lengths are copied from the authenticated historical metadata, with every local-body verification flag FALSE. GateA still requires actual body authentication/header/layout evidence.
- Frozen verification order: Qwen30 → Devstral Small2 → GLM4.7Flash → Nemotron3.5LightningBF16 → QwenNext. STOP MODEL SHOPPING remains YES. The final experimental roster, external normative protocol freeze and Study readiness are not established here. No independent-model PASS is transferred.

## 4. Failure policy

`failure_policy.json` freezes three classes. **A** is demonstrated protocol/model incompatibility and stops this configuration track. **B** is a demonstrated invariant-preserving infrastructure/configuration defect and quarantines the track for bounded repair. **C** is incomplete or ambiguous verification and remains PENDING. Missing telemetry, unobserved cap events and unknown determinism causes cannot become PASS. Insufficient provisioned resources alone do not establish model incompatibility. Original failure evidence always remains in provenance.

An observed repeat mismatch fails the exact equality predicate. With no proven defect cause, its root-cause classification is C/PENDING; this does not turn the mismatching gate into PASS. A classification requires positive fundamental-incompatibility evidence, not exhaustion of an engineering repair budget.

## 5. Repair governance

`repair_policy.json` allows at most **two implemented repair attempts per root cause and six total per configuration track**, unsuccessful attempts included. These are new pre-outcome engineering bounds, not historical experimental budgets. Renaming the same root cause cannot reset a counter. Exhaustion stops repair and preserves quarantine/pending; it does not automatically drop or replace a model.

Every repair records failureID/class/symptom/gate, evidence-supported root cause, exact files/config changes, semantic-invariance justification, before/after hashes, invalidated gates, rerun set, reviewer identity/disposition, counters/timestamps and linked new runIDs. Independent reviewer assignment is pending before any future repair. Review approves invariant preservation before rerun; it cannot approve a normative change under this policy.

The affected gates and **all transitive descendants** are invalidated. Shared runtime/runner/control changes invalidate the earliest owning gate and descendants, rather than a favorable subset. Every required rerun must PASS under the after-hashes. A governed new gate run is distinguishable from a request retry: every request still has exactly one invocation and zero automatic retries, and old runs remain append-only.

Checkpoint, nativeBF16/TP1 profile, P/K/H, BC ownership,32,768 capacity,2,048 reserve/cap, full replacement and full-stream retention, task population, controls, parser semantics, admission and adaptation conditions cannot change to obtain PASS. Any such proposal is rejected here; demonstrated incompatibility is A, otherwise a separate future normative amendment remains pending.

## 6. Gate dependency DAG

The original historical Qwen30 IDs, test names, stages and evidence descriptions are retained verbatim in `gate_dependency_graph.json`. The following is the explicit mapping; every gate is **NOT_RUN**. Each JSON entry additionally contains an independent acceptance predicate, required evidence, possible classes and its exact transitive invalidation/rerun set.

| ID | Historical test | Prerequisites | Frozen acceptance focus |
|---|---|---|---|
| A | Exact checkpoint bodies | none | All 16 body byte lengths/SHA256 match frozen upstream declarations |
| B | Runtime container and parser lock | none | Final content-addressed image, complete hashed package/build lock, Linux CPython 3.11.9 Unicode14.0.0 binary/library identities, CUDA12.8 build/runtime, compatible exact driver and TP1 device/topology identities all present and independently authenticated |
| C | Successful load and real capacity | A,B,L | Pristine original BF16 model loads on selected device |
| D | Exact prompt token parity | C | All frozen historical token vectors/rendered bytes and literal P/K/H hashes match backend prompt IDs exactly |
| E | Effective frozen controls | C | Typed requested/effective controls exactly match independent literal oracle and source mapping |
| F | Native terminal behavior | I,E | Both native terminal IDs and stop-at-cap precedence verified by literal instrument probes |
| G | Natural termination | F,D,L | Each single/multi-target fixture gets one unchanged-control request, natural native terminal within2048, full uncleaned text accepted by frozen complete-replacement parser |
| H | Forced 2048 token limit | F,D,L | One fixed long-output fixture yields actual LENGTH with2048 total generated tokens under unchanged controls |
| I | Raw token and byte retention | D,E | Whole generated vector retained |
| J | Repeated greedy generation | G,H,I | Three identical invocations per frozen repeat fixture in first process: token vectors, raw bytes and terminal/events exact |
| K | Fresh process repeat | J,B | Same frozen order and three invocations each in second fully fresh process |
| L | No tools reads history retry | B | Before model load, positive scoped writes and all synthetic negative read/network/tool/callback/history/credential probes pass under external OS enforcement |
| M | Peak VRAM RAM and storage | C,G,H,O,P,Q,R | Complete100ms host/device/disk telemetry for every selected lifecycle phase, framework peaks and observer availability |
| N | TTFT throughput and rebuild timing | M,J,K,S | All fixed repetitions/stages timed with monotonic/synchronized boundaries, TTFT from internal token events (detokenizeFalse), prompt/output lengths, decode and training tokens/s defined |
| O | Attention LoRA forward backward | C,D,E,I,L | Actual192 q/k/v/o target census and384 adapter tensors match explicit names/shapes |
| P | Adapter save reload | O,A | Adapter safetensors keys/shapes/dtypes/value hashes survive save/destroy/reload on authenticated original |
| Q | Required merge export or direct serve | P,B,I | Only selected BF16 merge/export route: fresh original + reloaded adapter |
| R | Second fresh original-base rebuild | P,Q,A,B,L | Second cycle destroys all first-cycle objects, verifies original body/tensor roots again, initializes same seed fresh adapter/optimizer and trains full fixed accumulated invented history |
| S | State contamination audit | R,J,K,L | Original control outputs token/byte/event exact before and after both cycles |

Bootstrap B→L verifies the runtime/isolation boundary before any model load; A supplies authenticated original bodies; C then loads the model and performs one native **prefill-only** forward on30720 fixed IDs with>=32768 verified KV slots. Pinned GPUModelRunner.execute_model computes logits/deferred state separately from sample_tokens; the latter is never called for this probe. Destroy the probe process with its deferred state, then load a fresh authenticated original for D/E/I. The30721+2048 probe is rejected before any forward; its original count is retained. A dummy forward alone cannot prove actualKV capacity. The runner's implementation/allocation receipts remain pending.

D/E precede the first actual completion at I. Literal byte/terminal probes run before that completion; F and G consume I's retained single-target trace. This resolves event-verification bootstrapping without a cyclic dependency, suppressed generated stream or extra retry. G adds exactly one multi-target call; H adds exactly one fixed long-output call. The24 J/K repeat requests are separate and fixed.

M and N aggregate measured phases after execution; the external observer and hard-stop enforcement must be armed **before every phase**, so M is not a cyclic prerequisite of load/training. No dependent gate can PASS with a non-PASS prerequisite. `execution_schedule.json` fixes smoke, repeat, roundtrip, teacher-forced, contamination and second-original call/step inventories.

## 7. Immutable runtime lock

`runtime_lock.json` is **SOURCE_LOCK_RESOLVED_EXECUTABLE_LOCK_PENDING**. The exact proposed stack is retained:

| Component | Frozen expectation / resolved identity | Remaining evidence |
|---|---|---|
| vLLM | 0.11.2 V1, `275de34170654274616082721348b7edd9741d32` | Final CUDA12.8 source-built wheel/binary hash |
| CPython | 3.11.9, Unicode14.0.0; source `de54cf5be371a6f5e2e9f208c38def5f81d3ef02` | Linux executable, stdlib, extensions and build hashes |
| Torch | 2.9.0+cu128; official CP311 Linux wheel SHA `e97c264478c9fc48f91832749d960f1e349aeb214224ebe65fb09435dd64c59a` | Body verification/installed library identities |
| Transformers | 4.57.6, `753d61104116eefc8ffc977327b441ee0c8d599f` | Installed/package closure hashes |
| PEFT | 0.18.0, `77daa8d3b7decf2b40238ab47e2c1bd0f26c7749` | Installed/package closure hashes |
| Tokenizers / Jinja | 0.22.2 /3.1.6; direct wheel declarations archived | Installed Linux dependency/body verification |
| CUDA | Toolkit12.8.1; nvcc/runtime12.8.90, NVRTC12.8.93 | Loaded library, nvcc and host driver identities |
| OS/base | Ubuntu22.04 Linuxamd64, `nvidia/cuda@sha256:6617a625f4090c76c545a0e7d63f2e441718ef9af7f4efe7dd1242a29e289fd7` | Layer verification, OS SBOM and final image digest |
| Triton / CUTLASS | 3.5.0 /v4.2.1 commit `f3fde58372d33e9a5650ba7b80fc48b3b49d40c8` | Build binaries and selected architecture kernels |
| vLLM FlashAttention | `58e0626a692f09241182582659e3bf8f16472659` | Actual FA2/FA3 dispatch and compiled kernel hashes |
| FlashInfer | 0.5.2 required by pinned source | Actual enabled kernels/caches and binary identities |

All eight archived vLLM source files match the newly resolved immutable commit byte-for-byte; the archived Qwen3Moe Transformers source also matches the pinned4.57.6 commit. The pinned [vLLM Dockerfile](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/docker/Dockerfile) defaults to **CUDA12.9.1 and Python3.12**. It cannot be executed unchanged as proof of this profile. Its mutable bootstrap/apt steps require a fully pinned replacement recipe; selecting the Python minor version through apt does not pin3.11.9.

The conservative host-driver requirement is **Linux≥570.124.06**, matching the CUDA12.8.1 release driver rather than relying on older minor-compatibility/PTX exceptions. This is an expectation, not an observed driver. [NVIDIA archived release notes](https://docs.nvidia.com/cuda/archive/12.8.1/cuda-toolkit-release-notes/index.html).

`package_metadata_lock.json` records fixed direct package versions, declared compatible wheel hashes and all source-declared dependency constraints. It is explicitly **not a complete installable transitive lock**. Compiler patch packages, build tools, full Linux Python package closure, kernel build/dispatch inputs, final runner and final container image remain PENDING; no versions are guessed or replaced with `latest`. The selected vLLM route is a12.8 source build; the PyPI vLLM wheel is an unselected metadata candidate whose CUDA binary identity is not asserted.

Later executable identity is the combination of final content-addressed image digest, exact original body hashes, package/build hashes, Python runtime, CUDA libraries/host driver, GPU UUID/count/topology/architecture, actual kernels/caches, parser/build/config and runner/instrumentation hashes. A Dockerfile or tag alone is insufficient.

The current parser revision is `current-repo-v1-draft3-implementation-r2`, policy SHA `d93f5136339153e65e35ef720333e21260292bc680f2cd3cfe608dfa46939a3b`, descriptor SHA `ccb9484cd342c00a3c8e49a9df5af745e9ab2a29fc24a26234e2fd24cc9d6bbb`, source build SHA `2ecd8d12df578abf03668271c39d3f3964d4a08d13e19cc2c8817f9bc0e1737a` and disabled-alias config SHA `bd4496ce5688c47b067e372a5db5e8d5d6194dcafbeb141dd8f49f1c77618b1e`. The historical r1 and Windows Python executable hashes remain historical; neither is silently substituted for the current revision or a Linux binary identity.

## 8. Acquisition vs execution separation

Acquisition is a distinct, future authenticated network process restricted to the frozen revision and16 declared shard paths. It streams SHA256/length receipts to temporary files, validates index/header/layout, atomically promotes only a complete matching snapshot and makes it read-only. ETags and repository metadata are not body authentication. Credentials/session are destroyed before execution. This step performed only bounded public runtime metadata retrieval and does **not** start acquisition.

Execution uses only the authenticated snapshot, immutable runtime and explicit synthetic input bundle. It is offline under an OS network namespace, without acquisition credentials or caches capable of fetching missing files. No dependency/model refresh occurs during execution.

## 9. Execution/isolation profile

`execution_profile.json` freezes Linuxamd64/CUDA, a non-root read-only container, dropped capabilities and one verified deviceUUID/TP1. Only read-only original model/runtime and frozen inputs, a scoped run output and fresh scratch are mounted. Product repositories, protected tasks/candidates/scorers/outcomes, host root, credentials, Docker/SSH control sockets and prior adapters/derivatives are excluded. The external supervisor prepares input bytes/tokenIDs; worker receives one request at a time with exactly one invocation.

No network, tools, retrieval, dynamic repository reads or model-output shell/Python/callback execution is permitted. Whole token vectors, strict raw byte blobs, stop/finish facts, terminal receipts and telemetry are retained. New sequences clear KV/history; prefix caching is disabled; K/R/lifecycle reset boundaries require new processes, RNG, adapter and optimizer. Kernel cache identity is recorded as a fixed hash or isolated fresh scratch.

The fixed negative probes use **invented canaries**, a synthetic socket/listener and synthetic credential sentinel, never actual protected paths/content. Positive scoped writes, denied outside reads/history/network/socket, absent credentials, text-only would-be tool calls, one-call injected failure and exact mount inventory are required before load. Seccomp/AppArmor, runner and observer implementation hashes are still pending; design is not enforcement certification.

## 10. Frozen generation controls

`generation_profile.json` restates the independent literal Draft3 oracle: greedy; temperature0; top_p1; top_k disabled; repetition1; frequency/presence0; seed0; no text stops; max2,048; n1; retries0; no shifting/clipping/truncation. It cross-checks the literal conformance-test oracle and normative policy; it never imports production constants. SYSTEM is likewise independently typed and byte-checked. This implements the earlier F2 lesson.

The exact SamplingParams mapping is temperature0.0/top_p1.0/top_k0/min_p0.0, neutral penalties, seed0,stop[], additional native stop_token_ids[151643], ignore_eosFalse,max_tokens2048,min_tokens0,n1,best_ofNone,truncate_prompt_tokensNone,detokenizeFalse and skip_special_tokensFalse. Logits processors, token masks, bad-word restrictions, structured outputs and logit bias are absent. Primary EOS151645 remains native; no text-stop surrogate is introduced.

Engine flags retain BF16, no quantization/remote code, generation_config=`vllm`, capacity32768,TP1,max_num_seqs1,seed0,enforce_eagerTrue,prefix cachingFalse,speculative_configNone. The previously unspecified max_num_batched_tokens is explicitly32768, selected before outcomes for the full30720-token prefill buffer; it does not change P/K/H, request concurrency, context/reserve or sampling controls. Its actual full-prefill workspace peak is unmeasured and cannot be adaptively tuned to obtain PASS. Offline V1 API has no server tools/reasoning parser/output projection. Deterministic-algorithm enforcement, disabled TF32/benchmarking and CUBLAS workspace settings are predeclared; actual effective kernel/settings receipts are required, with no silent fallback if unsupported.

The entire generated stream is retained. Only one actually observed **final** native terminal can be removed for normalization; internal special tokens remain. Raw count includes the terminal and is at most2048. Native EOS at token2048 is STOP, not LENGTH. Strict full-stream byte decoding never replaces invalidUTF8 or drops unknownIDs; literal U+FFFD remains. Normalization permits only justified final terminal accounting and CRLF/bareCR→LF. No fence, whitespace, thinking, header or semantic cleanup occurs.

## 11. Fixtures/goldens

`fixture_manifest.json` freezes **65** explicit fixture files, each with stableID, bytes, SHA256, purpose, independent expected invariant, origin and gate membership:

- 51 existing invented Qwen30 inputs:45 capacity/empty-registry and6 framing cases, covering A/B/M/C/BC, P/K/H maxima and boundary-minus-one, emptyH, Unicode/NFC expansion, code/delimiters and native chat framing.
- Four exact P/K/H/reference literal byte goldens extracted through AST literal evaluation from the independently authored conformance tests, without executing/importing tests or serializers.
- Four fixed invented prompt designs: single-target natural stop, multi-target natural stop, long-output2048 probe and divergent prior request. They contain only invented file/task material and the unchanged SYSTEM, never protected candidate tasks.
- Six fixed literal/recipe designs: terminal event vectors, strict raw-byte cases,30,720/30,721 direct-token operational capacity probes, isolation negatives, minimal invented lifecycle history and exact hand-authored teacher-forced comparison labels/mask.

Hand-authored terminal/byte vectors are **test designs, not generated completions or runtime observations**. They supplement instrumentation but cannot certify actual native termination or forced-cap behavior. Natural-stop output is judged only by native event and the frozen complete-replacement parser, with no code-quality scorer. An early native stop on the sole long-output fixture leaves H PENDING; no altered ignore_eos/min_tokens/retry/continuation or alternate prompt is allowed.

Existing native rendered-byte/tokenID goldens are reused unchanged. New prompt **bytes/recipes and oracle path are frozen**, but their native token vectors are not materialized here: D must persist the independent authoritative-tokenizer rendering/IDs before any completion and compare the worker's IDs. Tokenization is not silently inferred from raw byte size, especially for NFC expansion. The direct capacity token recipe is operational stress only, not a relaxation of P/K/H or a task-admission certificate.

## 12. Repeatability policy

`repeatability_policy.json` fixes four inputs in order: natural_single,natural_multi,historical.unicode,historical.protocol_delimiters. Each is invoked **three times in process1 and three times in a second fresh process**:24 requests, with each request's retry count zero. Token vectors, raw bytes/hashes, normalized hashes, exact counts and terminal/event/removal receipts must be exact within and between processes. Timestamps, runIDs, processIDs and telemetry differ and are excluded from equality, but retained.

Missing evidence is C/PENDING. Any observed equality mismatch fails the predicate and cannot be excused with relaxed tolerances or additional favorable repetitions. All resource traces are retained and summarized descriptively. The separate S schedule fixes target→divergent prior→reset→target→fresh process→target, plus original-control checks after both destroyed adaptation cycles. No repeat count is selected after seeing outputs.

## 13. Resource measurement policy

`resource_measurement_policy.json` measures model/runtime/derivative disk, host RSS/PSS/cgroup peaks, per-device VRAM, load/steady/prefill/generation peaks, tiny and intended-length adapter training, save/reload/merge/export, destruction/reset and second-original rebuild. External scoped polling is100ms, with raw samples retained; a contiguous gap over200ms or absent required counters leaves the measurement PENDING. Framework peaks and cgroup peak counters supplement polling because polling alone cannot prove an unsampled transient maximum.

Monotonic_ns and synchronized stage boundaries define load/destroy/rebuild time. TTFT uses the internal first-token event, compatible with detokenizeFalse. Decode rate=(N−1)/(last−first token time), null when N<2 or span invalid; supervised and total training-token throughput are separate. Cold first repetition and subsequent warm indices are retained; no cold/slow run is discarded. All24 repeat traces remain in min/max/median/range summaries.

OOM, exhausted storage, missing observer or isolation/invariant drift hard-stop the affected phase. Capacity shortfall does not justify quantization, sharding, clipping, reserve reduction or profile changes in this track. Measurements are descriptive infrastructure evidence, never post-hoc quality selection, benchmark outcomes or inferred price.

## 14. Conservative adaptation lifecycle

`adaptation_lifecycle_plan.json` freezes **rank16 attention-only LoRA**,192 exact modules `model.layers.0..47.self_attn.{q_proj,k_proj,v_proj,o_proj}`,384 A/B tensors and13,369,344 parameters. Weight shapes(out,in): q(4096,2048),k/v(512,2048),o(2048,4096). Experts, routers, MLP, NF4 and wider scopes are excluded from this claim.

Base tensors remain nativeBF16/frozen; adapter tensors must census as FP32 with pinned PEFT autocast. Seed0, PEFT default Kaiming-uniformA/zeroB,alpha16,dropout0,biasnone, no DoRA/RSLoRA/modules_to_save. First A gradient may be zero at zeroB initialization; intended gradients must be finite, B gradient/update nonzero and base values unchanged. Fresh AdamW is used only for minimal lifecycle verification:lr1e−4,betas(0.9,0.999),eps1e−8,weight_decay0,foreach/fusedFalse; FP32 parameters/gradients/two moments have a213,909,504-byte floor before activations. These are mechanical probe settings, not Study3 hyperparameter selection.

Cycle1 is one tiny invented teacher-forced step. Cycle2 is a new ORIGINAL process and two fixed steps over the full two-record invented history, with fresh seed/adapter/optimizer; first adapter/merged derivative cannot parent it. A separate fresh-original30,720-token one-step backward envelope uses a literal direct-token stress recipe. Gradient checkpointing, disabled training KV cache, batch1 and exact label masks/order are fixed. No training occurred here.

Adapter save uses safetensors/config with exact key/shape/dtype/value hashes. P destroys/reloads on authenticated original and requires exact serialized values, exact same-stack logits and token/byte/event parity. **Merge/export is the selected route**, not an outcome-dependent choice between direct serving and merge. A new authenticated BF16 original + reloaded adapter is safely merged into a separate nativeBF16 derivative; original/template/tokenizer remain unchanged and independently hashed.

Q freezes elementwise logit acceptance `abs(a−b) <=0.05+0.01*abs(a)` on every vocab logit of the two literal teacher-forced fixtures, all-finite and argmax-exact. These are pre-outcome engineering acceptance constants, not measured bounds or a claim that BF16 merge is mathematically lossless. They cannot be widened after results. vLLM merged-derivative save/reload output tokens/bytes/events must be exact. No alternate serving route, precision or parent is selected after a failure.

Before every adaptation/envelope/merge-original cycle, authenticate all16 bodies and canonical named tensor roots, create a new process/seed0/adapter/optimizerstep0 and verify parent ORIGINAL SHA. No optimizer resume, previously trained adapter initialization or mutable merged base is allowed. S checks pristine-control outputs and base hashes after both cycles and divergent-state resets.

## 15. Run manifest/provenance

`run_manifest_schema.json` is JSONSchema2020-12 for future external executable runs. It requires runID/UTCtimestamp, exact repo/SHA/body hashes, image/package/runtime/parser/runner/kernel identity, GPU model/count/UUID/topology/architecture, driver/CUDA, literal controls/effective receipt, fixture/hash/promptIDs/count, whole generated IDs/raw byte artifact/hash/count, finish/stop/terminal/removal receipt, normalized hash, wall/TTFT/throughput, peakVRAM/RAM/telemetry, isolation result, gate/result/class/failureID, prerequisites and provenance hashes, invocation/retry counts and original parent.

Null represents incomplete or inapplicable evidence, never fabricated zero. A PASS generation receipt requires non-null raw/control/prompt/resource evidence, prompt count<=30720 and one invocation; rejection receipts retain an overlength original count rather than clipping it to schema limits. H PASS additionally requires actualLENGTH and exactly2048 IDs without a final native terminal. Schema conditions prevent several incompletePASS forms. `semantic_receipt_rules.json` separately requires external hash checks, vector-length consistency, strict byte reconstruction, exact terminal accounting, path confinement, actual identities, telemetry coverage and current DAG prerequisites. JSONSchema alone cannot prove those cross-field or external facts. Runner/auditor implementation of these rules is still pending; this step emits **zero executable run manifests**.

## 16. Hardware planning envelope

`hardware_requirements.json` records estimates, not measurements/provider selection. BF16 payload is61,064,245,248 bytes≈56.872GiB; full-attention KV is98,304 bytes/token and3GiB at32768. Together≈59.871GiB before workspace/kernels. Historical inference planning is65–75GiB resident;70GiB initially free device memory is a plausible provision and80GiB free provides preferred margin. One80GB-class device is a starting class, with actual available bytes decisive; no fit guarantee follows from its label or3.3B active parameters.

Native CUDA BF16 capability>=8.0, selected TP1, matching locked compute architectures/driver/CUDA are required. Host RAM64GiB is a plausible low-memory load floor;128GiB is preferred safety provision, not a claimed technical minimum. Require **250,000,000,000 bytes free storage** before weights: three checkpoint-sized allocations (original, derivative, atomic export staging),30GB runtime/build allowance and20GB receipts/scratch leave a modest reserve. Additional retained inputs require explicit extra bytes. Values use GB=10⁹ and GiB=2³⁰.

The full30,720-token backward/merge peaks remain unknown and may exceed a single80GB-class allocation. Stop/provision more compatible single-device memory rather than alter the profile. Multi-GPU TP2 is not selected and cannot silently replace TP1. No cloud/provider/price is selected or rented. The historical local4GiB GPU/~23.7GiB RAM/~23.1GiB free disk is insufficient for this profile; it was not refreshed into a current hardware measurement. Intended target inventory remains PENDING.

## 17. Pre-download checklist

`pre_download_checklist.json` is fail-closed: every mandatory item must PASS before weight acquisition. Checkpoint identity, expected body manifest, hashing procedure, immutable source correspondence, isolation design, fixture hashes, DAG, failure/repair policy, run schema, candidate-free inputs and unchanged protocol are preparationPASS. Storage/host target proof, complete immutable build/transitive lock/final image identity and implemented runner/observer attestation are PENDING.

These preparationPASS labels do not represent A–S executionPASS. The checklist explicitly denies acquisition/execution authorization here. Later actual driver/topology/runtime/body/effective control/raw-event evidence must also satisfy B/A and subsequent gates before any certification.

## 18. Remaining blockers

1. **RUNTIME_BUILD:** Complete pinned Linux build recipe/transitive binary/build tools, exact CPython3.11.9 executable/library hashes, kernel inputs and final content-addressed image are absent. Upstream defaults contradict the proposed Python/CUDA lock.
2. **TARGET_CAPACITY:** No intended Linux target inventory proves250GB free storage,64GiB plausible host floor (128GiB preferred) and selected single-device BF16 capacity/topology/driver availability. No provider/rental is chosen to fill this gap.
3. **RUNNER_ATTESTATION:** Specified no-read/offline/raw-stream runner and resource observer have no content-addressed implementation/enforcement attestation. Frozen plans/schemas are not executable evidence.

All three are C/PENDING preparation blockers, not failed model incompatibility gates. Actual bodies/load/termination/control/repeat/adaptation remain NOT_RUN rather than additional claimed static failures. Reviewer assignment is required before a first repair, and new prompt token vectors before first generation; neither is invented here.

## 19. Freeze boundaries

This governance revision freezes engineering policy/design, controls, literal inputs/recipes, gate predicates/dependencies, repairs, repeats, adaptation scope/route and measurement definitions. It does not modify or externally freeze Draft2/Draft3, P/K/H, task population, final experimental roster, historical admission certificates or any Study protocol. Current implementation-r2 provenance is authoritative; the earlier r1 is preserved history.

Unresolved binary/build/target fields may be completed from authenticated preparation evidence **before any outputs**, under the fixed versions/profile. Completion creates a new lock/hash and requires provenance/review. A changed invariant, fixture, equality count, tolerance or acceptance predicate is a new governance revision, not a permitted PASS-seeking repair; previously consuming gates invalidate. Do not change these rules after observing behavior.

## 20. Files created/modified

All new files are under `experiments/model_preflight/qwen30_infrastructure_governance/`. All17 required artifacts are accompanied by baseline_integrity, request_source, expected_checkpoint_bodies, package_metadata_lock, semantic_receipt_rules, execution_schedule,10 newJSON fixture designs,4 literalUTF8 goldens, archived public metadata/sources and small preparation/validation scripts. `artifact_manifest.json` enumerates exact paths/byte counts/hashes, excluding itself to avoid self-reference; the final verification output records its digest rather than embedding a circular hash in `validation.json`.

The inherited allowlist has **1,231 prior files** (1,217 from roster closure plus its14 outputs), all hashed and required unchanged. No protected-tree enumeration is used. Source manifests separately bind authoritative prior inputs and fetched runtime metadata. Only the dedicated new tree is written; no commit is made.

## 21. Claim limitations

Static source support, declared registry/wheel hashes and independent design validation do not prove model body identity, successful load, actual32768 support, effective controls, decoder correctness, EOS/length events, repeatability, isolation enforcement, VRAM fit, logits/output parity, fresh-original lifecycle or cost. No executable gate result is inferred from earlier tokenizer checks or another model.

Validation checks preparation JSON/schema, literals/arithmetic, source/fixture/artifact hashes, acyclic dependencies/invalidation, parser provenance, historical preservation and Git state. It neither imports model frameworks nor executes harness/scorers/upstream code. New fixture construction paths remain subject to D's independent token parity; exact environment and numerical feasibility are still unmeasured. No generic model-quality, task-admission or Study readiness claim is made.

## 22. Final recommendation

Complete only the three named preparation blockers with authenticated build/runtime/runner metadata and intended capacity evidence while preserving this revision. Re-evaluate the fail-closed pre-download checklist. **STOP now: do not acquire weights, instantiate anything, use GPUs or start Qwen30 A–S execution.** The landscape and five-model order stay closed/frozen.

Qwen30 exact repo/SHA: `Qwen/Qwen3-Coder-30B-A3B-Instruct` / `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`  
Runtime lock status: SOURCE_LOCK_RESOLVED_EXECUTABLE_LOCK_PENDING  
Failure policy frozen: YES  
Repair policy frozen: YES  
Gate DAG frozen: YES  
Fixtures frozen: YES (literal bytes/recipes and existing goldens; new native prompt vectors remain future D evidence)  
Repeatability policy frozen: YES  
Run manifest schema frozen: YES  
Pre-download verdict: NOT READY — RUNTIME_BUILD, TARGET_CAPACITY, RUNNER_ATTESTATION  
Full weights downloaded: NO  
Model instantiated: NO  
Inference occurred: NO  
GPU used: NO  
Protected candidates accessed: NO  
Protocol changed: NO  
Commit made: NO  
Final HEAD/status: `7fcdecbe26f4fd01138edf8f58c02ce4b947db0b` / `?? experiments/model_preflight/`
