from fastapi import FastAPI, Depends
from typing import Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, text

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    email: str | None = Field(default=None, index=True)

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


@app.get("/db-check")
def db_check():
    with Session(engine) as session:
        result = session.exec(text("SELECT 1")).scalar_one()
        return {"database_connected": True, "result": result}
