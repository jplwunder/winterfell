import hashlib
from typing import Dict
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from backend.app.core.database import SessionDep
from app.models import Event, Event, EventCreate, EventMembership, EventRole, User, RoleUpdate
from app.schemas import EventCreate, EventList, EventResponse
from backend.app.core.security import get_current_user

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, session: SessionDep, current_user: User = Depends(get_current_user)):
    event = Event(id=uuid4(), **event.model_dump())
    existing_event = session.exec(select(Event).where(Event.name == event.name)).first()
    if existing_event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event already exists"
        )
    session.add(event)
    session.commit()
    session.refresh(event)

    membership = EventMembership(event_id=event.id, user_id=current_user.id, role=EventRole.owner)
    session.add(membership)
    session.commit()
    return {
        "message": "Event created successfully",
        "event": event
    }

@router.post("/{event_id}/join", response_model=Event, status_code=status.HTTP_200_OK)
def join_event(event_id: UUID, session: SessionDep, current_user: User = Depends(get_current_user)):
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    attendee = session.get(User, current_user.id)
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    existing_membership = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event.id,
            EventMembership.user_id == attendee.id
        )
    ).first()
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendee already a member of this event"
        )
    membership = EventMembership(event_id=event.id, user_id=attendee.id, role=EventRole.attendee)
    session.add(membership)
    session.commit()
    return {
        "message": "Attendee added to event successfully",
        "event": event
    }

@router.patch("/{event_id}/members/{user_id}/role")
def change_member_role(
    event_id: UUID,
    user_id: UUID,
    role_update: RoleUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):

    # Check if current user is admin/owner
    current_membership = session.exec(
        select(EventMembership).where(
            EventMembership.user_id == current_user.id,
            EventMembership.event_id == event_id
        )
    ).first()

    if not current_membership:
        raise HTTPException(403, "Not a member of this event")

    if current_membership.role != EventRole.owner:
        raise HTTPException(403, "Not allowed")

    # Find target user membership
    membership = session.exec(
        select(EventMembership).where(
            EventMembership.user_id == user_id,
            EventMembership.event_id == event_id
        )
    ).first()

    if not membership:
        raise HTTPException(404, "User not in event")

    # Update role
    membership.role = role_update.role

    session.add(membership)
    session.commit()
    session.refresh(membership)

    return {
        "message": "Role updated successfully"
    }

@router.get("/", response_model=EventList, status_code=status.HTTP_200_OK)
def list_events(session: SessionDep, current_user: User = Depends(get_current_user)):
    events = session.exec(select(Event).where(EventMembership.event_id == Event.id and EventMembership.user_id == current_user.id)).all()
    return EventList(events=events)

@router.get("/{event_id}", response_model=Event, status_code=status.HTTP_200_OK)
def read_event(event_id: UUID, session: SessionDep):
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )
    return event

@router.delete("/{event_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
def delete_event(event_id: UUID, session: SessionDep, current_user: User = Depends(get_current_user)):
    event = session.exec(select(Event).where(Event.id == event_id and EventMembership.user_id == current_user.id)).one_or_none()
    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )
    session.delete(event)
    session.commit()
    return {"message": "Event deleted successfully"}
