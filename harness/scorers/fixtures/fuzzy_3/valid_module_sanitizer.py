def canonicalize_text(content):
    return content.lstrip().rstrip().casefold()


class CommentService:
    def create_comment(self, content):
        return canonicalize_text(content)

    def edit_comment(self, content):
        return canonicalize_text(content)
