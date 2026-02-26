import os

import pytest
from dotenv import load_dotenv
from sqlalchemy.orm import close_all_sessions
from sqlalchemy_utils import drop_database
from werkzeug.security import generate_password_hash

from backend import create_app
from backend.user_model import User


@pytest.fixture(scope='session', autouse=True)
def load_env():
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env_test"))


@pytest.fixture()
def app():
    app = create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))
    from backend.db_manager import db
    # sample_user = User(email="sample@test.com", username="Sample User",password_hash=generate_password_hash("testing"))
    with app.app_context():
        db.create_all()
    yield app
    # cleanup the database
    with app.app_context():
        from backend.db_manager import db
        db.drop_all()
        close_all_sessions()
        db.engine.dispose()
    drop_database(app.config['SQLALCHEMY_DATABASE_URI'])


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


def test_index(client):
    response = client.get("/user")
    assert response.status_code == 200
    assert response.get_json() == {'message': 'User endpoint'}


def test_login(client, sample_user):
    response = client.post("/user/login", data={"email": "example@abc.com", "password": "testing"})
    assert response.status_code == 200
    assert response.get_json() == {'message': 'Welcome back, Example User!'}


def test_invalid_user(client, sample_user):
    response = client.post("/user/login", data={"email": "notexist@abc.com", "password": "testing"})
    assert response.status_code == 401
    assert response.get_json() == {'message': 'Invalid credentials'}


def test_invalid_password(client, sample_user):
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


def test_SQL_injection_attempt(client, sample_user):
    response = client.post("/user/login", data={"email": "example@abc.com", "password": "' OR '1'='1"})
    assert response.status_code == 401
    assert response.get_json() == {'message': 'Invalid credentials'}
