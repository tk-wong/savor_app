import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
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

_LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def _log(level: str, event: str, **fields: Any) -> None:
    """Emit structured logs with safe key/value context."""
    logger = current_app.logger
    level_no = _LOG_LEVELS.get(level.lower(), logging.INFO)
    if not fields:
        logger.log(level_no, "%s", event)
        return
    context = " ".join(f"{key}={value}" for key, value in fields.items())
    logger.log(level_no, "%s %s", event, context)


def _build_mock_ai_response(prompt: str) -> dict[str, Any]:
    prompt_lower = prompt.lower()
    recipe_hints = ["recipe", "cook", "bake", "dish", "meal"]
    if any(hint in prompt_lower for hint in recipe_hints):
        return {
            "prompt_type": "recipe",
            "recipe": {
                "title": "Mock Recipe",
                "description": f"Mock response for: {prompt}",
                "direction": ["Prepare ingredients", "Cook for 20 minutes", "Serve warm"],
                "tips": ["Adjust seasoning to taste"],
                "ingredients": [
                    {"name": "salt", "ingredient_name": "salt", "quantity": "1 tsp"},
                    {"name": "olive oil", "ingredient_name": "olive oil", "quantity": "1 tbsp"},
                ],
            },
        }
    return {
        "prompt_type": "question",
        "response": f"[MOCK] {prompt}",
    }


@chat_blueprint.route('/', methods=['POST'])
@jwt_required()
def chat():
    started_at = perf_counter()
    prompt = request.json.get('prompt')
    chat_group_id = request.json.get('chat_group_id')
    user_id = int(flask_jwt_extended.get_jwt_identity())
    _log("info", "Receive request for /chat", user_id=user_id, chat_group_id=chat_group_id,
         prompt_len=len(prompt) if isinstance(prompt, str) else 0)
    if not prompt:
        _log("warning", "Fail the validate the parameter", reason="missing_prompt", user_id=user_id,
             chat_group_id=chat_group_id)
        return {"message": "Prompt is required"}, 400
    if not chat_group_id:
        _log("warning", "Fail the validate the parameter", reason="missing_chat_group_id", user_id=user_id)
        return {"message": "Chat group id is required"}, 400
    chat_group = ChatGroupModel.query.filter_by(id=chat_group_id).first()
    if not chat_group:
        _log("warning", "Chat group not found", user_id=user_id, chat_group_id=chat_group_id)
        return {"message": "Chat group not found"}, 404
    _log("info", "Loaded chat group", user_id=user_id, chat_group_id=chat_group_id, group_name=chat_group.name)
    if current_app.config.get("MOCK_AI_MODELS", False):
        _log("info", "Start creating mock response", user_id=user_id, chat_group_id=chat_group_id)
        response_data = _build_mock_ai_response(prompt)
        _log("info", "Completed creating mock response", user_id=user_id, chat_group_id=chat_group_id)
    else:
        _log("info", "Start sending request to AI cooking agent", user_id=user_id, chat_group_id=chat_group_id,
             prompt=prompt)
        try:
            model_response = requests.post(current_app.config['AI_COOKING_AGENT_URL'],
                                           json={"prompt": prompt, "user_id": user_id, "group_id": chat_group_id},
                                           timeout=60)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            _log("error", "Fail to send request to AI cooking agent", user_id=user_id, chat_group_id=chat_group_id,
                 reason="timeout_or_connection_error")
            return {"message": "AI cooking agent response timed out"}, 504
        _log("info", "chat request completed", user_id=user_id, chat_group_id=chat_group_id,
             status_code=model_response.status_code)
        if model_response.status_code != 200:
            _log("error", "AI cooking agent invalid status", user_id=user_id, chat_group_id=chat_group_id,
                 status_code=model_response.status_code)
            return {"message": "Error generating response"}, 500
        try:
            response_data = model_response.json()
        except requests.exceptions.JSONDecodeError:
            _log("error", "AI cooking agent invalid JSON", user_id=user_id, chat_group_id=chat_group_id)
            return {"message": "Invalid response from model"}, 500
        _log("info", "Parsed the response from AI cooking agent", user_id=user_id, chat_group_id=chat_group_id)
    prompt_type = response_data.get("prompt_type")
    if not prompt_type:
        _log("error", "AI cooking agent missing prompt_type", user_id=user_id, chat_group_id=chat_group_id,
             json=response_data)
        return {"message": "Invalid response from model"}, 500
    _log("info", "Writing chat history to database", user_id=user_id, chat_group_id=chat_group_id,
         prompt_type=prompt_type)
    new_chat_history = ChatHistoryModel(chat_group_id=chat_group_id, user_id=int(flask_jwt_extended.get_jwt_identity()),
                                        prompt=prompt,
                                        response=response_data,
                                        timestamp=datetime.now(UTC))
    from backend.db_manager import db
    db.session.add(new_chat_history)
    db.session.commit()
    _log("info", "Complete writing chat history to database", user_id=user_id, chat_group_id=chat_group_id,
         chat_history_id=new_chat_history.id)
    if prompt_type == "question":
        _log("info", "Handling question response", user_id=user_id, chat_group_id=chat_group_id)
        return _handle_question_response(chat_group, prompt, response_data)
    elif prompt_type == "recipe":
        _log("info", "Handling recipe response", user_id=user_id, chat_group_id=chat_group_id,
             chat_history_id=new_chat_history.id)
        return _handle_recipe_response(chat_group, new_chat_history, response_data)
    _log("error", "Invalid prompt type from AI cooking agent", user_id=user_id, chat_group_id=chat_group_id,
         prompt_type=prompt_type, duration_ms=int((perf_counter() - started_at) * 1000))
    return {"message": "Invalid response from model"}, 500


