# Scorer validation fixtures

These files are permanent adversarial inputs for validating deterministic
scorers. They are scorer tests, not benchmark tasks or evidence of model
adaptation. Each cases.json records the expected convention outcome.

The Fuzzy-3 v2 fixtures intentionally cover the task's two relevant
operations, create_comment and edit_comment. There is no passing
"normalization is not shared because it is not needed" boundary fixture:
the frozen task requires the same whitespace-and-case normalization in both
operations, and inferring when that behavior is semantically unnecessary
would require speculative functional analysis. The scorer therefore uses the
narrow, auditable structural boundary represented by these fixtures.

Known static-analysis limits are deliberate. Fuzzy-3 recognizes direct calls
to module functions or CommentService methods and direct string operations;
aliases, inherited helpers, decorators, and dynamic dispatch may produce false
negatives. It does not try to prove that a helper's return reaches persistence.
Explicit-2 recognizes direct Ok/Err terminal returns across common if branches;
delegated result factories and complex Python control flow may also produce
false negatives. It cannot infer the business meaning of arbitrary branches,
so functional target tests remain responsible for proving the returned
outcomes correspond to actual repository behavior. Those limits keep these
scorers focused on their frozen structural conventions.
