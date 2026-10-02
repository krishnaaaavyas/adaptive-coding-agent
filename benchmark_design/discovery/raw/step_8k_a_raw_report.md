# STEP 8K-A — NATURAL CONVENTION DISCOVERY REPORT

## 1. AUDIT PRECONDITION

- **HEAD:** `66a7b94c47fa464b0e0b4f20f658efeefd62c238`
- **Working tree:** Clean before and after inspection.
- **Repositories inspected:** TaskFlow, OrderFlow, and SafeSync, independently and in that order.
- **Files inspected:** All tracked product source files, tests, package initializers, READMEs, dependency declarations, and available decision ledgers in those repositories.
- **Baseline verification:** No changes to OrderFlow or TaskFlow between `84e896e7551693a9da0142e297e6dda63af09edd` and current HEAD were reported by the scoped Git comparison.
- **Experimental areas avoided:** Results, experiment definitions/configurations, memory, rules, rubrics, scorers, scorer-validation fixtures, model outputs, benchmark notes, and previous candidate proposals.
- **Files modified:** NONE.
- **Files created:** NONE.
- **Tests or mutation probes run during this discovery:** NONE.
- **Model experiments:** NONE.

This report uses the current frozen product files as evidence. Earlier audit results are not used as discovery evidence.

## 2. DISCOVERY METHOD

I first traced each product’s supported workflows through its implementation and tests, then checked documentation for supporting intent. Cross-repository comparison followed completion of all three independent inspections.

Candidates were retained when their behavior recurred across operations, entities, boundaries, or behavioral expectations—and a future developer would reasonably need to preserve it.

Origin classifications describe the apparent source of the behavior:

- **PRODUCT-INVARIANT:** A product rule or observable contract.
- **IMPLEMENTATION-CONVENTION:** A recurring way the repository implements its work.
- **MIXED:** A product contract coupled to a particular recurring implementation approach.
- **UNCLEAR:** Insufficient evidence to separate those origins.

Evidence forms are distinguished as requested:

- **A:** Repeated implementation pattern.
- **B:** Repeated behavioral invariant.
- **C:** Single implementation supported by multiple tests or workflows.
- **D:** Isolated choice; normally not elevated.

**Evidence count** below means the number of listed evidence groups, not a count of independent implementations. Recurrence is stated separately. Parameterized cases are not counted as separate occurrences.

Historical overlap is assessed only against the historical TaskFlow concepts supplied in the request. **YES** identifies an independently observed match; **NO** means no match to that supplied list was identified. OrderFlow and SafeSync receive **UNCLEAR**, because their historical exposure was not established or investigated.

No candidates were ranked, assigned roles, or filtered for benchmark feasibility.

## 3. TASKFLOW INVENTORY

### TF-01 — Responsibilities follow the request-to-persistence path

**Repository:** TaskFlow  
**Origin:** IMPLEMENTATION-CONVENTION  
**Character:** PATTERN-LIKE  
**Confidence:** HIGH

**Observed behavior:** Routers assemble dependencies and translate service outcomes; services perform application work; repositories perform database operations. Both supported creation workflows follow this allocation.

**Concrete evidence:**

- [Project router](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/routers/projects.py) and [task router](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/routers/tasks.py): dependency construction and endpoint delegation.
- [ProjectService](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/services/project_service.py) and [TaskService](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/services/task_service.py): validation, model construction, and repository calls.
- [ProjectRepository](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/repositories/project_repository.py) and [TaskRepository](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/repositories/task_repository.py): querying and persistence.
- [README](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/README.md): explicitly describes these responsibilities.

**Repository specificity:** The allocation is demonstrated by both actual HTTP workflows, rather than inferred from directory names.

**Future preservation:** New supported endpoints would need to respect where application rules and persistence work currently reside.

**Distinct occurrences/evidence count:** A; two complete creation workflows; **4 evidence groups**.  
**Historical overlap:** YES.  
**Possible overlap with:** TF-02, TF-04, TF-06, OF-01.  
**Discovery concerns:** Only two routed workflows exist; this does not establish a universal architecture for unsupported subsystems.

### TF-02 — Expected service failures become Result values, then HTTP responses

**Repository:** TaskFlow  
**Origin:** IMPLEMENTATION-CONVENTION  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Services return `Ok` or `Err` for expected application outcomes. The router boundary converts successful models to DTOs and maps missing resources to 404 and validation errors to 422.

**Concrete evidence:**

- [Result types](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/core/result.py): `Ok`, `Err`, and `Result`.
- [ProjectService](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/services/project_service.py) and [TaskService](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/services/task_service.py): creation and tag-update outcomes.
- [Task router](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/routers/tasks.py): `handle_result`; the project router reuses it.
- [Project tests](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/tests/test_projects.py) and [task tests](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/tests/test_tasks.py): successful, validation-failure, and missing-project HTTP outcomes.

**Repository specificity:** The particular Result-to-HTTP contract recurs across both resource routes.

**Future preservation:** Changing expected failures into uncaught exceptions would bypass the established response mapping.

**Distinct occurrences/evidence count:** A/B; three service operations and two routes; **4 groups**.  
**Historical overlap:** YES.  
**Possible overlap with:** TF-01, TF-07, OF-10, SS-08.  
**Discovery concerns:** This applies to expected failures. Database errors and unsupported operations are not universally converted to `Err`.

### TF-03 — Response identity is distinct from persistence identity

**Repository:** TaskFlow  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Projects and tasks have integer database primary keys and separate UUID public identifiers. Response DTOs expose `public_id` and omit the internal primary key.

**Concrete evidence:**

- [Project model](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/models/project.py) and [task model](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/models/task.py): separate `id` and `public_id`.
- [Project DTO](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/dto/project_dto.py) and [task DTO](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/dto/task_dto.py): UUID response fields and explicit model conversion.
- Both test modules contain `test_public_id_is_a_uuid_not_internal_pk`, asserting response-field separation.

**Repository specificity:** This is a deliberate boundary across both exposed resource types.

**Future preservation:** New response representations should not accidentally expose database identifiers in place of public identifiers.

**Distinct occurrences/evidence count:** A/B; two model/DTO pairs and two response tests; **3 groups**.  
**Historical overlap:** YES.  
**Possible overlap with:** OF-08.  
**Discovery concerns:** The rule is about responses. Task creation still accepts an integer `project_id`; public UUIDs are not universal lookup keys.

### TF-04 — Creation validation is collected before persistence work

**Repository:** TaskFlow  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Each creation service delegates business validation to `_validate_create`, receives a list of messages, and returns a validation error before constructing or saving the entity. Task validation also precedes parent-project lookup.

**Concrete evidence:**

- `ProjectService._validate_create` and `create_project`: blank-name and length checks.
- `TaskService._validate_create` and `create_task`: blank-title and length checks before project lookup.
- [ValidationError](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/core/errors.py), `handle_result`, and blank-input HTTP tests preserve list-based validation reporting.

**Repository specificity:** The same service-level sequencing and error-list shape exist in both creation paths.

**Future preservation:** Additional creation rules should retain failure-before-write sequencing and compatible validation representation.

