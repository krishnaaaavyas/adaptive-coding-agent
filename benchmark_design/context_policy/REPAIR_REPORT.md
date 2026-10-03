# STEP 8K-B.1E2 — BOUNDED IMPLEMENTATION REPAIR REPORT

## 1. Verdict

READY FOR REPEAT INDEPENDENT AUDIT. F1–F5 repairs pass synthetic conformance.
This is not freeze approval or production runtime certification.

## 2. Pre-state

HEAD was `c013254367cb63cd4f45a65e484de5c6a18b8396`; working tree/index clean.
The expected workspace and HEAD matched. No protected candidate/historical
artifact was opened.

## 3. F1 repair

Canonical paths reject Unicode 14.0.0 category Cc, including U+0085, and
COM/LPT reserved basenames with digits ¹, ², or ³, including extensions.
The shared validator applies to public targets, acquisition and output paths.
Literal negative fixtures cover all seven requested paths. Positive fixtures
retain unrelated digit/superscript names and a Cf format character, avoiding
restriction expansion beyond Cc and the reserved device forms.

## 4. F2 repair

The test layer owns an independently typed complete control table and exact
common system string. Valid fixtures no longer import CONTROL_VALUES or SYSTEM
to manufacture these expectations. Negative request and production mutation
tests cover sample/temperature 2/seed 7; template/prompt identity tests remain
synthetic. The checked-in production control values were not changed.

## 5. F3 repair

Acquisition merges caught PolicyFailure diagnostics with previously detected
diagnostics. The existing PolicyFailure sorter supplies phase precedence,
ASCII ordering, and deterministic deduplication. The audit reproduction retains
existence_unverified and test_authentication_forbidden, with existence_unverified
primary. A second case retains incomplete-enumeration, product/deny-conflict,
and authentication failures without duplicate reason entries.

## 6. F4 repair

Provenance schema `current-repo-v1-provenance-v2` records raw decoded-envelope
identity before normalization, canonical P identity, installed source-build
identity, explicitly external repository commits, policy/config/receipt and
manifest identities, parser identity, exact K/H bytes and hashes, standalone K
token diagnostics, inventory presence/omission/accounting, historical registry,
cutoff and record/lane diagnostics, and module/import/declaration resolution
routes. Distinct declarations in one physical file retain their separate routes.

The interface receives a decoded envelope: raw P is explicitly J of that input,
not invented original transport bytes. Unknown transport/commit facts are null.
Implementation/product commits can be supplied through externally certified
run_identity; no live product/Git lookup is used to invent them. Installed source
hashing is not a binary-distribution attestation. Optional standalone K encoding
failure is diagnostic and introduces no new treatment admission failure.

At preparation, completion/common-population/matching fields are explicitly null
until their external workflow facts are available. After a separately authorized
generation, completion captures actual raw/normalized bytes, finish reason,
terminal accounting, classification inputs/category and secondary format
diagnostics. record_completion produces a new restricted record without
mutating the prepared record or model messages. Common-population/matching
metadata must reference certificates frozen at the required earlier stage.

## 7. F5 repair

Every supplied product regular-file blob is hash/length checked before filtering,
including unsupported, excluded and oversized files. Filtered files can remain
metadata-only. Literal old/DRIFT and same-length old/new cases fail acquisition;
correct supplied filtered bytes and metadata-only entries remain outside K.

## 8. Additional bounded coverage

Added provider fallback after removing each higher-priority provider, invalid
root-alias configurations, generation-template identity negatives, and exact
staged-provenance schema checks. No general coverage expansion was performed.

## 9. Independent verification

A temporary checker used typed literal expected controls/bytes/reasons rather
than production functions as its own oracle. It verified F1–F5, unchanged golden
hashes and K reuse. A process-only mutation of decoding=sample, temperature=2,
seed=7 yielded 11 failed and 123 passed, correctly disproving a green suite under
the nonconforming table. No source constants were changed by that probe.

## 10. P/K/H golden stability

The original independently authored embedded-marker fixtures remain exact:

- P: `9560bcdca58383e4b01b290506752d1daabea345440c636ace349cccf6ecb946`
- K: `9a209c405a177ed5db17ae54102233297ea258ce22d5bee3b27d903843896f44`
- H: `563e008c399e61f43fa2a8cf62890d8747c12748d9d9c7aaebf79a1469d69f16`

The existing mixed-target reference golden also passes the unchanged suite.

## 11. K-invariance verification

The old invariance tests and independent five-condition message checks pass.
Provenance is never inserted into P/K/H. Selection/expansion/packing semantics,
budgets, caps, BC allocation and no-read policy are unchanged.

## 12. Version/hash impact

F1 and F5 alter admission; F3 alters retained/primary diagnostics; F2 is test-only;
F4 changes restricted provenance. The user explicitly resolved the §26 identity
choice: preserve draft3 framing and use a new authenticated implementation/config
revision. This resolution does not silently reuse the old implementation identity.

- Normative policy/framing stays current-repo-v1-draft3, hash
  `d93f5136339153e65e35ef720333e21260292bc680f2cd3cfe608dfa46939a3b`.
