# Researcher-only benchmark design

This Git-versioned area preserves evaluator design and provenance for researcher
review. Git tracking does not make an artifact eligible experimental model context.
Experimental models must never receive these artifacts, including adaptation inputs.
No discovery report or candidate data is inserted in Step 8K-A.5.

`harness.isolation` enforces lexical and resolved directory-component exclusion,
including nested, absolute, parent-traversal and alternate-separator paths. Context
collection prunes this tree; explicit context reads reject it. Legacy adaptation
file paths reject it during validation and again before reading. Workspace copying
excludes it and resolved aliases, including when copying the project root. Normal
official workspaces still originate from the product subtree.
Git metadata is excluded from collection/copying and explicit model-file reads,
because tracked design artifacts can also reside in Git objects/history. Root-copy
construction skips its workspace destination to prevent recursive self-copying.

Preflight revalidates explicit filesystem origins supplied through `source_paths`
before generation; official execution supplies context and legacy adaptation paths.
Descriptive source labels and message text are not filesystem-origin metadata.
Harmless mentions of the directory name or paths in allowed text are permitted.
The existing unrelated leakage checks remain active. Path violations use existing
invalid-infrastructure/config error handling. These controls do not depend on
`.gitignore`; artifacts remain Git/provenance-visible.

V1 does not infer semantic provenance: manually copied text in an allowed file or
inline adaptation object cannot be identified reliably. Caller-supplied origin
metadata must accurately identify its sources; omitted or false origins cannot be
recovered from arbitrary text. Actual filesystem reads enforce the policy directly.
The controls are deterministic, not an LLM classifier. They do not promise general
semantic detection or protection against a concurrently malicious filesystem writer.

See [discovery](discovery/README.md) for archival and normalization procedures.