**Distinct occurrences/evidence count:** A/B; two creation paths; **3 groups**.  
**Historical overlap:** YES.  
**Possible overlap with:** TF-01, TF-02, OF-09, SS-10.  
**Discovery concerns:** Tests cover blank inputs but not every length or multi-error combination. Valid names and titles are stored as supplied, not automatically trimmed.

### TF-05 — Tag writes converge on one canonical representation

**Repository:** TaskFlow  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** MEDIUM

**Observed behavior:** Task creation and tag updates share normalization: trim, lowercase, remove blanks and duplicates, sort, and serialize to comma-separated storage. DTO conversion restores a list.

**Concrete evidence:**

- `TaskService.create_task`, `update_tags`, and `_normalize_tags` use the same transformation.
- [Task model](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/models/task.py) documents pre-normalized string storage; [TaskDTO.from_model](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/dto/task_dto.py) reconstructs a list.
- `test_creates_task_with_valid_payload` asserts normalized tags from mixed-case, duplicate, padded inputs.

**Repository specificity:** This is a complete TaskFlow-specific write/storage/read transformation, not generic string formatting.

**Future preservation:** New tag-writing operations should converge on the same representation.

**Distinct occurrences/evidence count:** A/C; two write operations share one normalizer; **3 groups**.  
**Historical overlap:** YES, for helper extraction; the specific tag semantics are separately evidenced.  
**Possible overlap with:** TF-04; superficial relationship to SS-02 and SS-04.  
**Discovery concerns:** Only creation is routed and directly tested. Tag-update recurrence is primarily implementation evidence.

### TF-06 — Repository save owns commit, refresh, and returned persistence state

**Repository:** TaskFlow  
**Origin:** IMPLEMENTATION-CONVENTION  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Supported repositories implement `save` as add, commit, refresh, and return the entity. Services consume the returned value rather than managing database sessions themselves.

**Concrete evidence:**

- `ProjectRepository.save` and `TaskRepository.save` have the same persistence sequence.
- `ProjectService.create_project`, `TaskService.create_task`, and `update_tags` wrap the returned saved model in `Ok`.
- Project-then-task HTTP workflows depend on committed project state and populated model fields.

**Repository specificity:** The convention includes transaction ownership and the save-return contract, beyond merely using SQLAlchemy.

**Future preservation:** Moving commit responsibility or changing save return values would affect existing service composition.

**Distinct occurrences/evidence count:** A; two supported repositories and three consumers; **3 groups**.  
**Historical overlap:** NO.  
**Possible overlap with:** TF-01, OF-05, OF-06.  
**Discovery concerns:** This establishes per-save behavior, not multi-repository transaction coordination.

### TF-07 — Missing-resource failures retain resource identity

**Repository:** TaskFlow  
**Origin:** IMPLEMENTATION-CONVENTION  
**Character:** CRISP  
**Confidence:** MEDIUM

**Observed behavior:** Missing projects and tasks are represented by resource-specific error classes carrying the requested identifier, while sharing the not-found HTTP mapping.

**Concrete evidence:**

- [Error classes](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/core/errors.py): `ProjectNotFoundError(project_id)` and `TaskNotFoundError(task_id)`.
- `TaskService.create_task` and `update_tags` produce the corresponding errors after missing lookups.
- `handle_result` maps their common superclass to 404; `test_rejects_unknown_project` covers one routed case.

**Repository specificity:** Resource context survives the service boundary through explicit classes and identifier fields.

**Future preservation:** New missing-resource outcomes should preserve meaningful resource context and the existing classification.

**Distinct occurrences/evidence count:** A; two error-producing operations and two error types; **3 groups**.  
**Historical overlap:** YES.  
**Possible overlap with:** TF-02, OF-10, OF-12.  
**Discovery concerns:** The task-not-found path has implementation support but no corresponding HTTP endpoint/test.

### TF-08 — In-memory database state spans requests; tests reset that shared state

**Repository:** TaskFlow  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** MEDIUM

**Observed behavior:** A process-shared in-memory SQLite engine preserves state across request sessions. Tests reset its tables between cases rather than receiving an independent database per request.

**Concrete evidence:**

- [Database configuration](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/core/db.py): `StaticPool`, session creation, and the explanation of request-spanning state.
- [Test fixture](C:/Users/admin/Documents/adaptive-coding-agent/taskflow_base/tests/conftest.py): autouse drop/recreate of shared metadata.
- Task tests create a project in one request and create a dependent task in another.
- README identifies in-memory SQLite as the product’s persistence implementation.

**Repository specificity:** The shared database lifetime is integral to TaskFlow’s actual multi-request workflow.

**Future preservation:** Connection-pool or fixture changes must retain request-spanning state without cross-test leakage.

**Distinct occurrences/evidence count:** C; one engine configuration supporting multiple workflows; **4 groups**.  
**Historical overlap:** NO.  
**Possible overlap with:** TF-06, OF-01.  
**Discovery concerns:** The fixture’s reliance on reset-generated integer IDs is test scaffolding, not an additional identity convention.

### TASKFLOW NEGATIVE / NONE EVIDENCE

| Observation ID | NONE/REJECTED observation | Reason not elevated |
|---|---|---|
| TF-N01 | Comment subsystem conventions | Comment model/repository exist, but the model imports `database.Base`, is not registered by the supported application, and has no route/service/tests. No functioning recurring comment workflow is established. |
| TF-N02 | General deletion lifecycle | Repository delete methods exist, but `ProjectService.delete_project` is unimplemented and no delete route is exposed. Insufficient supported workflow evidence. |
| TF-N03 | General helper-extraction rule | Specific validation and tag helpers are evidenced; “always extract helpers” is unsupported. |
| TF-N04 | Logging format as a product convention | Shared logger configuration and two calls are ordinary instrumentation, with no product-specific behavioral contract. |
| TF-N05 | Separate conventions for exact length limits or comma delimiter | These are details within TF-04 and TF-05, not separately recurring ways of working. |
| TF-N06 | Every identifier must be public UUID | Contradicted by integer request `project_id`, repository lookups, and foreign keys. |
| TF-N07 | AAA comments, naming, imports, and type annotations | Formatting or ordinary language/tooling choices, not repository-specific behavior. |

## 4. ORDERFLOW INVENTORY

### OF-01 — Application orchestration uses small entity-specific storage interfaces

**Repository:** OrderFlow  
**Origin:** IMPLEMENTATION-CONVENTION  
**Character:** PATTERN-LIKE  
**Confidence:** HIGH

**Observed behavior:** Domain rules are separated from application orchestration. The application receives customer, order, and shipment repositories through small protocols; in-memory adapters implement their distinct query/write responsibilities.

**Concrete evidence:**

- [Repository protocols](C:/Users/admin/Documents/adaptive-coding-agent/orderflow/repositories.py): three entity-specific interfaces.
- [OrderApplication](C:/Users/admin/Documents/adaptive-coding-agent/orderflow/application.py): constructor injection and domain-operation delegation.
- [In-memory adapters](C:/Users/admin/Documents/adaptive-coding-agent/orderflow/in_memory.py) and test fixtures: three concrete repositories composed into an application.
- [README](C:/Users/admin/Documents/adaptive-coding-agent/orderflow/README.md) and ledger OF-001/OF-004 describe storage separation.

