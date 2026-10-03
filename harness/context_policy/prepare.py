"""Versioned harness integration entry point. Preparation never generates.

All five conditions are prepared together. The legacy pilot runner cannot
execute a draft3 request. Actual serving/evaluation remains a separate future
authorized operation after external identity and certification verification.
"""

from dataclasses import dataclass
import json

from .boundary import Acquisition, public_task
from .core import POLICY_ID, canonical_json, digest, fail, verify_parser
from .evidence import registry_view
from .index import PythonIndex
from .protocol import output_preflight, treatments, validate_profile
from .selector import select


@dataclass(frozen=True)
class PreparedRun:
    task: object
    admission: tuple
    k: object
    historical_view: object
    conditions: object
    acquisition_identity: str
    provenance_bytes: bytes
    provenance_sha256: str


def prepare_run(configuration, *, acquisition_inputs, public_envelope, public_certificate,
                registry, registry_certificate, cutoff, task_release_sequence,
                cutoff_certificate,
                profile, profile_certificate, tokenizer, authentication, mode="official", run_identity=None):
    """Execute normative phases; accept no filesystem paths or manual K/H.

    Certification trust roots and tokenizer callbacks are external interfaces.
    This function has no completion, evaluator or retry interface.
    """
    verify_parser()
    if not isinstance(configuration, dict):
        fail("infrastructure_invalid", "configuration_invalid", 1)
    if any(key in configuration for key in ("context_files", "repository_context", "memory_file", "rule_file", "adaptation")):
        fail("infrastructure_invalid", "manual_context_forbidden", 1)
    if configuration.get("policy_id") != POLICY_ID:
        fail("infrastructure_invalid", "configuration_invalid", 1)
    # Capture signed metadata once; later caller mutation cannot change admission.
    try:
        configuration = json.loads(canonical_json(configuration))
        registry = json.loads(canonical_json(registry))
        profile = json.loads(canonical_json(profile))
        run_identity = None if run_identity is None else json.loads(canonical_json(run_identity))
    except (ValueError, UnicodeError, TypeError):
        fail("infrastructure_invalid", "metadata_invalid", 1)
    # Phase 1: validate all authenticated infrastructure before task admission.
    acquisition = Acquisition.verify(**acquisition_inputs, configuration=configuration,
                                     auth=authentication, mode=mode)
    index = PythonIndex(acquisition.snapshot, configuration)
    view = registry_view(registry, registry_certificate, authentication, cutoff=cutoff,
                         task_release_sequence=task_release_sequence, cutoff_certificate=cutoff_certificate,
                         public_task_sha256=cutoff_certificate.get("public_task_sha256") if isinstance(cutoff_certificate, dict) else None,
                         mode=mode)
    validate_profile(profile, profile_certificate, authentication, tokenizer, mode=mode)
    # Phase 2.
    task = public_task(public_envelope, public_certificate, authentication, mode=mode)
    if task.sha256 != cutoff_certificate["public_task_sha256"]:
        fail("infrastructure_invalid", "cutoff_task_mismatch", 1)
    admission = acquisition.admit(task)
    # Phases 3, 4 and 5. No post-failure progression or model invocation.
    k = select(task, acquisition.snapshot, index)
    reference = output_preflight(task, acquisition.snapshot, tokenizer)
    conditions = treatments(task, acquisition.snapshot, k, view, profile, tokenizer, reference)
    from .provenance import provenance
    audit = canonical_json(provenance(task, acquisition, index, configuration, k, view, conditions, profile, tokenizer,
                                     run_identity=run_identity))
    return PreparedRun(task, admission, k, view, conditions, acquisition.identity, audit, digest(audit))
