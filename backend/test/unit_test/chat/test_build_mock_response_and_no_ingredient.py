"""
Unit tests for _build_mock_ai_response function and recipe response with no ingredients.
Tests logging of mock responses and handling of recipes without ingredients.
"""
from unittest.mock import MagicMock


class TestBuildMockAIResponse:
    """Test cases for _build_mock_ai_response function"""

    def test_build_mock_ai_response_recipe_hint_recipe(self, app):
        """Test that 'recipe' keyword triggers recipe response type"""
        from backend.chat import _build_mock_ai_response
        prompt = "Can you give me a recipe for chicken soup?"
        with app.app_context():
            result = _build_mock_ai_response(prompt)

        assert result["prompt_type"] == "recipe"
        assert "recipe" in result
        assert result["recipe"]["title"] == "Mock Recipe"
        assert "direction" in result["recipe"]
        assert "ingredients" in result["recipe"]

    def test_build_mock_ai_response_recipe_hint_cook(self, app):
        """Test that 'cook' keyword triggers recipe response type"""
        from backend.chat import _build_mock_ai_response
        prompt = "How do I cook salmon?"
        with app.app_context():
            result = _build_mock_ai_response(prompt)

        assert result["prompt_type"] == "recipe"
        assert result["recipe"]["title"] == "Mock Recipe"

    def test_build_mock_ai_response_recipe_hint_bake(self, app):
        """Test that 'bake' keyword triggers recipe response type"""
        from backend.chat import _build_mock_ai_response
        prompt = "Can you help me bake a cake?"
        with app.app_context():
            result = _build_mock_ai_response(prompt)

        assert result["prompt_type"] == "recipe"
        assert result["recipe"]["title"] == "Mock Recipe"

    def test_build_mock_ai_response_recipe_hint_dish(self, app):
        """Test that 'dish' keyword triggers recipe response type"""
        from backend.chat import _build_mock_ai_response
        prompt = "What's a good dish to cook for dinner?"
        with app.app_context():
            result = _build_mock_ai_response(prompt)

        assert result["prompt_type"] == "recipe"
        assert result["recipe"]["title"] == "Mock Recipe"

    def test_build_mock_ai_response_recipe_hint_meal(self, app):
        """Test that 'meal' keyword triggers recipe response type"""
        from backend.chat import _build_mock_ai_response
        prompt = "What meal should I prepare today?"
        with app.app_context():
            result = _build_mock_ai_response(prompt)

        assert result["prompt_type"] == "recipe"
        assert result["recipe"]["title"] == "Mock Recipe"

    def test_build_mock_ai_response_recipe_hint_case_insensitive(self, app):
        """Test that recipe hints are case-insensitive"""
        from backend.chat import _build_mock_ai_response
        prompt = "RECIPE for pasta please!"
        with app.app_context():
            result = _build_mock_ai_response(prompt)

        assert result["prompt_type"] == "recipe"
        assert result["recipe"]["title"] == "Mock Recipe"

    def test_build_mock_ai_response_question_type(self, app):
        """Test that non-recipe prompts return question type"""
        from backend.chat import _build_mock_ai_response
        prompt = "What are the nutritional benefits of spinach?"
        with app.app_context():
            result = _build_mock_ai_response(prompt)

        assert result["prompt_type"] == "question"
        assert "response" in result
        assert "[MOCK]" in result["response"]

    def test_build_mock_ai_response_question_type_empty_prompt(self, app):
        """Test that empty prompt returns question type"""
        from backend.chat import _build_mock_ai_response
        prompt = ""
        with app.app_context():
            result = _build_mock_ai_response(prompt)

        assert result["prompt_type"] == "question"
        assert result["response"] == "[MOCK] "

    def test_build_mock_ai_response_recipe_description(self, app):
        """Test that recipe response contains description from prompt"""
        from backend.chat import _build_mock_ai_response
        prompt = "Give me a recipe for pizza"
        with app.app_context():
            result = _build_mock_ai_response(prompt)

        assert result["prompt_type"] == "recipe"
        assert f"Mock response for: {prompt}" in result["recipe"]["description"]

    def test_build_mock_ai_response_recipe_directions(self, app):
        """Test that recipe response contains directions"""
        from backend.chat import _build_mock_ai_response
        prompt = "recipe for tacos"
        with app.app_context():
            result = _build_mock_ai_response(prompt)

        assert result["prompt_type"] == "recipe"
        assert isinstance(result["recipe"]["direction"], list)
        assert len(result["recipe"]["direction"]) > 0
        assert "Prepare ingredients" in result["recipe"]["direction"]

    def test_build_mock_ai_response_recipe_tips(self, app):
        """Test that recipe response contains tips"""
        from backend.chat import _build_mock_ai_response
        prompt = "bake a bread"
        with app.app_context():
            result = _build_mock_ai_response(prompt)

        assert result["prompt_type"] == "recipe"
        assert isinstance(result["recipe"]["tips"], list)
        assert len(result["recipe"]["tips"]) > 0

    def test_build_mock_ai_response_recipe_ingredients(self, app):
        """Test that recipe response contains ingredients"""
        from backend.chat import _build_mock_ai_response
        prompt = "meal idea with salmon"
        with app.app_context():
            result = _build_mock_ai_response(prompt)

        assert result["prompt_type"] == "recipe"
        assert isinstance(result["recipe"]["ingredients"], list)
        assert len(result["recipe"]["ingredients"]) > 0

        # Check ingredient structure
        for ingredient in result["recipe"]["ingredients"]:
            assert "name" in ingredient
            assert "quantity" in ingredient

    def test_build_mock_ai_response_question_response_includes_prompt(self, app):
        """Test that question response includes the original prompt"""
        from backend.chat import _build_mock_ai_response
        prompt = "How to store vegetables?"
        with app.app_context():
            result = _build_mock_ai_response(prompt)

        assert result["prompt_type"] == "question"
        assert prompt in result["response"]


