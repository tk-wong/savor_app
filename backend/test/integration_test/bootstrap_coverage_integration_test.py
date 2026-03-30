import importlib
import runpy
import sys

import pytest

from backend import create_app


def _write_temp_config(tmp_path, drop_on_startup):
    config_file = tmp_path / "temp_test_config.py"
    config_file.write_text(
        "SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost:5432/test_db'\n"
        "SQLALCHEMY_TRACK_MODIFICATIONS = False\n"
        f"DROP_DB_ON_STARTUP = {drop_on_startup}\n"
        "JWT_SECRET_KEY = 'jwt-test'\n"
        "SECRET_KEY = 'secret-test'\n"
    )
    return str(config_file)


def test_create_app_drop_db_on_startup_branch(tmp_path, mocker):
    config_path = _write_temp_config(tmp_path, True)

    mock_database_exists = mocker.patch("backend.database_exists", return_value=True)
    mock_drop_database = mocker.patch("backend.drop_database")
    mock_create_database = mocker.patch("backend.create_database")
    mocker.patch("backend.db_manager.db.init_app")
    mocker.patch("backend.db_manager.migrate.init_app")
    mocker.patch("backend.jwt_manager.jwt.init_app")
    mocker.patch("backend.create_table")

    create_app(config=config_path)

    mock_database_exists.assert_called_once()
    mock_drop_database.assert_called_once()
    mock_create_database.assert_called_once()


def test_create_app_create_db_when_missing_branch(tmp_path, mocker):
    config_path = _write_temp_config(tmp_path, False)

    mock_database_exists = mocker.patch("backend.database_exists", return_value=False)
    mock_create_database = mocker.patch("backend.create_database")
    mocker.patch("backend.db_manager.db.init_app")
    mocker.patch("backend.db_manager.migrate.init_app")
    mocker.patch("backend.jwt_manager.jwt.init_app")
    mocker.patch("backend.create_table")

    create_app(config=config_path)

    mock_database_exists.assert_called_once()
    mock_create_database.assert_called_once()


def _import_fresh_config_module():
    sys.modules.pop("backend.config", None)
    return importlib.import_module("backend.config")


def test_backend_config_load_failure_branch(mocker):
    mocker.patch("dotenv.load_dotenv", return_value=False)
    mocker.patch("builtins.print")
    mocker.patch("builtins.exit", side_effect=SystemExit(1))

    with pytest.raises(SystemExit):
        _import_fresh_config_module()


def test_backend_config_load_success_branch(mocker, monkeypatch):
    mocker.patch("dotenv.load_dotenv", return_value=True)
    mocker.patch("secrets.token_hex", side_effect=["s1", "s2"])

    monkeypatch.setenv("DB_USER", "user")
    monkeypatch.setenv("DB_PASSWORD", "pass")
    monkeypatch.setenv("DB_HOST", "127.0.0.1")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "db")

    config = _import_fresh_config_module()

    assert config.SQLALCHEMY_DATABASE_URI == "postgresql://user:pass@127.0.0.1:5432/db"


def test_backend_main_executes_entrypoint(mocker, monkeypatch):
    mock_app = mocker.MagicMock()
    mocker.patch("backend.create_app", return_value=mock_app)
    mocker.patch("dotenv.load_dotenv", return_value=True)

    monkeypatch.setattr(sys, "argv", ["main.py", "/tmp/.env"])
    monkeypatch.setenv("PORT", "5055")
    monkeypatch.setenv("FLASK_DEBUG", "0")
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.delenv("APP_CONFIG_PATH", raising=False)

    sys.modules.pop("backend.main", None)
    runpy.run_module("backend.main", run_name="__main__")

    mock_app.run.assert_called_once_with(port=5055, debug=False, host="127.0.0.1")
