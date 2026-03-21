def test_chat_group_model_repr():
    """Test that chat_group_model is repr"""
    from backend.chat import ChatGroupModel
    chat_group = ChatGroupModel(id=1, create_user_id=1, name='group1')
    expected_repr = "<ChatGroup group1, id: 1>"
    assert repr(chat_group) == expected_repr


def test_chat_history_model_repr():
    """Test that chat_history_model is repr"""
    from backend.chat import ChatHistoryModel
    chat_history = ChatHistoryModel(id=1, user_id=1, timestamp="2024-01-01T00:00:00",
                                    prompt="Test prompt 1", response={"response": "Test response 1"},
                                    image_url="test_url1")
    expected_repr = "<ChatHistory id: 1, user_id: 1, prompt: Test prompt 1, response: {'response': 'Test response 1'}, timestamp: 2024-01-01T00:00:00>"
    assert repr(chat_history) == expected_repr


def test_ingredient_model_repr():
    """Test that ingredient_model is repr"""
    from backend.models.ingredient_model import Ingredient
    ingredient = Ingredient(id=1, name='ingredient1')
    expected_repr = "<Ingredient id: 1,name: ingredient1>"
    assert repr(ingredient) == expected_repr


def test_recipe_ingredient_model_repr():
    """Test that recipe_ingredient_model is repr"""
    from backend.models.recipe_ingredient_model import RecipeIngredient
    ingredient_recipe = RecipeIngredient(id=1, recipe_id=2, ingredient_id=3, quantity="100g")
    expected_repr = "<RecipeIngredient id: 1, recipe_id: 2, ingredient_id: 3, quantity: 100g>"
    assert repr(ingredient_recipe) == expected_repr


def test_recipe_model_repr():
    """Test that recipe_model is repr"""
    from backend.models.recipe_model import Recipe
    recipe = Recipe(id=1, title='recipe1')
    expected_repr = "<Recipe id: 1, title: recipe1>"
    assert repr(recipe) == expected_repr


def test_user_model_repr():
    """Test that user_model is repr"""
    from backend.models.user_model import User
    user = User(id=1, username='user1', email="test_email1")
    expected_repr = "<User id: 1, username: user1, email: test_email1>"
    assert repr(user) == expected_repr
