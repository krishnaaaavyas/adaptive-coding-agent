class CommentService:
    def create_comment(self, payload):
        errors = self._validate_input(payload)
        if errors:
            failure = ValidationError(errors)
            return Err(failure)
        return Ok(payload)

    def _validate_input(self, payload):
        if not payload.content.strip():
            return ["content required"]
        return []
