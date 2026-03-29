import json


def test_login(client, sample_user):
    response = client.post("/api/user/login", data=json.dumps({"email": "example@abc.com", "password": "testing"})
                           , content_type='application/json')
    assert response.status_code == 200
    response_json = response.get_json()
    assert "user" in response_json
    assert "access_token" in response_json["user"]
    assert response_json["user"]["id"] == 1
    assert response_json["user"]["username"] == "Example User"


def test_invalid_user(client):
    response = client.post("/api/user/login", data=json.dumps({"email": "notexist@abc.com", "password": "testing"}),
                           content_type='application/json')
    assert response.status_code == 401
    assert response.get_json() == {'message': 'Invalid credentials'}


def test_invalid_password(client, sample_user):
    response = client.post("/api/user/login",
                           data=json.dumps({"email": "example@abc.com", "password": "wrong_password"}),
                           content_type='application/json')
    assert response.status_code == 401
    assert response.get_json() == {'message': 'Invalid credentials'}


def test_missing_email(client):
    response = client.post("/api/user/login", data=json.dumps({"password": "testing"}), content_type='application/json')
    assert response.status_code == 400
    assert response.get_json() == {'message': 'Email and password are required'}


def test_missing_password(client):
    response = client.post("/api/user/login", data=json.dumps({"email": "example@abc.com"}),
                           content_type='application/json')
    assert response.status_code == 400
    assert response.get_json() == {'message': 'Email and password are required'}


def test_empty_email_and_password(client):
    response = client.post("/api/user/login", data=json.dumps({}), content_type='application/json')
    assert response.status_code == 400
    assert response.get_json() == {'message': 'Email and password are required'}


def test_incorrect_request_method(client):
    response = client.get("/api/user/login")
    assert response.status_code == 405  # Method Not Allowed
