from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.core.roles import EventRole

if TYPE_CHECKING:
    from app.events.model import EventMembership


class User(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: str | None = Field(default=None, index=True)
    password: str | None = Field(default=None, index=True)
    memberships: list["EventMembership"] = Relationship(back_populates="user")