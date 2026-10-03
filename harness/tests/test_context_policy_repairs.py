"""Bounded F1--F5 regressions. Normative expectations are independent literals."""

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from harness.context_policy.boundary import Acquisition, path
from harness.context_policy.core import PolicyFailure, SYSTEM
from harness.context_policy.evidence import cutoff_payload
from harness.context_policy.index import PythonIndex
from harness.context_policy.prepare import prepare_run
from harness.context_policy.protocol import CONTROL_VALUES, completion, validate_profile
from harness.context_policy.provenance import completion_provenance, record_completion
from harness.tests.policy_fixtures import (AUTH, EXPECTED_CONTROLS, EXPECTED_SYSTEM, acquire,
                                         acquisition_inputs, certificate, configuration, j,
                                         profile, recertify_acquisition, registry, task)
from harness.tests.test_context_policy import context


INVALID_PATHS = ("COM¹.py", "COM².txt", "COM³", "LPT¹.py", "LPT²", "LPT³.md", "a\u0085.py")


@pytest.mark.parametrize("name", INVALID_PATHS)
def test_reserved_devices_and_unicode_controls_rejected_everywhere(name):
    with pytest.raises(ValueError):
        path(name)
    with pytest.raises(PolicyFailure, match="task_invalid: invalid_target_path"):
        task(targets=(name,))
    with pytest.raises(PolicyFailure, match="infrastructure_invalid: snapshot_invalid"):
        acquire({name: ""})
    out = completion(f"=== FILE: {name} ===\n=== FILE: b.py ===\n", task(targets=("a.py", "b.py")),
                     integrity_verified=True, token_limit=False, output_tokens=10)
    assert out.category == "output_format_failure"
    assert "invalid_output_path" in out.diagnostics


@pytest.mark.parametrize("name", ("COM0.py", "COM10.py", "COM4x.py", "LPT¹notes.py", "worker².py", "a\u00ad.py"))
def test_unrelated_digit_superscript_and_format_character_paths_remain_valid(name):
    assert path(name) == name
    assert acquire({name: ""}).admit(task(targets=(name,)))[0].existing is True


def test_literal_control_table_and_common_system_are_independent():
    assert CONTROL_VALUES == EXPECTED_CONTROLS
    assert {key: type(value) for key, value in CONTROL_VALUES.items()} == {key: type(value) for key, value in EXPECTED_CONTROLS.items()}
    assert SYSTEM == EXPECTED_SYSTEM
    p, cert, tokenizer = profile()
    assert {k: s["requested"] for k, s in p["controls"].items()} == EXPECTED_CONTROLS
    assert p["generation_prompt_sha256"] == "d" * 64
    assert p["template_sha256"] == "c" * 64
    assert p["request_isolation"] == "fresh_sequence"
    validate_profile(p, cert, AUTH, tokenizer, mode="synthetic")


@pytest.mark.parametrize("key,value", (("decoding", "sample"), ("temperature", 2), ("seed", 7)))
def test_nonconforming_request_controls_rejected(key, value):
    p, _, tokenizer = profile()
    p["controls"][key].update(requested=value, effective=value)
    with pytest.raises(PolicyFailure, match="infrastructure_invalid: generation_controls_invalid"):
        validate_profile(p, certificate(p), AUTH, tokenizer, mode="synthetic")


def test_mutated_production_controls_cannot_mirror_valid_profile_fixture(monkeypatch):
    for key, value in (("decoding", "sample"), ("temperature", 2), ("seed", 7)):
        monkeypatch.setitem(CONTROL_VALUES, key, value)
    p, cert, tokenizer = profile()
    assert p["controls"]["decoding"]["requested"] == "greedy"
    assert p["controls"]["temperature"]["requested"] == 0
    assert p["controls"]["seed"]["requested"] == 0
    with pytest.raises(PolicyFailure, match="infrastructure_invalid: generation_controls_invalid"):
        validate_profile(p, cert, AUTH, tokenizer, mode="synthetic")


