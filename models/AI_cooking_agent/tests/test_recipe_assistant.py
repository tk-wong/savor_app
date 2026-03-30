import pathlib
import sys

from flask import Flask
from langchain_core.runnables import RunnableLambda

# Ensure tests can import top-level modules from recipe_generation_model/.
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from recipe_assistant import RecipeAssistant


class DummyRetriever:
    def get_retriever(self):
        # Keep retriever side deterministic and local for tests.
        return RunnableLambda(lambda question: [{"id": 1, "title": f"hit:{question}"}])


class FakeStrategy:
    def __init__(self, chain_name):
        self.chain_name = chain_name
        self.calls = []

    def build_chain(self, llm, runnable):
        self.calls.append((llm, runnable))
        return self.chain_name


class FakeClassifierChain:
    def __init__(self, output):
        self.output = output
        self.calls = []

    def invoke(self, payload):
        self.calls.append(payload)
        return self.output


class FakeRunnableWithMessageHistory:
    def __init__(self, chain, get_history, input_messages_key, history_messages_key):
        self.chain = chain
        self.get_history = get_history
        self.input_messages_key = input_messages_key
        self.history_messages_key = history_messages_key

    def invoke(self, payload, config):
        assert payload["request"]
        assert "session_id" in config["configurable"]
        return f"{self.chain}:final"


def make_assistant(monkeypatch):
    import recipe_assistant as module

    monkeypatch.setattr(module.psycopg, "connect", lambda **_: object())
    return RecipeAssistant(
        generation_model=object(),
        classification_model=object(),
        recipe_retriever=DummyRetriever(),
        db_path="postgresql://unused",
        app=Flask(__name__),
    )


def test_classify_recipe_keyword_path_skips_model(monkeypatch):
    assistant = make_assistant(monkeypatch)

    fake_chain = FakeClassifierChain("question")

    monkeypatch.setattr(
        assistant.model_strategies["classification"],
        "build_chain",
        lambda *_args, **_kwargs: fake_chain,
    )

    result = assistant.classify("Please create a pasta recipe with tomato", "s-1")

    assert result == "recipe"
    assert fake_chain.calls == []


def test_classify_question_keyword_path_skips_model(monkeypatch):
    assistant = make_assistant(monkeypatch)

    fake_chain = FakeClassifierChain("recipe")

    monkeypatch.setattr(
        assistant.model_strategies["classification"],
        "build_chain",
        lambda *_args, **_kwargs: fake_chain,
    )

    result = assistant.classify("How do I keep rice from getting mushy?", "s-2")

    assert result == "question"
    assert fake_chain.calls == []


def test_classify_falls_back_to_classifier_chain(monkeypatch):
    assistant = make_assistant(monkeypatch)
    fake_chain = FakeClassifierChain("  ReCiPe  ")

    monkeypatch.setattr(
        assistant.model_strategies["classification"],
        "build_chain",
        lambda *_args, **_kwargs: fake_chain,
    )
    monkeypatch.setattr(
        assistant,
        "get_conversation_history",
        lambda session_id: f"history-for:{session_id}",
    )

    result = assistant.classify("Could you assist with tonight dinner?", "session-xyz")

    assert result == "recipe"
    assert fake_chain.calls == [
        {
            "request": "Could you assist with tonight dinner?",
            "chat_history": "history-for:session-xyz",
        }
    ]


def test_handle_request_returns_recipe_strategy_response(monkeypatch):
    assistant = make_assistant(monkeypatch)
    recipe_strategy = FakeStrategy("recipe_chain")
    question_strategy = FakeStrategy("question_chain")

    assistant.model_strategies["recipe"] = recipe_strategy
    assistant.model_strategies["question"] = question_strategy

    monkeypatch.setattr(assistant, "classify", lambda *_args, **_kwargs: "recipe")

    import recipe_assistant as module

    monkeypatch.setattr(module, "RunnableWithMessageHistory", FakeRunnableWithMessageHistory)

    result = assistant.handle_request("create a salad", user_id=11, group_id=5)

    assert result == "recipe_chain:final"
    assert len(recipe_strategy.calls) == 1
    assert len(question_strategy.calls) == 0


def test_handle_request_returns_question_strategy_response(monkeypatch):
    assistant = make_assistant(monkeypatch)
    recipe_strategy = FakeStrategy("recipe_chain")
    question_strategy = FakeStrategy("question_chain")

    assistant.model_strategies["recipe"] = recipe_strategy
    assistant.model_strategies["question"] = question_strategy

    monkeypatch.setattr(assistant, "classify", lambda *_args, **_kwargs: "question")

    import recipe_assistant as module

    monkeypatch.setattr(module, "RunnableWithMessageHistory", FakeRunnableWithMessageHistory)

    result = assistant.handle_request("what can I do with basil?", user_id=2, group_id=9)

    assert result == "question_chain:final"
    assert len(recipe_strategy.calls) == 0
    assert len(question_strategy.calls) == 1




