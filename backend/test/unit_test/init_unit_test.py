import os

from flask import Flask

from backend import create_app


def test_create_app_returns_flask_instance(mocker):
    """Test that create_app returns a Flask app instance"""
    mocker.patch('backend.db_manager.db.init_app')
    mocker.patch('backend.database_exists', return_value=True)
    mocker.patch("backend.create_table")
    mocker.patch('backend.db_manager.migrate.init_app')
    mocker.patch('backend.jwt_manager.jwt.init_app')
    mocker.patch('backend.open')
    app = create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))
    assert isinstance(app, Flask)


def test_create_app_loads_config(mocker):
    """Test that create_app loads the correct configuration"""
    mocker.patch('backend.db_manager.db.init_app')
    mocker.patch('backend.database_exists', return_value=True)
    mocker.patch("backend.create_table")
    mocker.patch('backend.db_manager.migrate.init_app')
    mocker.patch('backend.jwt_manager.jwt.init_app')
    app = create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))
    assert app.config is not None


def test_db_init_app_called(mocker):
    """Test that db.init_app is called during app creation"""
    mock_db_init = mocker.patch('backend.db_manager.db.init_app')
    mocker.patch('backend.database_exists', return_value=True)
    mocker.patch('backend.db_manager.migrate.init_app')
    mocker.patch('backend.jwt_manager.jwt.init_app')
    mocker.patch("backend.create_table")
    create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))
    mock_db_init.assert_called_once()


def test_database_created_if_not_exists(mocker):
    """Test that create_database is called if database doesn't exist"""
    mock_create_db = mocker.patch('backend.create_database')
    mocker.patch('backend.database_exists', return_value=False)
    mocker.patch('backend.db_manager.db.init_app')
    mocker.patch('backend.db_manager.db.create_all')
    mocker.patch('backend.db_manager.migrate.init_app')
    mocker.patch('backend.jwt_manager.jwt.init_app')
    mocker.patch("backend.create_table")
    app = create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))
    mock_create_db.assert_called_once()


def test_database_not_created_if_exists(mocker):
    """Test that create_database is not called if database already exists"""
    mock_create_db = mocker.patch('sqlalchemy_utils.create_database')
    mocker.patch('backend.database_exists', return_value=True)
    mocker.patch('backend.db_manager.db.init_app')
    mocker.patch('backend.db_manager.db.create_all')
    mocker.patch('backend.db_manager.migrate.init_app')
    mocker.patch('backend.jwt_manager.jwt.init_app')

    app = create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))
    mock_create_db.assert_not_called()


def test_create_table_called(mocker):
    """Test that create_table is called during app creation"""
    mock_create_table = mocker.patch('backend.create_table')
    mocker.patch('backend.database_exists', return_value=True)
    mocker.patch('backend.db_manager.db.init_app')
    mocker.patch('backend.db_manager.migrate.init_app')
    mocker.patch('backend.jwt_manager.jwt.init_app')

    app = create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))
    mock_create_table.assert_called_once_with(app)


def test_migrate_init_app_called(mocker):
    """Test that migrate.init_app is called"""
    mock_migrate_init = mocker.patch('backend.db_manager.migrate.init_app')
    mocker.patch('backend.database_exists', return_value=True)
    mocker.patch('backend.db_manager.db.init_app')
    mocker.patch('backend.db_manager.db.create_all')
    mocker.patch('backend.jwt_manager.jwt.init_app')

    app = create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))
    mock_migrate_init.assert_called_once()


def test_api_blueprint_registered(mocker):
    """Test that API blueprint is registered"""
    mocker.patch('backend.database_exists', return_value=True)
    mocker.patch('backend.db_manager.db.init_app')
    mocker.patch('backend.db_manager.db.create_all')
    mocker.patch('backend.db_manager.migrate.init_app')
    mocker.patch('backend.jwt_manager.jwt.init_app')

    app = create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))
    # Check that the blueprint routes exist
    assert len(app.blueprints) > 0
    assert 'api' in app.blueprints


def test_jwt_init_app_called(mocker):
    """Test that JWT manager is initialized"""
    mock_jwt_init = mocker.patch('backend.jwt_manager.jwt.init_app')
    mocker.patch('backend.database_exists', return_value=True)
    mocker.patch('backend.db_manager.db.init_app')
    mocker.patch('backend.db_manager.db.create_all')
    mocker.patch('backend.db_manager.migrate.init_app')

    app = create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))
    mock_jwt_init.assert_called_once_with(app)


def test_static_folder_configured(mocker):
    """Test that static folder is properly configured"""
    mocker.patch('backend.database_exists', return_value=True)
    mocker.patch('backend.db_manager.db.init_app')
    mocker.patch('backend.db_manager.db.create_all')
    mocker.patch('backend.db_manager.migrate.init_app')
    mocker.patch('backend.jwt_manager.jwt.init_app')
    app = create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))
    assert app.static_folder == os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', "..", "backend", 'static'))
    assert '/api/static' in app.static_url_path


def test_create_table_creates_all_models(mocker):
    """Test that create_table calls db.create_all()"""
    mock_create_all = mocker.patch('backend.db_manager.db.create_all')
    mocker.patch('backend.database_exists', return_value=True)
    mocker.patch('backend.db_manager.db.init_app')
    mocker.patch('backend.db_manager.migrate.init_app')
    mocker.patch('backend.jwt_manager.jwt.init_app')

    app = create_app(config=os.path.join(os.path.dirname(__file__), "test_config.py"))
    mock_create_all.assert_called()
