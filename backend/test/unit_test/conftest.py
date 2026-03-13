import os

import pytest
from werkzeug.security import generate_password_hash

from backend import create_app
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
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def sample_user(app, mock_session):
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
    return mocker.patch("backend.recipe.get_jwt_identity", return_value="1")


@pytest.fixture()
def mock_recipe_list( mock_session):
    recipe1 = (1, "Recipe 1", "https://example.com/recipe1.jpg")
    recipe2 = (2, "Recipe 2", "https://example.com/recipe2.jpg")
    return [recipe1, recipe2]