**Repository specificity:** The interfaces reflect actual customer ownership and shipment relationships, not an abstract provider framework.

**Future preservation:** Additional storage implementations should support the application’s existing operations without relocating lifecycle rules.

**Distinct occurrences/evidence count:** A; three protocol/adapter pairs; **4 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** TF-01, TF-08, OF-03, OF-05.  
**Discovery concerns:** There is one production adapter family; broader backend compatibility is not demonstrated.

### OF-02 — Orders are edited and advanced through a guarded lifecycle

**Repository:** OrderFlow  
**Origin:** PRODUCT-INVARIANT  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Orders start DRAFT; item editing is confined to DRAFT; confirmation requires items; processing follows confirmation; cancellation is limited to pre-shipping states.

**Concrete evidence:**

- [Order](C:/Users/admin/Documents/adaptive-coding-agent/orderflow/domain.py): construction, item operations, `confirm`, `begin_processing`, `cancel`, and `_require_status`.
- [Workflow tests](C:/Users/admin/Documents/adaptive-coding-agent/orderflow/tests/test_order_workflows.py): normal progression, rejected transitions, empty confirmation, editing restrictions, and cancellation boundaries.
- README describes guarded editing and initial state.

**Repository specificity:** These are the product’s order-state rules, not merely enum usage.

**Future preservation:** New order operations must respect the lifecycle and its editing/terminal boundaries.

**Distinct occurrences/evidence count:** A/B; multiple order operations and transition families; **3 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** OF-03, OF-04, OF-11.  
**Discovery concerns:** Individual transitions are grouped as one lifecycle candidate rather than inflated into separate conventions.

### OF-03 — Shipment-backed transitions are coordinated before entity mutation

**Repository:** OrderFlow  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Dispatch and completion are application operations that check the related order/shipment state. Independent public shipment/order methods cannot bypass those cross-entity prerequisites.

**Concrete evidence:**

- `OrderApplication.dispatch_shipment` checks both entities before changing either; `complete_order` requires a dispatched shipment.
- Domain `_mark_shipped`, `_complete`, and `_dispatch` are internal transition helpers.
- [Integrity tests](C:/Users/admin/Documents/adaptive-coding-agent/orderflow/tests/test_integrity.py): cancelled-order dispatch, already-dispatched shipment validation, repeated dispatch, and absence of independent public transitions.
- README explicitly requires application coordination.

**Repository specificity:** Order and shipment progression are coupled by product relationships.

**Future preservation:** New cross-entity transitions should validate the participating state before invoking coordinated mutations.

**Distinct occurrences/evidence count:** A/B; dispatch and completion workflows; **4 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** OF-01, OF-02, OF-04, OF-07, SS-03.  
**Discovery concerns:** Validation-before-mutation is evidenced; transactional recovery from repository-save failure is not.

### OF-04 — Public state access does not confer unrestricted mutation authority

**Repository:** OrderFlow  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Order/shipment identities, owners, and statuses are read-only properties. Order items are exposed as a tuple snapshot; item/customer values are frozen. Mutations occur through supported domain/application operations.

**Concrete evidence:**

- Domain `Order`, `Shipment`, `Customer`, and `OrderItem` implement these access restrictions.
- Integrity tests attempt assignment to identity/relationship/status fields and mutation of returned item collections.
- README describes read-only relationships/status and immutable item snapshots.

**Repository specificity:** The restrictions protect lifecycle and ownership rules while allowing controlled aggregate changes.

**Future preservation:** New accessors should not expose mutable containers or assignment paths that bypass those rules.

**Distinct occurrences/evidence count:** A/B; two aggregates plus value objects; **3 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** OF-02, OF-03, OF-06, SS-09.  
**Discovery concerns:** This concerns the public API, not reflection or direct modification of underscore-prefixed internals.

### OF-05 — Application mutations explicitly persist changed entities

**Repository:** OrderFlow  
**Origin:** IMPLEMENTATION-CONVENTION  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Application commands save changed orders and shipments explicitly. Correctness does not depend on repositories returning shared live object references.

**Concrete evidence:**

- Application item changes, confirmation, processing, cancellation, dispatch, and completion call the appropriate `save`.
- Repository protocols expose save operations; adapters accept replacement objects.
- `SnapshotRepository`, `test_application_persists_lifecycle_with_detached_reads`, and detached cancellation tests cross deepcopy boundaries.

**Repository specificity:** Detached-read tests make explicit persistence an intentional application contract despite the live-reference default adapter.

**Future preservation:** New mutation operations must save every changed entity.

**Distinct occurrences/evidence count:** A/B; multiple commands and detached lifecycle/cancellation workflows; **3 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** TF-06, OF-01, OF-03, OF-06.  
**Discovery concerns:** Explicit save is established; a general unit-of-work or transaction mechanism is not.

### OF-06 — Save replaces an existing identity while preserving its owner

**Repository:** OrderFlow  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Order/shipment `save` is not an upsert. The identity must already exist, and a replacement must retain the original customer/order ownership.

**Concrete evidence:**

- `InMemoryOrderRepository.save` and `InMemoryShipmentRepository.save` enforce existence and owner preservation.
- [Persistence tests](C:/Users/admin/Documents/adaptive-coding-agent/orderflow/tests/test_persistence.py): missing-save IDs, owner reassignment rejection, and valid replacement acceptance.
- README documents replacement with the same identity and owner.

**Repository specificity:** The storage contract preserves lifecycle entity relationships while supporting detached objects.

**Future preservation:** New adapters must retain replacement semantics and prevent ownership reassignment.

**Distinct occurrences/evidence count:** A/B; two entity save implementations; **3 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** TF-06, OF-04, OF-05, OF-07.  
**Discovery concerns:** Customer repositories expose add/get only; this is not a universal save operation across every entity.

### OF-07 — Shipment cardinality is enforced at application and storage boundaries

**Repository:** OrderFlow  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** An order may have only one shipment. Application creation checks this relationship, and shipment repository add/save operations independently enforce it.

**Concrete evidence:**

- `OrderApplication.create_shipment` uses `get_for_order` before adding a shipment.
- Shipment adapter `add` and `save` reject conflicting order relationships.
- Workflow and persistence tests cover duplicate creation and conflicting replacement without changing stored relationships.
- README states the one-shipment-per-order save constraint.

**Repository specificity:** This is a particular order/shipment cardinality rule with more than one enforcement point.

**Future preservation:** New creation, replacement, or persistence paths must preserve it.

**Distinct occurrences/evidence count:** A/B; application creation and two storage writes; **4 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** OF-03, OF-06.  
**Discovery concerns:** Cardinality enforcement is related to, but not identical with, immutable ownership.

### OF-08 — Entity identities are generated before persistence through one application dependency

**Repository:** OrderFlow  
**Origin:** IMPLEMENTATION-CONVENTION  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Customer, order, and shipment creation use the application’s injected UUID factory before repository insertion.

**Concrete evidence:**

- Application constructor accepts `id_factory`; all three creation operations use it.
- [Fixtures](C:/Users/admin/Documents/adaptive-coding-agent/orderflow/tests/conftest.py): `SequentialIds` substitutes deterministic UUID generation.
- Ledger OF-002 records application-generated identity as independent of persistence.

