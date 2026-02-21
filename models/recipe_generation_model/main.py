import logging
import os
import time

import flask
from dotenv import load_dotenv
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
    env_path="./.env_dev"
    load_dotenv(env_path)
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_path = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    app = Flask(__name__)
    app.logger.info("Initializing models and retriever...")
    model = OllamaLLM(model="qwen3:1.7b",
                      keep_alive="0",
                      )
    classification_model = OllamaLLM(model="qwen3:0.6b")
    embedding_model = OllamaEmbeddings(model="qwen3-embedding:0.6b")
    recipe_retriever = RecipeRetriever(database_path=db_path,dataset_name="paultimothymooney/recipenlg",
                                       embeddings_model=embedding_model, csv_name="RecipeNLG_dataset.csv", data_length=10000, app=app)
    recipe_assistant = RecipeAssistant(
        generation_model=model, classification_model=classification_model, recipe_retriever=recipe_retriever, db_path=db_path, app=app)

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
