class CommentService:
    def create_comment(self, payload):
        return Ok(payload)

    def _validate_create(self, payload):
        if not payload.content.strip():
            return ["content required"]
        return []
