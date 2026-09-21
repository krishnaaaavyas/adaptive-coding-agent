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

Explicit-1 accepts ProjectRepository provenance only from a straightforward
constructor annotation importing that type or the frozen router wiring
ProjectService(ProjectRepository(...)). The receiving service attribute may be
renamed after provenance is established. Renamed unannotated dependencies
without equivalent explicit wiring intentionally fail; names and the presence
of a delete method are not evidence. Factory injection, container lookups,
helper-mediated delegation, and dynamic attribute access can produce false
negatives. It recognizes obvious direct database/session/engine calls and
constructors, not every possible persistence API.

Explicit-3 resolves direct UUID imports, straightforward aliases, qualified
uuid.UUID, and required Annotated UUID fields. Complex type aliases and custom
Pydantic field factories are outside its narrow static contract. It rejects
only the frozen internal-key names rather than all relationship fields ending
in _id.

Fuzzy-1 recognizes the frozen blank-content predicates based on strip, direct
private _validate_* calls, simple result assignments, and ordinary if gates.
Delegated predicates, complex boolean/data flow, and helper calls hidden behind
aliases can produce false negatives. It deliberately does not encode a comment
length limit or prove persistence behavior.

Fuzzy-2 recognizes direct or qualified Result/error construction and a simple
local assignment of the specific error before Err. It does not infer that a
branch represents a missing repository value, prove identifier propagation,
or follow delegated Result factories and complex control flow.
