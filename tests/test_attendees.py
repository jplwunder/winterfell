
from datetime import datetime

from tests.helper import create_event_test, create_user, random_email, random_string
from fastapi.testclient import TestClient
from app.main import app

def test_list_organizers(client):
    # Create a user and log in
    email = random_email()
    password = "password123"
    user = create_user(client, random_string(10), email, password)
    response_login = client.post("/auth/login", data={"username": email, "password": password})
    token = response_login.json()["access_token"]

    event_name = random_string(10)
    event_date = datetime.now().isoformat()
    event_location = random_string(10)
    event_description = random_string(20)
    event = create_event_test(client, token, event_name, event_date, event_location, event_description)

    response_organizers = client.get(
        f"/attendees/organizers/{event['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response_organizers.status_code == 200
    data_organizers = response_organizers.json()
    assert "users" in data_organizers