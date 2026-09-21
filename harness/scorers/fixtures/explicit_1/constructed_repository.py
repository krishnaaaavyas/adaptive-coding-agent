class ProjectService:
    def __init__(self, db):
        self.db = db

    def delete_project(self, project_id):
        projects = ProjectRepository(self.db)
        return projects.delete(project_id)
