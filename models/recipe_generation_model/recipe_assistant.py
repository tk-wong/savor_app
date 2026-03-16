import uuid
from operator import itemgetter

import psycopg
from flask import Flask
from langchain_core.runnables import RunnableParallel, RunnableWithMessageHistory, RunnableLambda
from langchain_ollama import OllamaLLM
from langchain_postgres import PostgresChatMessageHistory

from classification_strategy import ClassificationStrategy
from question_strategy import QuestionStrategy
from recipe_generation_strategy import RecipeGenerationStrategy
from recipe_retriever import RecipeRetriever


class RecipeAssistant:
    def __init__(self, generation_model: OllamaLLM, classification_model: OllamaLLM, recipe_retriever: RecipeRetriever,
                 db_path: str, app: Flask, table_name: str = "llm_chat_history"):
        self.model_strategies = {
            "recipe": RecipeGenerationStrategy(),
            "question": QuestionStrategy(),
            "classification": ClassificationStrategy()
        }
        self.db_path = db_path
        self.table_name = table_name
        self.app = app
        self.db_connection = psycopg.connect(conninfo=self.db_path, autocommit=True)
        self.generation_model: OllamaLLM = generation_model
        self.classification_model: OllamaLLM = classification_model
        self.recipe_retriever: RecipeRetriever = recipe_retriever
        self.request_runnable = (
                RunnableParallel(
                    {
                        "question": itemgetter("request"),
                        "chat_history": itemgetter("chat_history"),
                    }
                )
                | RunnableParallel(
            {
                "recipes": RunnableLambda(itemgetter("question")) | self.recipe_retriever.get_retriever(),
                "request": itemgetter("question"),
                "chat_history": itemgetter("chat_history"),
            }
        )
        )
        self.classify_runnable = RunnableParallel(
            {
                "request": itemgetter("request"),
                "chat_history": itemgetter("chat_history"),
            }
        )

    def classify(self, request, session_id):
        classifier_chain = self.model_strategies["classification"].build_chain(self.classification_model,
                                                                               self.classify_runnable)
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
        result = classifier_chain.invoke({"request": request, "chat_history": self.get_conversation_history(
            session_id)})  # cannot decide based on keywords, use model to classify
        return result.lower().strip()

    def handle_request(self, request, user_id, group_id):
        try:
            uuid_namespace = uuid.NAMESPACE_DNS
            session_str = f"{user_id}-{group_id}"
            session_id = str(uuid.uuid5(uuid_namespace, session_str))
            classification = self.classify(request, session_id)
            print(f"Classification result: {classification}")
            strategy = self.model_strategies.get(classification)
            if strategy is None:
                raise ValueError(f"Unsupported request type: {classification}")
            chain = strategy.build_chain(self.generation_model, self.request_runnable)
            chain_with_history = RunnableWithMessageHistory(
                chain,
                self.get_conversation_history,
                input_messages_key="request",
                history_messages_key="chat_history",
            )

            result = chain_with_history.stream({"request": request},
                                               config={"configurable": {"session_id": session_id}},
                                               )
            for chunk in result:
                yield chunk
        except Exception as e:
            # self.app.logger.error(f"Error handling request: {e}\n Traceback: {e.__traceback__}")
            yield "{\"error\": \"An error occurred while processing the request.\"}"
            raise e

    def get_conversation_history(self, session_id):
        history = PostgresChatMessageHistory(
            self.table_name,
            session_id,
            sync_connection=self.db_connection,
            # connection_string=self.db_path,
        )
        history.create_tables(self.db_connection, self.table_name)
        return history
        # if session_id not in self.store:
        #     self.store[session_id] = InMemoryChatMessageHistory()
        # return self.store[session_id]
        # return InMemoryChatMessageHistory()