- New revision: `current-repo-v1-draft3-implementation-r2`.
- Revision descriptor hash:
  `ccb9484cd342c00a3c8e49a9df5af745e9ab2a29fc24a26234e2fd24cc9d6bbb`.
- New disabled-root-alias configuration hash:
  `bd4496ce5688c47b067e372a5db5e8d5d6194dcafbeb141dd8f49f1c77618b1e`.
- Previous disabled-alias configuration hash:
  `55dbe6651c8cd5a3271c0b48a697e323275b8ff227b36b195f444ee7c8648176`.
- Installed policy source-build hash:
  `2ecd8d12df578abf03668271c39d3f3964d4a08d13e19cc2c8817f9bc0e1737a`.

Configuration requires implementation_revision and implementation_revision_sha256;
acquisition authentication binds them through the config hash. Old/missing
revision identities are rejected by indexing. Parser, evidence-contract and
normative specification hashes remain unchanged. repair_provenance.json defines
and records the new source/conformance manifest hashes, excluding self/report
hashes to avoid a circular identity. Original implementation artifacts are retained.

## 13. Commands executed

PowerShell bootstrap:

```powershell
$env:PYTHONHOME = Join-Path (Get-Location) '.venv\policy-python311'
$env:PYTHONPATH = Join-Path $env:PYTHONHOME 'site-packages'
$env:PYTHONDONTWRITEBYTECODE = '1'
```

Dedicated:

```powershell
& .venv/policy-python311/python.exe -m pytest harness/tests/test_context_policy.py harness/tests/test_policy_independent.py harness/tests/test_context_policy_repairs.py -p harness.tests.policy_scope_guard -p no:cacheprovider -q --tb=short --basetemp=.venv/policy-repair-conformance-temp
```

Combined:

```powershell
& .venv/policy-python311/python.exe -m pytest harness/tests taskflow_base/tests orderflow/tests safesync/tests -p harness.tests.policy_scope_guard -p no:cacheprovider --ignore=harness/tests/test_scorer_validation.py -k 'not test_all_historical_pilot_configs_remain_explicitly_legacy and not test_historical_adaptation_and_context_paths_validate and not test_all_migrated_experiment_configs_validate' -o pythonpath=taskflow_base -q --tb=short -rs --basetemp=.venv/policy-repair-root-temp
```

Isolation:

```powershell
& .venv/policy-python311/python.exe -m pytest harness/tests/test_design_isolation.py -p harness.tests.policy_scope_guard -p no:cacheprovider -k 'not test_historical_adaptation_and_context_paths_validate' -q --tb=short --basetemp=.venv/policy-repair-isolation-temp
```

Temporary independent/mutation scripts used the same pinned runtime and guard,
with the workspace appended to PYTHONPATH. Runtime execution was approved outside
the filesystem sandbox because of portable dependency access restrictions.
An initial development run exposed an oversized pytest parameter ID; compact IDs
fixed it. The final unmutated runs have no failures.

Final review: git diff --check, full diff and status review, source/manifest
verification, protected-path change checks, and one explicitly authorized commit.

## 14. Dedicated test results

134 passed, no skips/deselections.

## 15. Combined test results

518 passed, 8 skipped, 3 deselected, 1 dependency deprecation warning.
Eight skips require unavailable Windows symlink privileges. Three deselections
read historical real configurations. The scorer-validation file was ignored
because it reads protected legacy fixtures. No protected readers were run to
match counts.

## 16. Isolation results

37 passed, 1 historical-reader test deselected. Existing design-path, resolved
alias, workspace, adaptation and pre-inference isolation checks pass.

## 17. Files modified

Policy package: README.md, boundary.py, core.py, evidence.py, index.py, prepare.py,
protocol.py, provenance.py, selector.py. Test layer: policy_fixtures.py and new
test_context_policy_repairs.py. Researcher-only additions: implementation-r2.json,
REPAIR_REPORT.md and repair_provenance.json. Legacy runner and original policy
artifact/report/provenance are unchanged.

## 18. Product repositories modified?

NO.

## 19. Candidate artifacts inspected?

NO.

## 20. Model inference performed?

NO.

## 21. Step 8K-B rerun?

NO. Results, experiments, memory, rules and rubrics are unchanged.

## 22. Final git state

The repair is committed once with the prescribed message; the final HEAD and
clean state are verified and reported in the response. Temporary checker files
are removed. No exact self-referential commit hash is embedded in this report.

## 23. Commit hash

Reported after the commit in the response, avoiding a commit containing its own
hash. Commit message: Repair current-repo-v1 implementation audit findings.

## 24. Remaining external verification

Repeat independent implementation audit; certify product/deny/existence receipt
and authentication profiles; certify historical provenance, chronology,
confirmation and matching; verify actual model/tokenizer/template/controls,
terminal behavior and capacity; freeze common admission before outcomes.
No actual generation/application/evaluation pipeline was executed here.

## 25. Recommendation

READY FOR REPEAT INDEPENDENT AUDIT.
