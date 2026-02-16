import time

from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM

from recipe_assistant import RecipeAssistant
from recipe_retriever import RecipeRetriever


def main():
    model = OllamaLLM(model="qwen3:4b")
    classification_model = OllamaLLM(model="qwen3:0.6b")
    embedding_model = OllamaEmbeddings(model="qwen3-embedding:0.6b")
    recipe_retriever = RecipeRetriever(env_path="./.env_dev", dataset_path="../dataset/RecipeNLG/dataset/full_dataset.csv",
                                       embeddings_model=embedding_model)
    recipe_assistant = RecipeAssistant(model, classification_model, recipe_retriever)
    request = "create a recipe that use beef for mapo tofu"
    last = time.time()
    result = recipe_assistant.handle_request(request)
    for chunk in result:
        print(chunk, end="", flush=True)
    end = time.time()
    print(f"\nTime taken: {end - last:.2f} seconds")


if __name__ == '__main__':
    main()

# result = classifier_chain.invoke(request)
# print(result)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
