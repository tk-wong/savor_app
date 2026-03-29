import datetime


def test_get_chat_history_success(client, sample_login, sample_chat_group, sample_chat):
    """Test getting chat history for a chat group with actual sample data"""
    access_token = sample_login["user"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get("/api/chat/group/1/history", headers=headers)
    assert response.status_code == 200
    assert "chat_history" in response.json
    assert len(response.json["chat_history"]) == 1
    assert response.json["chat_history"][0]["prompt"] == "Test prompt 0"
    assert response.json["chat_history"][0]["response"] == {"response": "Test response 0"}
    assert response.json["chat_history"][0]["image_url"] == "test_url0"


def test_chat_group_not_found(client, sample_login):
    """Test that accessing non-existent chat group returns 404"""
    access_token = sample_login["user"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get("/api/chat/group/999/history", headers=headers)
    assert response.status_code == 404
    assert response.json == {"message": "Chat group not found"}


def test_user_id_not_match(client, sample_login, app):
    """Test that user cannot access chat groups from other users"""
    access_token = sample_login["user"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Create another user and their chat group
    other_group_id = None
    with app.app_context():
        from backend.db_manager import db
        from backend.models.user_model import User
        from backend.models.chat_group_model import ChatGroupModel
        from werkzeug.security import generate_password_hash

        other_user = User(email="other@abc.com",
                          username="Other User",
                          password_hash=generate_password_hash("testing"))
        db.session.add(other_user)
        db.session.commit()

        other_chat_group = ChatGroupModel(create_user_id=other_user.id, name="Other Group")
        db.session.add(other_chat_group)
        db.session.commit()
        other_group_id = other_chat_group.id

    # Try to access other user's chat group
    response = client.get(f"/api/chat/group/{other_group_id}/history", headers=headers)
    assert response.status_code == 403
    assert response.json == {"message": "Unauthorized access to chat group"}


def test_unauthorized(client):
    """Test that requests without token are unauthorized"""
    response = client.get("/api/chat/group/1/history")
    assert response.status_code == 401


def test_expired_token(client, app):
    """Test that expired tokens are rejected"""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        expired_token = create_access_token(identity="1", expires_delta=datetime.timedelta(seconds=-1))
    response = client.get("/api/chat/group/1/history", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert response.json == {"msg": "Token has expired"}


def test_invalid_token(client):
    """Test that invalid tokens are rejected"""
    response = client.get("/api/chat/group/1/history", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 422
    assert response.json == {"msg": "Not enough segments"}
