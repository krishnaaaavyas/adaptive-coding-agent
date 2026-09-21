class CommentService:
    def create_comment(self, content):
        cleaned = self._clean_content(content)
        return cleaned

    def edit_comment(self, content):
        cleaned = self._clean_content(content)
        return cleaned

    def _clean_content(self, content):
        return content.lower().strip()
