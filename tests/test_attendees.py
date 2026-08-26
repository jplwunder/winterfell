
from datetime import datetime, timedelta
import random
import string

from tests.helper import create_event_test, create_user, me_test, random_email, random_string, verify_code_test
from fastapi.testclient import TestClient
from app.main import app

def test_list_organizers(client):
    email = "".join(random.choices(string.ascii_lowercase, k=10)) + "@example.com"
    password = "password123"
    create_user(client, random_string(10), email, password)

    response_login = client.post(
        "/auth/login", data={"username": email, "password": password}
    )

    assert response_login.status_code == 200
    data_login = response_login.json()
    token = data_login["access_token"]

    verification_code = me_test(client, token)

    assert verification_code is not None

    response_verify = verify_code_test(client, email, verification_code)
    assert response_verify.status_code == 200

    event_name = random_string(10)
    event_date = (datetime.now() + timedelta(days=1)).isoformat()
    event_location = random_string(10)
    event_description = random_string(20)
    response_create_event = create_event_test(client, token, event_name, event_date, event_location, event_description)

    response_organizers = client.get(
        f"/attendees/organizers/{response_create_event['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response_organizers.status_code == 200
    data_organizers = response_organizers.json()
    assert "users" in data_organizers

def test_list_participants(client):
    email = "".join(random.choices(string.ascii_lowercase, k=10)) + "@example.com"
    password = "password123"
    create_user(client, random_string(10), email, password)

    response_login = client.post(
        "/auth/login", data={"username": email, "password": password}
    )

    assert response_login.status_code == 200
    data_login = response_login.json()
    token = data_login["access_token"]

    verification_code = me_test(client, token)

    assert verification_code is not None

    response_verify = verify_code_test(client, email, verification_code)
    assert response_verify.status_code == 200

    event_name = random_string(10)
    event_date = (datetime.now() + timedelta(days=1)).isoformat()
    event_location = random_string(10)
    event_description = random_string(20)
    response_create_event = create_event_test(client, token, event_name, event_date, event_location, event_description)

    response_participants = client.get(
        f"/attendees/participants/{response_create_event['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response_participants.status_code == 200
    data_participants = response_participants.json()
    assert "tickets" in data_participants