import hashlib
from datetime import datetime, timezone
from typing import Dict
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.roles import EventRole
from app.attendees.model import CheckInLog, Ticket
from app.attendees.schema import CheckInResponse, TicketList, TicketResponse, TicketRead
from app.events.model import Event, ParticipantList, ParticipantOut
from app.users.model import User
from app.users.schema import UserCreate, UserList, UserResponse
from app.core.security import generate_ticket_code, get_current_user, is_valid_email, require_role

router = APIRouter(prefix="/attendees", tags=["attendees"])

@router.get("/{event_id}", response_model=ParticipantList, status_code=status.HTTP_200_OK)
def list_organizers(
    event_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(EventRole.admin, EventRole.staff)),
):
    statement = (
        select(User, Ticket.role)
        .join(Ticket, Ticket.attendee_id == User.id)
        .where(Ticket.event_id == event_id)
    )
    rows = session.exec(statement).all()

    organizers = [
        ParticipantOut(**user.model_dump(), role=role)
        for user, role in rows
    ]
    return ParticipantList(users=organizers)

@router.post("/{event_id}", response_model=TicketList, status_code=status.HTTP_200_OK)
def list_participants(
    event_id:UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    tickets = session.exec(
        select(Ticket)
        .where(Ticket.event_id == event_id)
    ).all()

    return TicketList(tickets=tickets)


@router.get(
    "/events/{event_id}/tickets/{ticket_code}",
    response_model=TicketResponse,
)
def get_participant_by_ticket_code(
    event_id: UUID,
    ticket_code: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        require_role(EventRole.admin, EventRole.staff)
    ),
):
    ticket = session.exec(
        select(Ticket).where(
            Ticket.event_id == event_id,
            Ticket.ticket_code == ticket_code,
        )
    ).one_or_none()

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return TicketResponse(
        message="Ticket retrieved successfully",
        ticket=ticket,
    )


@router.get("/{attendee_id}", response_model=User, status_code=status.HTTP_200_OK)
def read_attendee(attendee_id: UUID, session: Session = Depends(get_session), current_user: User = Depends(require_role(EventRole.admin, EventRole.staff))):
    attendee = session.get(User, attendee_id)
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    return attendee

@router.delete("/{attendee_id}", response_model=CheckInResponse, status_code=status.HTTP_200_OK)
def delete_attendee(attendee_id: UUID, session: Session = Depends(get_session), current_user: User = Depends(require_role(EventRole.admin, EventRole.staff))):
    attendee = session.exec(select(User).where(User.id == attendee_id and User.id == current_user.id)).one_or_none()
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    session.delete(attendee)
    session.commit()
    return {"message": "Attendee check-in deleted successfully"}


@router.post("/", response_model=TicketResponse)
def create_ticket(
    event_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(404, "Event not found")

    attendee = session.get(User, current_user.id)
    if attendee is None:
        raise HTTPException(404, "User not found")

    existing_ticket = session.exec(
        select(Ticket).where(
            Ticket.event_id == event_id,
            Ticket.attendee_id == current_user.id
        )
    ).first()

    if existing_ticket:
        raise HTTPException(
            400,
            "User already has a ticket for this event"
        )

    ticket = Ticket(
        attendee_id=current_user.id,
        event_id=event_id,
        role=EventRole.attendee
    )

    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    return TicketResponse(
        message="Ticket created successfully",
        ticket=ticket
    )
