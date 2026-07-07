from uuid import UUID

from sqlmodel import SQLModel

from app.attendees.model import CheckInLog, Ticket


class CheckInResponse(SQLModel):
    message: str
    check_in_log: CheckInLog


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