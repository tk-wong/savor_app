from unittest.mock import MagicMock


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
