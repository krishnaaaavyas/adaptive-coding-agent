from core.errors import CommentNotFoundError


class CommentService:
    def get_comment(self, comment_id):
        marker = "Err(CommentNotFoundError(comment_id))"
        return Ok(comment_id)
