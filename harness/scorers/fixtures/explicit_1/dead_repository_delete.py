class ProjectService:
    def __init__(self, gateway):
        self.gateway = gateway

    def delete_project(self, project_id):
        return False
        self.gateway.delete(project_id)