**Repository specificity:** Identity generation consistently belongs to application construction rather than repository allocation.

**Future preservation:** New entity creation should use the same dependency rather than hardcoding UUID generation or requiring storage-assigned IDs.

**Distinct occurrences/evidence count:** A; three creation paths; **3 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** TF-03, OF-01.  
**Discovery concerns:** UUID type annotations do not establish exhaustive runtime validation of arbitrary identity inputs.

### OF-09 — Value construction establishes item validity before aggregate insertion

**Repository:** OrderFlow  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Customer/item values validate their own inputs at construction. Application item addition constructs an `OrderItem` before inserting it into the order. Quantity and price constraints are exact, including rejection of boolean quantities and non-finite prices.

**Concrete evidence:**

- Domain `Customer.__post_init__` and `OrderItem.__post_init__`.
- `OrderApplication.add_item` constructs the item before calling `order.add_item`.
- Workflow tests exercise invalid quantity/price inputs through the application.

**Repository specificity:** Validation lives in reusable domain values and includes OrderFlow’s specific numeric and textual constraints.

**Future preservation:** Alternative insertion paths should not introduce invalid domain values.

**Distinct occurrences/evidence count:** A/B; two value constructors plus application insertion; **3 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** TF-04, OF-02, OF-11, SS-10.  
**Discovery concerns:** No evidence establishes currency rounding, totals, or normalization of product codes.

### OF-10 — Expected product failures use a small exception vocabulary

**Repository:** OrderFlow  
**Origin:** IMPLEMENTATION-CONVENTION  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Product-facing validation, missing-entity, and invalid-operation failures use subclasses of `OrderFlowError`, without Result wrappers or framework response objects.

**Concrete evidence:**

- [Errors](C:/Users/admin/Documents/adaptive-coding-agent/orderflow/errors.py): `ValidationError`, `NotFoundError`, and `InvalidOperationError`.
- Domain and application operations raise these categories across value validation, lookups, and lifecycle restrictions.
- Workflow tests assert the categories; ledger OF-006 records the small expected-failure set.

**Repository specificity:** The categories correspond to this local component’s public failure contract.

**Future preservation:** New public product operations should preserve compatible failure classification.

**Distinct occurrences/evidence count:** A/B; domain and application layers, multiple failure families; **3 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** TF-02, TF-07, OF-12, SS-08.  
**Discovery concerns:** Direct adapter integrity errors use `ValueError`; the vocabulary does not encompass every storage error.

### OF-11 — Product code identifies an order line

**Repository:** OrderFlow  
**Origin:** PRODUCT-INVARIANT  
**Character:** CRISP  
**Confidence:** MEDIUM

**Observed behavior:** Order lines have no separate identifier. Product code determines duplicate detection and removal, so a product code may occur only once within an order.

**Concrete evidence:**

- `OrderItem.product_code`, `Order.add_item`, and `Order.remove_item` use product code as line identity.
- Workflow tests remove an item by product code and inspect the returned item.
- Ledger OF-005 explicitly records the uniqueness/removal rationale.

**Repository specificity:** This determines how the product represents and addresses order lines.

**Future preservation:** New line operations should preserve unambiguous code-based identity.

**Distinct occurrences/evidence count:** B/C; insertion and removal behavior; **3 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** OF-02, OF-09.  
**Discovery concerns:** Duplicate rejection lacks a dedicated named test in the inspected suite. Matching is exact; case folding or trimming on storage is not established.

### OF-12 — Application lookup converts storage absence into contextual product failure

**Repository:** OrderFlow  
**Origin:** IMPLEMENTATION-CONVENTION  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Repositories return `None` for absent entities. Application `_require_*` helpers convert absence into contextual `NotFoundError` before dependent operations proceed.

**Concrete evidence:**

- `_require_customer`, `_require_order`, and `_require_shipment` each implement this conversion.
- Creation, order retrieval, customer-order listing, and shipment dispatch call the appropriate helpers.
- `test_missing_entities_fail_explicitly` checks customer and order failures.

**Repository specificity:** Storage absence and public use-case failure are deliberately separated across three entity types.

**Future preservation:** New dependent operations should not continue with missing entities or leak `None` as a successful result.

**Distinct occurrences/evidence count:** A; three resolution helpers and multiple consumers; **3 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** TF-07, OF-01, OF-10.  
**Discovery concerns:** Shipment absence is primarily supported by implementation evidence; the named missing-entity test covers customer/order cases.

### ORDERFLOW NEGATIVE / NONE EVIDENCE

| Observation ID | NONE/REJECTED observation | Reason not elevated |
|---|---|---|
| OF-N01 | String enums as a standalone convention | Enum usage itself is ordinary; the meaningful behavior is the lifecycle in OF-02/OF-03. |
| OF-N02 | Application relies on live repository object identity | Default adapters return retained objects, but detached-read tests explicitly require correctness without that reliance. |
| OF-N03 | General ordering rule for repository lists | Dictionary iteration and a creation-order assertion exist, but no broadly documented/query-wide ordering convention is established. |
| OF-N04 | Currency arithmetic, rounding, or order totals | Decimal input validation exists; these additional operations do not. |
| OF-N05 | Cross-repository transactions or rollback | Dispatch validates before mutation, but there is no transactional save/recovery infrastructure. |
| OF-N06 | HTTP/CLI or messaging conventions | These subsystems are absent; the ledger explicitly excludes an interface and rejects broader infrastructure. |
| OF-N07 | Separate candidate for each transition/helper | Those would restate parts of the same lifecycle or coordination behavior without distinct discovery content. |

## 5. SAFESYNC INVENTORY

### SS-01 — Preview shares planning with run while remaining read-only

**Repository:** SafeSync  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Preview delegates to the planner and does not invoke execution. Run creates a current plan and executes it. The CLI preserves that separation.

**Concrete evidence:**

- [Application workflows](C:/Users/admin/Documents/adaptive-coding-agent/safesync/application.py): `preview`, `create_plan`, `run`.
- [CLI](C:/Users/admin/Documents/adaptive-coding-agent/safesync/__main__.py): distinct preview-action and execution-report branches.
- Tests `test_preview_zero_mutation_and_absent_destination` and `test_json_config_and_cli_preview_run` assert payload non-mutation and subsequent execution.
- README explains that CLI preview/run are separate invocations.

**Repository specificity:** The product’s inspection workflow uses the same planning semantics without performing synchronization writes.

**Future preservation:** New preview features must preserve read-only behavior and avoid a divergent action-generation path.

**Distinct occurrences/evidence count:** B/C; public API and CLI workflows; **4 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** SS-02, SS-03, SS-09.  
**Discovery concerns:** CLI run does not consume a saved preview artifact; it builds a fresh plan.

### SS-02 — Logical file state is content-based and deterministically ordered

**Repository:** SafeSync  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Files are represented by relative path, size, and SHA-256. Comparison uses size/hash rather than timestamps, and planning orders actions by relative path.

**Concrete evidence:**

- [Filesystem](C:/Users/admin/Documents/adaptive-coding-agent/safesync/filesystem.py): `read_entry` hashes streamed bytes; `scan` produces POSIX relative paths and sorts entries.
- `create_plan` compares size/hash and sorts the path union.
- Tests `test_update_uses_hash_not_timestamp_or_size`, `test_identical_skip_despite_timestamp`, and `test_deterministic_plan`.
- README and ledger SS-03 document content-based comparison.

