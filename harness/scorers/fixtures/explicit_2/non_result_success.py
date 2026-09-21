class ProjectService:
    def delete_project(self, project_id):
        project = self.repository.get(project_id)
        if project is None:
            return Err("not found")
        self.repository.delete(project)
        return project
