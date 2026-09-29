# Frozen adaptation conditions for future Protocol-v2 experiments

This document defines the Step-7 adaptation treatments for future benchmark
experiments. It does not reinterpret or modify the original pilot experiments.
Conditions D and E remain reserved for later weight-adaptation work.

Structured configs declare adaptation_schema "1" and an inline adaptation
object with memory, evidence, and rule components. Omitted inactive components
and explicit null values are equivalent. Values are strings or lists of
strings. Inline content is covered by the config's exact-byte SHA-256.
Historical configs without adaptation_schema and adaptation remain legacy.

## Conditions

- A — Fresh: no memory, evidence, or rule.
- B — Episodic Memory: one or more deliberately selected relevant historical
  experiences and no evidence or rule. An episode may contain prior
  task/context, implementation or behavior, developer correction, and corrected
  outcome. It remains an episode and must not contain an explicit generalized
  lesson or rule. The relevant memory is assumed to have already been selected;
  retrieval quality is not tested.
- M — Information-Matched Evidence: descriptive evidence representing the same
  underlying convention information as C, with no memory or rule. It is not
  normative and is never labeled as a rule or convention.
- C — Confirmed Rule: one concise generalized repository rule and no episode or
  evidence. This is a human-confirmed/oracle rule, not a rule autonomously
  learned by the agent.
- BC — Episodic Memory plus Confirmed Rule: the B-style episode and C-style
  confirmed rule, with no M evidence.

Lexical validation rejects obvious generalized-rule phrases in B and obvious
normative markers in M. These checks are safety rails, not semantic judges.
They cannot prove that memory is purely episodic or that M and C communicate
equivalent information.

## Information matching and budgets

Benchmark authors are responsible for making M and C communicate the same
underlying facts without extra task-specific hints. Their adaptation text
should have approximately similar token length, targeting no more than a
plus-or-minus 20 percent difference. Step 7 does not add a tokenizer or LLM
judge and cannot prove semantic or token equivalence.

For a fixed model and task, all compared conditions use the same model context
limit, generation-token allowance, temperature and inference settings, tool
availability, repository-context policy, and retry policy. BC receives no
larger budget merely because it has two adaptation sources. A is not padded or
truncated to equal adaptation-token counts. A single run cannot prove
cross-condition equality; benchmark generation and analysis must enforce it.
Unsupported per-run budget overrides in structured configs are rejected rather
than silently changing the frozen harness settings.

## Interpretation

- A to B estimates the effect of concrete previous experience.
- A to M estimates the effect of relevant distilled descriptive information.
- M to C estimates the effect of presenting approximately equivalent
  information as a confirmed normative rule.
- A to C estimates the total confirmed-rule effect versus Fresh.
- B to BC estimates incremental confirmed-rule benefit with memory present.
- C to BC estimates incremental episodic-memory benefit with a rule present.

B versus C alone does not prove either representation is fundamentally
superior. C success does not demonstrate autonomous rule induction. B success
does not demonstrate retrieval quality. Convention compliance without target
and regression success is not improvement. Protocol-v2 overall success remains
target-task pass AND regression pass AND convention pass.
