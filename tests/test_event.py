import random
import string
from datetime import UTC, datetime, timedelta

from tests.helper import (
    create_event_help,
    create_user_help,
    me_help,
    random_string,
    ticket_help,
    verify_code_help,
)


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
    event_date = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    event_location = random_string(10)
    event_description = random_string(20)
    response_create_event = create_event_help(
        client, token, event_name, event_date, event_location, event_description
    )
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
    event_date = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    event_location = random_string(10)
    event_description = random_string(20)
    response_create_event = create_event_help(
        client, token, event_name, event_date, event_location, event_description
    )
    assert response_create_event["name"] == event_name
    assert response_create_event["date"] == event_date
    assert response_create_event["location"] == event_location
    assert response_create_event["description"] == event_description

    response = client.get(
        f"/events/{response_create_event['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
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
    event_date = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    event_location = random_string(10)
    event_description = random_string(20)
    response_create_event = create_event_help(
        client, token, event_name, event_date, event_location, event_description
    )
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
    event_date = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    event_location = random_string(10)
    event_description = random_string(20)
    response_create_event = create_event_help(
        client, token, event_name, event_date, event_location, event_description
    )
    assert response_create_event["name"] == event_name
    assert response_create_event["date"] == event_date
    assert response_create_event["location"] == event_location
    assert response_create_event["description"] == event_description
    response_delete_event = client.post(
        f"/events/{response_create_event['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_delete_event.status_code == 200


def test_check_in_attendee(client):
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
    event_date = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    event_location = random_string(10)
    event_description = random_string(20)
    response_create_event = create_event_help(
        client, token, event_name, event_date, event_location, event_description
    )
    assert response_create_event["name"] == event_name
    assert response_create_event["date"] == event_date
    assert response_create_event["location"] == event_location
    assert response_create_event["description"] == event_description

    email2 = random_email()
    create_user_help(client, random_string(10), email2, password)

    response_login_2 = client.post(
        "/auth/login", data={"username": email2, "password": password}
    )

    assert response_login_2.status_code == 200
    data_login_2 = response_login_2.json()
    token_2 = data_login_2["access_token"]

    verification_code_2 = me_help(client, token_2)

    assert verification_code_2 is not None

    response_verify_2 = verify_code_help(client, email2, verification_code_2)
    assert response_verify_2.status_code == 200

    response_create_ticket = ticket_help(client, token_2, response_create_event["id"])

    assert response_create_ticket.status_code == 200
    data_create_ticket = response_create_ticket.json()
    assert "ticket_code" in data_create_ticket["ticket"]

    response_check_in = client.post(
        f"/events/{response_create_event['id']}/check-in/{data_create_ticket['check_in_log']['ticket_code']}",
        headers={"Authorization": f"Bearer {token_2}"},
    )
    assert response_check_in.status_code == 200


def test_check_in_log(client):
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
    event_date = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    event_location = random_string(10)
    event_description = random_string(20)
    response_create_event = create_event_help(
        client, token, event_name, event_date, event_location, event_description
    )

    assert response_create_event["name"] == event_name
    assert response_create_event["date"] == event_date
    assert response_create_event["location"] == event_location
    assert response_create_event["description"] == event_description

    email2 = random_email()
    create_user_help(client, random_string(10), email2, password)

    response_login_2 = client.post(
        "/auth/login", data={"username": email2, "password": password}
    )
    assert response_login_2.status_code == 200
    data_login_2 = response_login_2.json()
    token_2 = data_login_2["access_token"]

    verification_code_2 = me_help(client, token_2)
    assert verification_code_2 is not None

    response_verify_2 = verify_code_help(client, email2, verification_code_2)
    assert response_verify_2.status_code == 200

    response_create_ticket_2 = ticket_help(client, token_2, response_create_event["id"])
    assert response_create_ticket_2.status_code == 200

    data_create_ticket_2 = response_create_ticket_2.json()

    response_login_3 = client.post(
        "/auth/login", data={"username": email, "password": password}
    )
    assert response_login_3.status_code == 200
    data_login_3 = response_login_3.json()
    token_3 = data_login_3["access_token"]

    response_check_in = client.post(
        f"/events/{response_create_event['id']}/check-in/{data_create_ticket_2['check_in_log']['ticket_code']}",
        headers={"Authorization": f"Bearer {token_3}"},
    )
    assert response_check_in.status_code == 200

    response_check_in_log = client.get(
        f"/events/{response_create_event['id']}/check-in-logs",
        headers={"Authorization": f"Bearer {token_3}"},
    )
    data_check_in_log = response_check_in_log.json()
    assert "check_in_logs" in data_check_in_log


def test_add_staff(client):
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
    event_date = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    event_location = random_string(10)
    event_description = random_string(20)
    response_create_event = create_event_help(
        client, token, event_name, event_date, event_location, event_description
    )

    assert response_create_event["name"] == event_name
    assert response_create_event["date"] == event_date
    assert response_create_event["location"] == event_location
    assert response_create_event["description"] == event_description

    email2 = random_email()
    user2 = create_user_help(client, random_string(10), email2, password)

    response_login_2 = client.post(
        "/auth/login", data={"username": email2, "password": password}
    )
    assert response_login_2.status_code == 200
    data_login_2 = response_login_2.json()
    token_2 = data_login_2["access_token"]

    verification_code_2 = me_help(client, token_2)
    assert verification_code_2 is not None

    response_verify_2 = verify_code_help(client, email2, verification_code_2)
    assert response_verify_2.status_code == 200

    response_create_ticket_2 = ticket_help(client, token_2, response_create_event["id"])
    assert response_create_ticket_2.status_code == 200

    response_login_3 = client.post(
        "/auth/login", data={"username": email, "password": password}
    )
    assert response_login_3.status_code == 200
    data_login_3 = response_login_3.json()
    token_3 = data_login_3["access_token"]

    response_add_staff = client.post(
        f"/events/{response_create_event['id']}/addstaff/{user2['id']}",
        headers={"Authorization": f"Bearer {token_3}"},
    )
    data_add_staff = response_add_staff.json()
    assert data_add_staff["message"] == "Staff member added to event successfully"
    assert data_add_staff["event"]["name"] == event_name
    assert data_add_staff["event"]["date"] == event_date
    assert data_add_staff["event"]["location"] == event_location
    assert data_add_staff["event"]["description"] == event_description
