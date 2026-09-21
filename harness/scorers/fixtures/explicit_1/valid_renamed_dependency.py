from repositories.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, projects: ProjectRepository):
        self.gateway = projects

    def delete_project(self, project_id):
        return self.gateway.delete(project_id)
