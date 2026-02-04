import flask
from flask import Blueprint, request
from werkzeug.security import  check_password_hash
from flask_login import login_user

import logging
from backend.user_model import User

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/user')
def user():
    return flask.jsonify({"message": "User endpoint"})

@user_blueprint.route('/user/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        if not user:
            logging.log(logging.WARNING, f"Login attempt with non-existent email: {email}")
        else:
            logging.log(logging.WARNING, f"Invalid password attempt for email: {email}")
        return flask.jsonify({"message": "Invalid credentials"}), 401
    login_user(user)
    logging.log(logging.INFO, f"Login successful for email: {email}")
    return flask.jsonify({"message": f"Welcome back, {user.username}!"})
