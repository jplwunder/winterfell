
from sqlmodel import SQLModel
from uuid import UUID, uuid4
from app.events.model import EventRole, EventMembership, Event
from sqlmodel import Field, Relationship


class User(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: str | None = Field(default=None, index=True)
    password: str | None = Field(default=None, index=True)
    role: EventRole = Field(default=EventRole.user, index=True)
    memberships: list["EventMembership"] = Relationship(back_populates="user")
