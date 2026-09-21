class CommentService:
    def get_comment(self, comment_id):
        if comment_id < 0:
            return Err(CommentNotFoundError(comment_id))
        return Ok(comment_id)
