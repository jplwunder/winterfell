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

load_dotenv()
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    username: str | None = None

class User(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    email: str | None = Field(default=None, index=True)
    password: str | None = Field(default=None, index=True)

class Attendee(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: str | None = Field(default=None, index=True)
    ticket_code: str = Field(index=True)
    checked_in: bool = Field(default=False, index=True)
    checked_in_at: datetime | None = Field(default=None, index=True)
    checked_in_by: UUID | None = Field(default=None, foreign_key="user.id")


class CheckInLog(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    attendee_id: UUID = Field(foreign_key="attendee.id")
    user_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now, index=True)


class UserCreate(SQLModel):
    name: str
    age: int | None = None
    email: str | None = None
    password: str | None = None

class AttendeeCreate(SQLModel):
    name: str
    email: str | None = None

class CheckInLogCreate(SQLModel):
    attendee_id: UUID
    user_id: UUID


class UserList(SQLModel):
    users: List[User]

class UserResponse(SQLModel):
    message: str
    user: User

class AttendeeList(SQLModel):
    attendees: List[Attendee]

class AttendeeResponse(SQLModel):
    message: str
    attendee: Attendee

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
    user = User(id=uuid4(), **user.model_dump())
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest() if user.password else None
    user.password = hashed_password
    if (user.age is not None and user.age < 18):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be at least 18 years old"
        )
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

@app.get("/users/", response_model=UserList, status_code=status.HTTP_200_OK)
def list_users(session: SessionDep):
    users = session.exec(select(User)).all()
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

@app.post("/attendees/", response_model=AttendeeResponse, status_code=status.HTTP_201_CREATED)
def create_attendee(attendee: AttendeeCreate, session: SessionDep, current_user: User = Depends(get_current_user)):
    if is_valid_email(attendee.email):
        existing_attendee = session.exec(select(Attendee).where(Attendee.email == attendee.email)).first()
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
    
    while True:
        ticket_code = generate_ticket_code()
        clash = session.exec(select(Attendee).where(Attendee.ticket_code == ticket_code)).first()
        if not clash:
            break
    
    attendee = Attendee(id=uuid4(), ticket_code=generate_ticket_code(), **attendee.model_dump())
    session.add(attendee)
    session.commit()
    session.refresh(attendee)
    return {
    "message": "Attendee created successfully",
    "attendee": attendee
    }

@app.get("/attendees/", response_model=AttendeeList, status_code=status.HTTP_200_OK)
def list_attendees(session: SessionDep, current_user: User = Depends(get_current_user)):
    attendees = session.exec(select(Attendee)).all()
    return AttendeeList(attendees=attendees)

@app.get("/attendees/by-code/{ticket_code}", response_model=Attendee, status_code=status.HTTP_200_OK)
def read_attendee_by_code(ticket_code: str, session: SessionDep, current_user: User = Depends(get_current_user)):
    attendee = session.exec(
        select(Attendee).where(Attendee.ticket_code == ticket_code)
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
    attendee = session.get(Attendee, attendee_id)
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    session.delete(attendee)
    session.commit()
    return {"message": "Attendee deleted successfully"}

@app.get("/attendees/{attendee_id}", response_model=Attendee, status_code=status.HTTP_200_OK)
def read_attendee(attendee_id: UUID, session: SessionDep, current_user: User = Depends(get_current_user)):
    attendee = session.get(Attendee, attendee_id)
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    return attendee

@app.post("/attendees/{ticket_code}/check-in", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def check_in_attendee(ticket_code: str, session: SessionDep, current_user: User = Depends(get_current_user)):
    attendee = session.exec(
        select(Attendee).where(Attendee.ticket_code == ticket_code)
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

@app.delete("/attendees/{attendee_id}", response_model=CheckInResponse, status_code=status.HTTP_200_OK)
def delete_attendee(attendee_id: UUID, session: SessionDep, current_user: User = Depends(get_current_user)):
    attendee = session.get(Attendee, attendee_id)
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

