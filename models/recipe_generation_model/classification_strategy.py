from chain_strategy import ChainStrategy


class ClassificationStrategy(ChainStrategy):
    classifier_template = '''Decide whether the following user request is asking for a recipe creation or a question about cooking. 
    If it is asking for recipe creation, respond with 'recipe'. 
    If it is asking a question regarding on cooking, respond with 'question'.
    Otherwise, respond with 'question'.
    User request: {request}
    '''

    def build_chain(self, llm, runnable):
        from langchain_core.prompts import ChatPromptTemplate
        classifier_prompt = ChatPromptTemplate.from_template(self.classifier_template)
        classifier_chain = runnable | classifier_prompt | llm
        return classifier_chain

    def request_type(self):
        return "classification"