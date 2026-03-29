import datetime


def test_get_all_groups_success(
        client, sample_chat_group, sample_login, sample_chat
):
    access_token = sample_login.get("user").get("access_token")
    response = client.get("/api/chat/group/all", headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200

    # current endpoint returns "chat_groups", not "groups"
    assert response.json["chat_groups"][0]["id"] == 1
    assert response.json["chat_groups"][1]["id"] == 2


def test_get_all_groups_empty_history(
        client, sample_chat_group, sample_login
):
    access_token = sample_login.get("user").get("access_token")
    response = client.get("/api/chat/group/all", headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json["chat_groups"] == []


def test_get_all_groups_empty_groups(
        client, sample_login
):
    access_token = sample_login.get("user").get("access_token")
    response = client.get("/api/chat/group/all", headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json["chat_groups"] == []


def test_get_all_groups_unauthorized(client):
    response = client.get("/api/chat/group/all")
    assert response.status_code == 401


def test_get_all_groups_invalid_token(client):
    response = client.get("/api/chat/group/all", headers={"Authorization": "Bearer 123"})
    assert response.status_code == 422
    assert response.json == {"msg": "Not enough segments"}


def test_get_all_groups_expired_token(app, client):
    with app.app_context():
        from flask_jwt_extended import create_access_token
        expired_token = create_access_token(identity="1", expires_delta=datetime.timedelta(seconds=-1))
    response = client.get("/api/chat/group/all", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert response.json == {"msg": "Token has expired"}
