from enum import Enum


class EventRole(str, Enum):
    admin = "admin"
    staff = "staff"
    attendee = "attendee"
