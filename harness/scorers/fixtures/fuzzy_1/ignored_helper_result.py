class CommentService:
    def create_comment(self, payload):
        errors = self._validate_create(payload)
        return Ok(payload)

    def _validate_create(self, payload):
        if not payload.content.strip():
            return ["content required"]
        return []
