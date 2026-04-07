import pathlib
import sys

# Ensure tests can import top-level modules from recipe_generation_model/.
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from recipe_retriever import RecipeRetriever


class DummyLogger:
    def info(self, *_args, **_kwargs):
        return None


class DummyApp:
    logger = DummyLogger()


def test_retriever_creates_database_before_pgvector(monkeypatch):
    import recipe_retriever as module

    calls = []

    class FakePGVector:
        def __init__(self, *args, **kwargs):
            calls.append("pgvector_init")

        def as_retriever(self, search_kwargs):
            calls.append("as_retriever")
            return {"search_kwargs": search_kwargs}

    monkeypatch.setattr(module, "PGVector", FakePGVector)
    monkeypatch.setattr(module, "database_exists", lambda *_args, **_kwargs: calls.append("database_exists") or False)
    monkeypatch.setattr(module, "create_database", lambda *_args, **_kwargs: calls.append("create_database"))
    monkeypatch.setattr(module, "should_drop_tables", lambda: False)
    monkeypatch.setattr(module.RecipeRetriever, "_collection_exists", lambda *_args, **_kwargs: calls.append("collection_exists") or False)
    monkeypatch.setattr(module.RecipeRetriever, "create_embeddings", lambda self: calls.append("create_embeddings"))

    RecipeRetriever(
        app=DummyApp(),
        dataset_name="unused",
        csv_name="unused.csv",
        embeddings_model=object(),
        database_path="postgresql://unused",
        data_length=1,
    )

    assert calls == [
        "database_exists",
        "create_database",
        "pgvector_init",
        "create_embeddings",
        "as_retriever",
    ]


def test_retriever_skips_create_database_when_database_exists(monkeypatch):
    import recipe_retriever as module

    calls = []

    class FakePGVector:
        def __init__(self, *args, **kwargs):
            calls.append("pgvector_init")

        def as_retriever(self, search_kwargs):
            calls.append("as_retriever")
            return {"search_kwargs": search_kwargs}

    monkeypatch.setattr(module, "PGVector", FakePGVector)
    monkeypatch.setattr(module, "database_exists", lambda *_args, **_kwargs: calls.append("database_exists") or True)
    monkeypatch.setattr(module, "create_database", lambda *_args, **_kwargs: calls.append("create_database"))
    monkeypatch.setattr(module, "should_drop_tables", lambda: False)
    monkeypatch.setattr(module.RecipeRetriever, "_collection_exists", lambda *_args, **_kwargs: calls.append("collection_exists") or True)
    monkeypatch.setattr(module.RecipeRetriever, "create_embeddings", lambda self: calls.append("create_embeddings"))

    RecipeRetriever(
        app=DummyApp(),
        dataset_name="unused",
        csv_name="unused.csv",
        embeddings_model=object(),
        database_path="postgresql://unused",
        data_length=1,
    )

    assert calls == [
        "database_exists",
        "pgvector_init",
        "collection_exists",
        "as_retriever",
    ]

