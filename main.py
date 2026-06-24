import os
from datetime import datetime, timedelta, timezone
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

class Customer(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: str | None = Field(default=None, index=True)
    age: int | None = Field(default=None, index=True)
    password: str | None = Field(default=None, index=True)
    address: str | None = Field(default=None, index=True)

    created_by: UUID | None = Field(default=None, foreign_key="user.id")


class UserCreate(SQLModel):
    name: str
    age: int | None = None
    email: str | None = None
    password: str | None = None

class CustomerCreate(SQLModel):
    name: str
    email: str | None = None
    age: int | None = None
    address: str | None = None
    password: str | None = None

class CustomerList(SQLModel):
    customers: List[Customer]

class UserList(SQLModel):
    users: List[User]

class UserResponse(SQLModel):
    message: str
    user: User

class CustomerResponse(SQLModel):
    message: str
    customer: Customer

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
    return {"email": user.email}

@app.get("/")
def hello_world():
    return {"message": "Hello World"}

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: SessionDep):
    user = User(id=uuid4(), **user.model_dump())
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest() if user.password else None
    user.password = hashed_password
    if (user.age < 18):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be at least 18 years old"
        )
    if ((user.email).count("@") == 1 and (user.email).count(".") >= 1 and (user.email).find("@.") == -1 and (user.email).find(".@") == -1):
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

@app.post("/customers/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate, session: SessionDep, current_user: User = Depends(get_current_user)):
    customer = Customer(id=uuid4(), **customer.model_dump())
    hashed_password = hashlib.sha256(customer.password.encode()).hexdigest() if customer.password else None
    customer.password = hashed_password
    customer.created_by = current_user.id
    if (customer.email).count("@") == 1 and (customer.email).count(".") >= 1 and (customer.email).find("@.") == -1 and (customer.email).find(".@") == -1:
        existing_customer = session.exec(select(Customer).where(Customer.email == customer.email)).first()
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return {
    "message": "Customer created successfully",
    "customer": customer
    }

@app.get("/customers/", response_model=CustomerList, status_code=status.HTTP_200_OK)
def list_customers(session: SessionDep, current_user: User = Depends(get_current_user)):
    customers = session.exec(
    select(Customer).where(Customer.created_by == current_user.id)
    ).all()
    return CustomerList(customers=customers)

@app.get("/customers/{customer_id}", response_model=Customer, status_code=status.HTTP_200_OK)
def read_customer(customer_id: UUID, session: SessionDep, current_user: User = Depends(get_current_user)):
    customer = session.exec(
    select(Customer).where(Customer.created_by == current_user.id and Customer.id == customer_id)
    ).one_or_none()
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found or you're not authorized to access this customer"
        )
    return customer

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

@app.delete("/customers/{customer_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
def delete_customer(customer_id: UUID, session: SessionDep, current_user: User = Depends(get_current_user)):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    session.delete(customer)
    session.commit()
    return {"message": "Customer deleted successfully"}

@app.get("/db-check")
async def db_check():
    with Session(engine) as session:
        result = session.exec(text("SELECT 1")).scalar_one()
        return {"database_connected": True, "result": result}

