import datetime
from unittest.mock import MagicMock

import pytest
import requests


def _auth_headers(sample_login):
    return {"Authorization": f"Bearer {sample_login['user']['access_token']}"}


@pytest.fixture(autouse=True)
def chat_service_urls(app):
    app.config["AI_COOKING_AGENT_URL"] = "http://test-ai-agent"
    app.config["IMAGE_GENERATION_URL"] = "http://test-image-agent"


def test_handle_question_response(app, sample_chat_group):
    from backend.chat import _handle_question_response
    from backend.models.chat_group_model import ChatGroupModel

    with app.app_context():
        chat_group = ChatGroupModel.query.filter_by(id=1).first()
        chat_group.name = "Unnamed"

        prompt = "What is the best way to cook pasta?"
        response_data = {"prompt_type": "question", "response": "Boil water and add pasta."}
        result, status_code = _handle_question_response(chat_group, prompt, response_data)

        assert status_code == 200
        assert result == response_data
        assert chat_group.name == "What is the best way to cook pasta?"


def test_handle_question_response_named_group(app, sample_chat_group):
    from backend.chat import _handle_question_response
    from backend.models.chat_group_model import ChatGroupModel

    with app.app_context():
        chat_group = ChatGroupModel.query.filter_by(id=1).first()
        chat_group.name = "Existing Group"

        prompt = "What is the best way to cook pasta?"
        response_data = {"prompt_type": "question", "response": "Boil water and add pasta."}
        result, status_code = _handle_question_response(chat_group, prompt, response_data)

        assert status_code == 200
        assert result == response_data
        assert chat_group.name == "Existing Group"


def test_handle_recipe_response_success(app, mocker, sample_chat_group, sample_chat):
    from backend.chat import _handle_recipe_response
    from backend.models.chat_group_model import ChatGroupModel
    from backend.models.chat_history_model import ChatHistoryModel

    mocker.patch("flask_jwt_extended.get_jwt_identity", return_value="1")

    image_response = MagicMock(status_code=200)
    image_response.content = b"fake-image"
    mocker.patch("requests.post", return_value=image_response)
    mocker.patch("backend.chat.open", mocker.mock_open())
    mocker.patch("os.path.exists", return_value=True)

    with app.app_context():
        chat_group = ChatGroupModel.query.filter_by(id=1).first()
        new_chat_history = ChatHistoryModel.query.filter_by(id=1).first()
        response_data = {"recipe": {"title": "apple pie"}}

        _, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
        assert status_code == 200


def test_handle_recipe_response_no_recipe_data(app, sample_chat_group, sample_chat):
    from backend.chat import _handle_recipe_response
    from backend.models.chat_group_model import ChatGroupModel
    from backend.models.chat_history_model import ChatHistoryModel

    with app.app_context():
        chat_group = ChatGroupModel.query.filter_by(id=1).first()
        new_chat_history = ChatHistoryModel.query.filter_by(id=1).first()
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, {})

        assert status_code == 500
        assert result == {"message": "Invalid response from model"}


def test_handle_recipe_response_unnamed_group(app, mocker, sample_chat_group, sample_chat):
    from backend.chat import _handle_recipe_response
    from backend.models.chat_group_model import ChatGroupModel
    from backend.models.chat_history_model import ChatHistoryModel

    mocker.patch("flask_jwt_extended.get_jwt_identity", return_value="1")

    image_response = MagicMock(status_code=200)
    image_response.content = b"fake-image"
    mocker.patch("requests.post", return_value=image_response)
    mocker.patch("backend.chat.open", mocker.mock_open())
    mocker.patch("os.path.exists", return_value=True)

    with app.app_context():
        chat_group = ChatGroupModel.query.filter_by(id=1).first()
        chat_group.name = "Unnamed"
        new_chat_history = ChatHistoryModel.query.filter_by(id=1).first()
        response_data = {"recipe": {"title": "apple pie"}}

        _, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
        assert status_code == 200
        assert chat_group.name == "apple pie"


