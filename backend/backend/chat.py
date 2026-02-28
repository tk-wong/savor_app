import os

import requests
from flask import Blueprint, request

chat_blueprint = Blueprint('chat', __name__)


@chat_blueprint.route('/chat', methods=['POST'])
def chat():
    prompt = request.json.get('prompt')
    if not prompt:
        return {"message": "Prompt is required"}, 400
    model_response = requests.post("http://localhost:5010/recipe_generation", json={"prompt": prompt})
    if model_response.status_code != 200:
        return {"message": "Error generating response"}, 500
    try:
        response_data = model_response.json()
    except requests.exceptions.JSONDecodeError:
        return {"message": "Invalid response from model"}, 500
    prompt_type = response_data.get("prompt_type")
    if not prompt_type:
        return {"message": "Response missing prompt_type"}, 500
    if prompt_type == "question":
        return response_data, 200
    elif prompt_type == "recipe":
        recipe_data = response_data.get("recipe")
        if not recipe_data:
            return {"message": "Response missing recipe data"}, 500
        recipe_title = recipe_data.get("title")
        image_response = requests.post("http://localhost:5020/create_image", json={"prompt": recipe_title})
        if image_response.status_code != 200:
            return {"message": "Error generating image from the image generation model"}, 500
        if not os.path.exists("static/images"):
            os.makedirs("static/images")
        safe_filename = os.path.basename(recipe_title)
        with open(f"static/images/{safe_filename}.png", "wb") as f:
            f.write(image_response.content)
        return response_data, 200
    return {"message": "Error generating response"}, 500

# TODO: chat history, save to database, and retrieve from database
