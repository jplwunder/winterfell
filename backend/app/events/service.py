from asyncio import events
from datetime import datetime, timezone
import hashlib
from typing import Dict
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.roles import EventRole
from app.core.security import get_current_user, require_event_role
from app.events.model import Event, EventMembership
from app.events.schema import EventCreate, EventList, EventResponse, RoleUpdate
from app.core.security import require_role
from app.users.model import User
from app.attendees.model import CheckInLog, Ticket
from app.attendees.schema import CheckInResponse, TicketList, TicketResponse, TicketRead

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
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

	membership = EventMembership(event_id=event.id, user_id=current_user.id, role=EventRole.admin)
	session.add(membership)
	session.commit()
	return {
		"message": "Event created successfully",
		"event": event
	}


@router.post("/{event_id}/addstaff/{user_id}", response_model=Event, status_code=status.HTTP_200_OK)
def add_staff(user_id: UUID, event_id: UUID, session: Session = Depends(get_session), current_user: User = Depends(require_role(EventRole.admin))):
	event = session.get(Event, event_id)
	if event is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Event not found"
		)
	staff = session.get(User, user_id)
	if staff is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="User not found"
		)
	existing_membership = session.exec(
		select(EventMembership).where(
			EventMembership.event_id == event.id,
			EventMembership.user_id == staff.id
		)
	).first()
	if existing_membership and existing_membership.role == EventRole.admin:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Admin already a member of this event"
		)
	
	membership = EventMembership(event_id=event.id, user_id=staff.id, role=EventRole.staff)
	session.add(membership)
	session.commit()
	return {
		"message": "Staff member added to event successfully",
		"event": event
	}


@router.get("/", response_model=EventList, status_code=status.HTTP_200_OK)
def list_events(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
	statement = (
		select(Event, EventMembership.role)
		.join(EventMembership, EventMembership.event_id == Event.id)
		.where(EventMembership.user_id == current_user.id)
	)
	results = session.exec(statement).all()
	events = [
		{
			"id": event.id,
			"name": event.name,
			"date": event.date,
			"location": event.location,
			"description": event.description,
			"role": role,
		}
		for event, role in results
	]
	return EventList(events=events)


@router.get("/{event_id}", response_model=Event, status_code=status.HTTP_200_OK)
def read_event(event_id: UUID, session: Session = Depends(get_session)):
	event = session.get(Event, event_id)
	if event is None:
		raise HTTPException(
			status_code=404,
			detail="Event not found"
		)
	return event


@router.delete("/{event_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
def delete_event(event_id: UUID, session: Session = Depends(get_session), current_user: User = Depends(get_current_user), admin_check: User = Depends(require_event_role(EventRole.admin))):
	statement = select(Event).join(EventMembership, EventMembership.event_id == Event.id).where(Event.id == event_id, EventMembership.user_id == current_user.id)
	event = session.exec(statement).one_or_none()
	if event is None:
		raise HTTPException(
			status_code=404,
			detail="Event not found"
		)
	session.delete(event)
	session.commit()
	return {"message": "Event deleted successfully"}

@router.post("/{ticket_code}/check-in", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def check_in_attendee(ticket_code: str, session: Session = Depends(get_session), current_user: User = Depends(require_role(EventRole.admin, EventRole.staff))):
    attendee = session.exec(
        select(Ticket).where(Ticket.ticket_code == ticket_code)
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

    log = CheckInLog(id=uuid4(), ticket_id=attendee.id, checked_by=current_user.id)
    session.add(attendee)
    session.add(log)
    session.commit()
    session.refresh(attendee)
    return {
        "message": "Attendee checked in successfully",
        "check_in_log": log
    }