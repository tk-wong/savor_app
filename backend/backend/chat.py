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
    return model_response.json()