def test_handle_recipe_response_image_generation_timeout(app, mocker, sample_chat_group, sample_chat):
    from backend.chat import _handle_recipe_response
    from backend.models.chat_group_model import ChatGroupModel
    from backend.models.chat_history_model import ChatHistoryModel

    mocker.patch("requests.post", side_effect=requests.exceptions.Timeout)

    with app.app_context():
        chat_group = ChatGroupModel.query.filter_by(id=1).first()
        new_chat_history = ChatHistoryModel.query.filter_by(id=1).first()
        response_data = {"recipe": {"title": "apple pie"}}

        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
        assert status_code == 504
        assert result == {"message": "Image generation timed out"}


def test_handle_recipe_response_image_generation_connection_error(app, mocker, sample_chat_group, sample_chat):
    from backend.chat import _handle_recipe_response
    from backend.models.chat_group_model import ChatGroupModel
    from backend.models.chat_history_model import ChatHistoryModel

    mocker.patch("requests.post", side_effect=requests.exceptions.ConnectionError)

    with app.app_context():
        chat_group = ChatGroupModel.query.filter_by(id=1).first()
        new_chat_history = ChatHistoryModel.query.filter_by(id=1).first()
        response_data = {"recipe": {"title": "apple pie"}}

        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
        assert status_code == 504
        assert result == {"message": "Image generation timed out"}


def test_handle_recipe_response_image_generation_not_success(app, mocker, sample_chat_group, sample_chat):
    from backend.chat import _handle_recipe_response
    from backend.models.chat_group_model import ChatGroupModel
    from backend.models.chat_history_model import ChatHistoryModel

    mocker.patch("requests.post", return_value=MagicMock(status_code=404))

    with app.app_context():
        chat_group = ChatGroupModel.query.filter_by(id=1).first()
        new_chat_history = ChatHistoryModel.query.filter_by(id=1).first()
        response_data = {"recipe": {"title": "apple pie"}}

        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
        assert status_code == 500
        assert result == {"message": "Error generating image from the image generation model"}


def test_handle_recipe_response_mkdir(app, mocker, sample_chat_group, sample_chat):
    from backend.chat import _handle_recipe_response
    from backend.models.chat_group_model import ChatGroupModel
    from backend.models.chat_history_model import ChatHistoryModel

    mocker.patch("flask_jwt_extended.get_jwt_identity", return_value="1")

    image_response = MagicMock(status_code=200)
    image_response.content = b"fake-image"
    mocker.patch("requests.post", return_value=image_response)
    mocker.patch("backend.chat.open", mocker.mock_open())
    mocker.patch("os.path.exists", return_value=False)
    mock_makedir = mocker.patch("os.makedirs")

    with app.app_context():
        chat_group = ChatGroupModel.query.filter_by(id=1).first()
        new_chat_history = ChatHistoryModel.query.filter_by(id=1).first()
        response_data = {"recipe": {"title": "apple pie"}}

        _, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
        assert status_code == 200
        assert mock_makedir.called
        assert mock_makedir.call_args[0][0] == "static/images"


def test_chat_question_success(client, mocker, sample_login, sample_chat_group):
    mocker.patch("backend.chat._handle_question_response", return_value=({"response": "Test response"}, 200))
    mock_post = mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mock_post.return_value.json.return_value = {"recipe": {"title": "apple pie"}, "prompt_type": "question"}

    response = client.post(
        "/api/chat/",
        json={"prompt": "Test prompt", "chat_group_id": 1},
        headers=_auth_headers(sample_login),
    )
    assert response.status_code == 200
    assert response.json == {"response": "Test response"}


