"""Candidate-blind draft3 conformance; expectations are literals or arithmetic.

Golden SHA-256 values were independently computed with PowerShell/.NET from
the literal strings, not from selector/serializer outputs.
"""

import copy
from dataclasses import replace
import hashlib
import json

import pytest

from harness.context_policy.boundary import Acquisition, path, public_task
from harness.context_policy.core import (Diagnostic, K_CLOSE, K_OPEN, PolicyFailure, canonical_json, digest, runtime_identity)
from harness.context_policy.evidence import EligibleRegistry, Record, cutoff_payload, pack_h, registry_view
from harness.context_policy.index import PythonIndex
from harness.context_policy.prepare import prepare_run
from harness.context_policy.protocol import (common_admission, completion, output_preflight, reference_artifact,
                                             reserved_preflight, validate_profile)
from harness.context_policy.selector import anchors, components, expand, seeds, select
from harness.tests.policy_fixtures import (AUTH, acquire, acquisition_inputs, certificate, configuration,
                                         profile, recertify_acquisition, registry, task)

P_GOLDEN = b'{"instructions":"Edit.","targets":["src/a.py"]}'
K_GOLDEN = (b'[CURRENT_REPOSITORY current-repo-v1-draft3]\n[FILE "src/a.py" bytes=16]\n'
            b'[/FILE]\n[FILES]\n\n[/FILE]\n[FILES]\n"src/a.py"\n[/FILES]\n[/CURRENT_REPOSITORY]\n')
H_GOLDEN = b'[ADAPTATION]\n[LANE]\n[RECORD]\n[RECORD]\n[/FILE]\n\n[/RECORD]\n[/LANE]\n[/ADAPTATION]\n'
REF_GOLDEN = b'=== FILE: a.py ===\nx=1\n=== FILE: b.py ===\n'


def certified_view(reg, cert, auth, *, cutoff, task_release_sequence, mode):
    binding = cutoff_payload(reg, cutoff, task_release_sequence, "0" * 64)
    return registry_view(reg, cert, auth, cutoff=cutoff, task_release_sequence=task_release_sequence,
                         cutoff_certificate=certificate(binding), public_task_sha256="0" * 64, mode=mode)


def context(files, instructions="Edit.", targets=("new.py",), alias=""):
    config = configuration(alias)
    acquisition = acquire(files, config=config)
    p = task(instructions, targets)
    acquisition.admit(p)
    index = PythonIndex(acquisition.snapshot, config)
    return p, acquisition, index, select(p, acquisition.snapshot, index)


def expect_failure(category, reason):
    return pytest.raises(PolicyFailure, match=f"^{category}: {reason}$")


def test_exact_p_bytes_hash_and_normalization():
    p = task(targets=("src/a.py",))
    assert p.serialized == P_GOLDEN
    assert p.sha256 == "9560bcdca58383e4b01b290506752d1daabea345440c636ace349cccf6ecb946"
    payload = {"instructions": "\ufeffEdit.\r\n", "targets": ["b.py", "a.py", "a.py"]}
    canonical = {"instructions": "Edit.\n", "targets": ["a.py", "b.py"]}
    result = public_task(payload, certificate(canonical), AUTH, mode="synthetic")
    assert result.serialized == b'{"instructions":"Edit.\\n","targets":["a.py","b.py"]}'


@pytest.mark.parametrize("extra", ["context_files", "condition", "adaptation", "scorer", "candidate_id"])
def test_task_exact_schema(extra):
    with expect_failure("task_invalid", "invalid_task_schema"):
        public_task({"instructions": "x", "targets": ["a.py"], extra: []}, {}, AUTH, mode="synthetic")


def test_p_exact_boundary():
    # Empty instructions with this target take 38 bytes of JSON framing.
    base = b'{"instructions":"","targets":["a.py"]}'
    count = 4096 - len(base)
    p = task("x" * count, ("a.py",))
    assert len(p.serialized) == 4096
    with expect_failure("task_invalid", "public_task_overlength"):
        task("x" * (count + 1), ("a.py",))


@pytest.mark.parametrize("target", ["../a.py", "a//b.py", "./a.py", "a\\b.py", "C:/a.py", "NUL.py", "a./b.py"])
def test_invalid_structured_paths(target):
    with expect_failure("task_invalid", "invalid_target_path"):
        task(targets=(target,))


def test_target_nfc_duplicates_and_casefold():
    payload = {"instructions": "Edit.", "targets": ["e\u0301.py", "é.py"]}
    p = public_task(payload, certificate({"instructions": "Edit.", "targets": ["é.py"]}), AUTH, mode="synthetic")
    assert p.targets == ("é.py",)
    with expect_failure("task_invalid", "target_path_collision"):
        task(targets=("A.py", "a.py"))
    with expect_failure("task_invalid", "conflicting_targets"):
        task(targets=("a.py", "a.py/b.py"))


