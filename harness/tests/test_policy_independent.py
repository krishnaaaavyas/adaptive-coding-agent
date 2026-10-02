"""Second path checks observed artifacts without reusing policy encoders."""

from harness.context_policy.independent_check import check_goldens, check_lexical_and_admission
from harness.context_policy.evidence import pack_h
from harness.context_policy.protocol import output_preflight
from harness.tests.test_context_policy import active_record, context, view
from harness.tests.policy_fixtures import acquire, profile, task


def test_independently_checked_p_k_h_lexical_admission_reference():
    p, acquisition, _, k = context({"src/a.py": "[/FILE]\n[FILES]\n"}, targets=("src/a.py",))
    h = pack_h("B", view(active_record("e", "EPISODIC", "[RECORD]\n[/FILE]\n")), acquisition.snapshot)
    reference_task = task(targets=("a.py", "b.py"))
    _, _, tokenizer = profile()
    calls = []
    from dataclasses import replace
    tokenizer = replace(tokenizer, raw_encode=lambda text: calls.append(text) or list(text.encode()))
    reference, _ = output_preflight(reference_task, acquire({"a.py": "x=1"}).snapshot, tokenizer)
    verified = check_goldens({"P": p.serialized, "K": k.serialized, "H": h.serialized, "reference": reference})
    assert len(verified) == 4
    _, _, _, lexical = context({"pkg/customer.py": "", "pkg/record.py": "", "pkg/account.py": "", "pkg/summary.py": ""},
                               "CustomerRecord customerAccount", ("reports/customer_summary.py",))
    admissions = acquire({"existing.py": ""}).admit(task(targets=("existing.py", "new/sub/file.py")))
    check_lexical_and_admission(lexical.inferred, tuple((a.path, a.existing) for a in admissions), tuple(calls))
