from main import app
from fastapi.testclient import TestClient
import hashlib
import random 
import string

from tests.helper import  create_customer_test, create_order_test, get_auth_token, random_email, random_string

def test_create_order(client):
    token = get_auth_token(client)
    customer = create_customer_test(client, token, random_string(10), random_email(), 30, "password123", "123 Main St")
    order = create_order_test(client, token, customer["id"], "Test Order Description")
    assert order["description"] == "Test Order Description"
    assert order["customer_id"] == customer["id"]


def test_list_orders(client):
    token = get_auth_token(client)

    response = client.get("/orders/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert isinstance(data["orders"], list)

def test_read_order(client):
    token = get_auth_token(client)
    customer = create_customer_test(client, token, random_string(10), random_email(), 30, "password123", "123 Main St")
    order = create_order_test(client, token, customer["id"], "Test Order Description")

    response_read = client.get(f"/orders/{order['id']}", headers={"Authorization": f"Bearer {token}"})
    data_read = response_read.json()
    assert response_read.status_code == 200
    assert data_read["description"] == "Test Order Description"
    assert data_read["customer_id"] == customer["id"]

def test_read_nonexistent_order(client):
    token = get_auth_token(client)
    non_existent_id = "11111111-1111-1111-1111-111111111111"
    response_read = client.get(f"/orders/{non_existent_id}", headers={"Authorization": f"Bearer {token}"})
    assert response_read.status_code == 404
    data_read = response_read.json()
    assert data_read["detail"] == "Order not found or you're not authorized to access this order"

def test_delete_order(client):
    token = get_auth_token(client)
    customer = create_customer_test(client, token, random_string(10), random_email(), 30, "password123", "123 Main St")
    order = create_order_test(client, token, customer["id"], "Test Order Description")

    response_delete = client.delete(f"/orders/{order['id']}", headers={"Authorization": f"Bearer {token}"})
    assert response_delete.status_code == 200
    data_delete = response_delete.json()
    assert data_delete["message"] == "Order deleted successfully"

    # Verify that the order is no longer accessible
    response_read = client.get(f"/orders/{order['id']}", headers={"Authorization": f"Bearer {token}"})
    assert response_read.status_code == 404
    data_read = response_read.json()
    assert data_read["detail"] == "Order not found or you're not authorized to access this order"

def test_delete_nonexistent_order(client):
    token = get_auth_token(client)
    non_existent_id = "11111111-1111-1111-1111-111111111111"
    response_delete = client.delete(f"/orders/{non_existent_id}", headers={"Authorization": f"Bearer {token}"})
    assert response_delete.status_code == 404
    data_delete = response_delete.json()
    assert data_delete["detail"] == "Order not found or you're not authorized to delete this order"
