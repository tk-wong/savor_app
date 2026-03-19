import datetime
import os
from types import SimpleNamespace

import pytest
from werkzeug.security import generate_password_hash

from backend import create_app
from backend.models.chat_history_model import ChatHistoryModel
from backend.models.ingredient_model import Ingredient
from backend.models.recipe_ingredient_model import RecipeIngredient
from backend.models.recipe_model import Recipe
from backend.models.user_model import User


@pytest.fixture()
def app(mocker, mock_session):
    mocker.patch("sqlalchemy.create_engine")
    mocker.patch('backend.db_manager.db.init_app')
    mocker.patch('backend.db_manager.db.create_all')
    sqlalchemy_utils = mocker.MagicMock()
    sqlalchemy_utils.database_exists.return_value = True
    app = create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))
    from backend.db_manager import db
    mocker.patch.object(db, "session", new=mock_session)
    yield app
    # cleanup the database


@pytest.fixture(scope='session', autouse=True)
def load_env():
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env_unit_test"))


@pytest.fixture()
def mock_session(mocker):
    session = mocker.MagicMock(name="mock_session")
    query = mocker.MagicMock(name="mock_query")
    session.query.return_value = query
    for method in ['filter_by', 'first', 'all', 'get', 'join', 'limit', 'offset', 'group_by']:
        getattr(query, method).return_value = query

    query.first.return_value = None
    query.one.return_value = None
    query.one_or_none.return_value = None
    query.all.return_value = []
    query.scalar.return_value = None
    query.count.return_value = 0

    session.add = mocker.MagicMock()
    session.add_all = mocker.MagicMock()
    session.delete = mocker.MagicMock()
    session.commit = mocker.MagicMock()
    session.rollback = mocker.Mock()
    session.flush = mocker.MagicMock()
    session.expunge = mocker.MagicMock()

    return session


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def mock_user(app, mock_session):
    password_hash = generate_password_hash("testing")
    user = User(id=1, email="example@abc.com", username="Example User", password_hash=password_hash)
    return user


@pytest.fixture()
def mock_user_query(mocker, app):
    mock_query = mocker.patch.object(User, "query")
    yield mock_query


@pytest.fixture()
def mock_jwt_required(mocker):
    return mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')


@pytest.fixture()
def mock_get_jwt_identity(mocker):
    return mocker.patch("flask_jwt_extended.get_jwt_identity", return_value="1")


@pytest.fixture()
def mock_recipe_list(mock_session):
    recipe1 = (1, "Recipe 1", "https://example.com/recipe1.jpg")
    recipe2 = (2, "Recipe 2", "https://example.com/recipe2.jpg")
    return [recipe1, recipe2]


@pytest.fixture()
def mock_recipe_query(mocker, app):
    mock_query = mocker.patch.object(Recipe, "query")
    yield mock_query


@pytest.fixture()
def mock_recipe_ingredients_query(mocker, app):
    mock_query = mocker.patch.object(RecipeIngredient, "query")
    yield mock_query


@pytest.fixture()
def mock_detail_recipe(app):
    recipe_1 = Recipe(id=1, title="Recipe 1", image_url="https://example.com/recipe1.jpg",
                      direction="Test instruction1\n\nTest instruction2", tips="Test tip1\n\nTest tip2")
    return recipe_1


@pytest.fixture()
def mock_detail_ingredients(app):
    ingredient_list = [Ingredient(id=1, name="Ingredient 1"), Ingredient(id=2, name="Ingredient 2")]
    recipe_ingredient_1 = SimpleNamespace(recipe_id=1, ingredient_id=1, quantity="100g", ingredient=ingredient_list[0])
    recipe_ingredient_2 = SimpleNamespace(recipe_id=1, ingredient_id=2, quantity="200g", ingredient=ingredient_list[1])
    return [recipe_ingredient_1, recipe_ingredient_2]


@pytest.fixture()
def mock_chat_group_model_class(mocker, mock_session):
    mock_chat_group_model = mocker.patch('backend.chat.ChatGroupModel')
    return mock_chat_group_model


@pytest.fixture()
def mock_chat_group_data(mocker, mock_session):
    group_1 = SimpleNamespace(id=1, create_user_id=1, name='group1')
    group_2 = SimpleNamespace(id=2, create_user_id=1, name='group2')
    return [group_1, group_2]


@pytest.fixture()
def mock_chat_history_data(mocker, mock_session):
    chat_history_1 = SimpleNamespace(id=1, chat_group_id=1, user_id=1, prompt="Test prompt 1",
                                     response={"response": "Test response 1"},
                                     timestamp=datetime.datetime.fromisoformat("2024-01-01T00:00:00"),
                                     image_url="test_url1")
    chat_history_2 = SimpleNamespace(id=2, chat_group_id=2, user_id=1, prompt="Test prompt 2",
                                     response={"response": "Test response 2"},
                                     timestamp=datetime.datetime.fromisoformat("2024-01-02T00:00:00"),
                                     image_url="test_url2")
    chat_history_3 = SimpleNamespace(id=3, chat_group_id=1, user_id=1, prompt="Test prompt 3",
                                     response={"response": "Test response 3"},
                                     timestamp=datetime.datetime.fromisoformat("2024-01-03T00:00:00"),
                                     image_url="test_url3")
    return [chat_history_1, chat_history_2, chat_history_3]


@pytest.fixture()
def mock_chat_history_query(mocker, mock_session):
    chat_history_query = mocker.patch.object(ChatHistoryModel, "query")
    return chat_history_query
