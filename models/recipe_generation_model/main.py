import time

import flask
from flask import Flask
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM

from recipe_assistant import RecipeAssistant
from recipe_retriever import RecipeRetriever


def main():
    app = Flask(__name__)
    model = OllamaLLM(model="qwen3:1.7b")
    classification_model = OllamaLLM(model="qwen3:0.6b")
    embedding_model = OllamaEmbeddings(model="qwen3-embedding:0.6b")
    recipe_retriever = RecipeRetriever(env_path="./.env_dev", dataset_path="../dataset/RecipeNLG/dataset/full_dataset.csv",
                                       embeddings_model=embedding_model)
    recipe_assistant = RecipeAssistant(model, classification_model, recipe_retriever)


    @app.route('/recipe_generation', methods=['POST'])
    def recipe_generation():
        request = flask.request.json.get('createRequest')
        if not request:
            return {"error": "createRequest is required"}, 400
        result = recipe_assistant.handle_request(request)
        return flask.Response(result, mimetype="application/json")
    app.run(port=5010, debug=True)

if __name__ == '__main__':
    main()

# result = classifier_chain.invoke(request)
# print(result)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
