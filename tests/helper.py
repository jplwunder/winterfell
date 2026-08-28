import hashlib
from unittest.mock import AsyncMock, patch
from urllib import response

from app.email.service import create_user_verification_code
from app.core.security import get_current_user
from app.users.model import User

def random_string(length=10):
    import random
    import string

    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def random_email():
    return random_string(10) + "@example.com"

def create_user_help(client, name, email, password):
    payload = {
        "name": name,
        "email": email,
        "password": password,
    }

    with patch("app.core.auth.mail.send_message", new_callable=AsyncMock):
        response = client.post("/users", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == (
        "User created successfully. Waiting for e-mail confirmation."
    )

    assert data["user"]["email"] == email
    assert data["user"]["name"] == name

    assert "password" not in data["user"]
    return data["user"]

def create_event_help(client, token, name, date, location, description):
    response = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": name, "date": date, "location": location, "description": description},
    )
    assert response.status_code == 201
    return response.json()["event"]

def me_help(client, token):
    captured_code = None

    def capture_verification_code(email, session):
        nonlocal captured_code
        captured_code = create_user_verification_code(email, session)
        return captured_code

    with (
        patch(
            "app.core.auth.create_user_verification_code",
            side_effect=capture_verification_code,
        ),
        patch("app.core.auth.mail.send_message", new_callable=AsyncMock),
    ):
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    return response, captured_code

def ticket_help(client, token, event_id):
    with patch("app.attendees.service.mail.send_message", new_callable=AsyncMock):
        response = client.post(
            "/attendees/tickets",
            headers={"Authorization": f"Bearer {token}"},
            json={"event_id": event_id},
    )
    return response

def verify_code_help(client, email, code):
    response = client.post(
        "/auth/verify-code",
        json={"email": email, "code": str(code)},
    )
    return response