def test_production_refuses_test_or_missing_authentication():
    inputs = acquisition_inputs({"a.py": ""})
    with expect_failure("infrastructure_invalid", "test_authentication_forbidden"):
        Acquisition.verify(**inputs, configuration=configuration(), auth=AUTH)
    with expect_failure("infrastructure_invalid", "certification_missing"):
        Acquisition.verify(**inputs, configuration=configuration(), auth=None)


def test_snapshot_immutable_content_and_drift():
    inputs = acquisition_inputs({"a.py": "before"})
    acq = Acquisition.verify(**inputs, configuration=configuration(), auth=AUTH, mode="synthetic")
    inputs["raw_files"]["a.py"] = b"after"
    assert acq.snapshot.files["a.py"] == "before"
    with pytest.raises(TypeError):
        acq.snapshot.files["a.py"] = "after"
    with expect_failure("infrastructure_invalid", "snapshot_invalid"):
        Acquisition.verify(**inputs, configuration=configuration(), auth=AUTH, mode="synthetic")


@pytest.mark.parametrize("kind,reason", [("directory", "target_not_regular_file"), ("symlink", "prohibited_target_ancestry"),
                                        ("reparse", "prohibited_target_ancestry"), ("gitlink", "prohibited_target_ancestry")])
def test_target_entry_types(kind, reason):
    extra = {"path": "a.py", "type": kind, "product": False, "denied": False, "complete": True, "eligibility": "excluded"}
    acq = acquire({}, extras=(extra,))
    with expect_failure("task_invalid", reason):
        acq.admit(task(targets=("a.py",)))


def test_unmanifested_file_is_not_new_and_private_names_do_not_escape():
    extra = {"path": "private.py", "type": "regular", "product": False, "denied": False, "complete": True, "eligibility": "excluded"}
    acq = acquire({}, extras=(extra,))
    with expect_failure("task_invalid", "existing_target_not_product"):
        acq.admit(task(targets=("private.py",)))
    assert "private.py" not in acq.snapshot.files
    result = acq.admit(task(targets=("new.py",)))
    assert [(r.path, r.existing, r.content_sha256) for r in result] == [("new.py", False, None)]
    assert "private.py" not in repr(result)


def test_new_targets_and_parent_conflicts():
    acq = acquire({"a.py": ""})
    assert acq.admit(task(targets=("new/sub/new.py",)))[0].existing is False
    with expect_failure("task_invalid", "target_parent_not_directory"):
        acq.admit(task(targets=("a.py/new.py",)))
    with expect_failure("task_invalid", "target_path_collision"):
        acq.admit(task(targets=("A.py",)))
    with expect_failure("task_invalid", "prohibited_target_path"):
        acq.admit(task(targets=("results/new.py",)))
    with expect_failure("task_invalid", "unsupported_target_format"):
        acq.admit(task(targets=("new.bin",)))


def test_unmanifested_and_link_ancestry():
    for kind, reason in (("directory", "target_ancestry_not_product"), ("symlink", "prohibited_target_ancestry"),
                         ("reparse", "prohibited_target_ancestry"), ("gitlink", "prohibited_target_ancestry")):
        extra = {"path": "opaque", "type": kind, "product": False, "denied": False, "complete": True, "eligibility": "excluded"}
        with expect_failure("task_invalid", reason):
            acquire({}, extras=(extra,)).admit(task(targets=("opaque/new.py",)))


def test_conflict_incomplete_and_collision_acquisition():
    inputs = acquisition_inputs({"a.py": ""}, denied=("a.py",))
    inputs["existence"][1]["denied"] = True
    recertify_acquisition(inputs)
    with expect_failure("infrastructure_invalid", "product_evaluator_conflict"):
        Acquisition.verify(**inputs, configuration=configuration(), auth=AUTH, mode="synthetic")
    inputs = acquisition_inputs({})
    inputs["existence"][0]["complete"] = False
    recertify_acquisition(inputs)
    with expect_failure("infrastructure_invalid", "existence_unverified"):
        Acquisition.verify(**inputs, configuration=configuration(), auth=AUTH, mode="synthetic")
    with expect_failure("infrastructure_invalid", "snapshot_invalid"):
        acquire({"A.py": "", "a.py": ""})


@pytest.mark.parametrize("raw,classification", [(b"\xff", "invalid_text"), (b"a\0b", "invalid_text"),
                                              (b"x" * 1048577, "oversized")], ids=["invalid-utf8", "nul", "oversized"])
def test_ineligible_current_file(raw, classification):
    acq = acquire({"a.py": raw}, classifications={"a.py": classification})
    assert "a.py" not in acq.snapshot.files
    with expect_failure("task_invalid", "prohibited_target_path"):
        acq.admit(task(targets=("a.py",)))


def test_raw_source_size_inclusive_and_bom_crlf():
    assert len(acquire({"a.py": b"#" + b"x" * 1048575}).snapshot.files["a.py"]) == 1048576
    acq = acquire({"a.py": b"\xef\xbb\xbfx\r\ny\rz\n"})
    assert acq.snapshot.files["a.py"] == "x\ny\nz\n"


