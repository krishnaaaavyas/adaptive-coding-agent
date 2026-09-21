class CommentService:
    def create_comment(self, payload):
        errors = self._validate_create(payload)
        if errors:
            return Err(ValidationError(errors))
        if not payload.content.strip():
            return Err(ValidationError(["content required"]))
        return Ok(payload)

    def _validate_create(self, payload):
        if not payload.content.strip():
            return ["content required"]
        return []
