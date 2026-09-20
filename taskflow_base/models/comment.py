from sqlalchemy import Column, Integer, String

from database import Base


class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)