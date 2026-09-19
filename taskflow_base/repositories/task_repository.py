from sqlalchemy.orm import Session

from models.task import TaskModel


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, task: TaskModel) -> TaskModel:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get(self, task_id: int) -> TaskModel | None:
        return self.db.query(TaskModel).filter(TaskModel.id == task_id).first()

    def delete(self, task_id: int) -> bool:
        task = self.get(task_id)
        if task is None:
            return False
        self.db.delete(task)
        self.db.commit()
        return True
