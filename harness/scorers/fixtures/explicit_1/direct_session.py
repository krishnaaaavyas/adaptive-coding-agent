class ProjectService:
    def __init__(self, session):
        self.session = session

    def delete_project(self, project_id):
        project = self.session.query(Project).get(project_id)
        self.session.delete(project)
        self.session.commit()