**Repository specificity:** This defines what “same file state” means for SafeSync’s preview and execution.

**Future preservation:** New scan/comparison behavior should not substitute timestamps or unstable discovery order.

**Distinct occurrences/evidence count:** A/B; scan representation, planning, and multiple comparison behaviors; **4 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** SS-01, SS-03, SS-07, SS-11; superficial relationship to TF-05.  
**Discovery concerns:** Determinism is conditional on equivalent quiescent filesystem/configuration state, not absolute root-independent plan equality.

### SS-03 — Execution re-establishes authority instead of trusting plan construction

**Repository:** SafeSync  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Execution validates roots/actions, compares the supplied plan with a fresh plan, and rechecks action snapshots before mutation. A previously constructed or manually changed plan is not sufficient authority.

**Concrete evidence:**

- `execute`: whole-plan preflight followed by per-action state checks.
- Tests `test_plan_semantics_cannot_be_bypassed` and `test_invalid_action_after_valid_action_is_preflighted`.
- Tests `test_stale_plan_is_rejected` and `test_stale_delete_plan_preserves_changed_destination`.
- README and ledger SS-08 describe execution revalidation.

**Repository specificity:** The execution boundary independently enforces the planner’s semantics and current-state assumptions.

**Future preservation:** New actions or execution paths must not bypass freshness, policy, or semantic validation.

**Distinct occurrences/evidence count:** A/B; whole-plan and per-action stages with multiple tamper/stale families; **4 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** SS-01, SS-02, SS-04, SS-05, SS-06, SS-09, OF-03.  
**Discovery concerns:** Revalidation is not a lock or transaction. It does not guarantee preflight detection of every operational file/directory conflict.

### SS-04 — Filesystem access repeatedly enforces the ordinary-file boundary

**Repository:** SafeSync  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Root relationships, relative paths, resolved containment, links/reparse points, and ordinary-entry types are checked at filesystem access boundaries. These checks are reused across scanning and execution.

**Concrete evidence:**

- `validate_config`, `validate_relative`, `reject_links`, and `file_path`.
- `scan`, `read_entry`, `write_file`, and `delete_file` reuse the boundary checks.
- Tests cover malicious action paths, unsafe roots, root/ancestor links, post-preview links, Windows case aliases, and junctions.
- README and ledger SS-04/SS-05/SS-13 document the restricted filesystem policy.

**Repository specificity:** The checks collectively enforce SafeSync’s one-way local mutation boundary.

**Future preservation:** New filesystem operations must retain the same containment and unsupported-entry policy.

**Distinct occurrences/evidence count:** A/B; scanning, reading, writing, and deletion; **4 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** SS-03, SS-06, SS-07, SS-11.  
**Discovery concerns:** Individual traversal/device/link checks are not separate candidates. Hostile concurrent changes during system calls are explicitly outside V1 guarantees.

### SS-05 — Ignore policy excludes both trees and whole matching subtrees

**Repository:** SafeSync  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** The same case-sensitive ignore policy applies to source and destination. Full relative paths and directory prefixes are matched, so ignored directory content never generates actions, including deletion.

**Concrete evidence:**

- `ignored` checks path prefixes with `fnmatchcase`.
- `create_plan` scans both roots with the same patterns; `scan` stops traversal at ignored directories.
- `test_ignore_patterns_preserve_both_sides` checks source exclusion and destination preservation.
- README and ledger SS-07 specify prefix matching and glob behavior.

**Repository specificity:** Ignoring controls the synchronization universe rather than merely suppressing source copies.

**Future preservation:** New action types must not mutate excluded destination content.

**Distinct occurrences/evidence count:** B/C; one matcher governing both scans and multiple action consequences; **4 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** SS-03, SS-06, SS-10.  
**Discovery concerns:** Encountered links are checked before ignore matching. Ignored subtree contents are not traversed.

### SS-06 — Destination cleanup requires explicit deletion authority

**Repository:** SafeSync  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Destination-only files become SKIP when deletion is disabled and DELETE when enabled. Execution rejects changed plan semantics, and the deletion helper independently checks the opt-in.

**Concrete evidence:**

- `create_plan`: destination-only decision based on `delete_extra`.
- `execute` fresh-plan comparison and `delete_file` opt-in check.
- `test_destination_only` exercises both settings; `test_plan_semantics_cannot_be_bypassed` includes forged deletion.
- README states preservation/deletion behavior.

**Repository specificity:** Preserving extras is the default synchronization policy, with deletion requiring configuration authority.

**Future preservation:** New cleanup paths must not treat destination absence-from-source as unconditional deletion permission.

**Distinct occurrences/evidence count:** A/B; planning and deletion enforcement; **4 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** SS-03, SS-04, SS-05, SS-10.  
**Discovery concerns:** Changing the configuration and generating a valid new plan is authorized behavior, not a bypass.

### SS-07 — Payload updates replace destination entries after content verification

**Repository:** SafeSync  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** COPY and UPDATE stream into a temporary file within the destination directory, verify copied size/hash, and replace the destination entry. They do not truncate the existing destination inode.

**Concrete evidence:**

- `write_file`: destination-local temporary output, streamed digest/size checks, `os.replace`, and cleanup.
- `execute` sends both COPY and UPDATE through that function.
- Tests cover normal copy/update, operation-failure cleanup, and destination hard links preserving source content.
- README and ledger SS-09 explain replacement and hard-link protection.

**Repository specificity:** The write strategy supports SafeSync’s source-preservation and payload-integrity guarantees.

**Future preservation:** New write paths should not write through existing hard links or replace payloads before verifying copied content.

**Distinct occurrences/evidence count:** B/C; one write implementation serving two action kinds and several failure/safety behaviors; **4 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** SS-02, SS-04, SS-08.  
**Discovery concerns:** Per-file replacement is not whole-run atomicity; parent directories may remain after failure.

### SS-08 — Reports describe partial execution rather than implying rollback

**Repository:** SafeSync  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Execution stops at the first failure, retains earlier successes, and reports unattempted actions. Counts derive from successful action results; failed actions are not counted as completed.

**Concrete evidence:**

- `execute`: separate preflight-failure and per-action-failure reports.
- [SyncReport](C:/Users/admin/Documents/adaptive-coding-agent/safesync/models.py): derived copied/updated/deleted/skipped/failed counts and serialization.
- Tests `test_operation_failure_is_not_success`, `test_fail_fast_reports_unattempted`, `test_report_counts_all_actions`, and CLI failure reporting.
- README and ledger SS-06 specify no rollback and honest partial reporting.

**Repository specificity:** This is the synchronization utility’s failure/result contract across API and CLI.

**Future preservation:** New actions must preserve truthful counts, failure attribution, and remaining-action accounting.

**Distinct occurrences/evidence count:** A/B; validation failure, operation failure, and CLI reporting; **4 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** TF-02, OF-10, SS-03, SS-07, SS-09.  
**Discovery concerns:** One existing conflict-test comment overstates preflight detection; it does not establish transactional execution.

### SS-09 — Planning and reporting objects are stable snapshots

