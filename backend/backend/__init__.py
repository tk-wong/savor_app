import os

from flask import Flask
from sqlalchemy_utils import database_exists, create_database


def create_app(config="config.py"):
    app = Flask(__name__)
    app.config.from_pyfile(config)
    # print(app.config['SQLALCHEMY_DATABASE_URI'])
    from .database import db
    db.init_app(app)
    if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        create_database(app.config['SQLALCHEMY_DATABASE_URI'])
    from .user import user_blueprint
    app.register_blueprint(user_blueprint)
    from .chat import chat_blueprint
    app.register_blueprint(chat_blueprint)
    # from .login_manager import login_manager
    # login_manager.init_app(app)
    from .jwt_manager import jwt
    jwt.init_app(app)
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
    with app.app_context():
        db.create_all()
    return app

