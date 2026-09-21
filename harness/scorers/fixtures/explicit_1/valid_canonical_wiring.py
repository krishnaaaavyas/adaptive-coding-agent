from repositories.project_repository import ProjectRepository
from services.project_service import ProjectService


def get_project_service(db):
    return ProjectService(ProjectRepository(db))
