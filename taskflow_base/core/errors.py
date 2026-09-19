"""Base ServiceError plus resource-named subtypes.

Fuzzy-2 convention (see pilot spec): each resource defines its own
<Resource>NotFoundError subtype, carrying the resource's identifying
field, subclassing the shared NotFoundError. Establish it here for
`tasks` and `projects` — `comments` deliberately does not have one yet;
that's the held-out inference target.
"""


class ServiceError(Exception):
    """Base for all expected service-layer failures. These are returned
    as Err(...), never raised, per Explicit-2."""


class ValidationError(ServiceError):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"validation failed: {errors}")


class NotFoundError(ServiceError):
    pass


class TaskNotFoundError(NotFoundError):
    def __init__(self, task_id):
        self.task_id = task_id
        super().__init__(f"task {task_id} not found")


class ProjectNotFoundError(NotFoundError):
    def __init__(self, project_id):
        self.project_id = project_id
        super().__init__(f"project {project_id} not found")
