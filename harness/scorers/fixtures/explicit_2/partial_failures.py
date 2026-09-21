class ProjectService:
    def delete_project(self, project_id):
        project = self.repository.get(project_id)
        if project is None:
            return Err("not found")
        if not self.can_delete(project):
            return False
        self.repository.delete(project)
        return Ok(None)
