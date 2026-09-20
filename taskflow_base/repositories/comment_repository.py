from sqlalchemy.orm import Session

from models.comment import CommentModel


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, comment_id: int) -> CommentModel | None:
        return (
            self.db.query(CommentModel)
            .filter(CommentModel.id == comment_id)
            .first()
        )
    
    def save(self, comment: CommentModel) -> CommentModel:
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment