import os
import uuid
from typing import Any

import flask_jwt_extended
import requests
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required

from backend.models.chat_group_model import ChatGroupModel
from backend.models.chat_history_model import ChatHistoryModel
from backend.models.recipe_ingredient_model import RecipeIngredient
from backend.models.recipe_model import Recipe

chat_blueprint = Blueprint('chat', __name__, url_prefix='/chat')


@chat_blueprint.route('/', methods=['POST'])
@jwt_required()
def chat():
    prompt = request.json.get('prompt')
    chat_group_id = request.json.get('chat_group_id')
    user_id = int(flask_jwt_extended.get_jwt_identity())
    if not prompt:
        return {"message": "Prompt is required"}, 400
    if not chat_group_id:
        return {"message": "Chat group id is required"}, 400
    chat_group = ChatGroupModel.query.filter_by(id=chat_group_id).first()
    if not chat_group:
        return {"message": "Chat group not found"}, 404
    try:
        model_response = requests.post(current_app.config['AI_COOKING_AGENT_URL'],
                                       json={"prompt": prompt, "user_id": user_id, "group_id": chat_group_id},
                                       timeout=60)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        return {"message": "AI cooking agent response timed out"}, 504
    if model_response.status_code != 200:
        return {"message": "Error generating response"}, 500
    try:
        response_data = model_response.json()
    except requests.exceptions.JSONDecodeError:
        return {"message": "Invalid response from model"}, 500
    prompt_type = response_data.get("prompt_type")
    if not prompt_type:
        return {"message": "Invalid response from model"}, 500
    new_chat_history = ChatHistoryModel(chat_group_id=chat_group_id, user_id=int(flask_jwt_extended.get_jwt_identity()),
                                        prompt=prompt,
                                        response=response_data)
    from backend.db_manager import db
    db.session.add(new_chat_history)
    db.session.commit()
    if prompt_type == "question":
        return _handle_question_response(chat_group, prompt, response_data)
    elif prompt_type == "recipe":
        return _handle_recipe_response(chat_group, new_chat_history, response_data)
    return {"message": "Invalid response from model"}, 500


def _handle_question_response(chat_group: Any | None, prompt, response_data) -> tuple[Any, int]:
    if chat_group.name == "Unnamed":
        from backend.db_manager import db
        chat_group.name = prompt[:252] + "..." if len(prompt) > 255 else prompt
        db.session.commit()
    return response_data, 200


def _handle_recipe_response(chat_group: Any | None, new_chat_history: ChatHistoryModel, response_data) -> tuple[
    Any, int]:
    recipe_data = response_data.get("recipe")
    if not recipe_data:
        return {"message": "Invalid response from model"}, 500
    recipe_title = recipe_data.get("title")
    try:
        image_response = requests.post(current_app.config["IMAGE_GENERATION_URL"], json={"prompt": recipe_title},
                                       timeout=60)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        return {"message": "Image generation timed out"}, 504
    if image_response.status_code != 200:
        return {"message": "Error generating image from the image generation model"}, 500
    if not os.path.exists("static/images"):
        os.makedirs("static/images")
    image_url = f"static/images/{uuid.uuid4()}.png"
    with open(image_url, "wb") as f:
        f.write(image_response.content)
    new_recipe = Recipe(title=recipe_title, description=recipe_data.get("description"),
                        direction="\n\n".join(recipe_data.get("direction", [])),
                        create_user_id=int(flask_jwt_extended.get_jwt_identity()),
                        tips="\n\n".join(recipe_data.get("tips", [])), image_url=image_url)
    for ingredient in recipe_data.get("ingredients", []):
        from backend.models.ingredient_model import Ingredient
        ingredient_id = Ingredient.query.filter_by(name=ingredient.get("name")).first()
        if not ingredient_id:
            new_ingredient =  Ingredient(name=ingredient.get("ingredient_name")).save()
            ingredient_id = new_ingredient.id
        RecipeIngredient(recipe_id=new_recipe.id,ingredient_id=ingredient_id, quentity=ingredient.get("quantity")).save()
    if chat_group.name == "Unnamed" and recipe_title:
        chat_group.name = recipe_title[:252] + "..." if len(recipe_title) > 255 else recipe_title
    response_data["recipe"]["image_url"] = image_url
    response_data["recipe"]["id"] = new_recipe.id
    new_chat_history.image_url = image_url
    new_recipe.image_url = image_url
    from backend.db_manager import db
    db.session.add(new_recipe)
    db.session.commit()
    return response_data, 200


@chat_blueprint.route('/group/new', methods=['GET'])
@jwt_required()
def create_new_group():
    user_id = int(flask_jwt_extended.get_jwt_identity())
    new_group = ChatGroupModel(create_user_id=user_id)
    from backend.db_manager import db
    db.session.add(new_group)
    db.session.commit()
    return {"message": "New chat group created", "group_id": new_group.id}, 200


@chat_blueprint.route('/group/all', methods=['GET'])
@jwt_required()
def get_all_groups():
    user_id = int(flask_jwt_extended.get_jwt_identity())
    chat_groups = ChatGroupModel.query.filter_by(create_user_id=user_id).all()
    if chat_groups is None:
        return {"chat_groups": []}, 200
    last_chat_histories = {
        group.id: ChatHistoryModel.query.filter_by(chat_group_id=group.id).order_by(
            ChatHistoryModel.timestamp.desc()).first() for group in chat_groups}
    groups_data = [{"id": group.id, "name": group.name,
                    "last_edit": last_chat_histories.get(group.id).timestamp.isoformat()} for
                   group in chat_groups if last_chat_histories.get(
            group.id) is not None]  # avoid returning groups without any chat history
    return {"chat_groups": groups_data}, 200


@chat_blueprint.route('/group/<int:group_id>/history', methods=['GET'])
@jwt_required()
def get_chat_history(group_id):
    user_id = int(flask_jwt_extended.get_jwt_identity())
    chat_group = ChatGroupModel.query.filter_by(id=group_id).first()
    if not chat_group:
        return {"message": "Chat group not found"}, 404
    if chat_group.create_user_id != user_id:
        return {"message": "Unauthorized access to chat group"}, 403
    chat_history = ChatHistoryModel.query.filter_by(chat_group_id=group_id).order_by(
        ChatHistoryModel.timestamp.desc()).all()
    history_data = [
        {"id": history.id, "prompt": history.prompt, "response": history.response, "image_url": history.image_url,
         "timestamp": history.timestamp} for
        history in chat_history]
    return {"chat_history": history_data}, 200
