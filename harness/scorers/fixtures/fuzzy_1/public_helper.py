class CommentService:
    def create_comment(self, content):
        if self.check_content(content):
            return Err(ValidationError(["content required"]))
        return Ok(content)

    def check_content(self, content):
        return not content.strip()
