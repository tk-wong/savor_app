import flask
from flask import Blueprint, request
from werkzeug.security import  check_password_hash
from flask_login import login_user

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
        return flask.jsonify({"message": "Invalid credentials"}), 401
    login_user(user)
    return flask.jsonify({"message": f"Welcome back, {user.username}!"})