def test_lexical_component_offsets_and_order():
    assert [(c, offset) for c, offset, *_ in components("CustomerRecord customerAccount")] == [
        ("customer", 0), ("record", 8), ("customer", 15), ("account", 23)]
    files = {"pkg/customer.py": "", "pkg/record.py": "", "pkg/account.py": "", "pkg/summary.py": ""}
    _, _, _, k = context(files, "CustomerRecord customerAccount", ("reports/customer_summary.py",))
    assert k.inferred == ("pkg/customer.py", "pkg/record.py", "pkg/account.py", "pkg/summary.py")
    customer = [a for a in k.anchors if a.path == "pkg/customer.py"]
    assert {a.key[1] for a in customer} == {(0, 0), (0, 15), (1, 0, 8)}
    files["aaa/customer.py"] = ""
    _, _, _, k = context(files, "CustomerRecord customerAccount", ("reports/customer_summary.py",))
    assert k.inferred == ("aaa/customer.py", "pkg/customer.py", "pkg/record.py", "pkg/account.py")


def test_true_fallback_and_quoted_unicode_offsets():
    _, _, _, k = context({"src/a.py": "", "customer.py": ""}, "edit `src/a.py` Customer")
    assert k.protected == ("src/a.py",)
    assert k.inferred == ()
    assert [a.key[1] for a in k.anchors] == [(0, 6), (0, 6)]
    _, _, _, k = context({"src/a.py": ""}, "😀 edit `src/a.py`")
    assert {a.key[1] for a in k.anchors} == {(0, 8)}


def test_path_retry_internal_dots_and_invalid_prose():
    _, _, _, k = context({"src/worker..old.py": ""}, "edit src/worker..old.py.")
    assert k.protected == ("src/worker..old.py",)
    _, _, _, k = context({"src/worker.py": ""}, "src/../worker.py src//worker.py")
    assert all(not a.protected for a in k.anchors)
    _, _, _, k = context({"src/a.py": "", "src/b.py": ""}, "./src")
    assert k.inferred == ("src/a.py", "src/b.py")
    assert k.protected == ()


def test_filename_ambiguity_and_more_than_four_protected():
    _, _, _, k = context({"a/x.py": "", "b/x.py": ""}, "x.py")
    assert k.inferred == ("a/x.py", "b/x.py")
    assert k.protected == ()
    files = {f"p{i}.py": "" for i in range(6)}
    _, _, _, k = context(files, " ".join(files))
    assert k.protected == tuple(files)


def test_shadowed_declaration_owners_and_provider():
    files = {p: "def run(): pass\n" for p in ("x/__init__.py", "x.py", "x/__init__.pyi", "x.pyi")}
    p, acq, index, k = context(files, "x")
    assert k.inferred == ("x/__init__.py",)
    assert index.modules["x"] == ("x/__init__.py",)
    p = task("x.run")
    assert seeds(anchors(p, acq.snapshot, index))[1] == ("x.py", "x.pyi", "x/__init__.py", "x/__init__.pyi")


def test_uppercase_extension_and_parse_failure():
    _, acq, index, k = context({"a.py": "def run(): pass", "b.PY": "def run(): pass", "bad.py": "def :"}, "run")
    assert "b.PY" in acq.snapshot.files
    assert "b.PY" not in index.files
    assert set(index.declarations["run"]) == {"a.py"}
    assert index.edges["bad.py"] == set()
    assert index.diagnostics[0]["reason"] == "parse_failure"


def test_root_alias_union_and_route_initializers():
    files = {"__init__.py": "", "foo.py": "", "pkg/__init__.py": "", "pkg/foo.py": "", "caller.py": "import pkg.foo"}
    _, _, index, _ = context(files, alias="pkg")
    assert index.modules["pkg.foo"] == ("foo.py", "pkg/foo.py")
    assert index.edges["caller.py"] == {"foo.py", "pkg/foo.py", "pkg/__init__.py", "__init__.py"}
    routes = index.edge_reasons["caller.py"]
    assert any(r["target"] == "__init__.py" and r["prefixed"] for r in routes)
    assert not any(r["target"] == "__init__.py" and not r["prefixed"] for r in routes)
    disabled = PythonIndex(acquire(files).snapshot, configuration())
    assert disabled.modules["pkg.foo"] == ("pkg/foo.py",)
    with expect_failure("infrastructure_invalid", "invalid_root_alias_configuration"):
        PythonIndex(acquire({"a.py": ""}).snapshot, configuration("pkg"))


def test_relative_wildcard_dynamic_namespace_and_one_hop():
    files = {"__init__.py": "", "a.py": "from . import b\nfrom .b import *\n", "b.py": "import c\n", "c.py": "",
             "dynamic.py": "__import__('c')\n", "bad.py": "from .. import c\n", "ns/user.py": "import ns.leaf", "ns/leaf.py": ""}
    _, _, index, k = context(files, "a.py", alias="pkg")
    assert index.edges["a.py"] == {"__init__.py", "b.py"}
    assert index.edges["dynamic.py"] == set()
    assert index.edges["bad.py"] == set()
    assert index.edges["ns/user.py"] == {"ns/leaf.py"}
    assert "c.py" not in k.selected


