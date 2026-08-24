from unittest.mock import AsyncMock, patch

def random_string(length=10):
    import random
    import string

    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def random_email():
    return random_string(10) + "@example.com"

def create_user(client, name, email, password):
    payload = {
        "name": name,
        "email": email,
        "password": password,
    }

    with patch("app.email.service.create_message", new_callable=AsyncMock):
        response = client.post("/users", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == (
        "User created successfully. Waiting for e-mail confirmation."
    )

    assert data["user"]["email"] == email
    assert data["user"]["name"] == name

    assert "password" not in data["user"]
    return 

def create_event_test(client, token, name, date, location, description):
    response = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": name, "date": date, "location": location, "description": description},
    )
    assert response.status_code == 201
    return response.json()["event"]