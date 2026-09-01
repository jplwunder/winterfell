from datetime import UTC, datetime
from uuid import UUID

from pydantic import field_serializer
from sqlmodel import SQLModel

from app.core.roles import EventRole


class RoleUpdate(SQLModel):
    role: EventRole


class EventCreate(SQLModel):
    name: str
    date: datetime
    location: str
    description: str | None = None


class EventRead(SQLModel):
    id: UUID
    name: str
    date: datetime
    location: str
    description: str | None = None

    @field_serializer("date")
    @staticmethod
    def serialize_date(value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat()


class EventWithRole(SQLModel):
    id: UUID
    name: str
    date: datetime
    location: str
    description: str | None = None
    role: EventRole

    @field_serializer("date")
    @staticmethod
    def serialize_date(value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat()


class EventList(SQLModel):
    events: list[EventWithRole]


class EventResponse(SQLModel):
    message: str
    event: EventRead
