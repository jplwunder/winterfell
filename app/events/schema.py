from datetime import datetime
from uuid import UUID

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


class EventWithRole(SQLModel):
    id: UUID
    name: str
    date: datetime
    location: str
    description: str | None = None
    role: EventRole


class EventList(SQLModel):
    events: list[EventWithRole]


class EventResponse(SQLModel):
    message: str
    event: EventRead
