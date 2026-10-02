# STEP 8K-B.1E — Implementation and synthetic conformance

Verdict: READY FOR INDEPENDENT IMPLEMENTATION AUDIT. The policy is not frozen.

Pre-state HEAD: `cf9eeb22eced0913b5a1bc1d6a492a40ef5b201e`; working tree clean.
Policy: `current-repo-v1-draft3`. Curated-evidence contract:
`study1-curated-evidence-v1`.

## Implemented architecture

`harness/context_policy/prepare.py` is a separate no-inference entry point.
It validates authenticated infrastructure, admits the public task and targets,
selects K once, measures current-target reference output, and prepares all
A/B/M/C/BC messages. Legacy v2 semantics are retained for legacy requests;
versioned requests are rejected by the legacy runner before execution.

The package implements canonical P, captured product/private existence
interfaces, immutable product bytes, static CPython indexing, exact anchors,
protected/inferred seeds, one-hop expansion and fixture provenance, exact K/H
bytes, append-only historical registry validation, authenticated cutoff,
complete-file output, fixed failure precedence and runtime admission.

All numerical budgets/caps, whole-file/record packing, no-transfer rules,
no-sibling rule and no-read generation policy are retained. No real repository
selector run, candidate relevance evaluation, model inference or benchmark
rerun occurred.

## Certification and runtime limitations

No fake production signer was implemented. Official mode requires reviewed
external authentication algorithms, authorized key fingerprints/verifier code
identity and valid certificates. Test fixtures are clearly TEST-ONLY and are
refused officially. Source fidelity, confirmation, actor permissions, cutoff
truth and representation matching remain human/external certification duties.

No actual Qwen/model/tokenizer/template or capacity verification is claimed.
Synthetic tokenizers exercise only the admission interfaces. Production
acquisition/certification and actual serving profiles remain external work.

## Validation commands

PowerShell bootstrap for the ignored portable runtime:

```powershell
$env:PYTHONHOME = Join-Path (Get-Location) '.venv\policy-python311'
$env:PYTHONPATH = Join-Path $env:PYTHONHOME 'site-packages'
$env:PYTHONDONTWRITEBYTECODE = '1'
```

Final synthetic command:

```powershell
& .venv/policy-python311/python.exe -m pytest harness/tests/test_context_policy.py harness/tests/test_policy_independent.py -p harness.tests.policy_scope_guard -p no:cacheprovider -q --tb=short --basetemp=.venv/policy-conformance-temp
```

Result: **88 passed**.

Final candidate-blind root-equivalent command:

```powershell
& .venv/policy-python311/python.exe -m pytest harness/tests taskflow_base/tests orderflow/tests safesync/tests -p harness.tests.policy_scope_guard -p no:cacheprovider --ignore=harness/tests/test_scorer_validation.py -k 'not test_all_historical_pilot_configs_remain_explicitly_legacy and not test_historical_adaptation_and_context_paths_validate and not test_all_migrated_experiment_configs_validate' -o pythonpath=taskflow_base -q --tb=short -rs --basetemp=.venv/policy-root-temp
```

Result: **472 passed, 8 skipped, 3 deselected, 1 dependency deprecation warning**.
Eight skips require unavailable Windows symlink privileges. The three
deselected tests read real historical experiment configurations; the ignored
scorer-validation file reads private legacy fixtures. Those readers were not
executed. Audit hooks block real protected-artifact access and network/model
connections, allowing only Windows asyncio's stdlib socketpair wakeup pipe.

TaskFlow standalone regression check: **7 passed**, using the same guard and
`-o pythonpath=taskflow_base`. All three product suites are included above.

Development runs exposed and corrected test-expectation arithmetic/test-ID
errors, portable-interpreter PYTHONPATH bootstrap failures, and the overly
broad socketpair guard. No policy budget or candidate-based adjustment was
made. Final runs have no failures.

## Independent verification

P/K/H/reference SHA-256 goldens were independently computed with PowerShell
from typed literal strings. `independent_check.py` imports no policy selector,
serializer or admission function and verifies observed bytes/hashes, declared
K content lengths, lexical order, target admission and raw reference-encoding
inputs. Embedded presentation markers remain content, not machine boundaries.

## Identities

- Policy artifact SHA-256: `d93f5136339153e65e35ef720333e21260292bc680f2cd3cfe608dfa46939a3b`
- Normalized supplied draft3 specification SHA-256: `fd052b85dd184fa1e1df242eb05e7826a32dacf54d07991f00f36bacc9e1d559`
- Evidence-contract text SHA-256: `874b4ca9a5ee1ac4710a331e71ec469f048de5d7f63bc1442047b0110c98d8e9`
- Disabled-root-alias synthetic configuration SHA-256: `55dbe6651c8cd5a3271c0b48a697e323275b8ff227b36b195f444ee7c8648176`
- Parser: CPython 3.11.9, Unicode 14.0.0.
- Parser executable SHA-256: `5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec`

`implementation_provenance.json` records source/conformance file hashes and
test results. Its manifest excludes itself and this report to avoid a circular
self-hash. Model-specific configuration identities remain external.

## Scope and final recommendation

Frozen product sources unchanged. Results/experiments/memory/rules/rubrics
unchanged. Candidate artifacts neither inspected nor copied. The original
full-access sensitivity analysis is preserved. Runtime downloads/dependencies
and test scratch files remain in ignored `.venv` storage and are not committed.

Passing synthetic conformance does not freeze the policy or establish real
model operability, retrieval quality, semantic fidelity or adaptation effects.
Proceed to independent implementation review before official certification,
freeze, or any separately authorized benchmark/model run.
