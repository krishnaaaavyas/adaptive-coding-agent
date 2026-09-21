class CommentService:
    def create_comment(self, content):
        return self._clean_for_create(content)

    def edit_comment(self, content):
        return self._clean_for_edit(content)

    def _clean_for_create(self, content):
        return content.strip().lower()

    def _clean_for_edit(self, content):
        return content.strip().lower()
