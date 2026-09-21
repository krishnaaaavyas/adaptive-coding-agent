class CommentService:
    def get_comment(self, comment_id):
        return Ok(self.comments.get(comment_id))
