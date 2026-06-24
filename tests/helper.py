def random_string(length=10):
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_email():
    return random_string(10) + "@example.com"

def create_user_test(client, name, email, age, password):
    response = client.post("/users/", json={
        "name": name,
        "email": email,
        "age": age,
        "password": password
    })
    assert response.status_code == 201
    return response.json()["user"]

def create_customer_test(client,token, name, email, age, password, address):
    response = client.post("/customers/", headers={
        "Authorization": f"Bearer {token}"
    }, json={
        "name": name,
        "email": email,
        "age": age,
        "password": password,
        "address": address

    })
    assert response.status_code == 201
    return response.json()["customer"]

def get_auth_token(client):
    user = create_user_test(
        client,
        random_string(10),
        random_email(),
        18,
        "password123"
    )

    login = client.post("/token", data={
        "username": user["email"],
        "password": "password123"
    })

    return login.json()["access_token"]