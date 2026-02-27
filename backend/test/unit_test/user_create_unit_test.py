import pytest
from werkzeug.security import generate_password_hash, check_password_hash

from backend import create_app
from backend.user_model import User
import os


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
def app(mocker, mock_session):
    mocker.patch("sqlalchemy.create_engine")
    mocker.patch('backend.database.db.init_app')
    sqlalchemy_utils = mocker.MagicMock()
    sqlalchemy_utils.database_exists.return_value = True
    app = create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))
    from backend.database import db
    mocker.patch.object(db, "session", new=mock_session)
    yield app
    # cleanup the database


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

def test_create_user(client, mock_user_query):
    mock_user_query.filter_by.return_value.first.return_value = None
    email = "example@abc.com"
    username = "Example User"
    password = "testing"
    response = client.post("/user/create", data={
        "email": email,
        "username": username,
        "password": password
    })
    assert response.status_code == 201
    assert response.get_json() == {"message": f"User {username} created successfully!"}

def test_create_user_existing_email(client, mock_user_query,sample_user):
    mock_user_query.filter_by.return_value.first.return_value = sample_user
    email = "example@abc.com"
    username = "Example User"
    password = "testing"
    response = client.post("/user/create", data={
        "email": email,
        "username": username,
        "password": password
    })
    assert response.status_code == 409
    assert response.get_json() == {"message": "User with this email already exists"}

def test_create_user_missing_email(client):
    username = "Example User"
    password = "testing"
    response = client.post("/user/create", data={
        "username": username,
        "password": password
    })
    assert response.status_code == 400
    assert response.get_json() == {"message": "Email, username, and password are required"}

def test_create_user_missing_username(client):
    email = "example@abc.com"
    password = "testing"
    response = client.post("/user/create", data={
        "email": email,
        "password": password
    })
    assert response.status_code == 400
    assert response.get_json() == {"message": "Email, username, and password are required"}

def test_create_user_missing_password(client):
    email = "example@abc.com"
    username = "Example User"
    response = client.post("/user/create", data={
        "email": email,
        "username": username,
    })
    assert response.status_code == 400
    assert response.get_json() == {"message": "Email, username, and password are required"}