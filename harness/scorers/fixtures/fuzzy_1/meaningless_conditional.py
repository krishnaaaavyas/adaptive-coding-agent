class CommentService:
    def create_comment(self, payload):
        errors = self._validate_create(payload)
        if errors:
            return Err(ValidationError(errors))
        return Ok(payload)

    def _validate_create(self, payload):
        if payload.author:
            return []
        return ["author required"]
