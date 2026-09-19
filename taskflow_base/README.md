# TaskFlow — Phase 1 pilot repository

Canonical base repository for the Phase 1 pilot spec (v1.0). `tasks` and
`projects` are the frozen, fully-working resources. `comments` does not
exist — it's what the agent under test builds, either during an exposure
task (explicit conventions) or as the held-out task itself (fuzzy
conventions).

## Setup

```
pip install -r requirements.txt
pytest
```

## Where each pilot convention lives

**Explicit 1 — routers never touch the ORM/session directly**
`routers/tasks.py` and `routers/projects.py` only call into
`TaskService`/`ProjectService`. `routers/tasks.py::handle_result` is the
one place a `Result`'s error becomes an HTTP response.

**Explicit 2 — services return `Result[T, ServiceError]`, never raise**
See `core/result.py` and every method in `services/task_service.py`.
Expected failures return `Err(...)`.

**Explicit 3 — DTOs expose `public_id: UUID`, never the internal PK**
`dto/task_dto.py`, `dto/project_dto.py`. `models/*.py` still has an
internal integer `id` for the ORM, but it never reaches a DTO.

**Fuzzy 1 — validation extracted into `_validate_*`**
`TaskService._validate_create` and `ProjectService._validate_create`.
Never told to the agent — inferred by comparing the two.

**Fuzzy 2 — resource-named `NotFoundError` subtypes**
`core/errors.py`: `TaskNotFoundError`, `ProjectNotFoundError`. No
`CommentNotFoundError` yet — held-out.

**Fuzzy 3 — repetition threshold (2+ uses → extract; 1 use → inline)**
`TaskService._normalize_tags` is used in both `create_task` and
`update_tags` — that's what justifies extraction. There's no
single-use logic artificially extracted elsewhere; don't add one just to
illustrate the point, since that would itself be an inconsistent example
of the convention.

## Held-out task targets (do not implement before running the experiment)

- `ProjectService.delete_project` — currently raises `NotImplementedError`.
  This is the Explicit-1 and Explicit-2 held-out task.
- `DELETE /projects/{project_id}` — the corresponding router endpoint,
  absent from `routers/projects.py`.
- Everything under `comments` (model, repository, service, router, DTO,
  tests) — the Fuzzy-1/2/3 held-out task, and also needs Explicit-1/2/3
  applied if used as a combined exposure/held-out target later.

## Known limitation of this drop

This repo was built and syntax-checked (`python -m py_compile` on every
file) in a sandboxed environment with no network access, so `pytest`
itself could not be executed here — dependencies couldn't be installed to
run it live. Run `pytest` yourself after `pip install -r requirements.txt`
before trusting this as your frozen base; if anything fails, it's most
likely in the SQLAlchemy `StaticPool` wiring in `core/db.py` or the
`conftest.py` reset fixture, since those are the two pieces most sensitive
to exact library versions.
