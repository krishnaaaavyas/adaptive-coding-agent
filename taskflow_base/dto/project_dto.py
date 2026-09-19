from uuid import UUID

from pydantic import BaseModel


class ProjectCreateDTO(BaseModel):
    name: str


class ProjectDTO(BaseModel):
    public_id: UUID
    name: str

    @staticmethod
    def from_model(project) -> "ProjectDTO":
        return ProjectDTO(public_id=project.public_id, name=project.name)
