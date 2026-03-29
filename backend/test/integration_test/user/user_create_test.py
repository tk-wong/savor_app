import json


def test_create_user(client):
    email = "example@abc.com"
    username = "Example User"
    password = "testing"
    response = client.post("/api/user/create", data=json.dumps({
        "email": email,
        "username": username,
        "password": password
    }), content_type='application/json')
    assert response.status_code == 201
    assert response.get_json() == {"message": f"User {username} created successfully!"}


def test_create_user_existing_email(client, sample_user):
    email = "example@abc.com"
    username = "Example User"
    password = "testing"
    response = client.post("/api/user/create", data=json.dumps({
        "email": email,
        "username": username,
        "password": password
    }), content_type='application/json')
    assert response.status_code == 409
    assert response.get_json() == {"message": "User with this email already exists"}


def test_create_user_missing_email(client):
    username = "Example User"
    password = "testing"
    response = client.post("/api/user/create", data=json.dumps({
        "username": username,
        "password": password
    }), content_type='application/json')
    assert response.status_code == 400
    assert response.get_json() == {"message": "Email, username, and password are required"}


def test_create_user_missing_username(client):
    email = "example@abc.com"
    password = "testing"
    response = client.post("/api/user/create", data=json.dumps({
        "email": email,
        "password": password
    }), content_type='application/json')
    assert response.status_code == 400
    assert response.get_json() == {"message": "Email, username, and password are required"}


def test_create_user_missing_password(client):
    email = "example@abc.com"
    username = "Example User"
    response = client.post("/api/user/create", data=json.dumps({
        "email": email,
        "username": username,
    }), content_type='application/json')
    assert response.status_code == 400
    assert response.get_json() == {"message": "Email, username, and password are required"}

