from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient
import pytest
import os

from main import app, get_session

@pytest.fixture(scope="function")
def client():

    SQLModel.metadata.create_all(test_engine)

    with TestClient(app) as client:
        yield client

    
    test_engine.dispose()
    if os.path.exists(test_sqlite_file_name):
        os.remove(test_sqlite_file_name)

test_sqlite_file_name = "test_database.sqlite"
sqlite_url = f"sqlite:///{test_sqlite_file_name}"
test_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def override_get_session():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session
