import datetime
from unittest.mock import MagicMock

import requests


def test_handle_question_response(client, mock_jwt_required, mock_get_jwt_identity, mock_chat_group_model_class):
    chat_group = MagicMock()
    chat_group.name = "Unnamed"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group
    prompt = "What is the best way to cook pasta?"
    response_data = {"prompt_type": "question", "response": "Boil water and add pasta."}
    from backend.chat import _handle_question_response
    result, status_code = _handle_question_response(chat_group, prompt, response_data)
    assert status_code == 200
    assert result == response_data
    assert chat_group.name == "What is the best way to cook pasta?"


def test_handle_question_response_named_group(client, mock_jwt_required, mock_get_jwt_identity,
                                              mock_chat_group_model_class):
    chat_group = MagicMock()
    chat_group.name = "Existing Group"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group
    prompt = "What is the best way to cook pasta?"
    response_data = {"prompt_type": "question", "response": "Boil water and add pasta."}
    from backend.chat import _handle_question_response
    result, status_code = _handle_question_response(chat_group, prompt, response_data)
    assert status_code == 200
    assert result == response_data
    assert chat_group.name == "Existing Group"  # name should not change


def test_handle_recipe_response_success(app, mocker, client, mock_jwt_required, mock_get_jwt_identity,
                                        mock_chat_group_model_class, mock_session):
    chat_group = MagicMock()
    new_chat_history = MagicMock()
    chat_group.name = "Existing Group"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group
    response_data = {"recipe": {"title": "apple pie"}}
    mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mocker.patch("backend.chat.open")
    mocker.patch("os.path.exists", return_value=True)
    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 200


def test_handle_recipe_response_no_recipe_data(client, mock_jwt_required, mock_get_jwt_identity,
                                               mock_chat_group_model_class):
    chat_group = MagicMock()
    new_chat_history = MagicMock()
    response_data = {}
    from backend.chat import _handle_recipe_response
    result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 500
    assert result == {"message": "Response missing recipe data"}


def test_handle_recipe_response_unnamed_group(app, mocker, client, mock_jwt_required, mock_get_jwt_identity,
                                              mock_chat_group_model_class, mock_session):
    chat_group = MagicMock()
    new_chat_history = MagicMock()
    chat_group.name = "Unnamed"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group
    response_data = {"recipe": {"title": "apple pie"}}
    mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mocker.patch("backend.chat.open")
    mocker.patch("os.path.exists", return_value=True)
    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 200
    assert chat_group.name == "apple pie"


def test_handle_recipe_response_unnamed_group_long_title(app, mocker, client, mock_jwt_required, mock_get_jwt_identity,
                                                         mock_chat_group_model_class, mock_session):
    chat_group = MagicMock()
    new_chat_history = MagicMock()
    chat_group.name = "Unnamed"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group
    response_data = {"recipe": {"title": "test" * 63 + "123456"}}
    mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mocker.patch("backend.chat.open")
    mocker.patch("os.path.exists", return_value=True)
    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 200
    assert chat_group.name == "test" * 63 + "..."


def test_handle_recipe_response_image_generation_timeout(app, mocker, client, mock_jwt_required, mock_get_jwt_identity,
                                                         mock_chat_group_model_class, mock_session):
    chat_group = MagicMock()
    new_chat_history = MagicMock()
    chat_group.name = "Existing Group"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group
    response_data = {"recipe": {"title": "apple pie"}}
    mocker.patch("requests.post", side_effect=requests.exceptions.Timeout)
    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 504
    assert result == {"message": "Image generation timed out"}


def test_handle_recipe_response_image_generation_connection_error(app, mocker, client, mock_jwt_required,
                                                                  mock_get_jwt_identity,
                                                                  mock_chat_group_model_class, mock_session):
    chat_group = MagicMock()
    new_chat_history = MagicMock()
    chat_group.name = "Existing Group"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group
    response_data = {"recipe": {"title": "apple pie"}}
    mocker.patch("requests.post", side_effect=requests.exceptions.ConnectionError)
    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 504
    assert result == {"message": "Image generation timed out"}


def test_handle_recipe_response_image_generation_not_success(app, mocker, client, mock_jwt_required,
                                                             mock_get_jwt_identity,
                                                             mock_chat_group_model_class, mock_session):
    chat_group = MagicMock()
    new_chat_history = MagicMock()
    chat_group.name = "Existing Group"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group
    response_data = {"recipe": {"title": "apple pie"}}
    mocker.patch("requests.post", return_value=MagicMock(status_code=404))
    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 500
    assert result == {"message": "Error generating image from the image generation model"}


def test_handle_recipe_response_mkdir(app, mocker, client, mock_jwt_required, mock_get_jwt_identity,
                                      mock_chat_group_model_class, mock_session):
    chat_group = MagicMock()
    new_chat_history = MagicMock()
    chat_group.name = "Existing Group"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group
    response_data = {"recipe": {"title": "apple pie"}}
    mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mocker.patch("backend.chat.open")
    mocker.patch("os.path.exists", return_value=False)
    mock_makedir = mocker.patch("os.makedirs")
    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 200
    assert mock_makedir.called
    assert mock_makedir.call_args[0][0] == "static/images"


