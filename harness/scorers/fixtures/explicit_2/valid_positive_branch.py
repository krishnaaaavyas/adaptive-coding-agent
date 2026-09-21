class ProjectService:
    def delete_project(self, project_id):
        project = self.repository.get(project_id)
        if project is not None:
            self.repository.delete(project)
            return Ok(None)
        return Err("not found")
