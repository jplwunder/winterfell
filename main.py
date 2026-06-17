import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from uuid import UUID, uuid4
from typing import Annotated, Dict, List
from sqlmodel import Field, Session, SQLModel, create_engine, select, text
import hashlib
import jwt
from dotenv import load_dotenv
from contextlib import asynccontextmanager

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


class UserCreate(SQLModel):
    name: str
    age: int | None = None
    email: str | None = None
    password: str | None = None

class CustomerCreate(SQLModel):
    name: str
    email: str | None = None
    age: int | None = None
    password: str | None = None
    address: str | None = None
    password: str | None = None

class CustomerList(SQLModel):
    customers: List[Customer]

class UserList(SQLModel):
    users: List[User]


class UserList(SQLModel):
    users: List[User]

class UserResponse(SQLModel):
    message: str
    user: User

class CustomerResponse(SQLModel):
    message: str
    customer: Customer

sqlite_file_name = "database.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(lifespan=lifespan)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(
    token,
    SECRET_KEY,
    algorithms=[ALGORITHM]
    )

    user_email = payload.get("sub")

    if not user_email:
        raise HTTPException(401)

    return user_email

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

    payload = {
    "sub": user.email
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
    return {"email": user}

@app.get("/")
def hello_world():
    return {"message": "Hello World"}

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: SessionDep):
    user = User(id=uuid4(), **user.model_dump())
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest() if user.password else None
    user.password = hashed_password
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
        return {"error": "User not found"}, status.HTTP_404_NOT_FOUND
    return user

@app.post("/customers/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate, session: SessionDep):
    customer = Customer(id=uuid4(), **customer.model_dump())
    hashed_password = hashlib.sha256(customer.password.encode()).hexdigest() if customer.password else None
    customer.password = hashed_password
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return {
    "message": "Customer created successfully",
    "customer": customer
    }

@app.get("/customers/", response_model=CustomerList, status_code=status.HTTP_200_OK)
def list_customers(session: SessionDep):
    customers = session.exec(select(Customer)).all()
    return CustomerList(customers=customers)

@app.get("/customers/{customer_id}", response_model=Customer, status_code=status.HTTP_200_OK)
def read_customer(customer_id: UUID, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if customer is None:
        return {"error": "Customer not found"}, status.HTTP_404_NOT_FOUND
    return customer

@app.delete("/users/{user_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
def delete_user(user_id: UUID, session: SessionDep):
    user = session.get(User, user_id)
    if user is None:
        return {"error": "User not found"}, status.HTTP_404_NOT_FOUND
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}

@app.delete("/customers/{customer_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
def delete_customer(customer_id: UUID, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if customer is None:
        return {"error": "Customer not found"}, status.HTTP_404_NOT_FOUND
    session.delete(customer)
    session.commit()
    return {"message": "Customer deleted successfully"}

@app.get("/db-check")
async def db_check():
    with Session(engine) as session:
        result = session.exec(text("SELECT 1")).scalar_one()
        return {"database_connected": True, "result": result}

