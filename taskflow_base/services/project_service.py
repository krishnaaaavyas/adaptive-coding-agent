from core.errors import ServiceError, ValidationError
from core.logging import get_logger
from core.result import Err, Ok, Result
from dto.project_dto import ProjectCreateDTO
from models.project import ProjectModel

logger = get_logger(__name__)


class ProjectService:
    def __init__(self, project_repo):
        self.project_repo = project_repo

    def create_project(self, payload: ProjectCreateDTO) -> Result[ProjectModel, ServiceError]:
        errors = self._validate_create(payload)
        if errors:
            return Err(ValidationError(errors))
        project = ProjectModel(name=payload.name)
        logger.info("creating project '%s'", payload.name)
        return Ok(self.project_repo.save(project))

    def delete_project(self, project_id: int):
        raise NotImplementedError("project deletion is not implemented")

    def _validate_create(self, payload: ProjectCreateDTO) -> list[str]:
        errors = []
        if not payload.name.strip():
            errors.append("name required")
        if len(payload.name) > 100:
            errors.append("name too long")
        return errors
