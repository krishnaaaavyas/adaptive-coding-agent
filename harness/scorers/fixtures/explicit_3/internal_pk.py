from uuid import UUID


class CommentDTO(BaseModel):
    public_id: UUID
    task_id: int
    pk: int
