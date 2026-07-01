from datetime import datetime
from typing import List
from uuid import UUID

from sqlmodel import SQLModel

from app.models import CheckInLog, Event, User


class TicketCreate(SQLModel):
    attendee_id: UUID
    event_id: UUID


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None


class UserCreate(SQLModel):
    name: str
    age: int | None = None
    email: str | None = None
    password: str | None = None


class CheckInLogCreate(SQLModel):
    attendee_id: UUID
    ticket_id: UUID
    user_id: UUID
    event_id: UUID


class EventCreate(SQLModel):
    name: str
    date: datetime
    location: str
    description: str | None = None


class UserList(SQLModel):
    users: List[User]


class UserResponse(SQLModel):
    message: str
    user: User


class EventList(SQLModel):
    events: List[Event]


class EventResponse(SQLModel):
    message: str
    event: Event


class CheckInResponse(SQLModel):
    message: str
    check_in_log: CheckInLog
