import uuid

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from core.db import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    public_id = Column(String, default=lambda: str(uuid.uuid4()), unique=True, index=True)
    title = Column(String, nullable=False)
    priority = Column(String, default="normal")
    tags = Column(String, default="")  # comma-separated, always pre-normalized on write
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    project = relationship("ProjectModel", back_populates="tasks")
