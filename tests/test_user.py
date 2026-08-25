from app.main import app
from fastapi.testclient import TestClient
import hashlib
import random
import string
from tests.helper import create_user, random_string


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
    assert data["message"] == "User created successfully. Waiting for e-mail confirmation."



def test_create_user_with_existing_email(client):
    # First, create a user
    email = random_email()

    create_user(client, "Jake Paul", email, "password123")

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