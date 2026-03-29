from chain_strategy import ChainStrategy


class QuestionStrategy(ChainStrategy):
    question_template = '''You are a professional chef and trying to answer the question from the user. (You DO NOT need 
    to mention that you are a chef when answering the question)
    Here are some relevant recipes for your reference: {recipes} 
    You can combine the ideas from these recipes to answer the question. 
    Here are the previous conversions with the user: {chat_history}
    Here is the question from the user: {request}
    Respond with ONLY one valid JSON object. Do not include markdown fences or any extra text.
    The field "prompt_type" is REQUIRED and must be exactly "question".
    Use the following exact top-level structure:
    {{
        "prompt_type": "question",
        "answer": "the answer to the user's question, which should be detailed and informative, and refer to the relevant recipes when necessary.
        You should provide the recipe title, ingredients, and detailed directions in your answer if it is needed for explaining to the user.
        However, do not mention any ids of the recipes when answering the questions and providing the recipe example.
        You can use markdown format to make the answer more clear and organized. "
    }}
    '''
    def build_chain(self, llm, request_runnable):
        from langchain_core.prompts import ChatPromptTemplate
        question_prompt = ChatPromptTemplate.from_template(self.question_template)
        question_chain = request_runnable | question_prompt | llm
        return question_chain

    def request_type(self):
        return "question"