@pytest.mark.parametrize("alteration", ("missing_prompt", "invalid_prompt", "template_mismatch"))
def test_generation_template_identity_is_required(alteration):
    p, _, tokenizer = profile()
    if alteration == "missing_prompt":
        del p["generation_prompt_sha256"]
    elif alteration == "invalid_prompt":
        p["generation_prompt_sha256"] = "unverified"
    else:
        p["template_sha256"] = "e" * 64
    with pytest.raises(PolicyFailure):
        validate_profile(p, certificate(p), AUTH, tokenizer, mode="synthetic")


def test_incomplete_enumeration_and_forbidden_auth_diagnostics_are_retained():
    inputs = acquisition_inputs({})
    inputs["existence"][0]["complete"] = False
    recertify_acquisition(inputs)
    with pytest.raises(PolicyFailure) as caught:
        Acquisition.verify(**inputs, configuration=configuration(), auth=AUTH, mode="official")
    assert caught.value.primary.reason == "existence_unverified"
    assert [(d.phase, d.reason) for d in caught.value.diagnostics] == [
        (1, "existence_unverified"), (1, "test_authentication_forbidden")]


def test_multiple_infrastructure_failures_are_deduplicated_and_sorted():
    inputs = acquisition_inputs({"src/a.py": ""}, denied=("src/a.py",))
    for entry in inputs["existence"]:
        if entry["type"] == "directory":
            entry["complete"] = False
        if entry["path"] == "src/a.py":
            entry["denied"] = True
    recertify_acquisition(inputs)
    with pytest.raises(PolicyFailure) as caught:
        Acquisition.verify(**inputs, configuration=configuration(), auth=AUTH, mode="official")
    assert caught.value.primary.reason == "existence_unverified"
    assert [d.reason for d in caught.value.diagnostics] == [
        "existence_unverified", "product_evaluator_conflict", "test_authentication_forbidden"]


@pytest.mark.parametrize("name,classification,raw", (
    ("ignored.bin", "unsupported", b"old"),
    ("benchmark_design/private.txt", "excluded", b"old"),
    ("large.py", "oversized", b"x" * 1048577),
), ids=("unsupported", "excluded", "oversized"))
def test_every_supplied_filtered_blob_is_verified(name, classification, raw):
    inputs = acquisition_inputs({name: raw}, classifications={name: classification})
    inputs["raw_files"][name] = b"DRIFT"
    with pytest.raises(PolicyFailure, match="infrastructure_invalid: snapshot_invalid"):
        Acquisition.verify(**inputs, configuration=configuration(), auth=AUTH, mode="synthetic")


def test_filtered_same_length_hash_drift_also_fails():
    inputs = acquisition_inputs({"ignored.bin": b"old"}, classifications={"ignored.bin": "unsupported"})
    inputs["raw_files"]["ignored.bin"] = b"new"
    with pytest.raises(PolicyFailure, match="infrastructure_invalid: snapshot_invalid"):
        Acquisition.verify(**inputs, configuration=configuration(), auth=AUTH, mode="synthetic")


def test_filtered_metadata_only_and_verified_bytes_never_enter_snapshot():
    inputs = acquisition_inputs({"ignored.bin": b"old"}, classifications={"ignored.bin": "unsupported"})
    verified = Acquisition.verify(**inputs, configuration=configuration(), auth=AUTH, mode="synthetic")
    del inputs["raw_files"]["ignored.bin"]
    metadata_only = Acquisition.verify(**inputs, configuration=configuration(), auth=AUTH, mode="synthetic")
    assert dict(verified.snapshot.files) == dict(metadata_only.snapshot.files) == {}
    assert verified.identity == metadata_only.identity


@pytest.mark.parametrize("remaining,provider", (
    (("x/__init__.py", "x.py", "x/__init__.pyi", "x.pyi"), "x/__init__.py"),
    (("x.py", "x/__init__.pyi", "x.pyi"), "x.py"),
    (("x/__init__.pyi", "x.pyi"), "x/__init__.pyi"),
    (("x.pyi",), "x.pyi"),
))
def test_provider_precedence_falls_back_after_removal(remaining, provider):
    _, _, index, k = context({p: "" for p in remaining}, "x")
    assert index.modules["x"] == (provider,)
    assert k.inferred == (provider,)


