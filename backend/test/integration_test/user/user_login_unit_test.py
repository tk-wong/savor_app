import json


def test_login(client, mock_user, mock_user_query, mocker):
    mock_user_query.filter_by.return_value.first.return_value = mock_user
    mocker.patch("backend.user.create_access_token", return_value="mock_access_token")
    response = client.post("/api/user/login", data=json.dumps({"email": "example@abc.com", "password": "testing"})
                           , content_type='application/json')
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json == {
        "user": {"id": mock_user.id, "username": mock_user.username, "access_token": "mock_access_token"}}


def test_invalid_user(client, mock_user_query):
    mock_user_query.filter_by.return_value.first.return_value = None
    response = client.post("/api/user/login", data=json.dumps({"email": "notexist@abc.com", "password": "testing"}),
                           content_type='application/json')
    assert response.status_code == 401
    assert response.get_json() == {'message': 'Invalid credentials'}


def test_invalid_password(client, mock_user, mock_user_query):
    mock_user_query.filter_by.return_value.first.return_value = mock_user
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
