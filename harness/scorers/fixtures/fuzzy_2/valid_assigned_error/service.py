class CommentService:
    def get_comment(self, comment_id):
        comment = self.comments.get(comment_id)
        if comment is None:
            error = CommentNotFoundError(comment_id)
            return Err(error)
        return Ok(comment)
