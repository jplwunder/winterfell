from enum import Enum
from sched import Event
import secrets

from sqlmodel import Field, Relationship, SQLModel
from uuid import UUID, uuid4
from datetime import datetime

from app.models import EventMembership, EventRole

class CheckInLog(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    ticket_id: UUID = Field(foreign_key="ticket.id")
    checked_by: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now, index=True)

class Ticket(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    attendee_id: UUID = Field(foreign_key="user.id")
    event_id: UUID = Field(foreign_key="event.id")
    ticket_code: str = Field(default_factory=lambda: secrets.token_urlsafe(12), unique=True)
    checked_in: bool = Field(default=False)
    checked_in_at: datetime | None = None
    checked_in_by: UUID | None = Field(default=None, foreign_key="user.id")
    cancelled: bool = Field(default=False)
