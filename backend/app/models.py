from datetime import datetime
import secrets
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class EventRole(Enum):
    attendee = "attendee"
    user = "user"


class Event(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    date: datetime = Field(index=True)
    location: str = Field(index=True)
    description: str | None = Field(default=None, index=True)

class EventCreate(SQLModel):
    name: str
    date: datetime
    location: str
    description: str | None = None


class EventMembership(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    event_id: UUID = Field(foreign_key="event.id")
    user_id: UUID = Field(foreign_key="user.id")
    role: EventRole = Field(default=EventRole.attendee, index=True)


class Ticket(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    attendee_id: UUID = Field(foreign_key="user.id")
    event_id: UUID = Field(foreign_key="event.id")
    ticket_code: str = Field(default_factory=lambda: secrets.token_urlsafe(12), unique=True)
    checked_in: bool = Field(default=False)
    checked_in_at: datetime | None = None
    checked_in_by: UUID | None = Field(default=None, foreign_key="user.id")
    cancelled: bool = Field(default=False)


class User(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: str | None = Field(default=None, index=True)
    password: str | None = Field(default=None, index=True)
    role: EventRole = Field(default=EventRole.user, index=True)


class CheckInLog(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    ticket_id: UUID = Field(foreign_key="ticket.id")
    checked_by: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now, index=True)
