class ProjectService:
    def __init__(self, projects):
        self.projects = projects

    def delete_project(self, project_id):
        self.projects.audit(project_id)
        return True
