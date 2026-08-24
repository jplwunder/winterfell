import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.core.database import get_session
from app.main import app

@pytest.fixture(scope="function")
def client():

    print(f"\nTest database: {test_sqlite_file_name}")
    print(f"Exists before create_all: {test_sqlite_file_name.exists()}")
    
    SQLModel.metadata.create_all(test_engine)

    with TestClient(app) as client:
        yield client

    test_engine.dispose()
    if os.path.exists(test_sqlite_file_name):
        os.remove(test_sqlite_file_name)

BASE_DIR = Path(__file__).resolve().parent.parent
test_sqlite_file_name = BASE_DIR / "test_database.sqlite"
sqlite_url = f"sqlite:///{test_sqlite_file_name}"
test_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def override_get_session():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session
