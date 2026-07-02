from app.events.schema import EventCreate, EventList, EventResponse
from app.events.model import Event, EventMembership, EventRole
from sqlmodel import Session, select, SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from app.users.model import User


class EventRole(str, Enum):
    admin = "admin"
    staff = "staff"
    attendee = "attendee"

class RoleUpdate(SQLModel):
    role: EventRole


class EventMembership(SQLModel, table=True):
    event_id: UUID = Field(foreign_key="event.id", primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    role: EventRole = Field(default=EventRole.attendee, index=True)
    user: User = Relationship(back_populates="memberships")
    event: Event = Relationship(back_populates="memberships")

class Event(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    date: datetime = Field(index=True)
    location: str = Field(index=True)
    description: str | None = Field(default=None, index=True)
    memberships: list["EventMembership"] = Relationship(back_populates="event")