def test_chat_question_success(app, mocker, client, mock_jwt_required, mock_get_jwt_identity, mock_chat_group_data,
                               mock_chat_group_model_class):
    mocker.patch("backend.chat._handle_question_response", return_value=({"response": "Test response"}, 200))
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = mock_chat_group_data[0]
    mock_post = mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mock_post.return_value.json.return_value = {"recipe": {"title": "apple pie"}, "prompt_type": "question"}
    response = client.post("/api/chat/", json={"prompt": "Test prompt", "chat_group_id": 1})
    assert response.status_code == 200
    assert response.json == {"response": "Test response"}


def test_chat_recipe_success(app, mocker, client, mock_jwt_required, mock_get_jwt_identity, mock_chat_group_data,
                             mock_chat_group_model_class):
    mocker.patch("backend.chat._handle_recipe_response", return_value=({"response": "Test response"}, 200))
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = mock_chat_group_data[0]
    mock_post = mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mock_post.return_value.json.return_value = {"recipe": {"title": "apple pie"}, "prompt_type": "recipe"}
    response = client.post("/api/chat/", json={"prompt": "Test prompt", "chat_group_id": 1})
    assert response.status_code == 200
    assert response.json == {"response": "Test response"}


def test_chat_no_prompt(client, mock_jwt_required, mock_get_jwt_identity):
    response = client.post("/api/chat/", json={"chat_group_id": 1})
    assert response.status_code == 400
    assert response.json == {"message": "Prompt is required"}


def test_chat_no_chat_group_id(client, mock_jwt_required, mock_get_jwt_identity):
    response = client.post("/api/chat/", json={"prompt": "test prompt"})
    assert response.status_code == 400
    assert response.json == {"message": "Chat group id is required"}


def test_chat_invalid_chat_group(client, mock_jwt_required, mock_get_jwt_identity, mock_chat_group_model_class):
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = None
    response = client.post("/api/chat/", json={"chat_group_id": 1, "prompt": "test prompt"})
    assert response.status_code == 404
    assert response.json == {"message": "Chat group not found"}


def test_chat_timeout(mocker, client, mock_jwt_required, mock_get_jwt_identity, mock_chat_group_model_class,
                      mock_chat_group_data):
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = mock_chat_group_data[0]
    mocker.patch("requests.post", side_effect=requests.exceptions.Timeout)
    response = client.post("/api/chat/", json={"chat_group_id": 1, "prompt": "test prompt"})
    assert response.status_code == 504
    assert response.json == {"message": "Model response timed out"}


def test_chat_connection_error(mocker, client, mock_jwt_required, mock_get_jwt_identity, mock_chat_group_model_class,
                               mock_chat_group_data):
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = mock_chat_group_data[0]
    mocker.patch("requests.post", side_effect=requests.exceptions.ConnectionError)
    response = client.post("/api/chat/", json={"chat_group_id": 1, "prompt": "test prompt"})
    assert response.status_code == 504
    assert response.json == {"message": "Model response timed out"}


def test_chat_status_code_not_success(mocker, client, mock_jwt_required, mock_get_jwt_identity,
                                      mock_chat_group_model_class,
                                      mock_chat_group_data):
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = mock_chat_group_data[0]
    mocker.patch("requests.post", return_value=MagicMock(status_code=404))
    response = client.post("/api/chat/", json={"chat_group_id": 1, "prompt": "test prompt"})
    assert response.status_code == 500
    assert response.json == {"message": "Error generating response"}


def test_chat_invalid_json(mocker, client, mock_jwt_required, mock_get_jwt_identity, mock_chat_group_model_class,
                           mock_chat_group_data):
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = mock_chat_group_data[0]
    mock_post = mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mock_post.return_value.json.side_effect = requests.exceptions.JSONDecodeError("Invalid JSON", "invalid JSON string",
                                                                                  0)
    response = client.post("/api/chat/", json={"chat_group_id": 1, "prompt": "test prompt"})

    assert response.status_code == 500
    assert response.json == {"message": "Invalid response from model"}


def test_chat_no_prompt_type(mocker, client, mock_jwt_required, mock_get_jwt_identity, mock_chat_group_model_class,
                             mock_chat_group_data):
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = mock_chat_group_data[0]
    mock_post = mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mock_post.return_value.json.return_value = {"recipe": {"title": "apple pie"}}
    response = client.post("/api/chat/", json={"chat_group_id": 1, "prompt": "test prompt"})

    assert response.status_code == 500
    assert response.json == {"message": "Response missing prompt_type"}


def test_chat_invalid_prompt_type(mocker, client, mock_jwt_required, mock_get_jwt_identity, mock_chat_group_model_class,
                                  mock_chat_group_data):
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = mock_chat_group_data[0]
    mock_post = mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mock_post.return_value.json.return_value = {"recipe": {"title": "apple pie"}, "prompt_type": "invalid"}
    response = client.post("/api/chat/", json={"chat_group_id": 1, "prompt": "test prompt"})

    assert response.status_code == 500
    assert response.json == {"message": "Error generating response"}


def test_chat_invalid_method(client):
    response = client.get("/api/chat/", json={})
    assert response.status_code == 405  # Method Not Allowed


def test_chat_unauthorized(client):
    response = client.post("/api/chat/")
    assert response.status_code == 401


def test_chat_expired_token(client, app):
    with app.app_context():
        from flask_jwt_extended import create_access_token
        expired_token = create_access_token(identity="1", expires_delta=datetime.timedelta(seconds=-1))
    response = client.post("/api/chat/", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert response.json == {"msg": "Token has expired"}


def test_chat_invalid_token(client):
    response = client.post("/api/chat/", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 422
    assert response.json == {"msg": "Not enough segments"}
