# Evaluator defect policy

This policy is frozen for Protocol-v2 experiment handling.

1. Historical result JSON files are never edited to repair a defect.
2. A discovered defect is recorded separately in the append-only defect ledger.
3. All conditions for the affected task and version are quarantined,
   independent of observed outcome.
4. Selective exclusion based on model performance is forbidden.
5. Record the defect ID, discovery date, affected task, affected version,
   relevant hashes and run IDs where known, reason, and resolution.
6. A repaired evaluator or task receives new version and hash provenance.
7. If retained, all compared conditions are rerun under the repaired version.
8. Superseded runs remain historical or development evidence but are excluded
   from the corrected comparison.
9. Answer or held-out leakage contaminates that task lineage; removing the leak
   does not automatically restore untouched status.
10. Replacement and exclusion decisions are based on defect properties, not
    experimental outcome.

## Append-only ledger

harness/defects.jsonl is append-only. Each nonempty line is one JSON object
with this schema:

- defect_id: unique stable string.
- discovered_at_utc: timezone-aware UTC ISO-8601 string.
- affected_task: task identifier.
- affected_version: evaluator or task version, or null when unknown.
- affected_hashes: object mapping provenance labels to SHA-256 values.
- affected_run_ids: array of known run UUID strings.
- reason: concise description of the defect and contamination risk.
- resolution: concise disposition, including quarantine, repair, rerun, or
  exclusion status.

Unknown optional facts are represented by null or an empty collection rather
than guessed. Existing ledger lines are never rewritten or deleted.
