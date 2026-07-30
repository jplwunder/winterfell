from asyncio import events
from datetime import datetime, timezone
import hashlib
from typing import Dict
from uuid import UUID, uuid4
from sqlalchemy.orm import aliased

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.roles import EventRole
from app.core.security import get_current_user, require_event_role, require_verified_user
from app.events.model import Event
from app.events.schema import EventCreate, EventList, EventResponse, RoleUpdate
from app.core.security import require_role
from app.users.model import User
from app.attendees.model import CheckInLog, Ticket
from app.attendees.schema import CheckInLogList, CheckInLogResponse, CheckInResponse
from app.email.service import create_message, generate_staff_added_email, mail


Attendee = aliased(User)
Operator = aliased(User)

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user), require_verified: User = Depends(require_verified_user)):
	event = Event(id=uuid4(), **event.model_dump())
	existing_event = session.exec(select(Event).where(Event.id == event.id, Event.deleted == False)).first()
	if existing_event:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Event already exists"
		)
	session.add(event)
	session.commit()
	session.refresh(event)

	owner_ticket = Ticket(event_id=event.id, attendee_id=current_user.id, role=EventRole.admin, checked_in=True, checked_in_at=datetime.now(timezone.utc))
	session.add(owner_ticket)
	session.commit()
	return {
		"message": "Event created successfully",
		"event": event
	}


@router.post("/{event_id}/addstaff/{user_id}", response_model=Event, status_code=status.HTTP_200_OK)
async def add_staff(user_id: UUID, event_id: UUID, session: Session = Depends(get_session), current_user: User = Depends(require_role(EventRole.admin)), require_verified: User = Depends(require_verified_user)):
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
	existing_ticket = session.exec(
		select(Ticket).where(
			Ticket.event_id == event.id,
			Ticket.attendee_id == staff.id
		)
	).first()
	if existing_ticket and existing_ticket.role != EventRole.attendee:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="A staff member with this user ID already exists for this event"
		)
	if existing_ticket and existing_ticket.role == EventRole.attendee:
		existing_ticket.role = EventRole.staff
		session.add(existing_ticket)
		session.commit()
		return {
			"message": "User role updated to staff successfully",
			"event": event
		}
	ticket = Ticket(event_id=event.id, attendee_id=staff.id, role=EventRole.staff)
	session.add(ticket)
	session.commit()

	html_message = generate_staff_added_email(staff.name, event.name, event.date, event.location)

	message = create_message(
			reciepients=[staff.email],
			subject=f"Your Role in {event.name}",
			body=html_message
		)
	
	await mail.send_message(message)

	return {
		"message": "Staff member added to event successfully",
		"event": event
	}


@router.get("/", response_model=EventList, status_code=status.HTTP_200_OK)
def list_events(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
	statement = (
		select(Event, Ticket.role)
		.join(Ticket, Ticket.event_id == Event.id)
		.where(Ticket.attendee_id == current_user.id, Event.deleted == False)
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


@router.post("/{event_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
def delete_event(event_id: UUID, session: Session = Depends(get_session), current_user: User = Depends(get_current_user), require_verified: User = Depends(require_verified_user), admin_check: User = Depends(require_event_role(EventRole.admin))):
	statement = select(Event).join(Ticket, Ticket.event_id == Event.id).where(Event.id == event_id, Ticket.attendee_id == current_user.id)
	event = session.exec(statement).one_or_none()
	if event is None:
		raise HTTPException(
			status_code=404,
			detail="Event not found"
		)
	event.deleted = True
	session.add(event)
	session.commit()
	return {"message": "Event deleted successfully"}

@router.post("/{event_id}/check-in/{ticket_code}", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def check_in_attendee(event_id: UUID, ticket_code: str, session: Session = Depends(get_session), current_user: User = Depends(require_role(EventRole.admin, EventRole.staff)), require_verified: User = Depends(require_verified_user)):
    attendee = session.exec(
        select(Ticket).where(Ticket.ticket_code == ticket_code, Ticket.event_id == event_id)
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
    	"check_in_log": {
        	"id": log.id,
        	"ticket_code": attendee.ticket_code,
        	"attendee_name": attendee.attendee.name,
        	"checked_by_name": current_user.name,
        	"checked_at": log.checked_at,
    	}
    }

@router.get("/{event_id}/check-in-logs", response_model=CheckInLogList, status_code=status.HTTP_200_OK)
def get_check_in_logs(event_id: UUID, session: Session = Depends(get_session), current_user: User = Depends(require_role(EventRole.admin, EventRole.staff)), require_verified: User = Depends(require_verified_user)):
	logs = session.exec(
    select(
        CheckInLog.id,
        Ticket.ticket_code,
        Attendee.name.label("attendee_name"),
        Operator.name.label("checked_by_name"),
        CheckInLog.checked_at,
    )
    .join(Ticket, Ticket.id == CheckInLog.ticket_id)
    .join(Attendee, Attendee.id == Ticket.attendee_id)
    .join(Operator, Operator.id == CheckInLog.checked_by)
    .where(Ticket.event_id == event_id)
	).all()
	return CheckInLogList(
    logs=[
        CheckInLogResponse(
            id=row.id,
            ticket_code=row.ticket_code,
            attendee_name=row.attendee_name,
            checked_by_name=row.checked_by_name,
            checked_at=row.checked_at,
        )
        for row in logs
    ]
)