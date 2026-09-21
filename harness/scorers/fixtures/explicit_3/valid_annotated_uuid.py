from typing import Annotated
from uuid import UUID


class CommentDTO(BaseModel):
    public_id: Annotated[UUID, "public identifier"]
