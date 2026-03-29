import os
import json
from logging.config import dictConfig

import flask
from dotenv import load_dotenv
from flask import Flask
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from sqlalchemy_utils import create_database, database_exists

from recipe_assistant import RecipeAssistant
from recipe_retriever import RecipeRetriever


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
    env_path = "./.env_dev"
    load_dotenv(env_path)
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    drop_tables_on_init = os.getenv("DROP_TABLES_ON_INIT", "false").lower() == "true"
    db_path = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    if not database_exists(db_path):
        create_database(db_path)

    app = Flask(__name__)
    app.logger.info("DROP_TABLES_ON_INIT=%s", drop_tables_on_init)
    app.logger.info("Initializing models and retriever...")
    model = OllamaLLM(model="qwen3:1.7b",
                      keep_alive="0",
                      )
    classification_model = OllamaLLM(model="qwen3:0.6b",
                                     keep_alive="0",)
    embedding_model = OllamaEmbeddings(model="qwen3-embedding:0.6b",
                                       keep_alive=0,)
    recipe_retriever = RecipeRetriever(database_path=db_path, dataset_name="paultimothymooney/recipenlg",
                                       embeddings_model=embedding_model, csv_name="RecipeNLG_dataset.csv",
                                       data_length=10000, app=app)
    recipe_assistant = RecipeAssistant(
        generation_model=model, classification_model=classification_model, recipe_retriever=recipe_retriever,
        db_path=db_path, app=app)

    @app.route('/recipe_generation', methods=['POST'])
    def recipe_generation():
        request = flask.request.json.get('prompt')
        user_id = flask.request.json.get('user_id')
        group_id = flask.request.json.get('group_id')
        if not request or not user_id or not group_id:
            return {"error": "prompt, user_id, and group_id are required"}, 400
        result = recipe_assistant.handle_request(request, user_id, group_id)
        try:
            payload = json.loads(result)
            if isinstance(payload, dict) and "prompt_type" not in payload:
                if "recipe" in payload:
                    payload["prompt_type"] = "recipe"
                elif "answer" in payload:
                    payload["prompt_type"] = "question"
            return flask.jsonify(payload)
        except (TypeError, json.JSONDecodeError):
            return flask.Response(result, mimetype="application/json"), 500

    app.run(port=5010, debug=True)


if __name__ == '__main__':
    main()

# result = classifier_chain.invoke(request)
# print(result)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
