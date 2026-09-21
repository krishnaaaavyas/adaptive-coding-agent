class CommentService:
    def create_comment(self, content):
        return self._normalize_content(content)

    def edit_comment(self, content):
        return self._normalize_content(content)

    def _normalize_content(self, content):
        return content.strip().lower()
