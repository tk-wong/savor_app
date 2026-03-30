import os
from operator import itemgetter
from urllib.error import URLError
from urllib.request import urlopen

import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.models import OllamaModel
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from langchain_core.runnables import RunnableParallel
from langchain_ollama import OllamaLLM

from classification_strategy import ClassificationStrategy
from question_strategy import QuestionStrategy
from recipe_generation_strategy import RecipeGenerationStrategy

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "qwen3:0.6b")
EVAL_MODEL = os.getenv("DEEPEVAL_MODEL", "deepseek-r1:8b")


def _ollama_is_reachable(base_url: str) -> bool:
    try:
        with urlopen(f"{base_url}/api/tags", timeout=2):
            return True
    except (URLError, TimeoutError, ValueError):
        return False


pytestmark = pytest.mark.skipif(
    not _ollama_is_reachable(OLLAMA_BASE_URL),
    reason=(
        "Ollama is not reachable. Start Ollama and verify OLLAMA_BASE_URL "
        "before running DeepEval strategy tests."
    ),
)


eval_model = OllamaModel(
    model=EVAL_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0,
)


def _label_metric() -> GEval:
    return GEval(
        name="Strategy Label",
        criteria=(
            "Determine if the actual output label matches the expected output "
            "label semantically and exactly for intent classification."
        ),
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.5,
        model=eval_model,
    )


def _response_metric(name: str) -> GEval:
    return GEval(
        name=name,
        criteria=(
            "Determine whether the actual output follows the expected JSON format, "
            "matches the requested prompt_type intent, and provides a useful response."
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.5,
        model=eval_model,
    )


# def test_correctness():
#     correctness_metric = GEval(
#         name="Correctness",
#         criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
#         evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
#         threshold=0.5,
#         model=model
#     )
#     test_case = LLMTestCase(
#         input="I have a persistent cough and fever. Should I be worried?",
#         # Replace this with the actual output from your LLM application
#         actual_output="test",
#         expected_output="A persistent cough and fever could indicate a range of illnesses, from a mild viral "
#                         "infection to more serious conditions like pneumonia or COVID-19. You should seek medical "
#                         "attention if your symptoms worsen, persist for more than a few days, or are accompanied by "
#                         "difficulty breathing, chest pain, or other concerning signs."
#     )
#     assert_test(test_case, [correctness_metric])


def test_classification_strategy_label():
    classification_chain = ClassificationStrategy().build_chain(
        OllamaLLM(model=GENERATION_MODEL, base_url=OLLAMA_BASE_URL, temperature=0),
        RunnableParallel(
            {
                "request": itemgetter("request"),
                "chat_history": itemgetter("chat_history"),
            }
        ),
    )

    actual = classification_chain.invoke(
        {
            "request": "What is the difference between deep fried and stir-fried?",
            "chat_history": "User asked about cooking techniques.",
        }
    )

    test_case = LLMTestCase(
        input="What is the difference between deep fried and stir-fried?",
        actual_output=str(actual).strip().lower(),
        expected_output="question",
    )
    assert_test(test_case, [_label_metric()])


def test_question_strategy_response():
    question_chain = QuestionStrategy().build_chain(
        OllamaLLM(model=GENERATION_MODEL, base_url=OLLAMA_BASE_URL, temperature=0),
        RunnableParallel(
            {
                "request": itemgetter("request"),
                "chat_history": itemgetter("chat_history"),
                "recipes": itemgetter("recipes"),
            }
        ),
    )

    request = "How can I make scrambled eggs fluffier?"
    actual = question_chain.invoke(
        {
            "request": request,
            "chat_history": "User has eggs, butter, and milk.",
            "recipes": "[{\"title\": \"Soft Scrambled Eggs\", \"ingredients\": [\"eggs\", \"butter\"]}]",
        }
    )

    test_case = LLMTestCase(
        input=request,
        actual_output=str(actual),
        expected_output='{"prompt_type":"question","answer":"Provides actionable tips for fluffier scrambled eggs."}',
    )
    assert_test(test_case, [_response_metric("Question Strategy")])


def test_recipe_generation_strategy_response():
    recipe_chain = RecipeGenerationStrategy().build_chain(
        OllamaLLM(model=GENERATION_MODEL, base_url=OLLAMA_BASE_URL, temperature=0),
        RunnableParallel(
            {
                "request": itemgetter("request"),
                "chat_history": itemgetter("chat_history"),
                "recipes": itemgetter("recipes"),
            }
        ),
    )

    request = "Create a quick pasta recipe using tomato and garlic"
    actual = recipe_chain.invoke(
        {
            "request": request,
            "chat_history": "User prefers vegetarian dishes.",
            "recipes": "[{\"title\": \"Garlic Tomato Pasta\", \"ingredients\": [\"pasta\", \"garlic\", \"tomato\"]}]",
        }
    )

    test_case = LLMTestCase(
        input=request,
        actual_output=str(actual),
        expected_output=(
            '{"prompt_type":"recipe","recipe":{'
            '"title":"Pasta dish",'
            '"ingredients":[{"ingredient_name":"tomato","quantity":"..."}],'
            '"directions":["..."],"description":"...","tips":["..."]}}'
        ),
    )
    assert_test(test_case, [_response_metric("Recipe Strategy")])
