from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.db import get_db
from core.errors import NotFoundError, ValidationError
from core.result import Err, Ok
from dto.task_dto import TaskCreateDTO, TaskDTO
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from services.task_service import TaskService

router = APIRouter()


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(db), ProjectRepository(db))


def handle_result(result, to_dto=None):
    """Shared Result -> HTTP translation. Routers never inspect ORM models
    or sessions directly (Explicit-1) — this is the only place a Result's
    error gets turned into an HTTP status."""
    if isinstance(result, Ok):
        return to_dto(result.value) if to_dto else result.value
    error = result.error
    if isinstance(error, NotFoundError):
        raise HTTPException(status_code=404, detail=str(error))
    if isinstance(error, ValidationError):
        raise HTTPException(status_code=422, detail=error.errors)
    raise HTTPException(status_code=500, detail=str(error))


@router.post("/tasks", response_model=TaskDTO)
def create_task(payload: TaskCreateDTO, service: TaskService = Depends(get_task_service)):
    return handle_result(service.create_task(payload), TaskDTO.from_model)