def test_chat_recipe_success(client, mocker, sample_login, sample_chat_group):
    mocker.patch("backend.chat._handle_recipe_response", return_value=({"response": "Test response"}, 200))
    mock_post = mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mock_post.return_value.json.return_value = {"recipe": {"title": "apple pie"}, "prompt_type": "recipe"}

    response = client.post(
        "/api/chat/",
        json={"prompt": "Test prompt", "chat_group_id": 1},
        headers=_auth_headers(sample_login),
    )
    assert response.status_code == 200
    assert response.json == {"response": "Test response"}


def test_chat_no_prompt(client, sample_login, sample_chat_group):
    response = client.post(
        "/api/chat/",
        json={"chat_group_id": 1},
        headers=_auth_headers(sample_login),
    )
    assert response.status_code == 400
    assert response.json == {"message": "Prompt is required"}


def test_chat_no_chat_group_id(client, sample_login):
    response = client.post(
        "/api/chat/",
        json={"prompt": "test prompt"},
        headers=_auth_headers(sample_login),
    )
    assert response.status_code == 400
    assert response.json == {"message": "Chat group id is required"}


def test_chat_invalid_chat_group(client, sample_login):
    response = client.post(
        "/api/chat/",
        json={"chat_group_id": 999, "prompt": "test prompt"},
        headers=_auth_headers(sample_login),
    )
    assert response.status_code == 404
    assert response.json == {"message": "Chat group not found"}


def test_chat_timeout(mocker, client, sample_login, sample_chat_group):
    mocker.patch("requests.post", side_effect=requests.exceptions.Timeout)
    response = client.post(
        "/api/chat/",
        json={"chat_group_id": 1, "prompt": "test prompt"},
        headers=_auth_headers(sample_login),
    )
    assert response.status_code == 504
    assert response.json == {"message": "AI cooking agent response timed out"}


def test_chat_connection_error(mocker, client, sample_login, sample_chat_group):
    mocker.patch("requests.post", side_effect=requests.exceptions.ConnectionError)
    response = client.post(
        "/api/chat/",
        json={"chat_group_id": 1, "prompt": "test prompt"},
        headers=_auth_headers(sample_login),
    )
    assert response.status_code == 504
    assert response.json == {"message": "AI cooking agent response timed out"}


def test_chat_status_code_not_success(mocker, client, sample_login, sample_chat_group):
    mocker.patch("requests.post", return_value=MagicMock(status_code=404))
    response = client.post(
        "/api/chat/",
        json={"chat_group_id": 1, "prompt": "test prompt"},
        headers=_auth_headers(sample_login),
    )
    assert response.status_code == 500
    assert response.json == {"message": "Error generating response"}


def test_chat_invalid_json(mocker, client, sample_login, sample_chat_group):
    mock_post = mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mock_post.return_value.json.side_effect = requests.exceptions.JSONDecodeError("Invalid JSON", "invalid JSON", 0)

    response = client.post(
        "/api/chat/",
        json={"chat_group_id": 1, "prompt": "test prompt"},
        headers=_auth_headers(sample_login),
    )

    assert response.status_code == 500
    assert response.json == {"message": "Invalid response from model"}


def test_chat_no_prompt_type(mocker, client, sample_login, sample_chat_group):
    mock_post = mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mock_post.return_value.json.return_value = {"recipe": {"title": "apple pie"}}
    response = client.post(
        "/api/chat/",
        json={"chat_group_id": 1, "prompt": "test prompt"},
        headers=_auth_headers(sample_login),
    )

    assert response.status_code == 500
    assert response.json == {"message": "Invalid response from model"}


def test_chat_invalid_prompt_type(mocker, client, sample_login, sample_chat_group):
    mock_post = mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mock_post.return_value.json.return_value = {"recipe": {"title": "apple pie"}, "prompt_type": "invalid"}
    response = client.post(
        "/api/chat/",
        json={"chat_group_id": 1, "prompt": "test prompt"},
        headers=_auth_headers(sample_login),
    )

    assert response.status_code == 500
    assert response.json == {"message": "Invalid response from model"}


def test_chat_invalid_method(client):
    response = client.get("/api/chat/", json={})
    assert response.status_code == 405


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
