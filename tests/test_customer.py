from main import app
from fastapi.testclient import TestClient
import hashlib
import random 
import string

client = TestClient(app)

def random_email():
    return ''.join(random.choices(string.ascii_lowercase, k=10)) + "@example.com"

def test_create_customer():
    response = client.post("/customers/", json={
        "name": "John Doe",
        "email": random_email(),
        "age": 30,
        "password": "password123",
        "address": "123 Main St"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Customer created successfully"

def test_create_customer_with_existing_email():
    # First, create a customer
    client.post("/customers/", json={
        "name": "Jake Paul",
        "email": "jake.paul@example.com",
        "age": 25,
        "password": "password123",
        "address": "456 Oak Ave"
    })

    response = client.post("/customers/", json={
        "name": "Jane Doe",
        "email": "jake.paul@example.com",
        "age": 25,
        "password": "password456",
        "address": "789 Pine Rd"
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Email already registered"

def test_list_customers():
    response = client.get("/customers/")
    assert response.status_code == 200
    data = response.json()
    assert "customers" in data
    assert isinstance(data["customers"], list)

def test_read_customer():

    response_create = client.post("/customers/", json={
        "name": "Jane Doe",
        "email": random_email(),
        "age": 30,
        "password": "password123",
        "address": "123 Main St"
    })

    assert response_create.status_code == 201
    data_create = response_create.json()
    customer_id = data_create["customer"]["id"]
    response_read = client.get(f"/customers/{customer_id}")
    assert response_read.status_code == 200
    data_read = response_read.json()
    assert data_read["name"] == "Jane Doe"
    expected_hashed_password = hashlib.sha256(
        "password123".encode()
    ).hexdigest()

    assert data_read["password"] == expected_hashed_password

def test_read_nonexistent_customer():
    non_existent_id = "11111111-1111-1111-1111-111111111111"
    response_read = client.get(f"/customers/{non_existent_id}")
    assert response_read.status_code == 404
    data_read = response_read.json()
    assert data_read["detail"] == "Customer not found"

def test_delete_customer():
    response_create = client.post("/customers/", json={
        "name": "Alice Smith",
        "email": "alice.smith@example.com",
        "age": 30,
        "password": "password123",
        "address": "123 Oak St"
    })
    assert response_create.status_code == 201
    data_create = response_create.json()
    customer_id = data_create["customer"]["id"]

    response_delete = client.delete(f"/customers/{customer_id}")
    assert response_delete.status_code == 200
    data_delete = response_delete.json()
    assert data_delete["message"] == "Customer deleted successfully"

def test_delete_nonexistent_customer():
    non_existent_id = "11111111-1111-1111-1111-111111111111"
    response_delete = client.delete(f"/customers/{non_existent_id}")
    assert response_delete.status_code == 404
    data_delete = response_delete.json()
    assert data_delete["detail"] == "Customer not found"
