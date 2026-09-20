from core.errors import ProjectNotFoundError, ServiceError, TaskNotFoundError, ValidationError
from core.logging import get_logger
from core.result import Err, Ok, Result
from dto.task_dto import TaskCreateDTO
from models.task import TaskModel

logger = get_logger(__name__)


class TaskService:
    def __init__(self, task_repo, project_repo):
        self.task_repo = task_repo
        self.project_repo = project_repo

    def create_task(self, payload: TaskCreateDTO) -> Result[TaskModel, ServiceError]:
        errors = self._validate_create(payload)
        if errors:
            return Err(ValidationError(errors))

        project = self.project_repo.get(payload.project_id)
        if project is None:
            return Err(ProjectNotFoundError(payload.project_id))

        task = TaskModel(
            title=payload.title,
            project_id=payload.project_id,
            tags=self._normalize_tags(payload.tags),
        )
        logger.info("creating task '%s' in project %s", payload.title, payload.project_id)
        return Ok(self.task_repo.save(task))

    def update_tags(self, task_id: int, tags: list[str]) -> Result[TaskModel, ServiceError]:
        task = self.task_repo.get(task_id)
        if task is None:
            return Err(TaskNotFoundError(task_id))
        task.tags = self._normalize_tags(tags)
        logger.info("updating tags for task %s", task_id)
        return Ok(self.task_repo.save(task))

    def _validate_create(self, payload: TaskCreateDTO) -> list[str]:
        errors = []
        if not payload.title.strip():
            errors.append("title required")
        if len(payload.title) > 200:
            errors.append("title too long")
        return errors

    def _normalize_tags(self, tags: list[str]) -> str:
        cleaned = sorted(set(t.strip().lower() for t in tags if t.strip()))
        return ",".join(cleaned)
