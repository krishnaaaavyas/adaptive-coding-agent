class ProjectService:
    def __init__(self, worker):
        self.gateway = worker

    def delete_project(self, project_id):
        return self.gateway.delete(project_id)
