from chain_strategy import ChainStrategy


class RecipeGenerationStrategy(ChainStrategy):
    recipe_creation_template = '''You are a professional chef and trying to create a recipe based on the user request and describe each 
    directions in detail. 
    It is not necessary to use all the ingredients provided by the user, but you must use at least one of them.

    # Here are some relevant recipes for your reference: {recipes}
    You can combine the ideas from these recipes to create a new and unique recipe. 

    Here is the request from the user: {request}
    Response in JSON format with the following structure (Do not add extra information other than the JSON format, and make sure the response is in valid JSON format):
    {{
        "prompt_type": "recipe",
        "recipe": {{
        "title": "the title of the recipe you created",
        "ingredients": ["a list of ingredients needed for the recipe, which should be in a simple and concise format, and only include the ingredients that are necessary for the recipe"],
        "directions": ["a list of detailed directions for cooking the dish, which should be clear and easy to follow even for a beginner, and should include any necessary cooking tips or techniques that are relevant to the recipe. 
        Do not include the index of the direction step in the direction description. You can use markdown format to make the directions more clear and organized."],
        "description": "a detailed description of the flavor and texture of the dish after it is finished, which should be vivid and appetizing, and should give the user a clear idea of what to expect from the dish when they cook it",
        "tips": ["a list of some useful cooking tips for this recipe, which should be practical and relevant, and should help the user to cook the dish successfully and enhance the flavor and texture of the dish. 
        Do not include the index of the tip in the tip description. 
        You can use markdown format to make the tips more clear and organized."],
        }}
    }}
    '''

    def build_chain(self, llm, request_runnable):
        from langchain_core.prompts import ChatPromptTemplate
        recipe_generation_prompt = ChatPromptTemplate.from_template(self.recipe_creation_template)
        recipe_generation_chain = request_runnable | recipe_generation_prompt | llm
        return recipe_generation_chain


    def request_type(self):
        return "recipe"