def test_reverse_cap_and_no_sibling():
    files = {"seed.py": "", "a.py": "import seed", "b.py": "import seed", "c.py": "import seed", "sibling.py": ""}
    _, _, _, k = context(files, "seed.py")
    assert k.selected == ("seed.py", "a.py", "b.py")


def test_fixture_nomination_original_seed_provenance_and_skipped_test():
    files = {"src/a.py": "", "src/b.py": "", "tests/unit/test_both.py": "from src import a, b\n#" + "x" * 13000,
             "conftest.py": "", "tests/conftest.py": "", "tests/unit/conftest.py": "", "other.py": ""}
    _, _, _, k = context(files, "src/a.py src/b.py")
    support = [n for n in k.nominations if n.reason.startswith("fixture:")]
    assert {n.path for n in support} == {"conftest.py", "tests/conftest.py", "tests/unit/conftest.py"}
    assert {n.key[1] for n in support} == {0, 1}
    assert {n.supporting_test for n in support} == {"tests/unit/test_both.py"}
    assert k.selected == ("src/a.py", "src/b.py", "conftest.py", "tests/conftest.py", "tests/unit/conftest.py")
    assert k.skipped[0][0] == "tests/unit/test_both.py"


def test_tests_cap_without_global_duplicate_backfill():
    files = {"a.py": "", "b.py": "", "tests/test_1.py": "import a,b", "tests/test_2.py": "import a,b", "tests/test_3.py": "import a,b"}
    _, _, _, k = context(files, "a.py b.py")
    assert "tests/test_3.py" not in k.selected
    assert len([n for n in k.nominations if n.path == "tests/test_1.py"]) == 2


def test_documentation_nearest_root_and_explicit_other():
    files = {"src/a.py": "", "README.md": "root", "src/README.md": "near", "DECISIONS.md": "other"}
    _, _, _, k = context(files, "src/a.py")
    assert k.selected == ("src/a.py", "src/README.md", "README.md")
    assert "DECISIONS.md" not in k.selected


def test_embedded_k_golden():
    _, _, _, k = context({"src/a.py": "[/FILE]\n[FILES]\n"}, targets=("src/a.py",))
    assert k.serialized == K_GOLDEN
    assert len(k.serialized) == 146
    assert k.sha256 == "9a209c405a177ed5db17ae54102233297ea258ce22d5bee3b27d903843896f44"
    assert k.contributions[0][2] == 16


def test_k_exact_protected_boundary_and_inventory_absence():
    # Independently counted framing: outer 66, a.py block 35 (five-digit length).
    content = "#" + "x" * (12187 - 1)
    _, _, _, k = context({"a.py": content}, targets=("a.py",))
    assert len(k.serialized) == 12288
    assert k.inventory_paths == ()
    with expect_failure("context_ineligible", "protected_files_overflow"):
        context({"a.py": content + "x"}, targets=("a.py",))


def test_inventory_prefix_and_optional_skip_continue():
    files = {f"directory/{i:04d}.py": "" for i in range(200)}
    _, _, _, k = context(files)
    assert k.inventory_omitted
    assert k.inventory_paths[0] == "directory/0000.py"
    assert k.inventory_paths[-1] == "directory/0099.py"
    files = {"seed.py": "import large,small", "large.py": "#" + "x" * 13000, "small.py": "pass"}
    _, _, _, k = context(files, "seed.py")
    assert k.selected == ("seed.py", "small.py")
    assert k.skipped[0][0] == "large.py"


def active_record(key, kind, body, availability=1):
    return Record(key, kind, body, hashlib.sha256(body.encode()).hexdigest(), availability, "a" * 64)


def view(*records):
    return EligibleRegistry(tuple(records), "a" * 64, "0" * 64, 100, ())


def test_embedded_h_golden_and_overlap_retained():
    snapshot = acquire({"a.py": "[RECORD]\n[/FILE]\n"}).snapshot
    h = pack_h("B", view(active_record("e", "EPISODIC", "[RECORD]\n[/FILE]\n")), snapshot)
    assert h.serialized == H_GOLDEN
    assert h.sha256 == "563e008c399e61f43fa2a8cf62890d8747c12748d9d9c7aaebf79a1469d69f16"
    assert h.selected == ("e",)
    assert h.overlaps == (("e", "a.py", "exact_body_content"),)


@pytest.mark.parametrize("condition,kind", [("B", "EPISODIC"), ("M", "DESCRIPTIVE"), ("C", "CONFIRMED_RULE")])
def test_single_lane_h_exact_boundary(condition, kind):
    snapshot = acquire({}).snapshot
    # Independently counted H/L/record overhead: 62 bytes.
    h = pack_h(condition, view(active_record("one", kind, "x" * 4034)), snapshot)
    assert len(h.serialized) == 4096
    h = pack_h(condition, view(active_record("large", kind, "x" * 4035, 2), active_record("small", kind, "y")), snapshot)
    assert h.selected == ("small",)
    assert h.skipped[0][0] == "large"