**Repository:** SafeSync  
**Origin:** IMPLEMENTATION-CONVENTION  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** Configuration, entries, actions, plans, action results, and reports are frozen values. Sequence inputs are copied into tuples, preventing later caller-list mutation from changing snapshots.

**Concrete evidence:**

- Models use frozen dataclasses; `SyncConfig`, `SyncPlan`, and `SyncReport` defensively tuple-copy sequence fields.
- `test_public_values_are_immutable_and_defensively_copy_lists` covers input-list mutation and direct field assignment.
- README and ledger SS-08 describe stable public planning values.

**Repository specificity:** Stable values preserve the relationship between observed plan state and guarded execution.

**Future preservation:** New plan/report fields should not introduce mutable aliases that silently change approved or reported state.

**Distinct occurrences/evidence count:** A/B; multiple value classes and three defensive sequence conversions; **3 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** OF-04, SS-01, SS-03, SS-08.  
**Discovery concerns:** Immutability does not authenticate arbitrary constructed objects; SS-03 remains a separate execution safeguard.

### SS-10 — Configuration is strict and interpreted relative to its own location

**Repository:** SafeSync  
**Origin:** MIXED  
**Character:** CRISP  
**Confidence:** HIGH

**Observed behavior:** JSON configuration rejects unsupported fields and incorrect shapes/types. Relative roots are interpreted from the configuration file’s directory, and both CLI commands use the same loader.

**Concrete evidence:**

- `load_config`: supported/required fields, type checks, and configuration-relative path construction.
- `SyncConfig.__post_init__`: boolean and ignore-pattern validation; CLI preview/run share loading.
- Tests `test_invalid_configuration` and `test_json_config_and_cli_preview_run`.
- README and ledger SS-01 describe the portable configuration contract.

**Repository specificity:** Working-directory independence and strict schema behavior affect both public CLI workflows.

**Future preservation:** New configuration fields must be deliberately supported and interpreted consistently.

**Distinct occurrences/evidence count:** B/C; one loader serving both CLI workflows and multiple validation cases; **4 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** TF-04, OF-09, SS-05, SS-06.  
**Discovery concerns:** Direct `SyncConfig` construction does not perform every root check immediately; planning/execution validate roots separately.

### SS-11 — Directories support file payloads rather than being synchronization entities

**Repository:** SafeSync  
**Origin:** PRODUCT-INVARIANT  
**Character:** CRISP  
**Confidence:** MEDIUM

**Observed behavior:** Scans create entries for files, not directories. Writes create required parents; deletion removes files. Empty directories are not copied or removed, and blocking file/directory entries are not implicitly destroyed.

**Concrete evidence:**

- `scan` records ordinary-file entries while using directories for traversal.
- `write_file` creates parents; `delete_file` unlinks the target file; `read_entry` rejects nonordinary file targets.
- README and ledger SS-11 explicitly state empty-directory and conflict policy.
- Tests cover nested copying and blocking filesystem conflicts.

**Repository specificity:** This defines the product’s synchronization unit and prevents directory cleanup from being inferred from file cleanup.

**Future preservation:** New synchronization operations should not introduce implicit directory synchronization or destructive conflict resolution.

**Distinct occurrences/evidence count:** A/B; scanning, parent creation, and deletion boundaries; **4 groups**.  
**Historical overlap:** UNCLEAR.  
**Possible overlap with:** SS-02, SS-04, SS-06, SS-07.  
**Discovery concerns:** Empty-directory behavior is supported more strongly by code/documentation than dedicated assertions. Conflict detection is not universally completed during planning.

### SAFESYNC NEGATIVE / NONE EVIDENCE

| Observation ID | NONE/REJECTED observation | Reason not elevated |
|---|---|---|
| SS-N01 | Each traversal, drive, device, separator, or link check as a separate convention | These are constituent checks within SS-04; splitting them would restate one boundary policy. |
| SS-N02 | One-megabyte chunks and temporary filename prefix | Isolated implementation parameters, not independently recurring product behavior. |
| SS-N03 | JSON indentation and argparse mechanics | Presentation/library choices; no repository-specific invariant is established. |
| SS-N04 | Bytecode suppression as synchronization behavior | Python runtime cache behavior is distinct from payload synchronization; `-B` itself is generic. |
| SS-N05 | Universal global operational prevalidation | Fresh-plan and path validation exist, but per-action filesystem failures remain possible. A test comment alone does not establish a broader invariant. |
| SS-N06 | Locking, rollback, or crash-recovery convention | Absent and explicitly outside the documented V1 guarantees. |
| SS-N07 | Network, bidirectional sync, history, encryption, or restore behavior | Unsupported subsystems; no implementation recurrence exists. |

## 6. CROSS-REPOSITORY RELATIONSHIP MAP

These are provisional relationships, not decisions about independence.

| Candidates | Relationship | Evidence/rationale |
|---|---|---|
| TF-01, OF-01 | PARTIAL OVERLAP | Both allocate application/persistence responsibilities. TaskFlow includes HTTP/DTO boundaries and SQLAlchemy repositories; OrderFlow centers domain objects and injected protocols. |
| TF-02, OF-10, SS-08 | PARTIAL OVERLAP | All expose meaningful expected outcomes, but use different contracts: Result-to-HTTP, local exceptions, and partial-execution reports. |
| TF-07, OF-12 | POSSIBLY SAME HIGHER-LEVEL CONSTRUCT | Storage absence becomes contextual application failure. TaskFlow uses resource-specific classes; OrderFlow uses entity-specific resolver helpers and messages. |
| TF-03, OF-08 | SUPERFICIALLY SIMILAR | Both involve UUID identities. TaskFlow separates public response identity from database identity; OrderFlow allocates primary entity identity before persistence. |
| TF-04, OF-09, SS-10 | PARTIAL OVERLAP | Each places validation at a meaningful product boundary, but the boundaries and representations differ: service creation, domain value construction, and configuration loading. |
| TF-06, OF-05, OF-06 | PARTIAL OVERLAP | All make persistence interaction consequential. TaskFlow owns commit/refresh inside save; OrderFlow requires explicit saves and owner-preserving replacement. |
| TF-08, OF-01 | PARTIAL OVERLAP | Both support process-local persistence. TaskFlow shares an engine across requests; OrderFlow uses explicitly composed repository instances. |
| OF-04, SS-09 | POSSIBLY SAME HIGHER-LEVEL CONSTRUCT | Public access should not permit uncontrolled mutation. OrderFlow protects mutable aggregate rules; SafeSync preserves immutable workflow snapshots. |
| OF-03, SS-03 | PARTIAL OVERLAP | Both recheck prerequisites at the operation that authorizes mutation. Cross-entity lifecycle consistency differs from filesystem-plan freshness and safety. |
| OF-02, SS-03 | SUPERFICIALLY SIMILAR | Both inspect current state, but one governs domain progression and the other rejects stale execution assumptions. |
| TF-05, SS-02/SS-04 | SUPERFICIALLY SIMILAR | Both constrain representations. Canonical tag transformation differs from relative-path identity and filesystem alias rejection. |
| TF-01, TF-02, TF-04, TF-06 | PARTIAL OVERLAP | Responsibility allocation supports validation, outcome translation, and persistence ownership; these observations are related without being identical statements. |
| TF-02, TF-07 | PARTIAL OVERLAP | Result representation and resource-specific failure content participate in the same error path. |
| OF-02, OF-03, OF-04 | PARTIAL OVERLAP | Lifecycle rules, coordinated transitions, and restricted public mutation jointly preserve aggregate state. |
| OF-05, OF-06 | PARTIAL OVERLAP | Explicit application saves rely on a replacement-capable repository contract. |
| OF-03, OF-06, OF-07 | PARTIAL OVERLAP | Shipment coordination depends on stable ownership and cardinality, but each observation occurs at different operations/boundaries. |
| OF-02, OF-09, OF-11 | PARTIAL OVERLAP | Draft editing, valid item construction, and product-code identity meet in item operations. |
| OF-10, OF-12 | PARTIAL OVERLAP | The exception vocabulary supplies the category; resolver helpers supply repeated absence conversion and entity context. |
| SS-01, SS-02, SS-03, SS-09 | PARTIAL OVERLAP | Read-only planning, deterministic state, execution revalidation, and stable snapshots support a common preview/execution relationship. |
| SS-03, SS-04, SS-05, SS-06 | PARTIAL OVERLAP | Execution validation re-enforces filesystem, ignore, and deletion policies. |
| SS-02, SS-07 | PARTIAL OVERLAP | Hash-based state representation is reused when verifying copied payloads. |
| SS-07, SS-08 | PARTIAL OVERLAP | Atomic per-file replacement and cleanup support truthful failure accounting, without whole-run rollback. |
| SS-04, SS-07, SS-11 | PARTIAL OVERLAP | Ordinary-file access, guarded writes, and file-only synchronization define compatible filesystem boundaries. |
| SS-05, SS-06 | PARTIAL OVERLAP | Both preserve destination content under particular conditions: exclusion from scope versus lack of deletion authority. |

