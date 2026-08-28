from datetime import datetime, timedelta
import email
import token

from app.main import app
from fastapi.testclient import TestClient
import hashlib
import random
import string

from tests.conftest import client
from tests.helper import create_event_help, create_user_help, me_help, random_string, verify_code_help


def random_email():
    return "".join(random.choices(string.ascii_lowercase, k=10)) + "@example.com"


def test_create_event(client):
    email = random_email()
    password = "password123"
    create_user_help(client, random_string(10), email, password)

    response_login = client.post(
        "/auth/login", data={"username": email, "password": password}
    )

    assert response_login.status_code == 200
    data_login = response_login.json()
    token = data_login["access_token"]

    verification_code = me_help(client, token)

    assert verification_code is not None

    response_verify = verify_code_help(client, email, verification_code)
    assert response_verify.status_code == 200

    event_name = random_string(10)
    event_date = (datetime.now() + timedelta(days=1)).isoformat()
    event_location = random_string(10)
    event_description = random_string(20)
    response_create_event = create_event_help(client, token, event_name, event_date, event_location, event_description)
    assert response_create_event["name"] == event_name
    assert response_create_event["date"] == event_date
    assert response_create_event["location"] == event_location
    assert response_create_event["description"] == event_description

def test_read_event(client):
    email = random_email()
    password = "password123"
    create_user_help(client, random_string(10), email, password)

    response_login = client.post(
        "/auth/login", data={"username": email, "password": password}
    )

    assert response_login.status_code == 200
    data_login = response_login.json()
    token = data_login["access_token"]

    verification_code = me_help(client, token)

    assert verification_code is not None

    response_verify = verify_code_help(client, email, verification_code)
    assert response_verify.status_code == 200

    event_name = random_string(10)
    event_date = (datetime.now() + timedelta(days=1)).isoformat()
    event_location = random_string(10)
    event_description = random_string(20)
    response_create_event = create_event_help(client, token, event_name, event_date, event_location, event_description)
    assert response_create_event["name"] == event_name
    assert response_create_event["date"] == event_date
    assert response_create_event["location"] == event_location
    assert response_create_event["description"] == event_description

    response = client.get(f"/events/{response_create_event['id']}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == response_create_event["id"]
    assert data["name"] == response_create_event["name"]
    assert data["date"] == response_create_event["date"]
    assert data["location"] == response_create_event["location"]
    assert data["description"] == response_create_event["description"]


def test_list_events(client):
    email = random_email()
    password = "password123"
    create_user_help(client, random_string(10), email, password)

    response_login = client.post(
        "/auth/login", data={"username": email, "password": password}
    )

    assert response_login.status_code == 200
    data_login = response_login.json()
    token = data_login["access_token"]

    verification_code = me_help(client, token)

    assert verification_code is not None

    response_verify = verify_code_help(client, email, verification_code)
    assert response_verify.status_code == 200

    event_name = random_string(10)
    event_date = (datetime.now() + timedelta(days=1)).isoformat()
    event_location = random_string(10)
    event_description = random_string(20)
    response_create_event = create_event_help(client, token, event_name, event_date, event_location, event_description)
    assert response_create_event["name"] == event_name
    assert response_create_event["date"] == event_date
    assert response_create_event["location"] == event_location
    assert response_create_event["description"] == event_description

    response = client.get("/events/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert isinstance(data["events"], list)
    assert len(data["events"]) >= 1

def test_delete_event(client):
    email = random_email()
    password = "password123"
    create_user_help(client, random_string(10), email, password)

    response_login = client.post(
        "/auth/login", data={"username": email, "password": password}
    )

    assert response_login.status_code == 200
    data_login = response_login.json()
    token = data_login["access_token"]

    verification_code = me_help(client, token)

    assert verification_code is not None

    response_verify = verify_code_help(client, email, verification_code)
    assert response_verify.status_code == 200

    event_name = random_string(10)
    event_date = (datetime.now() + timedelta(days=1)).isoformat()
    event_location = random_string(10)
    event_description = random_string(20)
    response_create_event = create_event_help(client, token, event_name, event_date, event_location, event_description)
    assert response_create_event["name"] == event_name
    assert response_create_event["date"] == event_date
    assert response_create_event["location"] == event_location
    assert response_create_event["description"] == event_description
    response_delete_event = client.post(f"/events/{response_create_event['id']}", headers={"Authorization": f"Bearer {token}"})
    assert response_delete_event.status_code == 200