def test_bc_split_no_transfer_duplicates_and_empty():
    snapshot = acquire({}).snapshot
    rows = view(active_record("mem", "EPISODIC", "x" * 2000), active_record("rule", "CONFIRMED_RULE", "x" * 1999))
    h = pack_h("BC", rows, snapshot)
    assert h.lane_bytes == (("EPISODIC", 2048), ("CONFIRMED_RULE", 2048))
    assert len(h.serialized) == 4096
    h = pack_h("BC", view(active_record("too-big", "EPISODIC", "x" * 2001), active_record("rule", "CONFIRMED_RULE", "y")), snapshot)
    assert h.selected == ("rule",)
    assert h.skipped[0][0] == "too-big"
    h = pack_h("B", view(active_record("older", "EPISODIC", "same", 1), active_record("newer", "EPISODIC", "same", 2)), snapshot)
    assert h.selected == ("newer",)
    assert h.duplicates == (("older", "newer"),)
    assert pack_h("A", rows, snapshot).serialized == b""
    assert pack_h("B", view(), snapshot).serialized == b""


def test_registry_chronology_revisions_withdrawal_and_confirmation():
    reg, cert = registry(({"key": "old", "kind": "EPISODIC", "body": "old", "episode": "ep"},
                          {"key": "new", "kind": "EPISODIC", "body": "new", "episode": "ep", "predecessor": "old", "withdraw": True},
                          {"key": "rule", "kind": "CONFIRMED_RULE", "body": "Use prior supported behavior."}))
    early = certified_view(reg, cert, AUTH, cutoff=4, task_release_sequence=100, mode="synthetic")
    assert [r.key for r in early.records] == ["old"]
    late = certified_view(reg, cert, AUTH, cutoff=100, task_release_sequence=100, mode="synthetic")
    assert [r.key for r in late.records] == ["rule"]
    assert early.identity != late.identity
    reg["records"][-1].pop("confirmation")
    with expect_failure("infrastructure_invalid", "registry_invalid"):
        certified_view(reg, certificate(reg), AUTH, cutoff=100, task_release_sequence=100, mode="synthetic")


def test_registry_broken_chain_missing_certification_and_conflicting_revisions():
    reg, cert = registry(({"key": "a", "kind": "DESCRIPTIVE", "body": "prior"},))
    reg["events"][1]["previous_sha256"] = "f" * 64
    with expect_failure("infrastructure_invalid", "registry_invalid"):
        certified_view(reg, certificate(reg), AUTH, cutoff=100, task_release_sequence=100, mode="synthetic")
    rows = ({"key": "a", "kind": "DESCRIPTIVE", "body": "a"}, {"key": "b", "kind": "DESCRIPTIVE", "body": "b", "predecessor": "a"},
            {"key": "c", "kind": "DESCRIPTIVE", "body": "c", "predecessor": "a"})
    reg, cert = registry(rows)
    with expect_failure("infrastructure_invalid", "registry_invalid"):
        certified_view(reg, cert, AUTH, cutoff=100, task_release_sequence=100, mode="synthetic")


def test_output_single_lossless_and_mixed_reference_golden():
    p = task(targets=("a.py",))
    result = completion("\ufeff  ```\r\n=== FILE: a.py ===\r", p, integrity_verified=True, token_limit=False, output_tokens=5)
    assert result.artifacts == (("a.py", "\ufeff  ```\n=== FILE: a.py ===\n"),)
    p = task(targets=("a.py", "b.py"))
    reference = reference_artifact(p, acquire({"a.py": "x=1"}).snapshot)
    assert reference == REF_GOLDEN
    assert digest(reference) == "9b90bcf9516863f1b9eb1af264109c7518200eb1b1aceb15f63a9b51411360a0"
    result = completion(reference.decode(), p, integrity_verified=True, token_limit=False, output_tokens=20)
    assert result.artifacts == (("a.py", "x=1\n"), ("b.py", ""))
    assert completion("", task(), integrity_verified=True, token_limit=False, output_tokens=0).artifacts == (("new.py", ""),)


@pytest.mark.parametrize("text", ["", " === FILE: a.py ===\n", "=== FILE: b.py ===\n=== FILE: a.py ===\n",
                                  "=== FILE: a.py ===\n=== FILE: a.py ===\n=== FILE: b.py ===\n",
                                  "=== FILE: a.py ===\n=== FILE: c.py ===\n=== FILE: b.py ===\n",
                                  "=== FILE: a.py ===\n=== FILE: b.py ===",
                                  "=== FILE: a.py ===\n=== FILE: ../b.py ===\n"])
def test_output_header_failures(text):
    result = completion(text, task(targets=("a.py", "b.py")), integrity_verified=True, token_limit=False, output_tokens=10)
    assert result.category == "output_format_failure"


