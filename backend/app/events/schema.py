
from datetime import datetime
from sched import Event
from typing import List

from sqlmodel import SQLModel


class EventCreate(SQLModel):
    name: str
    date: datetime
    location: str
    description: str | None = None

class EventList(SQLModel):
    events: List[Event]

class EventResponse(SQLModel):
    message: str
    event: Event

class EventCreate(SQLModel):
    name: str
    date: datetime
    location: str
    description: str | None = None
