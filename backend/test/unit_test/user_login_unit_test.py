
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


def test_index(client):
    response = client.get("/user")
    assert response.status_code == 200
    assert response.get_json() == {'message': 'User endpoint'}


def test_login(client, sample_user, mock_user_query):
    # mock_query = mocker.patch.object(User, "query")
    mock_user_query.filter_by.return_value.first.return_value = sample_user
    response = client.post("/user/login", data={"email": "example@abc.com", "password": "testing"})
    print("\nTest sees User:", User)
    # print(f"\n{type(mock_user_query.return_value.filter_by.return_value.first.return_value)=}")
    # print(f"\n{type(mock_user_query.return_value.filter_by.return_value.first.return_value.password_hash)=}")
    # print(f"\n{id(sample_user)=}, {id(mock_user_query.return_value.filter_by.return_value.first.return_value)=}")
    assert response.status_code == 200
    assert response.get_json() == {'message': 'Welcome back, Example User!'}


def test_invalid_user(client, sample_user, mock_user_query):
    mock_user_query.filter_by.return_value.first.return_value = None
    response = client.post("/user/login", data={"email": "notexist@abc.com", "password": "testing"})
    assert response.status_code == 401
    assert response.get_json() == {'message': 'Invalid credentials'}


def test_invalid_password(client, sample_user, mock_user_query):
    mock_user_query.filter_by.return_value.first.return_value = sample_user
    response = client.post("/user/login", data={"email": "example@abc.com", "password": "wrong_password"})
    assert response.status_code == 401
    assert response.get_json() == {'message': 'Invalid credentials'}


def test_missing_email(client):
    response = client.post("/user/login", data={"password": "testing"})
    assert response.status_code == 400
    assert response.get_json() == {'message': 'Email and password are required'}


def test_missing_password(client):
    response = client.post("/user/login", data={"email": "example@abc.com"})
    assert response.status_code == 400
    assert response.get_json() == {'message': 'Email and password are required'}

def test_empty_email_and_password(client):
    response = client.post("/user/login", data={})
    assert response.status_code == 400
    assert response.get_json() == {'message': 'Email and password are required'}

def test_incorrect_request_method(client):
    response = client.get("/user/login")
    assert response.status_code == 405  # Method Not Allowed