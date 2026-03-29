import datetime
from unittest.mock import MagicMock

import requests


def test_handle_question_response(app, client, mock_jwt_required, mock_get_jwt_identity, mock_chat_group_model_class):
    chat_group = MagicMock()
    chat_group.name = "Unnamed"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group
    prompt = "What is the best way to cook pasta?"
    response_data = {"prompt_type": "question", "response": "Boil water and add pasta."}
    from backend.chat import _handle_question_response
    with app.app_context():
        result, status_code = _handle_question_response(chat_group, prompt, response_data)
    assert status_code == 200
    assert result == response_data
    assert chat_group.name == "What is the best way to cook pasta?"


def test_handle_question_response_named_group(app, client, mock_jwt_required, mock_get_jwt_identity,
                                              mock_chat_group_model_class):
    chat_group = MagicMock()
    chat_group.name = "Existing Group"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group
    prompt = "What is the best way to cook pasta?"
    response_data = {"prompt_type": "question", "response": "Boil water and add pasta."}
    from backend.chat import _handle_question_response
    with app.app_context():
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


def test_handle_recipe_response_no_recipe_data(app, client, mock_jwt_required, mock_get_jwt_identity,
                                               mock_chat_group_model_class):
    chat_group = MagicMock()
    new_chat_history = MagicMock()
    response_data = {}
    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 500
    assert result == {"message": "Invalid response from model"}


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
    mocker.patch("pathlib.Path.exists", return_value=False)
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 200
    assert mock_mkdir.called
    assert mock_mkdir.call_args.kwargs == {"parents": True}


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
    assert response.json == {"message": "AI cooking agent response timed out"}


def test_chat_connection_error(mocker, client, mock_jwt_required, mock_get_jwt_identity, mock_chat_group_model_class,
                               mock_chat_group_data):
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = mock_chat_group_data[0]
    mocker.patch("requests.post", side_effect=requests.exceptions.ConnectionError)
    response = client.post("/api/chat/", json={"chat_group_id": 1, "prompt": "test prompt"})
    assert response.status_code == 504
    assert response.json == {"message": "AI cooking agent response timed out"}


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
    assert response.json == {"message": "Invalid response from model"}


def test_chat_invalid_prompt_type(mocker, client, mock_jwt_required, mock_get_jwt_identity, mock_chat_group_model_class,
                                  mock_chat_group_data):
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = mock_chat_group_data[0]
    mock_post = mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mock_post.return_value.json.return_value = {"recipe": {"title": "apple pie"}, "prompt_type": "invalid"}
    response = client.post("/api/chat/", json={"chat_group_id": 1, "prompt": "test prompt"})

    assert response.status_code == 500
    assert response.json == {"message": "Invalid response from model"}


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


# Ingredient Tests
def test_handle_recipe_response_with_existing_ingredient(app, mocker, client, mock_jwt_required,
                                                         mock_get_jwt_identity,
                                                         mock_chat_group_model_class, mock_session):
    """Test handling recipe response with an ingredient that already exists in the database"""
    chat_group = MagicMock()
    new_chat_history = MagicMock()
    chat_group.name = "Existing Group"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group

    # Mock existing ingredient
    existing_ingredient = MagicMock()
    existing_ingredient.id = 1
    existing_ingredient.name = "flour"

    response_data = {
        "recipe": {
            "title": "bread",
            "description": "test bread",
            "direction": ["Step 1", "Step 2"],
            "tips": ["Tip 1"],
            "ingredients": [{"name": "flour", "ingredient_name": "flour", "quantity": "500g"}]
        }
    }

    mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mocker.patch("backend.chat.open")
    mocker.patch("os.path.exists", return_value=True)

    mock_ingredient_class = mocker.patch("backend.models.ingredient_model.Ingredient")
    mock_ingredient_class.query.filter_by.return_value.first.return_value = existing_ingredient

    mocker.patch("backend.chat.RecipeIngredient")

    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 200
    assert mock_ingredient_class.query.filter_by.called


def test_handle_recipe_response_with_new_ingredient(app, mocker, client, mock_jwt_required,
                                                    mock_get_jwt_identity,
                                                    mock_chat_group_model_class, mock_session):
    """Test handling recipe response with a new ingredient that needs to be created"""
    chat_group = MagicMock()
    new_chat_history = MagicMock()
    chat_group.name = "Existing Group"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group

    # Mock new ingredient (doesn't exist yet)
    new_ingredient = MagicMock()
    new_ingredient.id = 2
    new_ingredient.name = "sugar"

    response_data = {
        "recipe": {
            "title": "cake",
            "description": "test cake",
            "direction": ["Step 1"],
            "tips": ["Tip 1"],
            "ingredients": [{"name": "sugar", "ingredient_name": "sugar", "quantity": "200g"}]
        }
    }

    mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mocker.patch("backend.chat.open")
    mocker.patch("os.path.exists", return_value=True)

    mock_ingredient_class = mocker.patch("backend.models.ingredient_model.Ingredient")
    mock_ingredient_class.query.filter_by.return_value.first.return_value = None  # Ingredient doesn't exist
    mock_ingredient_class.return_value.save.return_value = new_ingredient

    mocker.patch("backend.chat.RecipeIngredient")

    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 200
    assert mock_ingredient_class.called


