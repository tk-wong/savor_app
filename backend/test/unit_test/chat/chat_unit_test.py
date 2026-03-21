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
    assert chat_group.name == "What is the best way..."


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
    response_data = {"recipe": {"title": "test" * 5 + "123"}}
    mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mocker.patch("backend.chat.open")
    mocker.patch("os.path.exists", return_value=True)
    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 200
    assert chat_group.name == "test" * 5 + "..."


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
