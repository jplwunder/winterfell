import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.core.database import get_session
from app.main import app
from app.users import model as user_model  # noqa: F401
from app.events import model as event_model  # noqa: F401
from app.attendees import model as attendee_model  # noqa: F401

BASE_DIR = Path(__file__).resolve().parent.parent
test_sqlite_file_name = BASE_DIR / "test_database.sqlite"
sqlite_url = f"sqlite:///{test_sqlite_file_name}"
test_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def override_get_session():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(scope="function")
def client():
    SQLModel.metadata.create_all(test_engine)

    with TestClient(app) as client:
        yield client

    SQLModel.metadata.drop_all(test_engine)
    test_engine.dispose()
    if os.path.exists(test_sqlite_file_name):
        os.remove(test_sqlite_file_name)