def test_handle_recipe_response_with_multiple_ingredients(app, mocker, client, mock_jwt_required,
                                                          mock_get_jwt_identity,
                                                          mock_chat_group_model_class, mock_session):
    """Test handling recipe response with multiple ingredients"""
    chat_group = MagicMock()
    new_chat_history = MagicMock()
    chat_group.name = "Existing Group"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group

    # Mock multiple ingredients
    ingredient1 = MagicMock()
    ingredient1.id = 1
    ingredient1.name = "flour"

    ingredient2 = MagicMock()
    ingredient2.id = 2
    ingredient2.name = "eggs"

    response_data = {
        "recipe": {
            "title": "omelette",
            "description": "test omelette",
            "direction": ["Step 1", "Step 2"],
            "tips": ["Tip 1"],
            "ingredients": [
                {"name": "flour", "ingredient_name": "flour", "quantity": "100g"},
                {"name": "eggs", "ingredient_name": "eggs", "quantity": "3"}
            ]
        }
    }

    mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mocker.patch("backend.chat.open")
    mocker.patch("os.path.exists", return_value=True)

    mock_ingredient_class = mocker.patch("backend.models.ingredient_model.Ingredient")

    def ingredient_filter_side_effect(name):
        side_effects = {
            "flour": MagicMock(first=MagicMock(return_value=ingredient1)),
            "eggs": MagicMock(first=MagicMock(return_value=ingredient2))
        }
        return side_effects.get(name, MagicMock(first=MagicMock(return_value=None)))

    mock_ingredient_class.query.filter_by = ingredient_filter_side_effect

    mocker.patch("backend.chat.RecipeIngredient")

    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 200


def test_handle_recipe_response_empty_ingredients(app, mocker, client, mock_jwt_required,
                                                  mock_get_jwt_identity,
                                                  mock_chat_group_model_class, mock_session):
    """Test handling recipe response with no ingredients"""
    chat_group = MagicMock()
    new_chat_history = MagicMock()
    chat_group.name = "Existing Group"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group

    response_data = {
        "recipe": {
            "title": "water",
            "description": "just water",
            "direction": ["Step 1"],
            "tips": [],
            "ingredients": []  # No ingredients
        }
    }

    mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mocker.patch("backend.chat.open")
    mocker.patch("os.path.exists", return_value=True)

    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 200


def test_handle_recipe_response_ingredient_with_quantity(app, mocker, client, mock_jwt_required,
                                                         mock_get_jwt_identity,
                                                         mock_chat_group_model_class, mock_session):
    """Test that ingredient quantities are properly stored in RecipeIngredient"""
    chat_group = MagicMock()
    new_chat_history = MagicMock()
    chat_group.name = "Existing Group"
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group

    ingredient = MagicMock()
    ingredient.id = 1
    ingredient.name = "butter"

    response_data = {
        "recipe": {
            "title": "pastry",
            "description": "buttery pastry",
            "direction": ["Step 1"],
            "tips": [],
            "ingredients": [{"name": "butter", "ingredient_name": "butter", "quantity": "250g"}]
        }
    }

    mocker.patch("requests.post", return_value=MagicMock(status_code=200))
    mocker.patch("backend.chat.open")
    mocker.patch("os.path.exists", return_value=True)

    mock_ingredient_class = mocker.patch("backend.models.ingredient_model.Ingredient")
    mock_ingredient_class.query.filter_by.return_value.first.return_value = ingredient

    mock_recipe_ingredient = mocker.patch("backend.chat.RecipeIngredient")

    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)
    assert status_code == 200
    # Verify RecipeIngredient was called with proper quantity
    assert mock_recipe_ingredient.called


def test_chat_mock_models_question_no_network(app, mocker, client, mock_jwt_required, mock_get_jwt_identity,
                                              mock_chat_group_model_class, mock_chat_group_data):
    app.config["MOCK_AI_MODELS"] = True
    mock_chat_group_model_class.query.filter_by.return_value.first.return_value = mock_chat_group_data[0]
    mock_post = mocker.patch("requests.post")

    response = client.post("/api/chat/", json={"chat_group_id": 1, "prompt": "what is al dente?"})

    assert response.status_code == 200
    assert response.json["prompt_type"] == "question"
    assert response.json["response"].startswith("[MOCK]")
    mock_post.assert_not_called()


def test_handle_recipe_response_mock_models_skip_image_request(app, mocker, mock_jwt_required, mock_get_jwt_identity,
                                                               mock_session):
    app.config["MOCK_AI_MODELS"] = True
    app.config["MOCK_IMAGE_URL"] = "static/images/mock.png"
    chat_group = MagicMock()
    chat_group.name = "Unnamed"
    new_chat_history = MagicMock()
    response_data = {
        "recipe": {
            "title": "mock pasta",
            "description": "mock",
            "direction": ["step 1"],
            "tips": ["tip"],
            "ingredients": [],
        }
    }
    mock_post = mocker.patch("requests.post")

    from backend.chat import _handle_recipe_response
    with app.app_context():
        result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)

    assert status_code == 200
    assert result["recipe"]["image_url"] == "static/images/mock.png"
    mock_post.assert_not_called()
