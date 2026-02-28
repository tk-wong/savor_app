from flask import Blueprint

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
from backend.chat import chat_blueprint
from backend.recipe import recipe_blueprint
from backend.user import user_blueprint

api_blueprint.register_blueprint(chat_blueprint)
api_blueprint.register_blueprint(recipe_blueprint)
api_blueprint.register_blueprint(user_blueprint)
