import os
import json

import pytest
from dotenv import load_dotenv
from sqlalchemy.orm import close_all_sessions
from sqlalchemy_utils import drop_database
from werkzeug.security import generate_password_hash

from backend import create_app
from backend.models.user_model import User


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


def test_create_user(client):
    email = "example@abc.com"
    username = "Example User"
    password = "testing"
    response = client.post("/api/user/create", data=json.dumps({
        "email": email,
        "username": username,
        "password": password
    }), content_type='application/json')
    assert response.status_code == 201
    assert response.get_json() == {"message": f"User {username} created successfully!"}

def test_create_user_existing_email(client, sample_user):
    email = "example@abc.com"
    username = "Example User"
    password = "testing"
    response = client.post("/api/user/create", data=json.dumps({
        "email": email,
        "username": username,
        "password": password
    }), content_type='application/json')
    assert response.status_code == 409
    assert response.get_json() == {"message": "User with this email already exists"}

def test_create_user_missing_email(client):
    username = "Example User"
    password = "testing"
    response = client.post("/api/user/create", data=json.dumps({
        "username": username,
        "password": password
    }), content_type='application/json')
    assert response.status_code == 400
    assert response.get_json() == {"message": "Email, username, and password are required"}

def test_create_user_missing_username(client):
    email = "example@abc.com"
    password = "testing"
    response = client.post("/api/user/create", data=json.dumps({
        "email": email,
        "password": password
    }), content_type='application/json')
    assert response.status_code == 400
    assert response.get_json() == {"message": "Email, username, and password are required"}

def test_create_user_missing_password(client):
    email = "example@abc.com"
    username = "Example User"
    response = client.post("/api/user/create", data=json.dumps({
        "email": email,
        "username": username,
    }), content_type='application/json')
    assert response.status_code == 400
    assert response.get_json() == {"message": "Email, username, and password are required"}