@pytest.mark.parametrize("mode,basename", (("disabled", "pkg"), ("enabled", ""), ("enabled", "bad-name"), ("enabled", 3), ("invalid", "pkg")))
def test_invalid_root_alias_configuration_has_no_silent_fallback(mode, basename):
    config = dict(configuration(), root_alias_mode=mode, root_alias_basename=basename)
    with pytest.raises(PolicyFailure, match="infrastructure_invalid: invalid_root_alias_configuration"):
        PythonIndex(acquire({"__init__.py": ""}).snapshot, config)


def prepared_fixture(files=None, envelope=None, canonical=None, run_identity=None, raw_encoder=None):
    files = {"src/a.py": "pass"} if files is None else files
    envelope = {"instructions": "Edit.", "targets": ["src/a.py"]} if envelope is None else envelope
    canonical = envelope if canonical is None else canonical
    reg, reg_cert = registry(({"key": "episode", "kind": "EPISODIC", "body": "old"},))
    p, p_cert, tok = profile()
    if raw_encoder is not None:
        tok = replace(tok, raw_encode=raw_encoder)
    # Input certificates bind independently encoded canonical envelopes.
    binding = cutoff_payload(reg, 100, 100, hashlib.sha256(j(canonical)).hexdigest())
    cutoff_cert = dict(certificate(binding), public_task_sha256=hashlib.sha256(j(canonical)).hexdigest())
    return prepare_run(configuration(), acquisition_inputs=acquisition_inputs(files), public_envelope=envelope,
                       public_certificate=certificate(canonical), registry=reg, registry_certificate=reg_cert,
                       cutoff=100, task_release_sequence=100, cutoff_certificate=cutoff_cert, profile=p,
                       profile_certificate=p_cert, tokenizer=tok, authentication=AUTH, mode="synthetic", run_identity=run_identity)


EXPECTED_PREPARED_FIELDS = frozenset((
    "schema_id", "stage", "implementation", "implementation_repository_commit", "product_repository_commit",
    "repository_commit_source", "external_run_identity", "policy_id", "policy_sha256", "configuration_sha256", "public_task",
    "product_manifest_sha256", "deny_manifest_sha256", "existence_index_sha256", "acquisition_identity", "acquisition_receipt_hex",
    "parser_runtime", "snapshot_sha256", "acquisition_receipt_sha256", "P_sha256", "P_bytes", "protected", "inferred", "selected",
    "anchors", "nominations", "files", "K_sha256", "K_bytes", "K_characters", "K_hex", "K_standalone_tokenization", "K_unused_bytes",
    "budget_skips", "inventory_paths", "inventory_omitted", "file_truncation", "inventory", "structural_resolution", "index_diagnostics",
    "registry_view_sha256", "ledger_root", "registry_sha256", "cutoff_binding_sha256", "first_public_release_sequence", "historical_cutoff",
    "historical_exclusions", "historical_records", "H", "inputs", "run_profile_sha256", "runtime_profile", "reference_sha256",
    "reference_bytes", "reference_tokens", "generation_reserve", "common_admission", "matching_manifest", "completion", "coverage",
))


