import datetime
import os

import pytest
from dotenv import load_dotenv
from sqlalchemy.orm import close_all_sessions
from sqlalchemy_utils import database_exists, create_database
from werkzeug.security import generate_password_hash

from backend import create_app
from backend.models.chat_history_model import ChatHistoryModel
from backend.models.ingredient_model import Ingredient
from backend.models.recipe_ingredient_model import RecipeIngredient
from backend.models.recipe_model import Recipe
from backend.models.user_model import User


@pytest.fixture(scope='session', autouse=True)
def load_env():
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env_test"), override=True)
    # Keep integration runs stable even if shell/session exports other modes.
    os.environ["DROP_DB_ON_STARTUP"] = "0"


@pytest.fixture()
def app():
    app = create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))

    # Ensure database exists before tests. Tables are already created in create_app().
    with app.app_context():
        if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
            create_database(app.config['SQLALCHEMY_DATABASE_URI'])

    yield app

    # Cleanup schema data after each test while reusing the same test DB.
    with app.app_context():
        from backend.db_manager import db
        db.drop_all()
        close_all_sessions()
        db.engine.dispose()



@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def sample_user(app):
    with app.app_context():
        from backend.db_manager import db
        user = User(email="example@abc.com",
                    username="Example User",
                    password_hash=generate_password_hash("testing"))
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture()
def sample_login(app, client, sample_user):
    """Login a sample user and return the login response with access token."""
    import json
    response = client.post("/api/user/login",
                           data=json.dumps({"email": "example@abc.com", "password": "testing"}),
                           content_type='application/json')
    assert response.status_code == 200
    return response.get_json()


@pytest.fixture()
def sample_chat_group(app, sample_user):
    with app.app_context():
        from backend.db_manager import db
        from backend.models.chat_group_model import ChatGroupModel
        chat_group_list = []
        for i in range(2):
            chat_group = ChatGroupModel(create_user_id=1, name=f"Test Group {i}")
            db.session.add(chat_group)
            chat_group_list.append(chat_group)
            db.session.commit()
        return chat_group_list


@pytest.fixture()
def sample_chat(app, sample_user, sample_chat_group):
    with app.app_context():
        from backend.db_manager import db
        chat_history_list = []
        for i in range(2):
            chat_history = ChatHistoryModel(chat_group_id=i + 1, user_id=1, prompt=f"Test prompt {i}",
                                            response={"response": f"Test response {i}"},
                                            timestamp=datetime.datetime.fromisoformat(
                                                "2024-01-0{}T00:00:00".format(i + 1)),
                                            image_url=f"test_url{i}")
            db.session.add(chat_history)
            chat_history_list.append(chat_history)
            db.session.commit()
        return chat_history_list


@pytest.fixture()
def sample_recipe(app, sample_user):
    """Create sample recipes for the main sample user."""
    with app.app_context():
        from backend.db_manager import db

        recipe_1 = Recipe(
            title="Recipe 1",
            description="Test description 1",
            direction="Step 1\n\nStep 2",
            tips="Tip 1\n\nTip 2",
            create_user_id=1,
            image_url="https://example.com/recipe1.jpg",
        )
        recipe_2 = Recipe(
            title="Recipe 2",
            description="Test description 2",
            direction="Step A\n\nStep B",
            tips="Tip A\n\nTip B",
            create_user_id=1,
            image_url="https://example.com/recipe2.jpg",
        )

        db.session.add(recipe_1)
        db.session.add(recipe_2)
        db.session.commit()

        return [recipe_1, recipe_2]


@pytest.fixture()
def sample_recipe_other_user(app):
    """Create one recipe for another user to validate ownership filtering."""
    with app.app_context():
        from backend.db_manager import db

        other_user = User(
            email="other_recipe_user@abc.com",
            username="Other Recipe User",
            password_hash=generate_password_hash("testing"),
        )
        db.session.add(other_user)
        db.session.commit()

        other_recipe = Recipe(
            title="Other User Recipe",
            description="Should not be visible for sample user",
            direction="Other step 1\n\nOther step 2",
            tips="Other tip",
            create_user_id=other_user.id,
            image_url="https://example.com/other-recipe.jpg",
        )
        db.session.add(other_recipe)
        db.session.commit()

        return other_recipe


@pytest.fixture()
def sample_recipe_ingredients(app, sample_recipe):
    """Create ingredient and recipe_ingredient rows for sample_recipe[0]."""
    with app.app_context():
        from backend.db_manager import db

        ingredient_1 = Ingredient(name="Ingredient 1")
        ingredient_2 = Ingredient(name="Ingredient 2")
        db.session.add(ingredient_1)
        db.session.add(ingredient_2)
        db.session.commit()

        recipe_1_id = Recipe.query.filter_by(title="Recipe 1").first().id

        recipe_ingredient_1 = RecipeIngredient(
            recipe_id=recipe_1_id,
            ingredient_id=ingredient_1.id,
            quantity="100g",
        )
        recipe_ingredient_2 = RecipeIngredient(
            recipe_id=recipe_1_id,
            ingredient_id=ingredient_2.id,
            quantity="200g",
        )

        db.session.add(recipe_ingredient_1)
        db.session.add(recipe_ingredient_2)
        db.session.commit()

        return [recipe_ingredient_1, recipe_ingredient_2]