def _handle_question_response(chat_group: Any | None, prompt, response_data) -> tuple[Any, int]:
    user_id = int(flask_jwt_extended.get_jwt_identity())
    _log("info", "Start handling question response", user_id=user_id, chat_group_id=chat_group.id)
    if chat_group.name == "Unnamed":
        from backend.db_manager import db
        chat_group.name = prompt[:252] + "..." if len(prompt) > 255 else prompt
        db.session.commit()
        _log("info", "Renamed unnamed chat group from prompt", user_id=user_id, chat_group_id=chat_group.id,
             new_name=chat_group.name)
    _log("info", "Completed handling question response", user_id=user_id, chat_group_id=chat_group.id)
    return response_data, 200


def _handle_recipe_response(chat_group: Any | None, new_chat_history: ChatHistoryModel, response_data) -> tuple[
    Any, int]:
    user_id = int(flask_jwt_extended.get_jwt_identity())
    _log("info", "Start handling recipe response", user_id=user_id, chat_group_id=chat_group.id,
         chat_history_id=new_chat_history.id)
    recipe_data = response_data.get("recipe")
    if not recipe_data:
        _log("error", "Recipe payload is missing", user_id=user_id, chat_group_id=chat_group.id)
        return {"message": "Invalid response from model"}, 500
    recipe_title = recipe_data.get("title")
    image_dir = Path(current_app.static_folder) / "images"
    if current_app.config.get("MOCK_AI_MODELS", False):
        _log("info", "Using mock image response", user_id=user_id, chat_group_id=chat_group.id)
        image_url = current_app.config.get("MOCK_IMAGE_URL", f"{current_app.static_url_path}/images/temp.png")
    else:
        _log("info", "Start generating recipe image", user_id=user_id, chat_group_id=chat_group.id)
        try:
            image_response = requests.post(current_app.config["IMAGE_GENERATION_URL"], json={"prompt": recipe_title},
                                           timeout=60)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            _log("error", "Fail to generate recipe image", user_id=user_id, chat_group_id=chat_group.id,
                 reason="timeout_or_connection_error")
            return {"message": "Image generation timed out"}, 504
        if image_response.status_code != 200:
            _log("error", "Recipe image generation invalid status", user_id=user_id, chat_group_id=chat_group.id,
                 status_code=image_response.status_code)
            return {"message": "Error generating image from the image generation model"}, 500
        if not image_dir.exists():
            image_dir.mkdir(parents=True)
            _log("info", "Created image storage directory", path=str(image_dir))
        image_filename = f"{uuid.uuid4()}.png"
        image_file_path = image_dir / image_filename
        image_url = f"{current_app.static_url_path}/images/{image_filename}"
        with open(image_file_path, "wb") as f:
            f.write(image_response.content)
        _log("info", "Generated recipe image", user_id=user_id, chat_group_id=chat_group.id,
             image_url=image_url, file_path=str(image_file_path))
    _log("info", "Start writing recipe to database", user_id=user_id, chat_group_id=chat_group.id,
         recipe_title=recipe_title)
    new_recipe = Recipe(title=recipe_title, description=recipe_data.get("description"),
                        direction="\n\n".join(recipe_data.get("directions", [])),
                        create_user_id=int(flask_jwt_extended.get_jwt_identity()),
                        tips="\n\n".join(recipe_data.get("tips", [])), image_url=image_url)
    from backend.db_manager import db
    db.session.add(new_recipe)
    db.session.flush()
    _log("info", "Recipe write flushed", user_id=user_id, chat_group_id=chat_group.id, recipe_id=new_recipe.id)
    for ingredient in recipe_data.get("ingredients", []):
        from backend.models.ingredient_model import Ingredient
        ingredient_name = ingredient.get("name")
        if not ingredient_name:
            _log("warning", "Skipped recipe ingredient", user_id=user_id, chat_group_id=chat_group.id,
                 reason="missing_ingredient_name")
            continue
        ingredient_row = Ingredient.query.filter_by(name=ingredient_name).first()
        if not ingredient_row:
            ingredient_row = Ingredient(name=ingredient_name)
            db.session.add(ingredient_row)
            db.session.flush()
            _log("info", "Created ingredient", user_id=user_id, ingredient_id=ingredient_row.id,
                 ingredient_name=ingredient_name)
        recipe_ingredient = RecipeIngredient(recipe_id=new_recipe.id, ingredient_id=ingredient_row.id,
                                             quantity=ingredient.get("quantity") or "")
        db.session.add(recipe_ingredient)
        _log("info", "Added recipe ingredient", user_id=user_id, recipe_id=new_recipe.id,
             ingredient_id=ingredient_row.id)
    if chat_group.name == "Unnamed" and recipe_title:
        chat_group.name = recipe_title[:252] + "..." if len(recipe_title) > 255 else recipe_title
        _log("info", "Renamed unnamed chat group from recipe title", user_id=user_id, chat_group_id=chat_group.id,
             new_name=chat_group.name)
    response_data["recipe"]["image_url"] = image_url
    response_data["recipe"]["id"] = new_recipe.id
    new_chat_history.image_url = image_url
    new_recipe.image_url = image_url
    db.session.commit()
    _log("info", "Completed handling recipe response", user_id=user_id, chat_group_id=chat_group.id,
         recipe_id=new_recipe.id)
    return response_data, 200


