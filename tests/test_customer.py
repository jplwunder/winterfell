import token

from main import app
from fastapi.testclient import TestClient
import hashlib
import random 
import string

from tests.helper import create_customer_test, get_auth_token, random_string


def random_email():
    return ''.join(random.choices(string.ascii_lowercase, k=10)) + "@example.com"

def test_create_customer(client):
    token = get_auth_token(client)
    create_customer_test(client, token, random_string(10), random_email(), 30, "password123", "123 Main St")

def test_create_customer_with_existing_email(client):
    token = get_auth_token(client)
    # First, create a customer
    create_customer_test(client, token, random_string(10), "jake.paul@example.com", 25, "password123", "456 Oak Ave")

    response = client.post("/customers/" ,headers={
        "Authorization": f"Bearer {token}"
    }, json={
        "name": "Jane Doe",
        "email": "jake.paul@example.com",
        "age": 25,
        "password": "password456",
        "address": "789 Pine Rd"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_list_customers(client):
    response = client.get("/customers/")
    assert response.status_code == 200
    data = response.json()
    assert "customers" in data
    assert isinstance(data["customers"], list)

def test_read_customer(client):
    token = get_auth_token(client)
    response_create = create_customer_test(client, token, "Jane Doe", random_email(), 30, "password123", "123 Main St")

    customer_id = response_create["id"]
    response_read = client.get(f"/customers/{customer_id}")
    data_read = response_read.json()
    assert response_read.status_code == 200
    assert data_read["name"] == "Jane Doe"
    expected_hashed_password = hashlib.sha256(
        "password123".encode()
    ).hexdigest()

    assert data_read["password"] == expected_hashed_password

def test_read_nonexistent_customer(client):
    non_existent_id = "11111111-1111-1111-1111-111111111111"
    response_read = client.get(f"/customers/{non_existent_id}")
    assert response_read.status_code == 404
    data_read = response_read.json()
    assert data_read["detail"] == "Customer not found"

def test_delete_customer(client):
    token = get_auth_token(client)
    response_create = create_customer_test(client, token, "Alice Smith", "alice.smith@example.com", 30, "password123", "123 Oak St")
    customer_id = response_create["id"]

    response_delete = client.delete(f"/customers/{customer_id}", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response_delete.status_code == 200
    data_delete = response_delete.json()
    assert data_delete["message"] == "Customer deleted successfully"

def test_delete_nonexistent_customer(client):
    token = get_auth_token(client)
    non_existent_id = "11111111-1111-1111-1111-111111111111"
    response_delete = client.delete(f"/customers/{non_existent_id}", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response_delete.status_code == 404
    data_delete = response_delete.json()
    assert data_delete["detail"] == "Customer not found"