The strongest visibly product-specific areas are TaskFlow’s response/storage identity split and tag transformation; OrderFlow’s shipment-backed lifecycle and line/ownership relationships; and SafeSync’s preview, content-state, exclusion, and mutation policies. This is a description of specificity, not a ranking.

## 7. GENERIC PRACTICES EXCLUDED

The following were observed but not treated as standalone repository-specific candidates:

- Dataclasses, including frozen dataclasses without a specific protected contract.
- Type annotations, `Protocol`, enums, properties, and underscore naming by themselves.
- pytest fixtures, parameterization, and assertion syntax.
- Standard library use and relative imports.
- Ordinary dictionary storage or iteration.
- Generic constructor/dependency injection.
- Generic validation, logging, or exception handling without product-specific placement or behavior.
- General advice to separate concerns or extract helpers.

Candidates retain concrete contracts implemented using these mechanisms; the mechanisms alone are excluded.

## 8. DISCOVERY REJECTION LEDGER

| Observation ID | Repository | Observed idea | Decision | Reason | Evidence |
|---|---|---|---|---|---|
| TF-N01 | TaskFlow | Comment subsystem pattern | NOT ELEVATED | Unsupported/inconsistent remnant, not a recurring workflow | Comment model/repository; application model registration; absence of routes/services/tests |
| TF-N02 | TaskFlow | Deletion lifecycle | NOT ELEVATED | No supported application/API deletion workflow | Repository deletes; unimplemented service deletion; routes |
| TF-N03 | TaskFlow | Always extract helpers | NOT ELEVATED | Generalization exceeds observed specific helpers | Service validation and tag helpers |
| TF-N04 | TaskFlow | Logging convention | NOT ELEVATED | Generic instrumentation | `core.logging.get_logger`; service logger calls |
| TF-N05 | TaskFlow | Exact limits/delimiter as separate conventions | NOT ELEVATED | Constituent details of retained behaviors | Creation validators; tag normalization/storage |
| TF-N06 | TaskFlow | All IDs are public UUIDs | NOT ELEVATED | Contradicted by request/persistence keys | Request DTO, foreign key, repository queries |
| TF-N07 | TaskFlow | Formatting/type/import conventions | NOT ELEVATED | Language/tooling choices | Source and test modules |
| OF-N01 | OrderFlow | String enums alone | NOT ELEVATED | Mechanism without independent behavior | Status definitions |
| OF-N02 | OrderFlow | Live-reference persistence dependency | NOT ELEVATED | Detached-read tests establish contrary application contract | In-memory gets; snapshot-adapter tests |
| OF-N03 | OrderFlow | Universal list ordering | NOT ELEVATED | Too little independent/documented recurrence | `list_for_customer`; retrieval test |
| OF-N04 | OrderFlow | Money arithmetic/rounding | NOT ELEVATED | Not implemented | Item price validation only |
| OF-N05 | OrderFlow | Transactional coordination | NOT ELEVATED | No transaction/rollback behavior demonstrated | Dispatch checks and sequential saves |
| OF-N06 | OrderFlow | Interface/messaging conventions | NOT ELEVATED | Subsystems absent | README; OF-007/OF-008 |
| OF-N07 | OrderFlow | One candidate per transition/helper | NOT ELEVATED | Duplicate fragments of observed behaviors | Domain lifecycle and application coordination |
| SS-N01 | SafeSync | One candidate per path/security check | NOT ELEVATED | Constituent checks of one boundary policy | Path/root/link validators |
| SS-N02 | SafeSync | Chunk size/temp prefix | NOT ELEVATED | Isolated implementation parameters | `read_entry`; `write_file` |
| SS-N03 | SafeSync | JSON/argparse presentation | NOT ELEVATED | Generic library/presentation mechanics | CLI serialization/parser |
| SS-N04 | SafeSync | Bytecode suppression | NOT ELEVATED | Generic interpreter behavior | README `-B` instructions |
| SS-N05 | SafeSync | Every failure globally prevalidated | NOT ELEVATED | Unsupported generalization | Execution loop; conflict checks; test comment |
| SS-N06 | SafeSync | Transactions/locking/crash recovery | NOT ELEVATED | Absent and explicitly excluded | README; SS-12; execution behavior |
| SS-N07 | SafeSync | Broader synchronization subsystems | NOT ELEVATED | Not implemented | README scope statement |

None of these observations was rejected for transfer difficulty, boundary difficulty, scorer difficulty, or expected model behavior.

## 9. RAW CANDIDATE SUMMARY

Evidence counts are the listed evidence groups; they are not scores.

