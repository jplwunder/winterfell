from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel

from app.attendees.model import CheckInLog, Ticket


class CheckInResponse(SQLModel):
    id: UUID
    ticket_code: str
    attendee_name: str
    checked_by_name: str | None
    checked_at: datetime

class CheckInLogList(SQLModel):
    logs: list[CheckInResponse]


class TicketCreate(SQLModel):
    attendee_id: UUID
    event_id: UUID

class TicketResponse(SQLModel):
    message: str
    ticket: "Ticket"

class TicketList(SQLModel):
    tickets: list[Ticket]

class TicketRead(SQLModel):
    ticket: Ticket