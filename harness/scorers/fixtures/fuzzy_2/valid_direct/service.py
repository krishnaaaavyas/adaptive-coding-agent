class CommentService:
    def get_comment(self, comment_id):
        comment = self.comments.get(comment_id)
        if comment is None:
            return Err(CommentNotFoundError(comment_id))
        return Ok(comment)
