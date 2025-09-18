from pydantic import BaseModel
from uuid import UUID

class DraftCreate(BaseModel):
    article: str
    summary: str | None = None

class DraftRead(BaseModel):
    id: UUID
    article: str
    summary: str | None = None
    user_id: UUID