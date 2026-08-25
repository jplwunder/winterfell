import hashlib
import random
import string
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import jwt
from fastapi.testclient import TestClient
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.main import app

from tests.helper import create_user, me_test, random_string, verify_code_test


def test_login(client):

    email = "".join(random.choices(string.ascii_lowercase, k=10)) + "@example.com"
    password = "password123"

    # First, create a user
    create_user(client, random_string(10), email, password)

    response = client.post("/auth/login", data={"username": email, "password": password})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data



def test_invalid_login(client):

    email = "".join(random.choices(string.ascii_lowercase, k=10)) + "@example.com"
    password = "password123"

    response = client.post("/auth/login", data={"username": email, "password": password})

    assert response.status_code == 404
    data = response.json()
    assert "access_token" not in data

def test_login_with_wrong_password(client):

    email = "".join(random.choices(string.ascii_lowercase, k=10)) + "@example.com"
    password = "password123"

    # First, create a user
    create_user(client, random_string(10), email, password)

    response = client.post(
        "/auth/login", data={"username": email, "password": "wrongpassword"}
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Senha incorreta"


def test_login_with_nonexistent_user(client):

    email = "".join(random.choices(string.ascii_lowercase, k=10)) + "@example.com"

    response = client.post(
        "/auth/login", data={"username": email, "password": "password123"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Usuário não encontrado"


def test_me(client):

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

    response_me = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response_me.status_code == 200
    assert response_me.json()["email"] == email


def test_me_with_invalid_token(client):

    response_me = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response_me.status_code == 401
    assert response_me.json()["detail"] == "Invalid token"

    response_me = client.get("/auth/me")
    assert response_me.status_code == 401
    assert response_me.json()["detail"] == "Not authenticated"


def test_me_with_expired_token(client):

    email = "test@example.com"

    expired_payload = {"sub": email, "exp": datetime.now() - timedelta(minutes=30)}

    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {expired_token}"})

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Token has expired"

def test_auth_with_missing_token(client):

    response_me = client.get("/auth/me", headers={})
    assert response_me.status_code == 401
    data_me = response_me.json()
    assert data_me["detail"] == "Not authenticated"
