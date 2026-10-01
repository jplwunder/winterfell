from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import ConfigDict, field_serializer
from sqlmodel import Field, Relationship, SQLModel

from app.core.roles import EventRole

if TYPE_CHECKING:
    from app.attendees.model import Ticket


class Event(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    date: datetime = Field(index=True)
    location: str = Field(index=True)
    description: str | None = Field(default=None, index=True)
    tickets: list[Ticket] = Relationship(
        back_populates="event", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    deleted: bool = Field(default=False, index=True)

    @field_serializer("date")
    @staticmethod
    def serialize_date(value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat()


class ParticipantOut(SQLModel):
    id: UUID
    email: str
    role: EventRole

    model_config = ConfigDict(from_attributes=True)


class ParticipantList(SQLModel):
    users: list[ParticipantOut]
