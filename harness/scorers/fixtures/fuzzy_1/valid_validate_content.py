class CommentService:
    def create_comment(self, content):
        if self._validate_content(content):
            return Err(ValidationError(["content required"]))
        return Ok(content)

    def _validate_content(self, content):
        return not content.strip()
