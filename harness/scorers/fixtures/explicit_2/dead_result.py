class ProjectService:
    def delete_project(self, project_id):
        return None
        if project_id is None:
            return Err("not found")
        return Ok(None)
