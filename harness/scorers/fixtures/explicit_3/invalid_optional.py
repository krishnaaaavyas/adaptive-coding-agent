from typing import Optional
from uuid import UUID


class CommentDTO(BaseModel):
    public_id: Optional[UUID]
