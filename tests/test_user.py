import random
import string

from tests.helper import create_user_help, me_help, random_string, verify_code_help


def random_email():
    return "".join(random.choices(string.ascii_lowercase, k=10)) + "@example.com"


def test_create_user(client):
    response = client.post(
        "/users",
        json={
            "name": random_string(10),
            "email": random_email(),
            "age": 30,
            "password": "password123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert (
        data["message"] == "User created successfully. Waiting for e-mail confirmation."
    )


def test_create_user_with_existing_email(client):
    # First, create a user
    email = random_email()

    create_user_help(client, "Jake Paul", email, "password123")

    response = client.post(
        "/users",
        json={"name": "Jane Doe", "email": email, "password": "password456"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Email já registrado."


def test_create_user_with_invalid_email(client):
    response = client.post(
        "/users",
        json={
            "name": "Jane Doe",
            "email": "invalid-email",
            "age": 25,
            "password": "password456",
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Formato de e-mail inválido"


def test_read_user(client):
    # Create a user first
    email = random_email()
    user = create_user_help(client, "John Doe", email, "password123")

    response_login = client.post(
        "/auth/login", data={"username": email, "password": "password123"}
    )

    assert response_login.status_code == 200
    data_login = response_login.json()
    token = data_login["access_token"]

    verification_code = me_help(client, token)

    assert verification_code is not None

    response_verify = verify_code_help(client, email, verification_code)
    assert response_verify.status_code == 200

    response_me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response_me.status_code == 200
    assert response_me.json()["email"] == email

    # Now read the user by ID
    response = client.get(
        f"/users/{response_me.json()['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["name"] == "John Doe"
    assert data["id"] == user["id"]


def test_read_user_by_email(client):
    # Create a user first
    email = random_email()
    user = create_user_help(client, "John Doe", email, "password123")

    response_login = client.post(
        "/auth/login", data={"username": email, "password": "password123"}
    )

    assert response_login.status_code == 200
    data_login = response_login.json()
    token = data_login["access_token"]

    verification_code = me_help(client, token)

    assert verification_code is not None

    response_verify = verify_code_help(client, email, verification_code)
    assert response_verify.status_code == 200

    response_me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response_me.status_code == 200
    assert response_me.json()["email"] == email

    # Now read the user by email
    response = client.get(
        f"/users/by-email/{email}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["name"] == "John Doe"
    assert data["id"] == user["id"]