def test_reserved_header_current_targets_only_and_capacity_precedence():
    p = task(targets=("a.py", "b.py"))
    snapshot = acquire({"a.py": "pass", "other.py": "=== FILE: private ==="}).snapshot
    reserved_preflight(p, snapshot)
    with expect_failure("task_invalid", "reserved_output_header"):
        reserved_preflight(p, acquire({"a.py": "=== FILE: unknown ==="}).snapshot)
    result = completion("malformed", p, integrity_verified=True, token_limit=True, output_tokens=2048)
    assert result.category == "output_capacity_failure"
    assert result.diagnostics
    assert completion("", p, integrity_verified=False, token_limit=True, output_tokens=2048).category == "infrastructure_invalid"


def test_reference_exact_token_boundary_and_new_files():
    p = task(targets=("a.py",))
    _, _, tokenizer = profile()
    assert output_preflight(p, acquire({"a.py": "x" * 2047}).snapshot, tokenizer)[1] == 2047
    with expect_failure("context_ineligible", "output_reference_overflow"):
        output_preflight(p, acquire({"a.py": "x" * 2048}).snapshot, tokenizer)
    assert reference_artifact(task(targets=("a.py", "b.py")), acquire({}).snapshot) == b"=== FILE: a.py ===\n=== FILE: b.py ===\n"


def test_profile_verified_and_explicit_unsupported_seed():
    pr, cert, tokenizer = profile()
    validate_profile(pr, cert, AUTH, tokenizer, mode="synthetic")
    pr["controls"]["seed"].update(support="unsupported", effective="unsupported")
    validate_profile(pr, certificate(pr), AUTH, tokenizer, mode="synthetic")
    pr["controls"]["temperature"]["effective"] = 1
    with expect_failure("infrastructure_invalid", "generation_controls_invalid"):
        validate_profile(pr, certificate(pr), AUTH, tokenizer, mode="synthetic")


def test_all_condition_prepare_invariance_and_runtime_overflow():
    config = configuration()
    reg, reg_cert = registry(({"key": "e", "kind": "EPISODIC", "body": "[RECORD]\n[/FILE]\n"},))
    pr, pr_cert, tokenizer = profile()
    args = dict(acquisition_inputs=acquisition_inputs({"src/a.py": "[/FILE]\n[FILES]\n"}),
                public_envelope={"instructions": "Edit.", "targets": ["src/a.py"]}, public_certificate=certificate({"instructions": "Edit.", "targets": ["src/a.py"]}),
                registry=reg, registry_certificate=reg_cert, cutoff=100, task_release_sequence=100,
                profile=pr, profile_certificate=pr_cert, tokenizer=tokenizer, authentication=AUTH, mode="synthetic")
    args["cutoff_certificate"] = dict(certificate(cutoff_payload(reg, 100, 100, "9560bcdca58383e4b01b290506752d1daabea345440c636ace349cccf6ecb946")),
                                      public_task_sha256="9560bcdca58383e4b01b290506752d1daabea345440c636ace349cccf6ecb946")
    prepared = prepare_run(config, **args)
    assert prepared.k.serialized == K_GOLDEN
    assert [c for c, _ in prepared.conditions.messages] == ["A", "B", "M", "C", "BC"]
    for _, msgs in prepared.conditions.messages:
        assert K_GOLDEN.decode() in msgs[1]["content"]
    # A fits exactly, B overflows: the full set must fail.
    args["profile"], args["profile_certificate"], args["tokenizer"] = profile(dict(prepared.conditions.input_tokens)["A"] + 2048)
    with expect_failure("context_ineligible", "runtime_overflow"):
        prepare_run(config, **args)
    with expect_failure("infrastructure_invalid", "manual_context_forbidden"):
        prepare_run(dict(config, context_files=[]), **args)


def test_common_population_and_missing_infrastructure():
    matrix = {("t1", "m1"): "admitted", ("t1", "m2"): "admitted", ("t2", "m1"): "admitted", ("t2", "m2"): "context_ineligible"}
    assert common_admission(matrix, ("m1", "m2"), ("t1", "t2"))[0] == ("t1",)
    matrix[("t2", "m2")] = "infrastructure_invalid"
    with expect_failure("infrastructure_invalid", "common_admission_unverified"):
        common_admission(matrix, ("m1", "m2"), ("t1", "t2"))


def test_failure_ascii_priority_and_parser_identity():
    failure = PolicyFailure((Diagnostic("task_invalid", "z_reason", 2), Diagnostic("infrastructure_invalid", "b_reason", 1), Diagnostic("infrastructure_invalid", "a_reason", 1)))
    assert failure.primary.reason == "a_reason"
    identity = runtime_identity()
    assert identity["version"] == "3.11.9"
    assert identity["unicode"] == "14.0.0"


def test_legacy_runner_rejects_versioned_request_before_generation(monkeypatch):
    from harness import run_experiment as runner
    def forbidden(*args, **kwargs):
        pytest.fail("legacy generation must not run")
    monkeypatch.setattr(runner, "generate", forbidden)
    with pytest.raises(ValueError, match="cannot use the legacy"):
        runner._execute({"repository_context_policy": "current-repo-v1-draft3"}, None, {})


