from uuid import UUID

from pydantic import BaseModel


class TaskCreateDTO(BaseModel):
    title: str
    project_id: int
    tags: list[str] = []


class TaskDTO(BaseModel):
    public_id: UUID
    title: str
    priority: str
    tags: list[str]

    @staticmethod
    def from_model(task) -> "TaskDTO":
        return TaskDTO(
            public_id=task.public_id,
            title=task.title,
            priority=task.priority,
            tags=[t for t in task.tags.split(",") if t],
        )
