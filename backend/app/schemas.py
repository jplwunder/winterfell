from datetime import datetime
from typing import List
from uuid import UUID

from sqlmodel import SQLModel

from app.models import CheckInLog, Event, User


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None

class CheckInLogCreate(SQLModel):
    attendee_id: UUID
    ticket_id: UUID
    user_id: UUID
    event_id: UUID