import hashlib
from datetime import datetime, timezone
from typing import Dict
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.roles import EventRole
from app.attendees.model import CheckInLog, Ticket
from app.attendees.schema import CheckInResponse
from app.events.model import EventMembership
from app.users.model import User
from app.users.schema import UserCreate, UserList, UserResponse
from app.core.security import generate_ticket_code, get_current_user, is_valid_email, require_role

router = APIRouter(prefix="/attendees", tags=["attendees"])

@router.get("/{event_id}", response_model=UserList, status_code=status.HTTP_200_OK)
def list_participants(event_id: UUID, session: Session = Depends(require_role(EventRole.admin, EventRole.staff))):
    statement = select(User, EventMembership.role).join(EventMembership, EventMembership.user_id == User.id).where(EventMembership.event_id == event_id)
    attendees = session.exec(statement).all()
    return UserList(users=attendees)


@router.get("/by-code/{ticket_code}", response_model=User, status_code=status.HTTP_200_OK)
def read_attendee_by_code(ticket_code: str, session: Session = Depends(require_role(EventRole.admin, EventRole.staff)), current_user: User = Depends(get_current_user)):
    attendee = session.exec(
        select(User).where(User.ticket_code == ticket_code)
    ).one_or_none()
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    return attendee


@router.get("/{attendee_id}", response_model=User, status_code=status.HTTP_200_OK)
def read_attendee(attendee_id: UUID, session: Session = Depends(require_role(EventRole.admin, EventRole.staff)), current_user: User = Depends(get_current_user)):
    attendee = session.get(User, attendee_id)
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    return attendee


@router.post("/{ticket_code}/check-in", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def check_in_attendee(ticket_code: str, session: Session = Depends(require_role(EventRole.admin, EventRole.staff)), current_user: User = Depends(require_role(EventRole.admin, EventRole.staff))):
    attendee = session.exec(
        select(User).where(User.ticket_code == ticket_code)
    ).one_or_none()
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    if attendee.checked_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendee already checked in at " + attendee.checked_in_at.isoformat()
        )
    attendee.checked_in = True
    attendee.checked_in_at = datetime.now(timezone.utc)
    attendee.checked_in_by = current_user.id

    log = CheckInLog(id=uuid4(), attendee_id=attendee.id, user_id=current_user.id)
    session.add(attendee)
    session.add(log)
    session.commit()
    session.refresh(attendee)
    return {
        "message": "Attendee checked in successfully",
        "check_in_log": log
    }


@router.delete("/{attendee_id}", response_model=CheckInResponse, status_code=status.HTTP_200_OK)
def delete_attendee(attendee_id: UUID, session: Session = Depends(require_role(EventRole.admin, EventRole.staff)), current_user: User = Depends(get_current_user)):
    attendee = session.exec(select(User).where(User.id == attendee_id and User.id == current_user.id)).one_or_none()
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    session.delete(attendee)
    session.commit()
    return {"message": "Attendee check-in deleted successfully"}

def create_ticket(
    event_id: UUID,
    attendee_id: UUID,
    session: Session = Depends(get_session)
):

    membership = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == attendee_id
        )
    ).first()

    if not membership:
        raise HTTPException(
            404,
            "User is not in this event"
        )

    if membership.role != EventRole.attendee:
        raise HTTPException(
            400,
            "Only attendees can have tickets"
        )

    ticket = Ticket(
        attendee_id=attendee_id,
        event_id=event_id
    )

    session.add(ticket)
    session.commit()

