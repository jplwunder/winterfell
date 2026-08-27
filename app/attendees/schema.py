from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel

from app.attendees.model import CheckInLog, Ticket


class CheckInLogResponse(SQLModel):
    id: UUID
    ticket_code: str
    attendee_name: str
    checked_by_name: str | None
    checked_at: datetime


class CheckInResponse(SQLModel):
    message: str
    check_in_log: CheckInLogResponse


class CheckInLogList(SQLModel):
    logs: list[CheckInLogResponse]


class TicketCreate(SQLModel):
    attendee_id: UUID | None = None
    event_id: UUID


class TicketResponse(SQLModel):
    message: str
    ticket: "Ticket"


class TicketList(SQLModel):
    tickets: list[Ticket]


class TicketRead(SQLModel):
    ticket: Ticket