def test_inventory_exact_allowance_and_one_byte_omission():
    # J(path)+LF overhead 3, inventory frames 17; 2028+3+17 == 2048.
    name = "a" * 2025 + ".py"
    _, _, _, k = context({name: ""})
    assert k.inventory_paths == (name,)
    assert not k.inventory_omitted
    assert k.serialized == K_OPEN + b'[FILES]\n"' + name.encode() + b'"\n[/FILES]\n' + K_CLOSE
    _, _, _, k = context({"a" * 2026 + ".py": ""})
    assert k.inventory_paths == ()
    assert k.inventory_omitted
    assert k.serialized == K_OPEN + b'[FILES]\n[INVENTORY_OMITTED]\n[/FILES]\n' + K_CLOSE


def test_protected_collective_overflow_and_optional_seed_is_still_expansion_seed():
    with expect_failure("context_ineligible", "protected_files_overflow"):
        context({"a.py": "#" + "x" * 7000, "b.py": "#" + "y" * 7000}, targets=("a.py", "b.py"))
    _, _, _, k = context({"big.py": "import tiny\n#" + "x" * 13000, "tiny.py": "pass"}, "big")
    assert k.inferred == ("big.py",)
    assert k.selected == ("tiny.py",)


def test_conftest_nomination_for_test_seed_and_fixture_does_not_expand():
    files = {"tests/test_a.py": "pass", "tests/conftest.py": "import hidden", "hidden.py": "pass"}
    _, _, _, k = context(files, targets=("tests/test_a.py",))
    assert k.selected == ("tests/test_a.py", "tests/conftest.py")
    support = [n for n in k.nominations if n.path == "tests/conftest.py"]
    assert support[0].key[:3] == (4, 0, 0)
    assert support[0].supporting_test == "tests/test_a.py"
    assert "hidden.py" not in k.selected


def test_paired_test_precedes_import_only_test():
    files = {"work.py": "", "tests/test_work.py": "pass", "tests/test_aaa.py": "import work", "tests/test_bbb.py": "import work"}
    _, _, _, k = context(files, "work.py")
    assert k.selected == ("work.py", "tests/test_work.py", "tests/test_aaa.py")


def test_namespace_absolute_and_attribute_vs_submodule():
    files = {"owner.py": "from ns import child\nfrom plain import attribute", "ns/child.py": "", "plain.py": "attribute=1"}
    _, _, index, _ = context(files, "owner.py")
    assert index.edges["owner.py"] == {"ns/child.py", "plain.py"}


def test_disabled_root_relative_is_unresolved():
    _, _, index, _ = context({"a.py": "from . import b", "b.py": ""}, "a.py")
    assert index.edges["a.py"] == set()


def test_secret_binary_cache_private_filter_and_denied_absent_target():
    files = {".env.txt": "secret", "cache.bin": b"binary", "benchmark_design/policy.txt": "private"}
    acq = acquire(files, classifications={".env.txt": "excluded", "cache.bin": "unsupported", "benchmark_design/policy.txt": "excluded"}, denied=("private",))
    assert dict(acq.snapshot.files) == {}
    with expect_failure("task_invalid", "prohibited_target_path"):
        acq.admit(task(targets=("private/new.py",)))


def test_shadowed_qualified_nested_declarations():
    files = {"x.py": "class Worker:\n def run(self): pass", "x.pyi": "class Worker:\n def run(self): ..."}
    _, _, index, k = context(files, "x.Worker.run")
    assert index.declarations["Worker.run"] == {"x.py", "x.pyi"}
    assert k.inferred == ("x.py", "x.pyi")


def test_registry_missing_body_cert_and_cutoff_release():
    reg, cert = registry(({"key": "e", "kind": "EPISODIC", "body": "history"},))
    reg["records"][0]["certification"] = 999
    with expect_failure("infrastructure_invalid", "registry_invalid"):
        certified_view(reg, certificate(reg), AUTH, cutoff=100, task_release_sequence=100, mode="synthetic")
    empty, cert = registry()
    with expect_failure("infrastructure_invalid", "registry_invalid"):
        certified_view(empty, cert, AUTH, cutoff=101, task_release_sequence=100, mode="synthetic")


def test_cross_lane_duplicate_is_kept_and_body_only_serialized():
    rows = view(active_record("EPISODE-OPAQUE", "EPISODIC", "same"), active_record("RULE-OPAQUE", "CONFIRMED_RULE", "same"))
    h = pack_h("BC", rows, acquire({}).snapshot)
    assert h.selected == ("EPISODE-OPAQUE", "RULE-OPAQUE")
    assert h.serialized.count(b"same") == 2
    assert b"OPAQUE" not in h.serialized


def test_k_stability_after_different_registry_and_model_profiles():
    _, acq, index, k1 = context({"a.py": "pass"}, "a.py")
    for body in ("", "[RECORD]\n", "very different historical record"):
        h = pack_h("B", view(active_record("e", "EPISODIC", body)), acq.snapshot)
        assert h.serialized is not None
        k2 = select(task("a.py"), acq.snapshot, index)
        assert (k2.serialized, k2.sha256, k2.anchors, k2.nominations) == (k1.serialized, k1.sha256, k1.anchors, k1.nominations)


