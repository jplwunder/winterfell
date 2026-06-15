from fastapi import FastAPI, Depends
from uuid import UUID, uuid4
from typing import Annotated, Dict, List
from sqlmodel import Field, Session, SQLModel, create_engine, select

class User(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    email: str | None = Field(default=None, index=True)

class UserCreate(SQLModel):
    name: str
    age: int | None = None
    email: str | None = None

class UserList(SQLModel):
    users: List[User]

sqlite_file_name = "database.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def hello_world():
    return {"message": "Hello World"}

@app.post("/users/", response_model=User)
async def create_user(user: UserCreate, session: SessionDep):
    user = User(id=uuid4(), **user.dict())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/users/", response_model=UserList)
async def list_users(session: SessionDep):
    users = session.exec(select(User)).all()
    return UserList(users=users)

@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: UUID, session: SessionDep):
    user = session.get(User, user_id)
    if user is None:
        return {"error": "User not found"}
    return user

@app.delete("/users/{user_id}", response_model=Dict[str, str])
async def delete_user(user_id: UUID, session: SessionDep):
    user = session.get(User, user_id)
    if user is None:
        return {"error": "User not found"}
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}

@app.get("/db-check")
async def db_check():
    with Session(engine) as session:
        result = session.exec(select(1)).scalar_one()
        return {"database_connected": True, "result": result}

