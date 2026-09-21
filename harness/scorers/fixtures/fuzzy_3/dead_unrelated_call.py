class CommentService:
    def create_comment(self, content):
        self._audit(content)
        return content

    def edit_comment(self, content):
        self._audit(content)
        return content

    def _audit(self, content):
        return content

    def _normalize_content(self, content):
        if False:
            return content.strip().lower()
        return content