def test_complete_preparation_provenance_schema_and_unavailable_runtime_facts():
    prepared = prepared_fixture()
    audit = json.loads(prepared.provenance_bytes)
    assert set(audit) == EXPECTED_PREPARED_FIELDS
    assert audit["schema_id"] == "current-repo-v1-provenance-v2"
    assert audit["stage"] == "prepared"
    assert audit["completion"] is audit["common_admission"] is audit["matching_manifest"] is None
    assert audit["implementation_repository_commit"] is audit["product_repository_commit"] is None
    assert audit["repository_commit_source"] == "unavailable"
    assert len(audit["implementation"]["build_sha256"]) == 64
    assert audit["implementation"]["revision"] == "current-repo-v1-draft3-implementation-r2"
    assert audit["K_standalone_tokenization"] == {"status": "measured", "tokens": len(prepared.k.serialized)}
    assert bytes.fromhex(audit["K_hex"]) == prepared.k.serialized
    assert audit["K_sha256"] == hashlib.sha256(prepared.k.serialized).hexdigest()
    assert audit["inventory"]["hex"] == b'[FILES]\n"src/a.py"\n[/FILES]\n'.hex()
    assert audit["inventory"]["present"] is True
    assert audit["registry_sha256"] is not None and audit["cutoff_binding_sha256"] is not None
    assert audit["historical_records"][0]["body_bytes"] == 3
    assert audit["historical_records"][0]["block_bytes"] == len(b'[RECORD]\nold\n[/RECORD]\n')
    assert audit["H"][1]["record_order"] == ["episode"]
    assert audit["H"][4]["lane_allocations"][1]["unused_bytes"] == 2048 - len(b'[LANE]\n[/LANE]\n[/ADAPTATION]\n')


def test_raw_p_identity_is_preserved_without_claiming_transport_bytes():
    envelope = {"instructions": "\ufeffEdit.\r\n", "targets": ["src/a.py"]}
    canonical = {"instructions": "Edit.\n", "targets": ["src/a.py"]}
    audit = json.loads(prepared_fixture(envelope=envelope, canonical=canonical).provenance_bytes)
    raw = b'{"instructions":"\\ufeffEdit.\\r\\n","targets":["src/a.py"]}'
    normalized = b'{"instructions":"Edit.\\n","targets":["src/a.py"]}'
    assert audit["public_task"]["raw_hex"] == raw.hex()
    assert audit["public_task"]["raw_sha256"] == hashlib.sha256(raw).hexdigest()
    assert audit["public_task"]["canonical_hex"] == normalized.hex()
    assert audit["public_task"]["canonical_sha256"] == hashlib.sha256(normalized).hexdigest()
    assert audit["public_task"]["transport_sha256"] is audit["public_task"]["transport_bytes"] is None


def test_unavailable_standalone_k_tokens_remain_a_diagnostic_not_admission():
    def encoder(text):
        if text.startswith("[CURRENT_REPOSITORY "):
            raise ValueError("synthetic standalone K encoding unavailable")
        return list(text.encode())
    prepared = prepared_fixture(raw_encoder=encoder)
    audit = json.loads(prepared.provenance_bytes)
    assert audit["K_standalone_tokenization"] == {"tokens": None, "status": "unavailable", "reason": "tokenization_unavailable"}
    assert prepared.k.serialized == prepared_fixture().k.serialized


def test_external_commit_identity_is_recorded_without_live_repository_lookup():
    identity = {"implementation_repository_commit": "a" * 40, "product_repository_commit": "b" * 40}
    prepared = prepared_fixture(run_identity=identity)
    identity["product_repository_commit"] = "c" * 40
    audit = json.loads(prepared.provenance_bytes)
    assert audit["implementation_repository_commit"] == "a" * 40
    assert audit["product_repository_commit"] == "b" * 40
    assert audit["repository_commit_source"] == "external-run-identity"
    assert audit["existence_index_sha256"] == json.loads(bytes.fromhex(audit["acquisition_receipt_hex"]))["existence_index_sha256"]


def test_absent_inventory_is_distinguished_from_present_empty_inventory():
    envelope = {"instructions": "Edit.", "targets": ["a.py"]}
    audit = json.loads(prepared_fixture(files={"a.py": "#" + "x" * 12186}, envelope=envelope, raw_encoder=lambda _: [0]).provenance_bytes)
    assert audit["inventory"] == {"present": False, "bytes": 0, "sha256": hashlib.sha256(b'').hexdigest(),
                                  "hex": "", "allowance": 0, "unused_allowance": 0, "paths": [], "omitted": False}


