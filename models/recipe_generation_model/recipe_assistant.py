from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from classification_strategy import ClassificationStrategy
from question_strategy import QuestionStrategy
from recipe_generation_strategy import RecipeGenerationStrategy


class RecipeAssistant:
    def __init__(self, generation_model, classification_model, retriever):
        self.model_strategies = {
            "recipe": RecipeGenerationStrategy(),
            "question": QuestionStrategy(),
            "classification": ClassificationStrategy()
        }
        self.generation_model = generation_model
        self.classification_model = classification_model
        self.retriever = retriever
        self.request_runnable = RunnableParallel({"recipes": retriever, "request": RunnablePassthrough()})

    def classify(self,request):
        classifier_chain = self.model_strategies["classification"].build_chain(self.classification_model, self.retriever)
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

    def handle_request(self, request):
        classification = self.classify(request)
        print(f"Classification result: {classification}")
        strategy = self.model_strategies.get(classification)
        if strategy is None:
            raise ValueError(f"Unsupported request type: {classification}")
        chain = strategy.build_chain(self.generation_model, self.request_runnable)
        result = chain.stream(request)
        for chunk in result:
            yield chunk