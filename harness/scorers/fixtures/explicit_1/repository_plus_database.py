class ProjectService:
    def __init__(self, project_repo, db):
        self.projects = project_repo
        self.db = db

    def delete_project(self, project_id):
        self.projects.delete(project_id)
        self.db.execute("DELETE FROM projects")
