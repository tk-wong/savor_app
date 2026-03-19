import datetime


def test_get_chat_history_success(client, mock_jwt_required, mock_get_jwt_identity, mock_session,
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
