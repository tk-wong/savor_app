from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

from vector_db import retriever


def main():
    model = OllamaLLM(model="qwen3:4b")
    classification_model = OllamaLLM(model="qwen3:0.6b")
    question_template = '''You are a professional chef and trying to answer the question from the user. (You DO NOT need 
to mention that you are a chef when answering the question)
You should provide detailed and informative answers, and refer to the relevant recipes when 
necessary. You should provide the recipe title, ingredients, and detailed directions in your answer if it is needed 
for explaining to the user. However, do not mention any ids of the recipes when answering the questions and providing the recipe example.
Here are some relevant recipes for your reference: {recipes} 
You can combine the ideas from these recipes to answer the question. 
Here is the question from the user: {request}'''
    recipe_creation_template = '''You are a professional chef and trying to create a recipe based on the user request and describe each 
directions in detail. (You do not need to introduce yourself)
You should describe the flavor and texture of the dish after it is finished, and provide some useful cooking tips.
It is not necessary to use all the ingredients provided by the user, but you must use at least one of them.

Here are some relevant recipes for your reference: {recipes}
You can combine the ideas from these recipes to create a new and unique recipe. 
You do not need to mention that which recipe you are referring to. 
Just create a new recipe based on the ideas you get from these recipes.

Here is the request from the user: {request}
'''
    request = "What is the difference between a cake and a bread? Please provide some recipes as examples."
    # recipe = retriever.invoke(request)
    request_runnable = RunnableParallel({"recipes": retriever, "request": RunnablePassthrough()})
    recipe_generation_prompt = ChatPromptTemplate.from_template(recipe_creation_template)
    recipe_generation_chain = request_runnable | recipe_generation_prompt | model
    question_prompt = ChatPromptTemplate.from_template(question_template)
    question_chain = request_runnable | question_prompt | model

    classifier_prompt = ChatPromptTemplate.from_template(
        "Decide whether the following user request is asking for a recipe creation or a question about cooking. "
        "If it is asking for recipe creation, respond with 'recipe'. "
        "If it is asking a question regarding on cooking, respond with 'question'.\n"
        "Otherwise, respond with 'question'.\n"
        "User request: {request}"
    )
    classifier_chain = request_runnable | classifier_prompt | classification_model

    classification = classify_question(request, classifier_chain)
    print(f"Classification result: {classification}")

    def route(x):
        if classification == "recipe":
            chain = recipe_generation_chain
        else:
            chain = question_chain
        for chunk in chain.stream(x):
            yield chunk

    r = RunnableLambda(route)
    result = r.stream(request)
    c = 0
    for data_chunk in result:
        print(data_chunk, end='', flush=True)
        c += 1
    print(f"\nTotal chunks: {c}")


def classify_question(request, classifier_chain):
    recipe_create_words = [
        "create", "make", "generate", "write", "give me", "provide", "i want", "need", "suggest", "develop",
        "formulate", "cook", "recipe", "recipes", "prepare", "example"
    ]
    question_words = [
        "what", "how", "why", "which", "explain", "difference", "tell me", "help", "advise",
        "recommend", "define", "vs", "versus", "compare", "benefits", "disadvantages", "advantages", "ways",
        "is it", "are there", "tell me about"
    ]
    lower_request = request.lower()
    create_recipe = any(word in lower_request for word in recipe_create_words)
    ask_question = any(word in lower_request for word in question_words)
    if create_recipe and ask_question:
        return "question"  # ambiguous, prefer question
    if create_recipe:
        return "recipe"
    if ask_question:
        return "question"
    result = classifier_chain.invoke(request)  # cannot decide based on keywords, use model to classify
    return result.lower().strip()


if __name__ == '__main__':
    main()

# result = classifier_chain.invoke(request)
# print(result)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
