# Step 8K-A record mapping

This transformation uses normalization schema/procedure version 1 without changing
either contract. The manifest remains draft pending independent verification and
the documented review/commit freeze workflow. The raw artifact preserves exact
external bytes, including original line endings and editorial language.
Local Git attributes disable text conversion for raw artifacts and retain LF
serialization for normalized JSON/manifest files. This repository enables
`core.autocrlf`; explicit attributes preserve byte-based provenance across Git.

- Candidate IDs/order and inventory fields come from sections 3–5. `short_name`
  uses the explicitly named short-name column in section 9. Repository, origin,
  character, confidence and evidence-group counts agree between those sections.
- Observed behavior, historical overlap (including qualifiers), recurrence/count
  text and discovery concerns are transcribed without rewriting their claims.
- `evidence` begins with the concrete-evidence bullets in source order. Its final
  two strings retain the separately labeled repository-specificity and factual
  future-preservation rationales. Array length therefore is **not** evidence count;
  the original evidence-group count remains in `distinct_occurrences`.
- `possible_overlaps` starts with the inventory's full overlap wording. Each
  applicable section-6 relationship row follows as a labeled string retaining
  original members, relationship type and rationale. Rows are repeated for their
  explicitly referenced candidate IDs, in source order. This preserves all 24
  provisional relationships without merge or independence decisions.
- `discovery_concerns` starts with the inventory concern. Applicable concentrated
  evidence notes, repository support limitations and report-wide discovery
  limitations from section 10 follow with labels; their uncertainty is preserved.
- Negative IDs/order, repository, observed idea, NOT ELEVATED decision, reason and
  evidence come from section 8. The more detailed inventory-table reason follows
  in `reason`; its observation wording follows in `evidence`. Thus both versions
  of each of the 21 observations remain traceable without adding observations.
- Labels identify source field context; they add no product facts. Markdown inside
  transcribed fields is retained. Parsing uses normalized newlines in memory;
  JSON is UTF-8 with sorted keys, two-space indentation and a final LF.

Section 6, raw line 877's editorial specificity/prioritization sentence is omitted
under the frozen procedure and recorded in the manifest. General audit workflow,
Git-state metadata, duplicate candidate-summary rows, and the next-step boundary
are archival context rather than additional normalized candidate records. No
candidate is removed, merged, ranked, assigned a role, or judged for suitability.
