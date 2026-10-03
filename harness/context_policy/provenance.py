"""Structured audit record; never appended to model-facing P/K/H."""

import json

from .core import (POLICY_ID, POLICY_SHA256, SYSTEM, PolicyFailure, canonical_json,
                   digest, fail, implementation_identity, runtime_identity, u)
from .evidence import record_block
from .protocol import token_count
from .selector import file_block


SCHEMA_ID = "current-repo-v1-provenance-v2"


def optional_tokens(tokenizer, text):
    """Diagnostic measurement cannot introduce a new treatment admission gate."""
    try:
        return {"tokens": token_count(tokenizer.raw_encode, text), "status": "measured"}
    except PolicyFailure as exc:
        return {"tokens": None, "status": "unavailable", "reason": exc.primary.reason}


def provenance(task, acquisition, index, configuration, k, view, conditions, profile, tokenizer, *, run_identity=None):
    snapshot = acquisition.snapshot
    receipt = json.loads(acquisition.receipt_bytes)
    # These commits describe separate implementation/product repositories. They
    # cannot be recovered from immutable snapshot bytes. A release/acquisition
    # workflow supplies and certifies them externally; missing values stay null.
    external_identity = run_identity if isinstance(run_identity, dict) else {}
    files = []
    for p, block_bytes, content_bytes, content_hash in k.contributions:
        files.append({"path": p, "raw_sha256": snapshot.raw_hashes[p], "raw_bytes": snapshot.raw_sizes[p],
                      "normalized_sha256": content_hash, "normalized_bytes": content_bytes,
                      "characters": len(snapshot.files[p]), "block_bytes": block_bytes,
                      "framing_bytes": block_bytes - content_bytes,
                      "standalone_block_tokens": token_count(tokenizer.raw_encode, file_block(p, snapshot.files[p]).decode())})
    return {
        "schema_id": SCHEMA_ID, "stage": "prepared",
        "implementation": implementation_identity(),
        "implementation_repository_commit": external_identity.get("implementation_repository_commit"),
        "product_repository_commit": external_identity.get("product_repository_commit"),
        "repository_commit_source": "external-run-identity" if external_identity else "unavailable",
        "external_run_identity": run_identity,
        "policy_id": POLICY_ID, "policy_sha256": POLICY_SHA256, "configuration_sha256": digest(canonical_json(configuration)),
        "public_task": {
            "raw_encoding": "J(decoded-input-envelope-before-normalization)",
            "raw_sha256": task.raw_sha256, "raw_bytes": len(task.raw_serialized), "raw_hex": task.raw_serialized.hex(),
            "canonical_sha256": task.sha256, "canonical_bytes": len(task.serialized), "canonical_hex": task.serialized.hex(),
            "transport_sha256": None, "transport_bytes": None,
        },
        "product_manifest_sha256": receipt["product_manifest_sha256"],
        "deny_manifest_sha256": receipt["deny_manifest_sha256"],
        "existence_index_sha256": receipt["existence_index_sha256"],
        "acquisition_identity": receipt["acquisition_identity"],
        "acquisition_receipt_hex": acquisition.receipt_bytes.hex(),
        "parser_runtime": runtime_identity(), "snapshot_sha256": snapshot.identity,
        "acquisition_receipt_sha256": acquisition.identity, "P_sha256": task.sha256, "P_bytes": len(task.serialized),
        "protected": list(k.protected), "inferred": list(k.inferred), "selected": list(k.selected),
        "anchors": [{"path": a.path, "rank": a.key[0], "field_location": list(a.key[1]), "path_sort_bytes_hex": a.key[2].hex(),
                     "protected": a.protected, "reason": a.reason, "occurrence": a.occurrence,
                     "metadata": dict(a.metadata), "resolution_reasons": [dict(r) for r in a.resolution_reasons]} for a in k.anchors],
        "nominations": [{"path": n.path, "priority": n.key[0], "originating_seed_index": n.key[1], "subrank": n.key[2],
                         "reason": n.reason, "seed": n.seed, "supporting_test": n.supporting_test} for n in k.nominations],
        "files": files, "K_sha256": k.sha256, "K_bytes": len(k.serialized), "K_characters": len(k.serialized.decode()),
        "K_hex": k.serialized.hex(), "K_standalone_tokenization": optional_tokens(tokenizer, k.serialized.decode()),
        "K_unused_bytes": 12288 - len(k.serialized),
        "budget_skips": [list(row) for row in k.skipped], "inventory_paths": list(k.inventory_paths),
        "inventory_omitted": k.inventory_omitted, "file_truncation": "none",
        "inventory": {"present": bool(k.inventory_serialized), "bytes": len(k.inventory_serialized),
                      "sha256": digest(k.inventory_serialized), "hex": k.inventory_serialized.hex(),
                      "allowance": k.inventory_allowance, "unused_allowance": k.inventory_allowance - len(k.inventory_serialized),
                      "paths": list(k.inventory_paths), "omitted": k.inventory_omitted},
        "structural_resolution": {
            "providers": dict(sorted(index.providers.items())),
            "module_routes": {alias: [{"owned_module": r.base, "provider": r.provider, "root_prefixed": r.prefixed} for r in routes]
                              for alias, routes in sorted(index.routes.items())},
            "declaration_routes": {alias: reasons for alias, reasons in sorted(index.declaration_reasons.items())},
            "import_edges": {p: index.edge_reasons[p] for p in sorted(index.edge_reasons, key=u)},
        },
        "index_diagnostics": index.diagnostics, "registry_view_sha256": view.identity, "ledger_root": view.ledger_root,
        "registry_sha256": view.registry_sha256, "cutoff_binding_sha256": view.cutoff_binding_sha256,
        "first_public_release_sequence": view.first_public_release_sequence,
        "historical_cutoff": view.cutoff, "historical_exclusions": [list(row) for row in view.excluded],
        "historical_records": [{"key": r.key, "kind": r.kind, "body_sha256": r.body_sha256, "availability": r.availability,
                                "metadata_sha256": r.metadata_sha256, "body_bytes": len(r.body.encode()),
                                "block_bytes": len(record_block(r.body)), "block_sha256": digest(record_block(r.body))} for r in view.records],
        "H": [{"condition": condition, "sha256": h.sha256, "bytes": len(h.serialized), "characters": len(h.serialized.decode()),
               "hex": h.serialized.hex(), "unused_bytes": 4096 - len(h.serialized),
               "selected": list(h.selected), "skipped": [list(row) for row in h.skipped], "duplicates": [list(row) for row in h.duplicates],
               "exact_overlap": [list(row) for row in h.overlaps], "semantic_overlap": "externally certified or unknown",
               "lanes": [list(row) for row in h.lane_bytes],
               "record_order": [r.key for kind in ({"A": (), "B": ("EPISODIC",), "M": ("DESCRIPTIVE",),
                                                    "C": ("CONFIRMED_RULE",), "BC": ("EPISODIC", "CONFIRMED_RULE")}[condition])
                                for r in sorted((r for r in view.records if r.kind == kind), key=lambda r: (-r.availability, r.body_sha256, u(r.key)))],
               "lane_allocations": [{"kind": kind, "limit": 2048 if condition == "BC" else 4096,
                                     "owned_bytes": dict(h.lane_bytes).get(kind, 0),
                                     "unused_bytes": (2048 if condition == "BC" else 4096) - dict(h.lane_bytes).get(kind, 0)}
                                    for kind in ({"A": (), "B": ("EPISODIC",), "M": ("DESCRIPTIVE",),
                                                  "C": ("CONFIRMED_RULE",), "BC": ("EPISODIC", "CONFIRMED_RULE")}[condition])]
              } for condition, h in conditions.adaptation],
        "inputs": [{"condition": condition, "system_sha256": digest(SYSTEM.encode()), "user_sha256": digest(messages[1]["content"].encode()),
                    "total_content_bytes": sum(len(m["content"].encode()) for m in messages),
                    "rendered_tokens": dict(conditions.input_tokens)[condition]} for condition, messages in conditions.messages],
        "run_profile_sha256": conditions.profile_sha256, "runtime_profile": profile,
        "reference_sha256": digest(conditions.reference_bytes), "reference_bytes": len(conditions.reference_bytes),
        "reference_tokens": conditions.reference_tokens, "generation_reserve": 2048,
        "common_admission": None, "matching_manifest": None, "completion": None,
        "coverage": {"eligible_files": len(snapshot.files), "selected_files": len(k.selected),
                     "eligible_content_bytes": sum(len(s.encode()) for s in snapshot.files.values()),
                     "selected_content_bytes": sum(row[2] for row in k.contributions),
                     "whole_eligible_repository": set(k.selected) == set(snapshot.files)},
    }


