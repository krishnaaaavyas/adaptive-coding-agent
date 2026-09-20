from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.db import get_db
from dto.project_dto import ProjectCreateDTO, ProjectDTO
from repositories.project_repository import ProjectRepository
from routers.tasks import handle_result
from services.project_service import ProjectService

router = APIRouter()


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(ProjectRepository(db))


@router.post("/projects", response_model=ProjectDTO)
def create_project(payload: ProjectCreateDTO, service: ProjectService = Depends(get_project_service)):
    return handle_result(service.create_project(payload), ProjectDTO.from_model)
