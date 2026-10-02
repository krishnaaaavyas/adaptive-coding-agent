"""Structured audit record; never appended to model-facing P/K/H."""

from .core import POLICY_ID, POLICY_SHA256, SYSTEM, canonical_json, digest, runtime_identity
from .protocol import token_count
from .selector import file_block


def provenance(task, acquisition, index, configuration, k, view, conditions, profile, tokenizer):
    snapshot = acquisition.snapshot
    files = []
    for p, block_bytes, content_bytes, content_hash in k.contributions:
        files.append({"path": p, "raw_sha256": snapshot.raw_hashes[p], "raw_bytes": snapshot.raw_sizes[p],
                      "normalized_sha256": content_hash, "normalized_bytes": content_bytes,
                      "characters": len(snapshot.files[p]), "block_bytes": block_bytes,
                      "framing_bytes": block_bytes - content_bytes,
                      "standalone_block_tokens": token_count(tokenizer.raw_encode, file_block(p, snapshot.files[p]).decode())})
    return {
        "policy_id": POLICY_ID, "policy_sha256": POLICY_SHA256, "configuration_sha256": digest(canonical_json(configuration)),
        "parser_runtime": runtime_identity(), "snapshot_sha256": snapshot.identity,
        "acquisition_receipt_sha256": acquisition.identity, "P_sha256": task.sha256, "P_bytes": len(task.serialized),
        "protected": list(k.protected), "inferred": list(k.inferred), "selected": list(k.selected),
        "anchors": [{"path": a.path, "rank": a.key[0], "field_location": list(a.key[1]), "path_sort_bytes_hex": a.key[2].hex(),
                     "protected": a.protected, "reason": a.reason, "occurrence": a.occurrence,
                     "metadata": dict(a.metadata)} for a in k.anchors],
        "nominations": [{"path": n.path, "priority": n.key[0], "originating_seed_index": n.key[1], "subrank": n.key[2],
                         "reason": n.reason, "seed": n.seed, "supporting_test": n.supporting_test} for n in k.nominations],
        "files": files, "K_sha256": k.sha256, "K_bytes": len(k.serialized), "K_characters": len(k.serialized.decode()),
        "budget_skips": [list(row) for row in k.skipped], "inventory_paths": list(k.inventory_paths),
        "inventory_omitted": k.inventory_omitted, "file_truncation": "none",
        "index_diagnostics": index.diagnostics, "registry_view_sha256": view.identity, "ledger_root": view.ledger_root,
        "historical_cutoff": view.cutoff, "historical_exclusions": [list(row) for row in view.excluded],
        "historical_records": [{"key": r.key, "kind": r.kind, "body_sha256": r.body_sha256, "availability": r.availability,
                                "metadata_sha256": r.metadata_sha256} for r in view.records],
        "H": [{"condition": condition, "sha256": h.sha256, "bytes": len(h.serialized), "characters": len(h.serialized.decode()),
               "selected": list(h.selected), "skipped": [list(row) for row in h.skipped], "duplicates": [list(row) for row in h.duplicates],
               "exact_overlap": [list(row) for row in h.overlaps], "semantic_overlap": "externally certified or unknown",
               "lanes": [list(row) for row in h.lane_bytes]} for condition, h in conditions.adaptation],
        "inputs": [{"condition": condition, "system_sha256": digest(SYSTEM.encode()), "user_sha256": digest(messages[1]["content"].encode()),
                    "total_content_bytes": sum(len(m["content"].encode()) for m in messages),
                    "rendered_tokens": dict(conditions.input_tokens)[condition]} for condition, messages in conditions.messages],
        "run_profile_sha256": conditions.profile_sha256, "runtime_profile": profile,
        "reference_sha256": digest(conditions.reference_bytes), "reference_bytes": len(conditions.reference_bytes),
        "reference_tokens": conditions.reference_tokens, "generation_reserve": 2048,
        "coverage": {"eligible_files": len(snapshot.files), "selected_files": len(k.selected),
                     "eligible_content_bytes": sum(len(s.encode()) for s in snapshot.files.values()),
                     "selected_content_bytes": sum(row[2] for row in k.contributions),
                     "whole_eligible_repository": set(k.selected) == set(snapshot.files)},
    }
