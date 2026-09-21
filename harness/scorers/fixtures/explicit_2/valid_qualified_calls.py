class ProjectService:
    def delete_project(self, project_id):
        project = self.repository.get(project_id)
        if project == None:
            return result.Err("not found")
        self.repository.delete(project)
        return result.Ok(None)
