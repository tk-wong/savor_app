import logging
import time

import flask
from flask import Flask
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM

from recipe_assistant import RecipeAssistant
from recipe_retriever import RecipeRetriever
from logging.config import dictConfig


def main():
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })
    app = Flask(__name__)
    app.logger.info("Initializing models and retriever...")
    model = OllamaLLM(model="qwen3:1.7b")
    classification_model = OllamaLLM(model="qwen3:0.6b")
    embedding_model = OllamaEmbeddings(model="qwen3-embedding:0.6b")
    recipe_retriever = RecipeRetriever(env_path="./.env_dev", dataset_name="paultimothymooney/recipenlg",
                                       embeddings_model=embedding_model, csv_name="RecipeNLG_dataset.csv", data_length=10000, app=app)
    recipe_assistant = RecipeAssistant(
        model, classification_model, recipe_retriever)

    @app.route('/recipe_generation', methods=['POST'])
    def recipe_generation():
        request = flask.request.json.get('prompt')
        if not request:
            return {"error": "prompt is required"}, 400
        result = recipe_assistant.handle_request(request)
        return flask.Response(result, mimetype="application/json")
    app.run(port=5010, debug=True)


if __name__ == '__main__':
    main()

# result = classifier_chain.invoke(request)
# print(result)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
