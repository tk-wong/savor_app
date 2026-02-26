import os

from flask import Flask
from sqlalchemy_utils import database_exists, create_database


def create_app(config="config.py"):
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_pyfile(config)
    # print(app.config['SQLALCHEMY_DATABASE_URI'])
    from .db_manager import db
    db.init_app(app)
    if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        create_database(app.config['SQLALCHEMY_DATABASE_URI'])
    with app.app_context():
        from backend.models.recipe_model import Recipe
        from backend.models.user_model import User
        from backend.models.chat_history_model import ChatHistoryModel
        from backend.models.recipe_ingredient_model import RecipeIngredient
        from backend.models.ingredient_model import Ingredient
        db.create_all()
    from backend.db_manager import migrate
    migrate.init_app(app, db)
    from backend.user import user_blueprint
    app.register_blueprint(user_blueprint)
    from backend.chat import chat_blueprint
    app.register_blueprint(chat_blueprint)
    from backend.recipe import recipe_blueprint
    app.register_blueprint(recipe_blueprint)
    # from .login_manager import login_manager
    # login_manager.init_app(app)
    from backend.jwt_manager import jwt
    jwt.init_app(app)
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
    return app

