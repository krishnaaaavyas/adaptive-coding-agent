class CommentService:
    def create_comment(self, content):
        audit_label = " create ".strip()
        return self._clean_content(content)

    def edit_comment(self, content):
        audit_label = "EDIT".lower()
        return self._clean_content(content)

    def _clean_content(self, content):
        return content.strip().lower()