| ID | Repository | Short name | Origin | Character | Confidence | Evidence count | Historical overlap | Possible overlaps |
|---|---|---|---|---|---|---:|---|---|
| TF-01 | TaskFlow | Request-to-persistence responsibilities | IMPLEMENTATION-CONVENTION | PATTERN-LIKE | HIGH | 4 | YES | TF-02/04/06; OF-01 |
| TF-02 | TaskFlow | Result-to-HTTP outcomes | IMPLEMENTATION-CONVENTION | CRISP | HIGH | 4 | YES | TF-01/07; OF-10; SS-08 |
| TF-03 | TaskFlow | Response/persistence identity split | MIXED | CRISP | HIGH | 3 | YES | OF-08 |
| TF-04 | TaskFlow | Collected creation validation | MIXED | CRISP | HIGH | 3 | YES | TF-01/02; OF-09; SS-10 |
| TF-05 | TaskFlow | Canonical tag writes | MIXED | CRISP | MEDIUM | 3 | YES | TF-04; SS-02/04 |
| TF-06 | TaskFlow | Save commits, refreshes, returns | IMPLEMENTATION-CONVENTION | CRISP | HIGH | 3 | NO | TF-01; OF-05/06 |
| TF-07 | TaskFlow | Resource-specific missing failures | IMPLEMENTATION-CONVENTION | CRISP | MEDIUM | 3 | YES | TF-02; OF-10/12 |
| TF-08 | TaskFlow | Request-spanning in-memory state | MIXED | CRISP | MEDIUM | 4 | NO | TF-06; OF-01 |
| OF-01 | OrderFlow | Entity-specific storage interfaces | IMPLEMENTATION-CONVENTION | PATTERN-LIKE | HIGH | 4 | UNCLEAR | TF-01/08; OF-03/05 |
| OF-02 | OrderFlow | Guarded order lifecycle | PRODUCT-INVARIANT | CRISP | HIGH | 3 | UNCLEAR | OF-03/04/11 |
| OF-03 | OrderFlow | Coordinated shipment transitions | MIXED | CRISP | HIGH | 4 | UNCLEAR | OF-01/02/04/07; SS-03 |
| OF-04 | OrderFlow | Restricted public mutation | MIXED | CRISP | HIGH | 3 | UNCLEAR | OF-02/03/06; SS-09 |
| OF-05 | OrderFlow | Explicit persistence after mutation | IMPLEMENTATION-CONVENTION | CRISP | HIGH | 3 | UNCLEAR | TF-06; OF-01/03/06 |
| OF-06 | OrderFlow | Owner-preserving replacement saves | MIXED | CRISP | HIGH | 3 | UNCLEAR | TF-06; OF-04/05/07 |
| OF-07 | OrderFlow | One shipment at both boundaries | MIXED | CRISP | HIGH | 4 | UNCLEAR | OF-03/06 |
| OF-08 | OrderFlow | Application-generated identities | IMPLEMENTATION-CONVENTION | CRISP | HIGH | 3 | UNCLEAR | TF-03; OF-01 |
| OF-09 | OrderFlow | Valid values before insertion | MIXED | CRISP | HIGH | 3 | UNCLEAR | TF-04; OF-02/11; SS-10 |
| OF-10 | OrderFlow | Expected exception vocabulary | IMPLEMENTATION-CONVENTION | CRISP | HIGH | 3 | UNCLEAR | TF-02/07; OF-12; SS-08 |
| OF-11 | OrderFlow | Product-code line identity | PRODUCT-INVARIANT | CRISP | MEDIUM | 3 | UNCLEAR | OF-02/09 |
| OF-12 | OrderFlow | Contextual required lookups | IMPLEMENTATION-CONVENTION | CRISP | HIGH | 3 | UNCLEAR | TF-07; OF-01/10 |
| SS-01 | SafeSync | Shared read-only planning | MIXED | CRISP | HIGH | 4 | UNCLEAR | SS-02/03/09 |
| SS-02 | SafeSync | Deterministic content-state plans | MIXED | CRISP | HIGH | 4 | UNCLEAR | SS-01/03/07/11; TF-05 |
| SS-03 | SafeSync | Execution re-establishes authority | MIXED | CRISP | HIGH | 4 | UNCLEAR | SS-01/02/04/05/06/09; OF-03 |
| SS-04 | SafeSync | Repeated filesystem boundary checks | MIXED | CRISP | HIGH | 4 | UNCLEAR | SS-03/06/07/11 |
| SS-05 | SafeSync | Symmetric subtree exclusion | MIXED | CRISP | HIGH | 4 | UNCLEAR | SS-03/06/10 |
| SS-06 | SafeSync | Explicit deletion authority | MIXED | CRISP | HIGH | 4 | UNCLEAR | SS-03/04/05/10 |
| SS-07 | SafeSync | Verified destination replacement | MIXED | CRISP | HIGH | 4 | UNCLEAR | SS-02/04/08 |
| SS-08 | SafeSync | Honest partial-execution reports | MIXED | CRISP | HIGH | 4 | UNCLEAR | TF-02; OF-10; SS-03/07/09 |
| SS-09 | SafeSync | Stable workflow snapshots | IMPLEMENTATION-CONVENTION | CRISP | HIGH | 3 | UNCLEAR | OF-04; SS-01/03/08 |
| SS-10 | SafeSync | Strict configuration-relative loading | MIXED | CRISP | HIGH | 4 | UNCLEAR | TF-04; OF-09; SS-05/06 |
| SS-11 | SafeSync | Files are synchronization entities | PRODUCT-INVARIANT | CRISP | MEDIUM | 4 | UNCLEAR | SS-02/04/06/07 |

## 10. COVERAGE / UNCERTAINTY

**Coverage**

- TaskFlow: application entry point, routes, services, repositories, models, DTOs, errors/results, database/logging utilities, tests, README, and requirements.
- OrderFlow: domain, application, protocols, in-memory adapters, public exports, errors, all tests/fixtures, README, and every decision-ledger entry.
- SafeSync: configuration/model construction, scanner, planner, executor, filesystem operations, reports, CLI, exports, tests, README, and every ledger entry.

**Insufficient recurrence or support**

- TaskFlow comments and application deletion do not establish supported recurring workflows.
- OrderFlow has no alternate production storage family, transport layer, monetary calculations, or transactional subsystem.
- SafeSync has no directory-entity synchronization, concurrency locking, broader backup-management subsystem, or provider abstraction.

**Candidates with concentrated evidence**

- TF-05: two write callers, but behavioral tests mainly cover creation.
- TF-07: both resource errors exist; only missing-project behavior is routed/tested.
- TF-08: one database configuration supports multiple request workflows.
- OF-11: line identity has insertion/removal and ledger support, but duplicate rejection lacks a dedicated test.
- OF-12: three resolver implementations; named missing-entity tests cover two types.
- SS-01, SS-05, SS-07, SS-10: central implementations supported by multiple workflows/tests, rather than independent alternative implementations.
- SS-11: empty-directory policy relies substantially on code/documentation.

**Limitations**

This was static read-only discovery. Tests were inspected, not executed. Test assertions describe intended expectations; this pass does not newly certify runtime correctness or platform behavior.

Historical exposure beyond the supplied TaskFlow concepts was not investigated. Product provenance cannot be fully inferred from current files.

Overlap flags remain unresolved. No transfer tasks, boundary cases, scorers, candidate rankings, or role assignments were designed.

## 11. NEXT-STEP BOUNDARY

“No candidate in this report has yet passed benchmark-family quality, independence, transfer, boundary, scorer-validity, Selection, or Confirmation review.”

**Step 8K-B was not performed.**

## 12. FINAL GIT STATE

Final verification returned no status entries and:

```text
66a7b94c47fa464b0e0b4f20f658efeefd62c238
```

The working tree remains clean; staged and working-tree diffs are empty.

- **Files modified:** NONE.
- **Files created:** NONE.
- **Commits:** NONE.
- **Model experiments:** NONE.
- **Benchmark roles assigned:** NONE.