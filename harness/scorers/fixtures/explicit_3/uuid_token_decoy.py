from uuid import UUID


class OtherDTO(BaseModel):
    public_id: UUID


class CommentDTO(BaseModel):
    public_id: str
