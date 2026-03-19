import datetime
from unittest.mock import MagicMock


def test_get_all_groups_success(
        client, mock_jwt_required, mock_get_jwt_identity,
        mock_chat_group_model_class, mock_chat_group_data,
        mock_chat_history_data, mock_chat_history_query
):
    mock_chat_group_model_class.query.filter_by.return_value.all.return_value = mock_chat_group_data

    # Map chat history by group id (or None if no history)
    by_group_id = {
        1: mock_chat_history_data[0],
        2: mock_chat_history_data[1],  # make sure this one has chat_group_id=2 in fixture
    }

    def filter_by_side_effect(**kwargs):
        gid = kwargs.get("chat_group_id")
        query = MagicMock()
        query.order_by.return_value.first.return_value = by_group_id.get(gid)
        return query

    mock_chat_history_query.filter_by.side_effect = filter_by_side_effect

    response = client.get("/api/chat/group/all")
    assert response.status_code == 200

    # current endpoint returns "chat_groups", not "groups"
    assert response.json["chat_groups"][0]["id"] == 1
    assert response.json["chat_groups"][1]["id"] == 2


def test_get_all_groups_empty_history(
        client, mock_jwt_required, mock_get_jwt_identity,
        mock_chat_group_model_class, mock_chat_group_data,
        mock_chat_history_data, mock_chat_history_query
):
    mock_chat_group_model_class.query.filter_by.return_value.all.return_value = mock_chat_group_data
    mock_chat_history_query.filter_by.return_value.order_by.return_value.first.return_value = None
    response = client.get("/api/chat/group/all")
    assert response.status_code == 200
    assert response.json["chat_groups"] == []


def test_get_all_groups_empty_groups(
        client, mock_jwt_required, mock_get_jwt_identity,
        mock_chat_group_model_class
):
    mock_chat_group_model_class.query.filter_by.return_value.all.return_value = None
    response = client.get("/api/chat/group/all")
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
