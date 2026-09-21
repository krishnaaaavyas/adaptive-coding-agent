class ProjectService:
    def delete_project(self, project_id):
        project = self.repository.get(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)
        self.repository.delete(project)
        return Ok(None)
