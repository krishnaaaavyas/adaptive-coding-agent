from sqlalchemy.orm import Session

from models.project import ProjectModel


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, project: ProjectModel) -> ProjectModel:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get(self, project_id: int) -> ProjectModel | None:
        return self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()

    def delete(self, project_id: int) -> bool:
        project = self.get(project_id)
        if project is None:
            return False
        self.db.delete(project)
        self.db.commit()
        return True
