from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.models.recipe_model import Recipe

recipe_blueprint = Blueprint('recipe', __name__, url_prefix='/recipes')


@recipe_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_recipes():
    # Placeholder for fetching recipes from the database
    user_id = int(get_jwt_identity())
    all_recipe = Recipe.query.filter_by(create_user_id=user_id).all()
    return {"recipes": all_recipe}, 200
