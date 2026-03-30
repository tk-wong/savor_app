import importlib
import os
import sys


def _reload_integration_test_config():
    module_name = "test.integration_test.test_config"
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


def test_integration_test_config_loads_env_test_by_default(monkeypatch):
    monkeypatch.delenv("APP_MODE", raising=False)

    config = _reload_integration_test_config()

    expected_uri = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    assert config.SQLALCHEMY_DATABASE_URI == expected_uri
    assert config.TESTING is True
    assert config.SECRET_KEY == "dev" * 32


def test_integration_test_config_builds_service_urls_and_flags(monkeypatch):
    monkeypatch.delenv("APP_MODE", raising=False)

    config = _reload_integration_test_config()

    assert config.AI_COOKING_AGENT_URL == (
        f"http://{os.getenv('AI_COOKING_AGENT_HOST', 'localhost')}:"
        f"{os.getenv('AI_COOKING_AGENT_PORT', '5010')}/recipe_generation"
    )
    assert config.IMAGE_GENERATION_URL == (
        f"http://{os.getenv('IMAGE_GENERATION_HOST', 'localhost')}:"
        f"{os.getenv('IMAGE_GENERATION_PORT', '5020')}/create_image"
    )
    assert config.MOCK_AI_MODELS == (os.getenv("MOCK_AI_MODELS", "0") == "1")
    assert config.MOCK_IMAGE_URL == os.getenv("MOCK_IMAGE_URL", "static/images/temp.png")
    assert config.DROP_DB_ON_STARTUP == (os.getenv("DROP_DB_ON_STARTUP", "0") == "1")


def test_integration_test_config_switches_to_frontend_env_file(monkeypatch):
    monkeypatch.setenv("APP_MODE", "frontend_integration")
    monkeypatch.setenv("DROP_DB_ON_STARTUP", "1")

    config = _reload_integration_test_config()

    # Module-level selector should switch env file when APP_MODE is set.
    assert config.selected_env_file == ".env_frontend_integration"
    assert config.DROP_DB_ON_STARTUP is True
