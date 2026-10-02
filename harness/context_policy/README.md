# current-repo-v1-draft3 implementation

This is a proposed, unfrozen Study-1 information protocol. It never performs
inference. The canonical researcher artifact is
`benchmark_design/context_policy/current-repo-v1-draft3.json`; its SHA-256 is
bound by `core.POLICY_SHA256` and every public selector configuration.

`prepare.prepare_run` is the versioned integration entry point. It validates
authenticated infrastructure, admits P/targets, constructs K once, checks
the current-target output reference, and prepares all five condition messages
with their complete generation reserves. It accepts no live repository path,
manual context override, completion transport, scorer, or evaluator.

The legacy v2 runner remains unchanged for legacy requests and refuses a
versioned policy request before its execution path. Historical artifacts are
not migrated or reinterpreted.

## Required external trust inputs

Official execution requires reviewed acquisition/registry/profile signatures,
an authorized external verifier, its algorithm/key fingerprints/code identity,
and a signed cutoff binding the registry, release sequence and canonical P.
There is no default production authentication or signing implementation.
The verifier must enforce signer permissions/roles in its frozen profile.
Human certifiers remain responsible for public-task eligibility, authorized
source lineage, semantic fidelity, rule confirmation, matching and cutoff
truth. Structural validation cannot establish those semantic facts.

`harness/tests/policy_fixtures.py` is clearly TEST-ONLY. Its deterministic hash
certificates have no security value and are prohibited in official mode.
Synthetic tokenizers are also test-only; no real model fit is claimed.

## Immutable interfaces

Acquisition accepts captured metadata and byte blobs, verifies manifest hashes
and classifications, and exposes only the product view to selection. It does
not walk a live checkout or read private contents. The restricted existence
index stays in acquisition/admission machinery. Index/serializer share the
same normalized product bytes. Prepared K/H and audit records are exact bytes.
Presentation delimiters are never used to discover machine record boundaries.

The implementation requires CPython 3.11.9 and Unicode 14.0.0. Synthetic tests
use an ignored portable runtime under `.venv/policy-python311`; binaries and
downloaded dependencies are not committed.

## Candidate-blind testing

Load `-p harness.tests.policy_scope_guard` to block real experiment/result,
memory/rule/rubric, discovery and scorer-fixture access. Real network connects
are blocked except the stdlib Windows socketpair used by asyncio's wakeup pipe.
Legacy tests referring to real historical configurations and scorer fixtures
must be deselected/ignored; synthetic temporary experiments remain allowed.

PowerShell bootstrap for the local portable test runtime:

```powershell
$env:PYTHONHOME = Join-Path (Get-Location) '.venv\policy-python311'
$env:PYTHONPATH = Join-Path $env:PYTHONHOME 'site-packages'
$env:PYTHONDONTWRITEBYTECODE = '1'
```

The independent checker imports no selection/serialization/admission code.
P/K/H/reference golden hashes were also checked with PowerShell SHA256 over
independently typed literal bytes. Conformance establishes behavior against
synthetic fixtures, not production certification, retrieval quality, or freeze.