@chat_blueprint.route('/group/new', methods=['GET'])
@jwt_required()
def create_new_group():
    user_id = int(flask_jwt_extended.get_jwt_identity())
    _log("info", "Receive request for /chat/group/new", user_id=user_id)
    new_group = ChatGroupModel(create_user_id=user_id)
    from backend.db_manager import db
    db.session.add(new_group)
    db.session.commit()
    _log("info", "Completed creating new chat group", user_id=user_id, chat_group_id=new_group.id)
    return {"message": "New chat group created", "group_id": new_group.id}, 200


@chat_blueprint.route('/group/all', methods=['GET'])
@jwt_required()
def get_all_groups():
    user_id = int(flask_jwt_extended.get_jwt_identity())
    _log("info", "Receive request for /chat/group/all", user_id=user_id)
    chat_groups = ChatGroupModel.query.filter_by(create_user_id=user_id).all()
    if not chat_groups:
        _log("info", "Completed listing chat groups", user_id=user_id, group_count=0)
        return {"chat_groups": []}, 200
    last_chat_histories = {
        group.id: ChatHistoryModel.query.filter_by(chat_group_id=group.id).order_by(
            ChatHistoryModel.timestamp.desc()).first() for group in chat_groups}
    groups_data = [{"id": group.id, "name": group.name,
                    "last_edit": last_chat_histories.get(group.id).timestamp.isoformat()} for
                   group in chat_groups if last_chat_histories.get(
            group.id) is not None]  # avoid returning groups without any chat history
    _log("info", "Completed listing chat groups", user_id=user_id, group_count=len(groups_data))
    return {"chat_groups": groups_data}, 200


@chat_blueprint.route('/group/<int:group_id>/history', methods=['GET'])
@jwt_required()
def get_chat_history(group_id):
    user_id = int(flask_jwt_extended.get_jwt_identity())
    _log("info", "Receive request for /chat/group/<group_id>/history", user_id=user_id, chat_group_id=group_id)
    chat_group = ChatGroupModel.query.filter_by(id=group_id).first()
    if not chat_group:
        _log("warning", "Chat group not found for history request", user_id=user_id, chat_group_id=group_id)
        return {"message": "Chat group not found"}, 404
    if chat_group.create_user_id != user_id:
        _log("warning", "Unauthorized access to chat history", user_id=user_id, chat_group_id=group_id)
        return {"message": "Unauthorized access to chat group"}, 403
    chat_history = ChatHistoryModel.query.filter_by(chat_group_id=group_id).order_by(
        ChatHistoryModel.timestamp.desc()).all()
    history_data = [
        {"id": history.id, "prompt": history.prompt, "response": history.response, "image_url": history.image_url,
         "timestamp": history.timestamp.isoformat() if history.timestamp else None} for
        history in chat_history]
    _log("info", "Completed reading chat history", user_id=user_id, chat_group_id=group_id,
         history_count=len(history_data))
    return {"chat_history": history_data}, 200
