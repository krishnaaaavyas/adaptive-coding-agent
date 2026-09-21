class ProjectService:
    def __init__(self, project_repo):
        self.project_repo = project_repo

    def delete_project(self, project_id):
        self.project_repo.delete(project_id)