class TestNoIngredientRecipeResponse:
    """Test cases for recipe response handling with no ingredients"""

    def test_handle_recipe_response_no_ingredients_list(self, app, mocker, mock_jwt_required,
                                                        mock_get_jwt_identity, mock_chat_group_model_class,
                                                        mock_session):
        """Test handling recipe response when ingredients list is missing"""
        chat_group = MagicMock()
        new_chat_history = MagicMock()
        chat_group.name = "Test Group"
        mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group

        response_data = {
            "recipe": {
                "title": "Simple Soup",
                "description": "A simple soup",
                "direction": ["Boil water", "Add salt"],
                "tips": ["Season to taste"],
                # Missing ingredients key
            }
        }

        mocker.patch("requests.post", return_value=MagicMock(status_code=200))
        mocker.patch("backend.chat.open")
        mocker.patch("os.path.exists", return_value=True)

        from backend.chat import _handle_recipe_response
        with app.app_context():
            result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)

        assert status_code == 200
        assert result["recipe"]["title"] == "Simple Soup"

    def test_handle_recipe_response_empty_ingredients_array(self, app, mocker, mock_jwt_required,
                                                            mock_get_jwt_identity, mock_chat_group_model_class,
                                                            mock_session):
        """Test handling recipe response when ingredients array is empty"""
        chat_group = MagicMock()
        new_chat_history = MagicMock()
        chat_group.name = "Test Group"
        mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group

        response_data = {
            "recipe": {
                "title": "Water",
                "description": "Just water",
                "direction": ["Get water"],
                "tips": [],
                "ingredients": []  # Empty ingredients
            }
        }

        mocker.patch("requests.post", return_value=MagicMock(status_code=200))
        mocker.patch("backend.chat.open")
        mocker.patch("os.path.exists", return_value=True)

        from backend.chat import _handle_recipe_response
        with app.app_context():
            result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)

        assert status_code == 200
        assert result["recipe"]["title"] == "Water"

    def test_handle_recipe_response_ingredient_with_no_name(self, app, mocker, mock_jwt_required,
                                                            mock_get_jwt_identity, mock_chat_group_model_class,
                                                            mock_session):
        """Test that ingredients without name are skipped"""
        chat_group = MagicMock()
        new_chat_history = MagicMock()
        chat_group.name = "Test Group"
        mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group

        response_data = {
            "recipe": {
                "title": "Mystery Dish",
                "description": "A mystery",
                "direction": ["Mix it"],
                "tips": [],
                "ingredients": [
                    {"quantity": "1 cup"},  # Missing 'name'
                    {"name": "salt", "quantity": "1 tsp"}  # Valid ingredient
                ]
            }
        }

        mocker.patch("requests.post", return_value=MagicMock(status_code=200))
        mocker.patch("backend.chat.open")
        mocker.patch("os.path.exists", return_value=True)

        mock_ingredient_class = mocker.patch("backend.models.ingredient_model.Ingredient")
        existing_ingredient = MagicMock()
        existing_ingredient.id = 1
        mock_ingredient_class.query.filter_by.return_value.first.return_value = existing_ingredient
        mocker.patch("backend.chat.RecipeIngredient")

        from backend.chat import _handle_recipe_response
        with app.app_context():
            result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)

        assert status_code == 200
        # The valid ingredient should still be processed
        assert mock_ingredient_class.query.filter_by.called

    def test_handle_recipe_response_ingredient_with_empty_name(self, app, mocker, mock_jwt_required,
                                                               mock_get_jwt_identity, mock_chat_group_model_class,
                                                               mock_session):
        """Test that ingredients with empty name are skipped"""
        chat_group = MagicMock()
        new_chat_history = MagicMock()
        chat_group.name = "Test Group"
        mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group

        response_data = {
            "recipe": {
                "title": "Vague Recipe",
                "description": "Vague",
                "direction": ["Step 1"],
                "tips": [],
                "ingredients": [
                    {"name": "", "quantity": "1 cup"},  # Empty name
                    {"name": "pepper", "quantity": "1 tsp"}  # Valid ingredient
                ]
            }
        }

        mocker.patch("requests.post", return_value=MagicMock(status_code=200))
        mocker.patch("backend.chat.open")
        mocker.patch("os.path.exists", return_value=True)

        mock_ingredient_class = mocker.patch("backend.models.ingredient_model.Ingredient")
        existing_ingredient = MagicMock()
        existing_ingredient.id = 2
        mock_ingredient_class.query.filter_by.return_value.first.return_value = existing_ingredient
        mocker.patch("backend.chat.RecipeIngredient")

        from backend.chat import _handle_recipe_response
        with app.app_context():
            result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)

        assert status_code == 200

    def test_handle_recipe_response_ingredient_with_missing_quantity(self, app, mocker, mock_jwt_required,
                                                                     mock_get_jwt_identity,
                                                                     mock_chat_group_model_class, mock_session):
        """Test that ingredients with missing quantity are handled with empty string"""
        chat_group = MagicMock()
        new_chat_history = MagicMock()
        chat_group.name = "Test Group"
        mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group

        response_data = {
            "recipe": {
                "title": "Flexible Recipe",
                "description": "Flexible",
                "direction": ["Step 1"],
                "tips": [],
                "ingredients": [
                    {"name": "garlic"},  # No quantity key
                    {"name": "onion", "quantity": None}  # Null quantity
                ]
            }
        }

        mocker.patch("requests.post", return_value=MagicMock(status_code=200))
        mocker.patch("backend.chat.open")
        mocker.patch("os.path.exists", return_value=True)

        mock_ingredient_class = mocker.patch("backend.models.ingredient_model.Ingredient")
        ingredient1 = MagicMock()
        ingredient1.id = 1
        ingredient2 = MagicMock()
        ingredient2.id = 2

        # Create a list of ingredients to return
        ingredients_to_return = [ingredient1, ingredient2]
        mock_ingredient_class.query.filter_by.return_value.first.side_effect = ingredients_to_return

        mock_recipe_ingredient = mocker.patch("backend.chat.RecipeIngredient")

        from backend.chat import _handle_recipe_response
        with app.app_context():
            result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)

        assert status_code == 200
        # Verify RecipeIngredient was instantiated for both ingredients
        assert mock_recipe_ingredient.call_count >= 2

    def test_chat_mock_recipe_no_ingredients_no_network(self, app, mocker, mock_jwt_required, mock_get_jwt_identity,
                                                        mock_chat_group_model_class, mock_chat_group_data):
        """Test chat endpoint with mock model returning recipe with no ingredients"""
        app.config["MOCK_AI_MODELS"] = True
        app.config["MOCK_IMAGE_URL"] = "static/images/test.png"
        mock_chat_group_model_class.query.filter_by.return_value.first.return_value = mock_chat_group_data[0]

        client = app.test_client()

        # Mock the requests.post to ensure it's not called
        mock_post = mocker.patch("requests.post")

        response = client.post("/api/chat/", json={"chat_group_id": 1, "prompt": "recipe for water"})

        assert response.status_code == 200
        assert response.json["prompt_type"] == "recipe"
        assert response.json["recipe"]["title"] == "Mock Recipe"
        assert "ingredients" in response.json["recipe"]
        # Network calls should not be made
        mock_post.assert_not_called()

    def test_handle_recipe_response_all_invalid_ingredients(self, app, mocker, mock_jwt_required,
                                                            mock_get_jwt_identity, mock_chat_group_model_class,
                                                            mock_session):
        """Test recipe response where all ingredients are invalid (missing names)"""
        chat_group = MagicMock()
        new_chat_history = MagicMock()
        chat_group.name = "Test Group"
        mock_chat_group_model_class.query.filter_by.return_value.first.return_value = chat_group

        response_data = {
            "recipe": {
                "title": "No Valid Ingredients",
                "description": "No ingredients",
                "direction": ["Step 1"],
                "tips": [],
                "ingredients": [
                    {"quantity": "1 cup"},  # No name
                    {"name": "", "quantity": "2 cups"},  # Empty name
                    {"quantity": "1 tbsp"}  # No name
                ]
            }
        }

        mocker.patch("requests.post", return_value=MagicMock(status_code=200))
        mocker.patch("backend.chat.open")
        mocker.patch("os.path.exists", return_value=True)

        mock_ingredient_class = mocker.patch("backend.models.ingredient_model.Ingredient")
        mocker.patch("backend.chat.RecipeIngredient")

        from backend.chat import _handle_recipe_response
        with app.app_context():
            result, status_code = _handle_recipe_response(chat_group, new_chat_history, response_data)

        # Should still succeed despite no valid ingredients
        assert status_code == 200
        assert result["recipe"]["title"] == "No Valid Ingredients"
