"""Service-layer error types."""


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
