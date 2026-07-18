import secrets
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel
from app.events.model import Event
from app.users.model import User
from app.core.roles import EventRole

class Ticket(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    attendee_id: UUID = Field(foreign_key="user.id")
    event_id: UUID = Field(foreign_key="event.id")
    ticket_code: str = Field(default_factory=lambda: secrets.token_urlsafe(12), unique=True)
    checked_in: bool = Field(default=False)
    checked_in_at: datetime | None = None
    cancelled: bool = Field(default=False)
    attendee: User = Relationship(back_populates="tickets")
    event: Event = Relationship(back_populates="tickets")
    check_in_logs: list["CheckInLog"] = Relationship(back_populates="ticket", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    role: EventRole = Field(default=EventRole.attendee, index=True)  # Default role is "attendee"

class CheckInLog(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    ticket_id: UUID = Field(foreign_key="ticket.id")
    checked_by: UUID = Field(foreign_key="user.id")
    checked_at: datetime = Field(default_factory=datetime.now, index=True)
    ticket: Ticket = Relationship(back_populates="check_in_logs")
