class CommentService:
    def create_comment(self, payload):
        problems = self._validate_comment(payload)
        if not problems:
            return Ok(payload)
        else:
            return Err(ValidationError(problems))

    def _validate_comment(self, payload):
        problems = []
        if payload.content.strip() == "":
            problems.append("content required")
        return problems
