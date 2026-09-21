class CommentService:
    def create_comment(self, payload):
        errors = self._validate_author(payload)
        if errors:
            return Err(ValidationError(errors))
        if not payload.content.strip():
            return Err(ValidationError(["content required"]))
        return Ok(payload)

    def _validate_author(self, payload):
        if not payload.author:
            return ["author required"]
        return []
