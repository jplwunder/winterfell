
from datetime import datetime, timedelta
import random
import string

from tests.helper import create_event_test, create_user, me_test, random_email, random_string, ticket_test, verify_code_test
from fastapi.testclient import TestClient
from app.main import app

def test_list_organizers(client):
    email = random_email()
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
    email = random_email()
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

def test_create_ticket(client):
    email = random_email()
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

    email2 = random_email()
    create_user(client, random_string(10), email2, password)
    response_login2 = client.post(
        "/auth/login", data={"username": email2, "password": password}
    )
    
    assert response_login2.status_code == 200
    data_login2 = response_login2.json()
    token2 = data_login2["access_token"]
    
    verification_code2 = me_test(client, token2)
    
    assert verification_code2 is not None
    
    response_verify2 = verify_code_test(client, email2, verification_code2)
    assert response_verify2.status_code == 200

    response_create_ticket = ticket_test(client, token2, response_create_event['id'])

    assert response_create_ticket.status_code == 200
    data_create_ticket = response_create_ticket.json()
    assert "ticket_code" in data_create_ticket["ticket"]