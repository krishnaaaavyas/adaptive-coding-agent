"""Generate reviewable report from preparation evidence, never model/target execution."""
import json
from pathlib import Path
P=Path(__file__).resolve().parent
def load(name):return json.loads((P/name).read_text(encoding='utf-8'))
def main():
    runner=load('runner_manifest.json');v=load('validation.json');source=load('source_manifest.json');recheck=load('pre_download_recheck.json');build=load('runtime_build_lock.json')
    table='\n'.join('| '+r['id']+' | '+r['previous_state']+' | '+r['current_state']+' | '+r['reason']+' |' for r in recheck['items'])
    text=f'''# STEP 8K-B.1G2A-0R — Qwen30 pre-download blocker closure

## 1. Verdict

**NOT READY — RUNTIME_BUILD, TARGET_CAPACITY, RUNNER_ATTESTATION.**

Preparation has advanced: a pinned executable build bundle, target contract, and content-addressed runner implementation exist. The unchanged checklist still requires an actual executable image and compatible host/isolation evidence. Missing evidence is class C/PENDING; no model failure is declared. Acquisition and A–S remain unauthorized.

## 2. Scope/prohibitions

Only the three preparation blockers were addressed. Executed work comprised public runtime source/metadata retrieval, bounded FlashInfer package-metadata ranges, model-free tests, and explicit prior-artifact hash checks. Seven public runtime code archives were downloaded; no Qwen checkpoint body, complete runtime wheel or Debian package body was downloaded.

No Qwen/model/adapter instantiation, forward pass, inference, training, A–S, A/B/M/C/BC experiment, Study1/2/3, GPU workload/rental/provisioning, protected candidate/task/scorer/outcome access, product tracked-file modification or commit occurred. The future native worker, target probe, Docker builder and runtime image self-test were **not executed**.

## 3. Frozen inputs

The authoritative directory is `../qwen30_infrastructure_governance/`. Its sixteen controlling JSON artifacts are copied byte-for-byte under `frozen/` for later image binding. The source originals remain unchanged. `baseline_integrity.json` extends the prior explicit allowlist with every governance artifact and its manifest: **1,317 prior files** were checked without enumerating protected trees.

The subject remains `Qwen/Qwen3-Coder-30B-A3B-Instruct` at `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`. The frozen parser implementation-r2 and roster/Draft2/Draft3 hashes remain those recorded in the original lock. This step does not replace those definitions with the new runner's oracle or tests.

## 4. RUNTIME_BUILD resolution

**PARTIALLY CLOSED — TARGET BUILD REQUIRED.** The complete metadata-resolved input definition includes 179 exact Python distributions plus the separate FlashInfer CUDA cache, 114 exact Ubuntu packages, source commits and archive hashes, source-build overrides and an offline build route. Wheel/deb hashes are declarations until their bodies are authenticated; generated binaries have no invented hash.

| Identity | Frozen selection retained |
| --- | --- |
| Platform / interpreter / Unicode | Linux amd64 / CPython 3.11.9 / 14.0.0 |
| Base | `{build['platform']['base_image']}` |
| Torch / CUDA toolkit | 2.9.0+cu128 / 12.8.1 |
| NVCC / CUDA runtime / NVRTC | 12.8.90 / 12.8.90 / 12.8.93 |
| vLLM source | 0.11.2 / 275de34170654274616082721348b7edd9741d32 |
| Transformers source | 4.57.6 / 753d61104116eefc8ffc977327b441ee0c8d599f |
| PEFT source | 0.18.0 / 77daa8d3b7decf2b40238ab47e2c1bd0f26c7749 |
| Tokenizers / Jinja2 | 0.22.2 / 3.1.6 |
| Triton / FlashInfer / NCCL | 3.5.0 / 0.5.2 / 2.27.5 |
| vLLM CUTLASS | v4.2.1 / f3fde58372d33e9a5650ba7b80fc48b3b49d40c8 |
| vLLM attention source | 58e0626a692f09241182582659e3bf8f16472659 |
| Attention's separate CUTLASS gitlink | 62750a2b75c802660e4894434dc55e839f322277 |

The FlashAttention CUDA CMake subproject contains an older Torch 2.4.0 expectation that emits a warning, while the frozen parent vLLM build uses Torch 2.9.0. It is not independently pip-built against that old requirement. Compiled compatibility is a target-build obligation; the frozen Torch version has not been substituted. The ROCm composable-kernel gitlink is explicitly unselected for this CUDA build.

## 5. Executable build definition

`Dockerfile`, `requirements-linux-cp311.lock`, the Python/apt/source/extra locks, and `build/` contain the actual recipe. Apt uses the fixed Ubuntu snapshot `20261003T000000Z`, exact package versions and SHA256-checked index declarations. Target GPGV/apt must validate the captured InRelease signatures with the archive keyring inherited from the digest-pinned base. Disabling snapshot expiration checks does not disable signatures or package hashes.

CPython is built from its pinned commit with gcc/g++10 and a fixed prefix, without mutable ensurepip/get-pip bootstrap. Pip25.0.1, setuptools80.9.0, setuptools-scm9.2.2, wheel0.45.1, CMake3.31.6 and Ninja1.11.1.3 are pinned. vLLM, Transformers and PEFT are built from exact source archives with build isolation/dependency fetching disabled; all other wheels, including Torch and both FlashInfer cache packages, are exact hash inputs. No mutable upstream Dockerfile defaults are used.

`build/collect_inputs.py` authenticates future package bodies, verifies actual wheel METADATA constraints and stages an allowlisted context. `build/prepare_sources.py` supplies separate offline CUTLASS/attention sources. `build/build_image.py` makes one CPU-only Docker build attempt with network=none, fixed jobs/flags and a mandatory attested target architecture. `build/verify_build.py`, `runtime_self_test.py` and `sbom.py` capture installed versions/RECORD hashes, compiler/CPython/CUDA/extension binary hashes, generated wheels and image delivery evidence. All failures stop and retain evidence without automatic retry or version substitution.

No build was attempted: docker/podman/uv are absent on this Windows workspace. The presence of wsl.exe is not proof of a configured Linux build environment. Actual base layers, package bodies, signature checks, dpkg compatibility, build-engine/kernel identity, compiled architecture/ABI, SBOM and final image remain pending. A local image config digest, registry manifest digest and exported archive SHA are distinct; none is fabricated. Deterministic inputs/commands are defined; bit-identical output across unmeasured engines is not asserted.

## 6. Runtime self-test design/results

The executable self-test checks interpreter/Unicode/platform, every exact distribution, installed RECORD hashes, pinned apt/compiler versions, NVCC identity, Torch CUDA declaration, vLLM/attention extension presence, source archives and the runner content root. It reads metadata/binaries without importing Torch/vLLM or constructing a model. SBOM generation hashes relevant runtime libraries and compiler/interpreter binaries.

| Evidence stage | Current status |
| --- | --- |
| Local model-free runner/target-contract tests | PASS: 25 + 11 |
| BUILD-TIME image self-test | NOT_RUN — PENDING_TARGET_BUILD |
| TARGET-RUNTIME identities/driver/kernels | NOT_RUN — PENDING TARGET EVIDENCE |
| GPU-dependent compatibility/phase peaks | NOT_RUN — PENDING TARGET EVIDENCE |

These stages are deliberately distinct. Local Python3.12.14 is only the preparation/test host and is not represented as the target interpreter.

## 7. TARGET_CAPACITY contract

**TARGET CONTRACT COMPLETE — ACTUAL HOST ATTESTATION PENDING.** The JSON schema, capacity policy, Linux probe and validator cover physical GPU count, selected UUID/model/CC, total/free VRAM, ECC/MIG, TP1/topology, driver/CUDA report, RAM/storage/FS/scratch, OS/kernel/CPU/container, clock, cgroup/PSS support and hash-bound actual OS probe receipts.

The planning envelope remains ~56.872 GiB BF16 payload plus ~3 GiB KV before workspace; 70 GiB free device memory is a plausible planning point and 80 GiB preferred. Host RAM64 GiB is the plausible provision floor and128 GiB preferred; staging requires250,000,000,000 free bytes. The validator screens evidence against these planning points, records available capacities, and never converts them into measured model-fit guarantees. Insufficient/missing capacity evidence remains class C/PENDING, not a fundamental model failure. Exactly one selected full device is required; no switch to TP2 is provided.

## 8. Actual target-attestation status

No actual compatible Linux host is attested, no provider is selected and no hardware is provisioned or rented. The future probe reads host inventory and explicitly supplied scoped scratch/receipt paths, never protected project material. The local model-free tests use invented inventory and explicitly prevent it establishing an actual target. A fresh authentic inventory plus actual CPU-only container enforcement receipts is required before the frozen checklist can close.

## 9. RUNNER_ATTESTATION implementation

`runner/supervisor.py` is an executable one-child transport supervisor, with strict input controls, exclusive output IDs, an exclusive journal lock, retained stdout/stderr, bounded timeout handling for the same process, raw byte/vector/event preservation, semantic/schema validators, telemetry and append-only SHA-chained provenance. No callback evaluator, cleanup, final-only extraction, dynamic retrieval, model-request retry or fallback exists.

The future native dispatcher/worker/receipt processor are implemented separately and were not run. They require separate execution authority, bound target/build/OS/request evidence, current frozen prerequisites, exact original checkpoint and metadata authentication, a fresh scoped output/scratch and actual container probes before model instantiation. The prepared dispatcher covers the first prerequisite-gated native completion; it does not execute the entire frozen A–S lifecycle schedule. It retains native raw events, process/runtime/model identity fields, artifacts, failure classification and a frozen-schema-shaped receipt. It never automatically promotes transport success to a gate PASS.

Whole ByteLevel bytes are reconstructed from authenticated token metadata; UTF8 decoding is strict. Only one actually observed final native terminal is removed on STOP; LENGTH requires exactly2048 IDs without relabeling a final native stop. Internal markers and literal content remain. Normalization consists only of CRLF/CR to LF. Synthetic checkpoint labels are clearly requested target labels, not acquired model identities or observed Qwen behavior.

## 10. OS isolation implementation

The prepared Docker boundary fixes network=none, readonly root, UID/GID65532, capability drop ALL, no-new-privileges, custom default-deny amd64 seccomp, optional exact AppArmor profile, private IPC, bounded pids and tmpfs, and exactly four approved bind destinations: readonly model/input, scoped writable output and fresh scratch. One selected GPU UUID is an explicit future parameter. No Docker/SSH socket, acquisition credentials, host root, product repository or protected-material mount is provided by the recipe.

`isolation_probe.py` makes actual future denied network/read/write attempts, inspects current UID/caps/seccomp/no-new-privileges/network/mount flags, checks credential presence without printing values, and verifies a positive scoped write. Docker inspect receipts are retained as configuration evidence. **Configuration alone is never enforcement PASS.** Current Windows results establish application broker admission denial only; all Linux enforcement is **PENDING TARGET LINUX ATTESTATION**. Actual profile compatibility with CUDA/kernel execution remains untested.

## 11. Synthetic runner tests

The latest invented-worker batch passes25 tests. It covers normal/native terminal receipts, LENGTH2048, native stop at the cap, strict invalid UTF8 retention, CR normalization, internal special-token retention, controls/retry violations, attempted application broker network/outside/credential denial, inert callback text, output confinement/no overwrite, telemetry, schema/semantic receipts, append-only provenance, injected failure, missing telemetry C/PENDING, repeat mismatch and stale history. The11 target-preparation tests cover schema validity, invented-versus-actual separation, TP1, capacity, MIG, driver format, missing/mutated OS evidence and seccomp namespace denial.

Three runner batches and two preparation batches remain intact, including all injected failures and admission failures. These are separate model-free implementation attempts, not Qwen gate failures, model-request retries or governed repair reruns. The frozen repair log/counters are untouched. Synthetic receipts cannot PASS an actual Qwen gate.

## 12. Independent oracle

`tests/oracle.py` contains manually written literal controls, token-to-byte expectations, terminal/normalization counts, zero-retry/one-call expectations, all frozen required manifest field names, isolation decisions and dispositions. It imports no production code or constants. Tests compare production receipts against those literals; expected bytes are not computed by the production normalization/decoder. Target tests independently specify denial probes and the namespace-mask literal. This provides anti-circularity for infrastructure tests; it does not invent an independent human reviewer.

## 13. Runner content addressing

`runner_manifest.json` binds49 implementation/configuration/oracle/build/frozen-copy files. Its root is SHA256 of UTF8-path-sorted path/SHA rows encoded as canonical compact sorted-key ensure_ascii JSON without a terminal LF:

`{runner['content_root_sha256']}`

Individual hashes cover supervisor/interface/native transport, isolation command/probe, seccomp/AppArmor, observer, semantic/schema validators, invented fixtures/independent oracle/tests, build scripts, target contract and copied policies. The image self-test must recompute these hashes. `artifact_manifest.json` separately seals all new evidence, archived metadata/code, reports, test batches and validation, excluding only its own bytes.

## 14. Reviewer policy

`reviewer_policy.json` records **REVIEWER_IDENTITY_PENDING** and separates the implementer from an assigned independent infrastructure reviewer. Future classB repair requires root-cause evidence, invariant proof, before/after hashes, complete dependent-gate invalidation, frozen2-per-root/6-total counters and a signed/hash-bound disposition before rerun. Identity overlap, missing/invalid signature or disagreement blocks repair and requires separately assigned adjudication; no self-approval or invented person is supplied.

The frozen acquisition checklist does not independently require a reviewer identity before initial acquisition; the frozen repair policy requires it before the first repair rerun. The current run is implementer verification, not an assigned independent review.

## 15. Pre-download checklist re-evaluation

`pre_download_recheck.json` applies every exact original requirement and mandatory flag, preserving previous status and recording new evidence/current status/reason. No easier acquisition criterion was introduced.

| Item | Previous | Current | Reason |
| --- | --- | --- | --- |
{table}

TARGET_CAPACITY remains the aggregate capacity blocker; STORAGE is its mandatory checklist item. Source/design PASS values retain their original preparation-only meaning. No A–S gate was evaluated or relabeled.

## 16. Remaining blockers

- **RUNTIME_BUILD:** authenticate exact package bodies/base layers/signatures; perform the actual Linux source build with bound architecture/engine; establish installed binaries, self-test, SBOM and final image identity.
- **TARGET_CAPACITY:** attest an actual compatible Linux host, fresh selected-device capacity, RAM/storage, driver/topology and observer/container capability evidence.
- **RUNNER_ATTESTATION:** prove the exact built runner's actual Linux enforcement and observer support on that host. Realized controls, native stream/kernel behavior and phase measurements remain later frozen gate observations.

These are preparation evidence gaps (class C), not demonstrated incompatibility or an eligible governed repair failure. The full bundle can be reviewed now, but its existence alone does not close the checklist.

## 17. Freeze boundaries

Checkpoint/roster/order, P/K/H, BC ownership,32768 context,2048 cap/reserve, controls, full-stream/terminal rules, fixtures, repeat counts, numeric tolerances, adaptation scope/rank and required BF16 merge/export route remain unchanged. In particular, the frozen prefill-only C path, deferred-state destruction/fresh D/E worker,24 repeat design, adapter lifecycle and all dependency/repair rules remain authoritative. No native gate implementation was executed to test those behaviors here.

Validation reports `{v['status']}` with37 preparation-integrity checks,1,317 previous hashes preserved and no tracked diff. Content hashing of previously allowlisted parser/protocol artifacts does not run their private/product tests or inspect protected outcomes.

## 18. Files created/modified

All writes are inside this new `qwen30_pre_download_closure/` directory. Required outputs are REPORT.md, blocker_resolution.json, runtime_build_lock.json, runtime_build_manifest.json, runtime_self_test_plan.json, target_attestation_schema.json, target_capacity_policy.json, runner_attestation.json, runner_manifest.json, reviewer_policy.json, pre_download_recheck.json, source_manifest.json, artifact_manifest.json and validation.json.

Additional files contain Dockerfile/build scripts, apt/Python/source/cache locks, Linux probe/validator, runnable supervisor/worker/observer/validators/isolation profiles, literal oracle/invented tests, retained test evidence, frozen copies, source metadata/code archives and assembly/validation/sealing tools. The manifests enumerate their exact byte lengths/hashes; they are the inventory authority.

## 19. Claim limitations

Metadata resolution and source hashes do not prove compiled ABI or image execution. Runtime package full-body hashes, Ubuntu cryptographic signatures, actual base dpkg compatibility, build-engine identity and all generated binary/image hashes remain target-build obligations. The1.07GB FlashInfer runtime cache was inspected only through bounded metadata ranges; its complete body SHA remains mandatory. Its pinned [official CUDA12.8 cache index](https://flashinfer.ai/whl/cu128/flashinfer-jit-cache/) is recorded in source evidence.

No model-free test establishes Qwen behavior, deterministic native logits/tokens, model fit, adaptation/merge correctness or actual Linux isolation. The observer includes100ms selected-process RSS/HWM, Linux PSS/cgroup current/peak and future selected-device queries; the never-executed native worker includes synchronized framework peak counters. Polling/available hooks alone cannot establish full-phase resource acceptance. TTFT/throughput/effective engine/kernel attestations have not been measured. No source/config text is presented as runtime PASS, and no operator/reviewer attestation is fabricated.

## 20. Final recommendation

Retain the frozen governance and this sealed preparation bundle. The next preparation work is actual CPU-only Linux build and real host/container attestation under separate suitable execution access. Reapply the same checklist to fresh evidence. Stop here: do not acquire Qwen weights or start A–S. Even a future acquisition-ready verdict would not imply Gate A/B PASS, inference authority or Study1 authority.

Qwen30 repo/SHA: Qwen/Qwen3-Coder-30B-A3B-Instruct / b2cff646eb4bb1d68355c01b18ae02e7cf42d120  
RUNTIME_BUILD: PARTIALLY CLOSED — TARGET BUILD REQUIRED; frozen checklist PENDING  
TARGET_CAPACITY: TARGET CONTRACT COMPLETE — ACTUAL HOST ATTESTATION PENDING  
RUNNER_ATTESTATION: Implementation content-addressed; model-free tests PASS; PENDING TARGET LINUX ATTESTATION  
Actual compatible target attested: NO  
Runtime final image digest established: NO  
Runner implementation hash established: YES  
Model-free runner tests:25 PASS;11 additional preparation tests PASS  
Pre-download verdict: NOT READY — RUNTIME_BUILD, TARGET_CAPACITY, RUNNER_ATTESTATION  
Weights downloaded: NO  
Model instantiated: NO  
Adapter instantiated: NO  
Inference occurred: NO  
Model forward occurred: NO  
Training occurred: NO  
GPU used/rented: NO  
Protected candidates accessed: NO  
Protected tasks/scorers/outcomes accessed: NO  
Protocol changed: NO  
Commit made: NO  
Final HEAD/status: `{v['head']}` / `{v['git_status']}`  

**STOP.**
'''
    (P/'REPORT.md').write_text(text,encoding='utf-8')
if __name__=='__main__':main()
