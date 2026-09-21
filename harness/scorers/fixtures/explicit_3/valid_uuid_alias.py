from uuid import UUID as PublicUUID


class CommentDTO(BaseModel):
    public_id: PublicUUID
