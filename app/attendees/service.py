from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.attendees.model import Ticket
from app.attendees.schema import (
    CheckInLogResponse,
    TicketCreate,
    TicketList,
    TicketResponse,
)
from app.core.database import get_session
from app.core.roles import EventRole
from app.core.security import (
    get_current_user,
    get_verified_user,
    require_event_role,
)
from app.email.service import create_message, generate_ticket_email, mail
from app.events.model import Event, ParticipantList, ParticipantOut
from app.users.model import User

router = APIRouter(prefix="/attendees", tags=["attendees"])


@router.get(
    "/organizers/{event_id}",
    response_model=ParticipantList,
    status_code=status.HTTP_200_OK,
)
def list_organizers(
    event_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[
        User, Depends(require_event_role(EventRole.admin, EventRole.staff))
    ],
    require_verified: Annotated[User, Depends(get_verified_user)],
):
    statement = (
        select(User, Ticket.role)
        .join(Ticket, Ticket.attendee_id == User.id)
        .where(Ticket.event_id == event_id)
    )
    rows = session.exec(statement).all()

    organizers = [ParticipantOut(**user.model_dump(), role=role) for user, role in rows]
    return ParticipantList(users=organizers)


@router.get(
    "/participants/{event_id}",
    response_model=TicketList,
    status_code=status.HTTP_200_OK,
)
def list_participants(
    event_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    require_verified: Annotated[User, Depends(get_verified_user)],
):
    tickets = session.exec(select(Ticket).where(Ticket.event_id == event_id)).all()

    return TicketList(tickets=tickets)


@router.post("/tickets", response_model=TicketResponse)
async def create_ticket(
    ticket_payload: TicketCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    require_verified: Annotated[User, Depends(get_verified_user)],
):
    event_id = ticket_payload.event_id
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(404, "Event not found")

    attendee = session.get(User, current_user.id)
    if attendee is None:
        raise HTTPException(404, "User not found")

    existing_ticket = session.exec(
        select(Ticket).where(
            Ticket.event_id == event_id, Ticket.attendee_id == current_user.id
        )
    ).first()

    if existing_ticket:
        raise HTTPException(400, "User already has a ticket for this event")

    ticket = Ticket(
        attendee_id=current_user.id, event_id=event_id, role=EventRole.attendee
    )

    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    html_message = generate_ticket_email(
        attendee.name,
        event.name,
        event.date,
        event.location,
        ticket.ticket_code,
    )

    message = create_message(
        reciepients=[attendee.email],
        subject=f"Your Ticket for {event.name}",
        body=html_message,
    )
    await mail.send_message(message)

    check_in_log = CheckInLogResponse(
        id=ticket.id,
        ticket_code=ticket.ticket_code,
        attendee_name=attendee.name,
        checked_by_name=attendee.name,
        checked_at=datetime.now(UTC),
    )

    return TicketResponse(
        message="Ticket created successfully",
        ticket=ticket,
        check_in_log=check_in_log,
    )
