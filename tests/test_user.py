from main import app
from fastapi.testclient import TestClient
import hashlib
import random 
import string

from tests.helper import create_user_test, random_string

def random_email():
    return ''.join(random.choices(string.ascii_lowercase, k=10)) + "@example.com"

def test_create_user(client):
    response = create_user_test(client, random_string(10), random_email(), 30, "password123")
    user_id = response["id"]

def test_create_user_with_existing_email(client):
    # First, create a user
    email = random_email()

    create_user_test(client, "Jake Paul", email, 30, "password123")

    response = client.post("/users/", json={
        "name": "Jane Doe",
        "email": email,
        "age": 25,
        "password": "password456"
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Email already registered"

def test_list_users(client):
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert isinstance(data["users"], list)

def test_read_user(client):

    response_create = create_user_test(client, "Jane Doe", random_email(), 30, "password123")

    user_id = response_create["id"]

    # faz a leitura primeiro
    response_read = client.get(f"/users/{user_id}")

    # depois verifica status
    assert response_read.status_code == 200

    data_read = response_read.json()

    assert data_read["name"] == "Jane Doe"

    expected_hashed_password = hashlib.sha256(
        "password123".encode()
    ).hexdigest()

    assert data_read["password"] == expected_hashed_password

def test_read_nonexistent_user(client):
    non_existent_id = "11111111-1111-1111-1111-111111111111"
    response_read = client.get(f"/users/{non_existent_id}")
    assert response_read.status_code == 404
    data_read = response_read.json()
    assert data_read["detail"] == "User not found"

def test_delete_user(client):
    response_create = create_user_test(client, "Alice Smith", "alice.smith@example.com", 30, "password123")
    user_id = response_create["id"]

    response_delete = client.delete(f"/users/{user_id}")
    assert response_delete.status_code == 200
    data_delete = response_delete.json()
    assert data_delete["message"] == "User deleted successfully"

def test_delete_nonexistent_user(client):
    non_existent_id = "11111111-1111-1111-1111-111111111111"
    response_delete = client.delete(f"/users/{non_existent_id}")
    assert response_delete.status_code == 404
    data_delete = response_delete.json()
    assert data_delete["detail"] == "User not found"
