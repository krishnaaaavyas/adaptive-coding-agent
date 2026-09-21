class CommentService:
    def create_comment(self, payload):
        if not payload.content.strip():
            return Err(ValidationError(["content required"]))
        return Ok(payload)
