from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.models.ingredient_model import Ingredient
from backend.models.recipe_ingredient_model import RecipeIngredient
from backend.models.recipe_model import Recipe

recipe_blueprint = Blueprint('recipe', __name__, url_prefix='/recipes')


@recipe_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_recipes():
    user_id = int(get_jwt_identity())
    all_recipe = Recipe.query(Recipe.id, Recipe.title, Recipe.image_url).filter_by(create_user_id=user_id).all()
    return {"recipes": [{'id': recipe_id, 'title': title, 'image_url': image_url} for recipe_id, title, image_url in
                        all_recipe]}, 200


@recipe_blueprint.route('/<int:recipe_id>', methods=['GET'])
@jwt_required()
def get_recipe(recipe_id):
    user_id = int(get_jwt_identity())
    recipe = Recipe.query.filter_by(id=recipe_id, create_user_id=user_id).first()
    if not recipe:
        return {"message": "Recipe not found"}, 404
    ingredients = RecipeIngredient.query.join(Ingredient).filter_by(recipe_id=recipe_id).all()
    message = {"id": recipe.id, "title": recipe.title, "description": recipe.description,
               "direction": recipe.direction.split("\n\n"), "ingredients": [
            {"id": ingredient.ingredient.id, "name": ingredient.ingredient.name, "quantity": ingredient.quantity} for
            ingredient in ingredients], "image_url": recipe.image_url}
    return {"recipe": message}, 200
