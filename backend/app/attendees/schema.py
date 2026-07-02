from sqlmodel import UUID, SQLModel
from backend.app.attendees.model import CheckInLog


class CheckInResponse(SQLModel):
    message: str
    check_in_log: CheckInLog

class TicketCreate(SQLModel):
    attendee_id: UUID
    event_id: UUID