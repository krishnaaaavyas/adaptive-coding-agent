class CommentService:
    def create_comment(self, content):
        return content

    def edit_comment(self, content):
        return self._clean_content(content)

    def _clean_content(self, content):
        return content.strip().lower()
