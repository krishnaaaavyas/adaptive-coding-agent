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
        """HELD-OUT TASK TARGET (Explicit-1 and Explicit-2).

        Deliberately unimplemented. The agent under test implements this
        method during the experiment — not the harness. A correct
        implementation: looks up the project via self.project_repo (never
        touching a Session/ORM model directly, per Explicit-1), returns
        Err(ProjectNotFoundError(...)) rather than raising if missing
        (Explicit-2), and returns Ok(None) on success.
        """
        raise NotImplementedError("held-out task: implemented by the agent under test")

    def _validate_create(self, payload: ProjectCreateDTO) -> list[str]:
        errors = []
        if not payload.name.strip():
            errors.append("name required")
        if len(payload.name) > 100:
            errors.append("name too long")
        return errors
