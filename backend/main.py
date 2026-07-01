import os
from datetime import datetime, timedelta, timezone
import secrets
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from uuid import UUID, uuid4
from typing import Annotated, Dict, List
from sqlmodel import Field, Session, SQLModel, create_engine, select, text
import hashlib
import jwt
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from pathlib import Path
from email_validator import validate_email, EmailNotValidError
from enum import Enum

load_dotenv()
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Event(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    date: datetime = Field(index=True)
    location: str = Field(index=True)
    description: str | None = Field(default=None, index=True)

class EventRole(Enum):
    attendee = "attendee"
    user = "user"

class EventMembership(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    event_id: UUID = Field(foreign_key="event.id")
    user_id: UUID = Field(foreign_key="user.id")
    role: EventRole = Field(default=EventRole.attendee, index=True)

class Ticket(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    attendee_id: UUID = Field(foreign_key="user.id")
    event_id: UUID = Field(foreign_key="event.id")
    ticket_code: str = Field(default_factory=lambda: secrets.token_urlsafe(12), unique=True)
    checked_in: bool = Field(default=False)
    checked_in_at: datetime | None = None
    checked_in_by: UUID | None = Field(default=None, foreign_key="user.id")
    cancelled: bool = Field(default=False)

class TicketCreate(SQLModel):
    attendee_id: UUID
    event_id: UUID

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    username: str | None = None

class User(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: str | None = Field(default=None, index=True)
    password: str | None = Field(default=None, index=True)
    role: EventRole = Field(default=EventRole.user, index=True)

class CheckInLog(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    ticket_id: UUID = Field(foreign_key="ticket.id")
    checked_by: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now, index=True)


class UserCreate(SQLModel):
    name: str
    age: int | None = None
    email: str | None = None
    password: str | None = None


class CheckInLogCreate(SQLModel):
    attendee_id: UUID
    ticket_id: UUID
    user_id: UUID
    event_id: UUID

class EventCreate(SQLModel):
    name: str
    date: datetime
    location: str
    description: str | None = None

class UserList(SQLModel):
    users: List[User]

class UserResponse(SQLModel):
    message: str
    user: User

class EventList(SQLModel):
    events: List[Event]

class EventResponse(SQLModel):
    message: str
    event: Event

class CheckInResponse(SQLModel):
    message: str
    check_in_log: CheckInLog

BASE_DIR = Path(__file__).resolve().parent
sqlite_file_name = BASE_DIR / "database.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True}
              )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_id = UUID(user_id)
        
        user = session.exec(select(User).where(User.id == user_id)).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def generate_ticket_code() -> str:
    return secrets.token_urlsafe(16)

def is_valid_email(email: str) -> bool:
    if not email:
        return False
    return (
        email.count("@") == 1 and
        email.count(".") >= 1 and
        email.find("@.") == -1 and
        email.find(".@") == -1
    )

@app.get("/auth/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}

@app.post("/token")
async def login(
    
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):

    statement = select(User).where(
        User.email == form_data.username
    )

    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    hashed_password = hashlib.sha256(
        form_data.password.encode()
    ).hexdigest()

    if user.password != hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta"
        )
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
    "sub": str(user.id),
    "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/me")
async def me(user = Depends(get_current_user)):
    return {"id": str(user.id), "name": user.name, "email": user.email}

@app.get("/")
def hello_world():
    return {"message": "Hello World"}

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: SessionDep):
    user = User(id=uuid4(),role=EventRole.user, **user.model_dump())
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest() if user.password else None
    user.password = hashed_password
    if is_valid_email(user.email):
        existing_user = session.exec(select(User).where(User.email == user.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {
    "message": "User created successfully",
    "user": user
    }

@app.get("/users/{event_id}", response_model=UserList, status_code=status.HTTP_200_OK)
def list_users(event_id: UUID, session: SessionDep):
    users = session.exec(select(User).where(User.role == EventRole.user and User.id == EventMembership.user_id)).all()
    return UserList(users=users)

@app.get("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
def read_user(user_id: UUID, session: SessionDep):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user

@app.post("/attendees/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_attendee(attendee: UserCreate, session: SessionDep):
    attendee = User(id=uuid4(), ticket_code=generate_ticket_code(), role=EventRole.attendee, **attendee.model_dump())
    hashed_password = hashlib.sha256(attendee.password.encode()).hexdigest() if attendee.password else None
    attendee.password = hashed_password
    if is_valid_email(attendee.email):
        existing_attendee = session.exec(select(User).where(User.email == attendee.email)).first()
        if existing_attendee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    session.add(attendee)
    session.commit()
    session.refresh(attendee)
    return {
    "message": "Attendee created successfully",
    "user": attendee
    }

@app.get("/attendees/{event_id}", response_model=UserList, status_code=status.HTTP_200_OK)
def list_attendees(event_id: UUID, session: SessionDep):
    attendees = session.exec(select(User).where(User.role == EventRole.attendee and User.id == EventMembership.user_id)).all()
    return UserList(users=attendees)

@app.get("/attendees/by-code/{ticket_code}", response_model=User, status_code=status.HTTP_200_OK)
def read_attendee_by_code(ticket_code: str, session: SessionDep, current_user: User = Depends(get_current_user)):
    attendee = session.exec(
        select(User).where(User.ticket_code == ticket_code)
    ).one_or_none()
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    return attendee

@app.delete("/users/{user_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
def delete_user(user_id: UUID, session: SessionDep):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}

@app.delete("/attendees/{attendee_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
def delete_attendee(attendee_id: UUID, session: SessionDep, current_user: User = Depends(get_current_user)):
    attendee = session.get(User, attendee_id)
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    session.delete(attendee)
    session.commit()
    return {"message": "Attendee deleted successfully"}

@app.get("/attendees/{attendee_id}", response_model=User, status_code=status.HTTP_200_OK)
def read_attendee(attendee_id: UUID, session: SessionDep, current_user: User = Depends(get_current_user)):
    attendee = session.get(User, attendee_id)
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    return attendee

@app.post("/attendees/{ticket_code}/check-in", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def check_in_attendee(ticket_code: str, session: SessionDep, current_user: User = Depends(get_current_user)):
    ticket = session.exec(
        select(Ticket).where(Ticket.code == ticket_code)
    ).one_or_none()
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    if ticket.checked_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendee already checked in at " + ticket.checked_in_at.isoformat()
        )
    ticket.checked_in = True
    ticket.checked_in_at = datetime.now(timezone.utc)
    ticket.checked_in_by = current_user.id

    log = CheckInLog(id=uuid4(), attendee_id=ticket.attendee_id, user_id=current_user.id)
    session.add(ticket)
    session.add(log)
    session.commit()
    session.refresh(ticket)
    return {
        "message": "Attendee checked in successfully",
        "check_in_log": log
    }

@app.delete("/attendees/{attendee_id}", response_model=CheckInResponse, status_code=status.HTTP_200_OK)
def delete_attendee(attendee_id: UUID, session: SessionDep, current_user: User = Depends(get_current_user)):
    attendee = session.get(User, attendee_id)
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    session.delete(attendee)
    session.commit()
    return {"message": "Attendee check-in deleted successfully"}

@app.get("/db-check")
async def db_check():
    with Session(engine) as session:
        result = session.exec(text("SELECT 1")).scalar_one()
        return {"database_connected": True, "result": result}