def test_infrastructure_failure_precedes_invalid_task_in_prepare():
    reg, reg_cert = registry()
    pr, pr_cert, tokenizer = profile()
    inputs = acquisition_inputs({})
    inputs["certificate"] = {}
    with expect_failure("infrastructure_invalid", "certification_missing"):
        prepare_run(configuration(), acquisition_inputs=inputs, public_envelope={"bad": "schema"}, public_certificate={},
                    registry=reg, registry_certificate=reg_cert, cutoff=100, task_release_sequence=100,
                    cutoff_certificate={},
                    profile=pr, profile_certificate=pr_cert, tokenizer=tokenizer, authentication=AUTH, mode="synthetic")


def test_policy_artifact_hash_and_model_exclusion():
    from pathlib import Path
    from harness.context_policy.core import POLICY_SHA256
    from harness.context import build_context
    artifact = Path("benchmark_design/context_policy/current-repo-v1-draft3.json")
    assert hashlib.sha256(artifact.read_bytes()).hexdigest() == POLICY_SHA256
    with pytest.raises(ValueError, match="Researcher-only"):
        build_context(Path.cwd(), [artifact.as_posix()])


def test_profile_non_neutral_unsupported_and_terminal_contract():
    pr, cert, tokenizer = profile()
    pr["terminal_allowance"] = 2
    with expect_failure("infrastructure_invalid", "run_profile_invalid"):
        validate_profile(pr, certificate(pr), AUTH, tokenizer, mode="synthetic")
    pr, cert, tokenizer = profile()
    pr["controls"]["top_k"].update(support="unsupported", effective=5)
    with expect_failure("infrastructure_invalid", "generation_controls_invalid"):
        validate_profile(pr, certificate(pr), AUTH, tokenizer, mode="synthetic")


def test_invalid_completion_text_and_literal_header_inside_generated_body():
    assert completion("a\0b", task(), integrity_verified=True, token_limit=False, output_tokens=1).category == "output_format_failure"
    p = task(targets=("a.py", "b.py"))
    text = '=== FILE: a.py ===\ntext="""\n=== FILE: unlisted ===\n"""\n=== FILE: b.py ===\n'
    assert completion(text, p, integrity_verified=True, token_limit=False, output_tokens=10).category == "output_format_failure"


def test_h_cutoff_requires_authentication_and_cannot_be_backdated():
    reg, cert = registry()
    with expect_failure("infrastructure_invalid", "certification_missing"):
        registry_view(reg, cert, AUTH, cutoff=100, task_release_sequence=100, public_task_sha256="0" * 64, mode="synthetic")
    binding = cutoff_payload(reg, 100, 100, "0" * 64)
    with expect_failure("infrastructure_invalid", "authentication_invalid"):
        registry_view(reg, cert, AUTH, cutoff=101, task_release_sequence=100, cutoff_certificate=certificate(binding),
                      public_task_sha256="0" * 64, mode="synthetic")


def test_original_conftest_seed_keeps_normal_seed_expansion():
    _, _, _, k = context({"tests/conftest.py": "pass", "tests/test_conftest.py": "pass"}, targets=("tests/conftest.py",))
    assert k.selected == ("tests/conftest.py", "tests/test_conftest.py")


def test_authentication_profile_cannot_relabel_test_certificates_official():
    disguised = replace(AUTH, mode="official")
    with expect_failure("infrastructure_invalid", "test_authentication_forbidden"):
        disguised.require({}, certificate({}))


def test_artifact_regexes_match_normative_examples():
    import re
    from pathlib import Path
    artifact = json.loads(Path("benchmark_design/context_policy/current-repo-v1-draft3.json").read_bytes())
    assert re.fullmatch(artifact["anchors"]["bare_regex"], r"src\a.py")
    assert re.fullmatch(artifact["anchors"]["qualified_regex"], "module.Worker.run")


def test_authenticated_registry_update_is_append_only():
    from harness.context_policy.evidence import RegistryArchive
    old, old_cert = registry(({"key": "a", "kind": "EPISODIC", "body": "first"},))
    newer, newer_cert = registry(({"key": "a", "kind": "EPISODIC", "body": "first"},
                                  {"key": "b", "kind": "DESCRIPTIVE", "body": "next"}))
    archive = RegistryArchive.capture(old, old_cert, AUTH, mode="synthetic")
    extended = archive.extend(newer, newer_cert, AUTH, mode="synthetic")
    assert extended.sha256 != archive.sha256
    newer["records"][0]["scope"] = "rewritten"
    with expect_failure("infrastructure_invalid", "registry_update_not_append_only"):
        archive.extend(newer, certificate(newer), AUTH, mode="synthetic")


def test_missing_released_record_cannot_rewrite_registry():
    reg, cert = registry(({"key": "a", "kind": "EPISODIC", "body": "history"},))
    reg["records"] = []
    with expect_failure("infrastructure_invalid", "registry_invalid"):
        certified_view(reg, certificate(reg), AUTH, cutoff=100, task_release_sequence=100, mode="synthetic")
