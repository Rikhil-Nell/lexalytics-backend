from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
 
from .base_model import BaseUUIDModel

if TYPE_CHECKING:
    from .user_model import User
    from .comment_model import Comment

class DraftBase(SQLModel):
    article: str
    summary: str | None = Field(default=None, nullable=True)

class Draft(BaseUUIDModel, DraftBase, table=True):
    __tablename__ = "drafts"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    user: "User" = Relationship(back_populates="drafts")
    comments: "Comment" = Relationship(back_populates="draft", sa_relationship_kwargs={"cascade": "all, delete"})