class ProjectService:
    def __init__(self, projects):
        self.projects = projects

    def delete_project(self, project_id):
        if project_id:
            return True
        else:
            return False
        self.projects.delete(project_id)
