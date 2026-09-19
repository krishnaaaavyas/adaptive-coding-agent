import uuid

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from core.db import Base


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    public_id = Column(String, default=lambda: str(uuid.uuid4()), unique=True, index=True)
    name = Column(String, nullable=False)

    tasks = relationship("TaskModel", back_populates="project")
