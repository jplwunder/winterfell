from pathlib import Path
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

BASE_DIR = Path(__file__).resolve().parents[2]
sqlite_file_name = BASE_DIR / "database.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    from app.attendees import model as attendee_model  # noqa: F401
    from app.events import model as event_model  # noqa: F401
    from app.users import model as user_model  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
