class CommentService:
    def get_comment(self, comment_id):
        return Ok(comment_id)
        return Err(CommentNotFoundError(comment_id))
