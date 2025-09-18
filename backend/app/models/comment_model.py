from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID

from .base_model import BaseUUIDModel

if TYPE_CHECKING:
    from .draft_model import Draft

class CommentBase(SQLModel):
    comment: str
    sentiment: str

class Comment(BaseUUIDModel, CommentBase, table=True):
    __tablename__ = "comments"

    draft_id: UUID = Field(foreign_key="drafts.id", index=True)
    draft: "Draft" = Relationship(back_populates="comments")