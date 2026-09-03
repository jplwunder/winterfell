import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.core.database as core_database
from app.attendees import model as attendee_model  # noqa: F401
from app.core.database import get_session
from app.events import model as event_model  # noqa: F401
from app.main import app
from app.users import model as user_model  # noqa: F401

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
core_database.engine = test_engine


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
