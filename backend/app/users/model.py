from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.attendees.model import Ticket
    from app.events.model import EventMembership
from app.core.roles import EventRole


class User(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: str | None = Field(default=None, index=True)
    password: str | None = Field(default=None, index=True)
    memberships: list["EventMembership"] = Relationship(back_populates="user")
    tickets: list["Ticket"] = Relationship(back_populates="attendee")

    def get_role(self, event_id: UUID) -> EventRole | None:
        for membership in self.memberships:
            if membership.event_id == event_id:
                return membership.role
        return None