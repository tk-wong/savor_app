from flask import Blueprint

chat_blueprint = Blueprint('chat', __name__)

@chat_blueprint.route('/chat', methods=['GET', 'POST'])
def chat():
    return "Chat endpoint"
