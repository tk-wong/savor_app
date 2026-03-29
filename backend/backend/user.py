import logging
from time import perf_counter

import flask
from flask import Blueprint, request, current_app
from flask_jwt_extended import create_access_token
# from flask_login import login_user
from werkzeug.security import check_password_hash, generate_password_hash

from backend.models.user_model import User

user_blueprint = Blueprint('user', __name__)

_LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def _log(level: str, message: str, **fields):
    level_no = _LOG_LEVELS.get(level.lower(), logging.INFO)
    if not fields:
        current_app.logger.log(level_no, "%s", message)
        return
    context = " ".join(f"{key}={value}" for key, value in fields.items())
    current_app.logger.log(level_no, "%s %s", message, context)


@user_blueprint.route('/user/login', methods=['POST'])
def login():
    started_at = perf_counter()
    email = request.json.get('email')
    password = request.json.get('password')
    _log("info", "Receive request for /user/login", email=email if email else "missing")
    if not email or not password:
        _log("warning", "Fail to validate login parameters", has_email=bool(email), has_password=bool(password),
             status_code=400, duration_ms=int((perf_counter() - started_at) * 1000))
        return flask.jsonify({"message": "Email and password are required"}), 400
    user_query = User.query.filter_by(email=email).first()
    if not user_query or not check_password_hash(user_query.password_hash, password):
        if not user_query:
            _log("warning", "Login failed with non-existent email", email=email)
        else:
            _log("warning", "Login failed with invalid password", email=email)
        _log("warning", "Completed login request", email=email, status_code=401,
             duration_ms=int((perf_counter() - started_at) * 1000))
        return flask.jsonify({"message": "Invalid credentials"}), 401
    access_token = create_access_token(identity=str(user_query.id))
    _log("info", "Login successful", user_id=user_query.id, email=email)
    message = {"user": {"id": user_query.id, "username": user_query.username, "access_token": access_token}}
    _log("info", "Completed login request", user_id=user_query.id, status_code=200,
         duration_ms=int((perf_counter() - started_at) * 1000))
    return flask.jsonify(message), 200

@user_blueprint.route('/user/create',methods=['POST'])
def create_user():
    started_at = perf_counter()
    email = request.json.get('email')
    username = request.json.get('username')
    password = request.json.get('password')
    _log("info", "Receive request for /user/create", email=email if email else "missing", username=username)
    if not email or not username or not password:
        _log("warning", "Fail to validate user creation parameters", has_email=bool(email),
             has_username=bool(username), has_password=bool(password), status_code=400,
             duration_ms=int((perf_counter() - started_at) * 1000))
        return flask.jsonify({"message": "Email, username, and password are required"}), 400
    user_query = User.query.filter_by(email=email).first()
    if user_query:
        _log("warning", "User creation failed because email already exists", email=email, status_code=409,
             duration_ms=int((perf_counter() - started_at) * 1000))
        return flask.jsonify({"message": "User with this email already exists"}), 409
    password_hash = generate_password_hash(password)
    new_user = User(email=email, username=username, password_hash=password_hash)
    from backend.db_manager import db
    db.session.add(new_user)
    db.session.commit()
    _log("info", "User created successfully", user_id=new_user.id, email=email, status_code=201,
         duration_ms=int((perf_counter() - started_at) * 1000))
    return flask.jsonify({"message": f"User {username} created successfully!"}), 201
