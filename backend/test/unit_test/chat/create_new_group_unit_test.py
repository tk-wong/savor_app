import datetime
import time


def test_create_new_group_success(client, mock_jwt_required, mock_get_jwt_identity, mock_chat_group_model_class,
                                  mock_session):
    mock_chat_group_model_class.return_value = mock_chat_group_model_class
    mock_chat_group_model_class.id = 1
    response = client.get('/api/chat/group/new')
    assert response.status_code == 200
    assert response.json == {"message": "New chat group created", "group_id": 1}
    mock_chat_group_model_class.assert_called_once_with(create_user_id=1)
    mock_session.add.assert_called_once_with(mock_chat_group_model_class)
    mock_session.commit.assert_called_once()


def test_create_new_group_invalid_method(client):
    response = client.post('/api/chat/group/new')
    assert response.status_code == 405


def test_create_new_group_unauthorized(client):
    response = client.get('/api/chat/group/new')
    assert response.status_code == 401
    assert response.json == {"msg": "Missing Authorization Header"}


def test_create_new_group_invalid_token(client):
    response = client.get('/api/chat/group/new', headers={'Authorization': 'Bearer mock_token'})
    assert response.status_code == 422
    assert response.json == {'msg': 'Not enough segments'}


def test_create_new_group_expired_token(client, app):
    with app.app_context():
        from flask_jwt_extended import create_access_token
        expired_token = create_access_token(identity="1", expires_delta=datetime.timedelta(seconds=1))
        time.sleep(1)  # Wait for the token to expire
    response = client.get('/api/chat/group/new', headers={'Authorization': f'Bearer {expired_token}'})
    assert response.status_code == 401
    assert response.json == {'msg': 'Token has expired'}
