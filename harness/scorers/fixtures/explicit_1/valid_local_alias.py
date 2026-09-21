from repositories.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, storage: ProjectRepository):
        self.store = storage

    def delete_project(self, project_id):
        projects = self.store
        return projects.delete(project_id)
