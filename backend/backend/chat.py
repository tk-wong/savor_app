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
    prompt = response_data.get("prompt_type")
    if not prompt:
        return {"message": "Response missing prompt_type"}, 500
    if prompt == "question":
        return response_data, 200
    elif prompt == "recipe":
        recipe_data = response_data.get("recipe")
        if not recipe_data:
            return {"message": "Response missing recipe data"}, 500
        recipe_title = recipe_data.get("title")
        image_response = requests.post("http://localhost:5020/create_image", json={"prompt": recipe_title})
        if image_response.status_code != 200:
            return {"message": "Error generating image"}, 500
        with open(f"static/images/{recipe_title}.png", "wb") as f:
            f.write(image_response.content)
        return response_data, 200
    else:
        return {"message": "Error generating response"}, 500
    return model_response.json()