def test_distinct_declaration_routes_survive_same_physical_file_dedup():
    source = "class Alpha:\n def run(self): pass\nclass Beta:\n def run(self): pass\n"
    envelope = {"instructions": "run", "targets": ["new.py"]}
    prepared = prepared_fixture(files={"x.py": source}, envelope=envelope)
    audit = json.loads(prepared.provenance_bytes)
    assert prepared.k.inferred == ("x.py",)
    reasons = audit["structural_resolution"]["declaration_routes"]["run"]
    assert [(r["owner_qualified"], r["alias_kind"], r["line"], r["path"]) for r in reasons] == [
        ("Alpha.run", "unqualified", 2, "x.py"), ("Beta.run", "unqualified", 4, "x.py")]
    assert audit["anchors"][0]["resolution_reasons"] == reasons
    assert b"owner_qualified" not in prepared.conditions.messages[0][1][1]["content"].encode()


def test_completion_provenance_is_populated_only_after_generation_stage():
    prepared = prepared_fixture()
    before = prepared.provenance_bytes
    accounting = {"native_terminal_ids": [0], "terminal_tokens": 1, "included_in_output_tokens": True}
    result = completion("\ufeffx\r\n", prepared.task, integrity_verified=True, token_limit=False, output_tokens=3,
                        finish_reason="eos", terminal_token_accounting=accounting)
    accounting["terminal_tokens"] = 9
    after = json.loads(record_completion(prepared, result))
    assert after["stage"] == "completion_recorded"
    assert prepared.provenance_bytes == before
    out = after["completion"]
    assert out["raw_hex"] == b'\xef\xbb\xbfx\r\n'.hex()
    assert out["normalized_hex"] == b'\xef\xbb\xbfx\n'.hex()
    assert out["raw_sha256"] == hashlib.sha256(b'\xef\xbb\xbfx\r\n').hexdigest()
    assert out["normalized_sha256"] == hashlib.sha256(b'\xef\xbb\xbfx\n').hexdigest()
    assert out["finish_reason"] == "eos"
    assert out["terminal_token_accounting"]["terminal_tokens"] == 1
    assert out["category"] == "artifact_ready"
    assert out["classification_inputs"] == {"integrity_verified": True, "verified_token_limit": False}
    assert completion_provenance(completion("", task(), integrity_verified=True, token_limit=False, output_tokens=0))["finish_reason"] is None


def test_partial_capacity_output_retains_raw_bytes_and_secondary_format_diagnostics():
    result = completion("partial\r", task(targets=("a.py", "b.py")), integrity_verified=True, token_limit=True,
                        output_tokens=2048, finish_reason="length")
    out = completion_provenance(result)
    assert out["category"] == "output_capacity_failure"
    assert out["raw_hex"] == b'partial\r'.hex()
    assert out["normalized_hex"] == b'partial\n'.hex()
    assert out["finish_reason"] == "length" and out["terminal_token_accounting"] is None
    assert out["format_diagnostics"] == ["first_header_not_zero", "header_vector_mismatch"]


def test_new_revision_identity_is_authenticated_and_old_config_is_rejected():
    from harness.context_policy.core import IMPLEMENTATION_REVISION_SHA256
    artifact = Path("benchmark_design/context_policy/implementation-r2.json").read_bytes()
    assert hashlib.sha256(artifact).hexdigest() == IMPLEMENTATION_REVISION_SHA256
    config = configuration()
    del config["implementation_revision"]
    del config["implementation_revision_sha256"]
    with pytest.raises(PolicyFailure, match="infrastructure_invalid: configuration_invalid"):
        PythonIndex(acquire({}).snapshot, config)
    inputs = acquisition_inputs({})
    changed = dict(configuration(), implementation_revision="old")
    with pytest.raises(PolicyFailure, match="infrastructure_invalid: snapshot_invalid"):
        Acquisition.verify(**inputs, configuration=changed, auth=AUTH, mode="synthetic")