def completion_provenance(result):
    """Observed post-generation facts only; absence is not a zero/stop claim."""
    return {
        "raw_sha256": result.raw_sha256,
        "raw_bytes": None if result.raw_bytes is None else len(result.raw_bytes),
        "raw_hex": None if result.raw_bytes is None else result.raw_bytes.hex(),
        "normalized_sha256": result.normalized_sha256,
        "normalized_bytes": None if result.normalized_bytes is None else len(result.normalized_bytes),
        "normalized_hex": None if result.normalized_bytes is None else result.normalized_bytes.hex(),
        "finish_reason": result.finish_reason, "output_tokens": result.output_tokens,
        "terminal_token_accounting": None if result.terminal_accounting_bytes is None else json.loads(result.terminal_accounting_bytes),
        "classification_inputs": {"integrity_verified": result.integrity_verified, "verified_token_limit": result.token_limit},
        "category": result.category, "format_diagnostics": list(result.diagnostics),
        "artifacts": [{"path": p, "bytes": len(content.encode()), "sha256": digest(content.encode())} for p, content in result.artifacts],
    }


def record_completion(prepared, result, *, common_admission=None, matching_manifest=None):
    """Return a new restricted audit record; never mutate prepared treatment.

    Population/matching certificates are external facts supplied at their own
    workflow stages. This function neither certifies them nor invokes a model.
    """
    if digest(prepared.provenance_bytes) != prepared.provenance_sha256:
        fail("infrastructure_invalid", "provenance_hash_mismatch", 1)
    audit = json.loads(prepared.provenance_bytes)
    audit.update(stage="completion_recorded", completion=completion_provenance(result),
                 common_admission=common_admission, matching_manifest=matching_manifest)
    return canonical_json(audit)
