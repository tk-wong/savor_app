import logging
from time import perf_counter

import flask_jwt_extended
from flask import Blueprint, current_app
from flask_jwt_extended import jwt_required

from backend.models.ingredient_model import Ingredient
from backend.models.recipe_ingredient_model import RecipeIngredient
from backend.models.recipe_model import Recipe

recipe_blueprint = Blueprint('recipe', __name__, url_prefix='/recipes')

_LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def _log(level: str, message: str, **fields):
    level_no = _LOG_LEVELS.get(level.lower(), logging.INFO)
    if not fields:
        current_app.logger.log(level_no, "%s", message)
        return
    context = " ".join(f"{key}={value}" for key, value in fields.items())
    current_app.logger.log(level_no, "%s %s", message, context)


@recipe_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_all_recipe():
    started_at = perf_counter()
    user_id = int(flask_jwt_extended.get_jwt_identity())
    _log("info", "Receive request for /recipes", user_id=user_id)
    from backend.db_manager import db
    all_recipe = db.session.query(Recipe.id, Recipe.title, Recipe.image_url).filter_by(create_user_id=user_id).all()
    recipes = [{'id': recipe_id, 'title': title, 'image_url': image_url} for recipe_id, title, image_url in
               all_recipe]
    _log("info", "Completed listing recipes", user_id=user_id, recipe_count=len(recipes), status_code=200,
         duration_ms=int((perf_counter() - started_at) * 1000))
    return {"recipes": recipes}, 200


@recipe_blueprint.route('/<int:recipe_id>', methods=['GET'])
@jwt_required()
def get_recipe_by_id(recipe_id):
    started_at = perf_counter()
    user_id = int(flask_jwt_extended.get_jwt_identity())
    _log("info", "Receive request for /recipes/<recipe_id>", user_id=user_id, recipe_id=recipe_id)
    recipe = Recipe.query.filter_by(id=recipe_id, create_user_id=user_id).first()
    if not recipe:
        _log("warning", "Recipe not found", user_id=user_id, recipe_id=recipe_id, status_code=404,
             duration_ms=int((perf_counter() - started_at) * 1000))
        return {"message": "Recipe not found"}, 404
    from backend.db_manager import db

    ingredients = db.session.query(RecipeIngredient, Ingredient).join(
        Ingredient, RecipeIngredient.ingredient_id == Ingredient.id
    ).filter(RecipeIngredient.recipe_id == recipe_id).all()
    message = {"id": recipe.id, "title": recipe.title, "description": recipe.description,
               "direction": recipe.direction.split("\n\n"), "ingredients": [
            {"id": ingredient.id, "name": ingredient.name, "quantity": recipe_ingredient.quantity} for
            recipe_ingredient, ingredient in ingredients], "image_url": recipe.image_url,
               "tips": recipe.tips.split("\n\n") if recipe.tips else []}
    _log("info", "Completed reading recipe", user_id=user_id, recipe_id=recipe_id,
         ingredient_count=len(ingredients), status_code=200,
         duration_ms=int((perf_counter() - started_at) * 1000))
    return {"recipe": message}, 200
