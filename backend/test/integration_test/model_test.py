def test_chat_group_model_repr(app, sample_chat_group):
    """Test ChatGroupModel __repr__ using persisted integration data."""
    from backend.models.chat_group_model import ChatGroupModel

    with app.app_context():
        chat_group = ChatGroupModel.query.filter_by(id=1).first()
        assert repr(chat_group) == "<ChatGroup Test Group 0, id: 1>"


def test_chat_history_model_repr(app, sample_chat):
    """Test ChatHistoryModel __repr__ using persisted integration data."""
    from backend.models.chat_history_model import ChatHistoryModel

    with app.app_context():
        chat_history = ChatHistoryModel.query.filter_by(id=1).first()
        expected_repr = (
            "<ChatHistory id: 1, user_id: 1, prompt: Test prompt 0, "
            "response: {'response': 'Test response 0'}, timestamp: 2024-01-01 00:00:00>"
        )
        assert repr(chat_history) == expected_repr


def test_ingredient_model_repr(app, sample_recipe_ingredients):
    """Test Ingredient __repr__ using persisted integration data."""
    from backend.models.ingredient_model import Ingredient

    with app.app_context():
        ingredient = Ingredient.query.filter_by(name="Ingredient 1").first()
        assert repr(ingredient) == f"<Ingredient id: {ingredient.id},name: Ingredient 1>"


def test_recipe_ingredient_model_repr(app, sample_recipe_ingredients):
    """Test RecipeIngredient __repr__ using persisted integration data."""
    from backend.models.recipe_ingredient_model import RecipeIngredient

    with app.app_context():
        recipe_ingredient = RecipeIngredient.query.filter_by(quantity="100g").first()
        expected_repr = (
            f"<RecipeIngredient id: {recipe_ingredient.id}, recipe_id: {recipe_ingredient.recipe_id}, "
            f"ingredient_id: {recipe_ingredient.ingredient_id}, quantity: 100g>"
        )
        assert repr(recipe_ingredient) == expected_repr


def test_recipe_model_repr(app, sample_recipe):
    """Test Recipe __repr__ using persisted integration data."""
    from backend.models.recipe_model import Recipe

    with app.app_context():
        recipe = Recipe.query.filter_by(title="Recipe 1").first()
        assert repr(recipe) == f"<Recipe id: {recipe.id}, title: Recipe 1>"


def test_user_model_repr(app, sample_user):
    """Test User __repr__ using persisted integration data."""
    from backend.models.user_model import User

    with app.app_context():
        user = User.query.filter_by(email="example@abc.com").first()
        assert repr(user) == f"<User id: {user.id}, username: Example User, email: example@abc.com>"
