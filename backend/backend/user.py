import logging

import flask
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
# from flask_login import login_user
from werkzeug.security import check_password_hash, generate_password_hash

from backend.models.user_model import User

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/user')
def user():
    return flask.jsonify({"message": "User endpoint"})

@user_blueprint.route('/user/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
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
    access_token = create_access_token(identity=str(user_query.id))
    logging.log(logging.INFO, f"Login successful for email: {email}")
    message = {"user": {"id": user_query.id, "username": user_query.username, "access_token": access_token}}
    return flask.jsonify(message), 200

@user_blueprint.route('/user/create',methods=['POST'])
def create_user():
    email = request.json.get('email')
    username = request.json.get('username')
    password = request.json.get('password')
    if not email or not username or not password:
        logging.log(logging.WARNING, "User creation attempt with missing fields: ")
        if not email:
            logging.log(logging.WARNING, "User creation attempt with missing email")
        if not username:
            logging.log(logging.WARNING, "User creation attempt with missing username")
        if not password:
            logging.log(logging.WARNING, "User creation attempt with missing password")
        return flask.jsonify({"message": "Email, username, and password are required"}), 400
    user_query = User.query.filter_by(email=email).first()
    if user_query:
        logging.log(logging.WARNING, f"User creation attempt with existing email: {email}")
        return flask.jsonify({"message": "User with this email already exists"}), 409
    password_hash = generate_password_hash(password)
    new_user = User(email=email, username=username, password_hash=password_hash)
    from backend.db_manager import db
    db.session.add(new_user)
    db.session.commit()
    logging.log(logging.INFO, f"User created successfully with email: {email}")
    return flask.jsonify({"message": f"User {username} created successfully!"}), 201
