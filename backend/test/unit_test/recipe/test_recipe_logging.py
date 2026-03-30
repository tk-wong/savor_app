"""
Unit tests for the _log function in recipe.py.
Tests structured logging with various log levels and field combinations.
"""
import logging
from unittest.mock import MagicMock


class TestRecipeLogFunction:
    """Test cases for _log function in recipe module"""

    def test_log_with_no_fields(self, app, mocker):
        """Test logging with event only, no fields"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("info", "Test event")

        mock_logger.log.assert_called_once_with(logging.INFO, "%s", "Test event")

    def test_log_with_single_field(self, app, mocker):
        """Test logging with event and one field"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("info", "Test event", user_id=123)

        mock_logger.log.assert_called_once_with(logging.INFO, "%s %s", "Test event", "user_id=123")

    def test_log_with_multiple_fields(self, app, mocker):
        """Test logging with event and multiple fields"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("info", "Test event", user_id=123, recipe_id=456, ingredient_count=10)

        assert mock_logger.log.call_count == 1
        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.INFO
        assert call_args[0][1] == "%s %s"
        assert call_args[0][2] == "Test event"
        assert "user_id=123" in call_args[0][3]
        assert "recipe_id=456" in call_args[0][3]
        assert "ingredient_count=10" in call_args[0][3]

    def test_log_debug_level(self, app, mocker):
        """Test logging at DEBUG level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("debug", "Debug event")

        mock_logger.log.assert_called_once_with(logging.DEBUG, "%s", "Debug event")

    def test_log_info_level(self, app, mocker):
        """Test logging at INFO level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("info", "Info event")

        mock_logger.log.assert_called_once_with(logging.INFO, "%s", "Info event")

    def test_log_warning_level(self, app, mocker):
        """Test logging at WARNING level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("warning", "Warning event")

        mock_logger.log.assert_called_once_with(logging.WARNING, "%s", "Warning event")

    def test_log_error_level(self, app, mocker):
        """Test logging at ERROR level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("error", "Error event")

        mock_logger.log.assert_called_once_with(logging.ERROR, "%s", "Error event")

    def test_log_critical_level(self, app, mocker):
        """Test logging at CRITICAL level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("critical", "Critical event")

        mock_logger.log.assert_called_once_with(logging.CRITICAL, "%s", "Critical event")

    def test_log_case_insensitive(self, app, mocker):
        """Test that log level is case-insensitive"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("WARNING", "Test event")

        mock_logger.log.assert_called_once_with(logging.WARNING, "%s", "Test event")

    def test_log_invalid_level_defaults_to_info(self, app, mocker):
        """Test that invalid log level defaults to INFO"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("invalid_level", "Test event")

        mock_logger.log.assert_called_once_with(logging.INFO, "%s", "Test event")

    def test_log_with_recipe_specific_fields(self, app, mocker):
        """Test logging with recipe-specific fields"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("info", "Recipe fetched", user_id=1, recipe_id=10, ingredient_count=5, status_code=200)

        call_args = mock_logger.log.call_args
        context = call_args[0][3]
        assert "user_id=1" in context
        assert "recipe_id=10" in context
        assert "ingredient_count=5" in context
        assert "status_code=200" in context

    def test_log_with_duration_field(self, app, mocker):
        """Test logging with duration_ms field"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("info", "Request completed", duration_ms=150)

        call_args = mock_logger.log.call_args
        assert "duration_ms=150" in call_args[0][3]

    def test_log_receive_request_event(self, app, mocker):
        """Test logging of receive request events"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("info", "Receive request for /recipes", user_id=1)

        call_args = mock_logger.log.call_args
        assert "Receive request for /recipes" in call_args[0][2]
        assert "user_id=1" in call_args[0][3]

    def test_log_completed_listing_recipes_event(self, app, mocker):
        """Test logging of completed listing recipes event"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("info", "Completed listing recipes", user_id=1, recipe_count=5, status_code=200, duration_ms=50)

        call_args = mock_logger.log.call_args
        context = call_args[0][3]
        assert "user_id=1" in context
        assert "recipe_count=5" in context
        assert "status_code=200" in context
        assert "duration_ms=50" in context

    def test_log_recipe_not_found_warning(self, app, mocker):
        """Test logging of recipe not found warning"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("warning", "Recipe not found", user_id=1, recipe_id=999, status_code=404, duration_ms=10)

        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.WARNING
        context = call_args[0][3]
        assert "user_id=1" in context
        assert "recipe_id=999" in context
        assert "status_code=404" in context

    def test_log_with_numeric_fields(self, app, mocker):
        """Test logging with various numeric field values"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("info", "Metrics", user_id=123, recipe_id=456, ingredient_count=789, status_code=200)

        call_args = mock_logger.log.call_args
        context = call_args[0][3]
        assert "user_id=123" in context
        assert "recipe_id=456" in context
        assert "ingredient_count=789" in context
        assert "status_code=200" in context

    def test_log_returns_none(self, app, mocker):
        """Test that _log function returns None"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            result = _log("info", "Test event", user_id=1)

        assert result is None

    def test_log_early_return_when_no_fields(self, app, mocker):
        """Test that function returns early when no fields provided"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("info", "Test event")

        assert mock_logger.log.call_count == 1
        call_args = mock_logger.log.call_args
        assert len(call_args[0]) == 3

    def test_log_calls_context_join_with_fields(self, app, mocker):
        """Test that function joins fields into context string"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.recipe import _log
        with app.app_context():
            _log("info", "Test event", field1="value1", field2="value2")

        call_args = mock_logger.log.call_args
        assert len(call_args[0]) == 4
        context = call_args[0][3]
        assert isinstance(context, str)
        assert "field1=value1" in context
        assert "field2=value2" in context
