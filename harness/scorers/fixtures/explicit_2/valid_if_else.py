class ProjectService:
    def delete_project(self, project_id):
        project = self.repository.get(project_id)
        if not project:
            return Err("not found")
        else:
            self.repository.delete(project)
            return Ok(None)
