from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel

from app.core.roles import EventRole
from app.users.model import User

if TYPE_CHECKING:
    from app.attendees.model import Ticket


class Event(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    date: datetime = Field(index=True)
    location: str = Field(index=True)
    description: str | None = Field(default=None, index=True)
    tickets: list["Ticket"] = Relationship(back_populates="event", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class ParticipantOut(SQLModel):
    id: UUID
    email: str
    role: EventRole

    class Config:
        from_attributes = True


class ParticipantList(SQLModel):
    users: list[ParticipantOut]


