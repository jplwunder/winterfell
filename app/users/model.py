from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.attendees.model import Ticket
from app.core.roles import EventRole


class User(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(index=True)
    password: str | None = Field(default=None, index=True, nullable=True)
    tickets: list[Ticket] = Relationship(back_populates="attendee")
    is_verified: bool = Field(default=False, index=True)

    def get_role(self, event_id: UUID) -> EventRole | None:
        for ticket in self.tickets:
            if ticket.event_id == event_id:
                return ticket.role
        return None


class UserPublic(SQLModel):
    id: UUID
    name: str
    email: str | None = None
