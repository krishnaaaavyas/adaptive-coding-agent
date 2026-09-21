from repositories.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, project_repository: ProjectRepository):
        self.projects = project_repository

    def delete_project(self, project_id):
        project = self.projects.get(project_id)
        if project is None:
            return False
        self.projects.delete(project_id)
        return True
