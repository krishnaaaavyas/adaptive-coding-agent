# Normalization procedure — version 1

The raw audit remains unchanged. Normalization creates a separate derived artifact;
omissions follow these rules, never outcome-driven judgment. Read raw material only
as a researcher, never in an experimental model run.

1. Archive exact source bytes and compute SHA-256 before transformation.
2. Preserve stable source IDs and source order. Transcribe factual candidate fields
   and negative/rejected observations into the closed schema. Retain evidence
   locations, origin, CRISP/PATTERN-LIKE/UNCLEAR character, discovery confidence,
   factual repository rationale/future-preservation rationale, distinct occurrences,
   historical/possible overlap and discovery concerns. Do not infer missing facts;
   use null or empty evidence arrays and flag uncertainty in discovery concerns.
3. Remove rankings, priority, strongest/best-candidate wording, recommendations,
   evidence-role or Selection/Confirmation suitability suggestions, experimental
   usefulness, model-difficulty/adaptation-gain speculation and LoRA usefulness.
   Exclude cross-repository prose whose only purpose is editorial prioritization.
   Factual overlap relationships are allowed. Free-text fields follow the same rules
   as structured fields; a closed schema alone cannot police editorial prose.
4. Record omissions by source location and rule category in the manifest; do not
   reproduce excluded editorial wording in normalized input. Review ambiguous
   factual/editorial mixtures separately instead of substituting new judgments.
5. Validate the record, serialize canonically, hash exact bytes, record versions and
   creation status in the manifest, then review/freeze. Never overwrite raw bytes.

# Later Step 8K-B adaptation relevance procedure (recorded only)

Adaptation relevance asks whether repository experience supplies information that
matters for a future task. It concerns information value, not model difficulty.

1. Author the held-out task prompt first, deliberately omitting the candidate
   convention. Freeze wording before evaluating adaptation relevance.
2. Consider a competent developer who normally understands the language, framework
   and domain, can inspect the repository context the eventual experimental
   condition allows, and lacks the prior convention exposure/history being tested.
3. Determine whether general engineering knowledge and the task already force or
   strongly default to the same behavior.
4. FAIL if a reasonable repo-unfamiliar/generalist implementation already matches
   without repository-specific experience. PASS if experience supplies information
   needed to choose among multiple otherwise reasonable implementations. UNCLEAR
   if hidden assumptions or subjective taste determine the answer; require review.

Absence from the task prompt alone does not establish relevance: explicitly consider
whether allowed repository context already makes the behavior unambiguous. Do not
run a model or ask whether Qwen/GPT will fail. No candidate judgments, filtering,
merging, independence assessment, tasks, scorers or evidence-role assignments are
performed here.
