# Evaluation protocol v2

Every new runner result is Protocol v2. Existing pilot configs/results, application
code, convention scorers, memory/rule rendering and leakage detection are unchanged.
Old configs need an explicit target-test source before they can produce a valid new
run; there is no regression-as-target fallback.

## Configuration and privacy

Add this field to a future experiment config:

```json
{"target_tests": {"source": "target_tests"}}
```

`source` is a directory resolved relative to the config's directory (absolute paths
also work). It must contain `test_*.py` files, reside outside the base repository,
and contain no symlinks. Supporting fixtures/data may reside in this directory.
Target tests should be self-contained: fixtures in `tests/conftest.py` do not apply
to the sibling target suite. Repository-root fixtures apply to both suites.

The model receives only assembled chat messages; it has no filesystem/tool access
in the current inference wrapper. Context paths cannot escape the base checkout.
Target-test configuration/content is never appended to messages. The private
directory is copied to `_evaluation_target_tests` only after inference and output
application. That destination must not already exist or be a generated target.
If filesystem-capable model tools are introduced later, enforce a separate mount
boundary for evaluator sources before enabling them.

Lifecycle: validate config → create workspace → fingerprint regression files →
assemble context → unchanged leakage preflight → inference → apply output →
fingerprint the generated application artifact → check regression integrity →
inject target tests → target pytest → artifact check → regression pytest → artifact
check → convention scorer → artifact check → save result. A leakage error still raises the original
`LeakageDetectedError` before inference, and now also saves an invalid v2 record.

## Results

The exact evaluation envelope for an ordinary successful run is below. Pytest
reports and scorer-specific fields supplement it; values/counts shown are examples.

```json
{
  "evaluation_protocol": "v2",
  "run_status": "valid",
  "errors": [],
  "evaluation": {
    "target": {
      "passed": true,
      "status": "completed",
      "tests_passed": 5,
      "tests_failed": 0,
      "tests_skipped": 0,
      "returncode": 0,
      "stdout": "pytest output",
      "stderr": "",
      "errors": [],
      "reports": []
    },
    "regression": {
      "passed": true,
      "status": "completed",
      "tests_passed": 7,
      "tests_failed": 0,
      "tests_skipped": 0,
      "returncode": 0,
      "stdout": "pytest output",
      "stderr": "",
      "errors": [],
      "reports": [],
      "regression_tests_modified": false,
      "changed_files": [],
      "missing_files": [],
      "added_files": [],
      "fingerprints": {"tests/test_example.py": "sha256-hex"}
    },
    "convention": {
      "passed": true,
      "status": "completed",
      "errors": []
    },
    "artifact": {
      "evaluated_artifact_modified": false,
      "changed_files": [],
      "missing_files": [],
      "added_files": [],
      "fingerprints": {"services/example.py": "sha256-hex"},
      "checks": [
        {"stage": "target", "evaluated_artifact_modified": false},
        {"stage": "regression", "evaluated_artifact_modified": false},
        {"stage": "convention", "evaluated_artifact_modified": false}
      ],
      "errors": []
    },
    "overall_success": true
  },
  "evaluated_artifact_modified": false,
  "overall_success": true
}
```

`reports` contains per-node setup/call/teardown or failed-collection records with
`nodeid`, `phase`, `outcome`, `traceback_paths`, `assertion_failure`, and `detail`.
Failed node IDs count once even if multiple phases fail. A test with a passing call
and failing teardown counts as failed, not passed. A collection failure counts as
one failed collection node; the report's phase distinguishes it from a test case.
No-tests/all-skipped suites cannot establish correctness and invalidate the run.

Existing audit fields remain: experiment, condition, model, context file list, task,
memory/rule source and contents, prompts, raw generation, target paths, originals
and applied generation. `config_path`, the full `config`, and resolved `target_tests`
are also retained. Metadata not reached before failure is absent. Legacy
`tests_passed`, `test_returncode`, `test_stdout`, and `test_stderr` refer only to
regression evaluation; `convention_passed`/`convention_result` mirror that gate.
Both overall-success fields always agree. Result filenames have a UUID suffix and
are created exclusively, preventing overwrites of historical evidence.

## Integrity and failure attribution

Before inference, SHA-256 fingerprints cover every file under `tests/`, including
fixtures/data, except runtime caches. Existing root `conftest.py`, `pytest.ini`,
`pyproject.toml`, `setup.cfg`, and `tox.ini` are protected as well. Inventory checks
also detect additions of protected files. Changes, missing files, replacements by
directories/symlinks and renames invalidate the run before regression results are
trusted. Checks run after application, after target evaluation, after regression
evaluation and after scoring. An observed violation stays invalid even if later
restored.

After generated output is successfully applied, a separate SHA-256 inventory fixes
the application artifact that is being evaluated. It excludes the existing
`tests/` tree, `_evaluation_target_tests/`, root pytest configuration, Python and
pytest caches, bytecode, coverage output, and common evaluator cache directories.
The inventory is checked after target tests, regression tests, and convention
scoring. Any changed, missing, renamed, or added application file marks the
responsible gate and the run `invalid_infrastructure`, records the affected paths,
sets both overall-success fields to `null`, and prevents later gates from running.
Generated changes are accepted because this baseline is taken only after generation
has been applied.

Target and regression tests execute in separate pytest subprocesses with explicit
suite paths, independent counts/output and the current Python interpreter. A
trusted reporting plugin produces structured reports outside the generated
workspace. Existing pytest configuration is retained, except `addopts` and inherited
`PYTEST_ADDOPTS` are cleared so they cannot silently select another suite or report
destination. This is evaluation integrity, not a hostile-code sandbox.

Each gate has `passed: true/false` only for completed, attributable evaluation.
Assertions (including `pytest.fail`) are model failures. Exceptions attributable
to generated source via traceback/exception provenance, including import/syntax
errors and missing generated attributes, are also model failures. Other evaluator
exceptions, collection/setup errors without generated-code provenance, timeout,
launch/internal pytest errors, missing reports, no executed tests, injection errors
and scorer crashes conservatively invalidate the run. Ambiguous timeouts/errors
require investigation; they are never charged to the model automatically.

A malformed multi-file response is recorded as a model-output error and forces
target failure if the evaluators otherwise execute successfully. Scorer-returned
`passed: false` is a valid failure; unavailable/crashing/malformed scorers invalidate
the run without altering scorer semantics.

Infrastructure-invalid runs use `run_status: "invalid_infrastructure"` and both
overall-success fields are `null`. The affected gate has `passed: null`, status
`invalid_infrastructure`, and structured `{stage, type, message}` errors. Gates not
reached have status `not_run`. Configuration/outer orchestration errors appear in
top-level `errors`. Trustworthy completed gates remain available for audit, but
cannot make an invalid run successful. CLI infrastructure failures exit with code
2; legitimate model failures still produce a normal valid result.

Persistence failures propagate to the caller: a storage failure cannot guarantee a
saved result. No paired rescue/harm classification is written into individual runs.
