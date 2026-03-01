from flask import Flask
from sqlalchemy_utils import database_exists, create_database


def create_app(config="config.py"):
    app = Flask(__name__, static_folder='static', static_url_path='/api/static')
    app.config.from_pyfile(config)
    # print(app.config['SQLALCHEMY_DATABASE_URI'])
    from .db_manager import db
    db.init_app(app)
    if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        create_database(app.config['SQLALCHEMY_DATABASE_URI'])
    create_table(app)
    from backend.db_manager import migrate
    migrate.init_app(app, db)
    from backend.api import api_blueprint
    app.register_blueprint(api_blueprint)
    from backend.jwt_manager import jwt
    jwt.init_app(app)
    app.config['JWT_SECRET_KEY'] = app.config["JWT_SECRET_KEY"]
    return app


def create_table(app: Flask):
    from backend.db_manager import db
    with app.app_context():
        from backend.models.recipe_model import Recipe
        from backend.models.user_model import User
        from backend.models.chat_history_model import ChatHistoryModel
        from backend.models.chat_group_model import ChatGroupModel
        from backend.models.recipe_ingredient_model import RecipeIngredient
        from backend.models.ingredient_model import Ingredient
        db.create_all()
