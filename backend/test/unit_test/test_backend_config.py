import importlib
import sys

import pytest

_CONFIG_ENV_KEYS = [
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "SECRET_KEY",
    "JWT_SECRET_KEY",
    "AI_COOKING_AGENT_HOST",
    "AI_COOKING_AGENT_PORT",
    "IMAGE_GENERATION_HOST",
    "IMAGE_GENERATION_PORT",
    "MOCK_AI_MODELS",
    "MOCK_IMAGE_URL",
]


def _import_fresh_config():
    sys.modules.pop("backend.config", None)
    return importlib.import_module("backend.config")


@pytest.fixture(autouse=True)
def _clear_config_module_cache():
    sys.modules.pop("backend.config", None)
    yield
    sys.modules.pop("backend.config", None)


@pytest.fixture(autouse=True)
def _clear_config_env(monkeypatch):
    for key in _CONFIG_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_config_dotenv_failure_exits(mocker, capsys):
    mocker.patch("dotenv.load_dotenv", return_value=False)
    exit_mock = mocker.patch("builtins.exit", side_effect=SystemExit(1))

    with pytest.raises(SystemExit) as exc_info:
        _import_fresh_config()

    assert exc_info.value.code == 1
    exit_mock.assert_called_once_with(1)
    captured = capsys.readouterr()
    assert "Warning: .env_dev file not found" in captured.out


def test_config_builds_db_and_service_urls_from_env(mocker, monkeypatch):
    mocker.patch("dotenv.load_dotenv", return_value=True)

    monkeypatch.setenv("DB_USER", "db_user")
    monkeypatch.setenv("DB_PASSWORD", "db_pass")
    monkeypatch.setenv("DB_HOST", "db.example")
    monkeypatch.setenv("DB_PORT", "5433")
    monkeypatch.setenv("DB_NAME", "savor")

    monkeypatch.setenv("AI_COOKING_AGENT_HOST", "agent.example")
    monkeypatch.setenv("AI_COOKING_AGENT_PORT", "6010")
    monkeypatch.setenv("IMAGE_GENERATION_HOST", "img.example")
    monkeypatch.setenv("IMAGE_GENERATION_PORT", "6020")

    monkeypatch.setenv("MOCK_AI_MODELS", "1")
    monkeypatch.setenv("MOCK_IMAGE_URL", "static/images/mock_custom.png")

    config = _import_fresh_config()

    assert config.SQLALCHEMY_DATABASE_URI == "postgresql://db_user:db_pass@db.example:5433/savor"
    assert config.AI_COOKING_AGENT_URL == "http://agent.example:6010/recipe_generation"
    assert config.IMAGE_GENERATION_URL == "http://img.example:6020/create_image"
    assert config.MOCK_AI_MODELS is True
    assert config.MOCK_IMAGE_URL == "static/images/mock_custom.png"


def test_config_uses_service_defaults_when_env_missing(mocker, monkeypatch):
    mocker.patch("dotenv.load_dotenv", return_value=True)

    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASSWORD", "p")
    monkeypatch.setenv("DB_HOST", "h")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "n")

    config = _import_fresh_config()

    assert config.AI_COOKING_AGENT_URL == "http://localhost:5010/recipe_generation"
    assert config.IMAGE_GENERATION_URL == "http://localhost:5020/create_image"
    assert config.MOCK_AI_MODELS is False
    assert config.MOCK_IMAGE_URL == "static/images/temp.png"


def test_config_secret_keys_use_env_values_when_provided(mocker, monkeypatch):
    mocker.patch("dotenv.load_dotenv", return_value=True)
    token_hex_mock = mocker.patch("secrets.token_hex", side_effect=["generated-1", "generated-2"])

    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASSWORD", "p")
    monkeypatch.setenv("DB_HOST", "h")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "n")

    monkeypatch.setenv("SECRET_KEY", "env-secret")
    monkeypatch.setenv("JWT_SECRET_KEY", "env-jwt-secret")

    config = _import_fresh_config()

    assert config.SECRET_KEY == "env-secret"
    assert config.JWT_SECRET_KEY == "env-jwt-secret"
    assert token_hex_mock.call_count == 2


def test_config_secret_keys_fallback_to_generated_values(mocker, monkeypatch):
    mocker.patch("dotenv.load_dotenv", return_value=True)
    mocker.patch("secrets.token_hex", side_effect=["generated-secret", "generated-jwt"])

    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASSWORD", "p")
    monkeypatch.setenv("DB_HOST", "h")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "n")

    config = _import_fresh_config()

    assert config.SECRET_KEY == "generated-secret"
    assert config.JWT_SECRET_KEY == "generated-jwt"


def test_config_mock_ai_models_is_true_only_for_string_one(mocker, monkeypatch):
    mocker.patch("dotenv.load_dotenv", return_value=True)

    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASSWORD", "p")
    monkeypatch.setenv("DB_HOST", "h")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "n")
    monkeypatch.setenv("MOCK_AI_MODELS", "true")

    config = _import_fresh_config()

    assert config.MOCK_AI_MODELS is False
