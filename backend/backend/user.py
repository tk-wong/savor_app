import flask
from flask import Blueprint, request
from werkzeug.security import check_password_hash, generate_password_hash
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
    if not email or not password:
        logging.log(logging.WARNING, "Login attempt with missing email or password")
        return flask.jsonify({"message": "Email and password are required"}), 400
    user_query = User.query.filter_by(email=email).first()
    if not user_query or not check_password_hash(user_query.password_hash, password):
        if not user_query:
            logging.log(logging.WARNING, f"Login attempt with non-existent email: {email}")
        else:
            logging.log(logging.WARNING, f"Invalid password attempt for email: {email}")
        return flask.jsonify({"message": "Invalid credentials"}), 401
    login_user(user_query)
    logging.log(logging.INFO, f"Login successful for email: {email}")
    return flask.jsonify({"message": f"Welcome back, {user_query.username}!"})

@user_blueprint.route('/user/create',methods=['POST'])
def create_user():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    if not email or not username or not password:
        logging.log(logging.WARNING, "User creation attempt with missing fields")
        return flask.jsonify({"message": "Email, username, and password are required"}), 400
    user_query = User.query.filter_by(email=email).first()
    if user_query:
        logging.log(logging.WARNING, f"User creation attempt with existing email: {email}")
        return flask.jsonify({"message": "User with this email already exists"}), 409
    password_hash = generate_password_hash(password)
    new_user = User(email=email, username=username, password_hash=password_hash)
    from backend.database import db
    db.session.add(new_user)
    db.session.commit()
    logging.log(logging.INFO, f"User created successfully with email: {email}")
    return flask.jsonify({"message": f"User {username} created successfully!"}), 201
