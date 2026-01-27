from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector_db import retriever


model = OllamaLLM(model="qwen3:4b")

question_template = '''You are a professional chef and trying to answer the question from the user. (You do not need 
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

router_destinations = {
    "question": question_template,
    "recipe_creation": recipe_creation_template,
}

# recipe_generation_prompt = ChatPromptTemplate.from_template(recipe_creation_template)
# chain = recipe_generation_prompt | model
question_prompt = ChatPromptTemplate.from_template(question_template)
chain = question_prompt | model
request = "What is the difference between a cake and a bread? Please provide some recipes as examples."
recipe = retriever.invoke(request)
result = chain.invoke({"recipes": recipe, "request": request})
print(result)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


