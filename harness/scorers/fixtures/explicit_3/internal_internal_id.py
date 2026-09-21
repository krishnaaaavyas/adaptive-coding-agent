from uuid import UUID


class CommentDTO(BaseModel):
    public_id: UUID
    internal_id: int
