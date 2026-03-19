import datetime


def test_get_chat_history_success(client, mock_jwt_required, mock_get_jwt_identity,
                                  mock_chat_group_model_class, mock_chat_group_data, mock_chat_history_data,
                                  mock_chat_history_query):
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = mock_chat_group_data[0]
    mock_chat_history_query.filter_by.return_value.all.return_value = [mock_chat_history_data[0]]
    correct_response = {"chat_history": [
        {"id": 1, "prompt": "Test prompt 1", "response": {"response": "Test response 1"}, "image_url": "test_url1",
         "timestamp": datetime.datetime.fromisoformat("2024-01-01T00:00:00").strftime('%a, %d %b %Y %H:%M:%S GMT')}]}
    response = client.get("/api/chat/group/1/history")
    assert response.status_code == 200
    assert response.json == correct_response


def test_chat_group_not_found(client, mock_jwt_required, mock_get_jwt_identity,
                              mock_chat_group_model_class):
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = None
    response = client.get("/api/chat/group/1/history")
    assert response.status_code == 404
    assert response.json == {"message": "Chat group not found"}


def test_user_id_not_match(client, mock_jwt_required, mock_get_jwt_identity, mock_chat_group_data,
                           mock_chat_group_model_class):
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = mock_chat_group_data[1]
    response = client.get("/api/chat/group/1/history")
    assert response.status_code == 403
    assert response.json == {"message": "Unauthorized access to chat group"}


def test_unauthorized(client):
    response = client.get("/api/recipes/")
    assert response.status_code == 401


def test_expired_token(client, app):
    with app.app_context():
        from flask_jwt_extended import create_access_token
        expired_token = create_access_token(identity="1", expires_delta=datetime.timedelta(seconds=-1))
    response = client.get("/api/recipes/", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert response.json == {"msg": "Token has expired"}


def test_invalid_token(client):
    response = client.get("/api/recipes/", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 422
    assert response.json == {"msg": "Not enough segments"}
