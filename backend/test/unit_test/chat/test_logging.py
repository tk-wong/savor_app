"""
Unit tests for the _log function in chat.py.
Tests structured logging with various log levels and field combinations.
"""
import logging
from unittest.mock import MagicMock


class TestLogFunction:
    """Test cases for _log function"""

    def test_log_with_no_fields(self, app, mocker):
        """Test logging with event only, no fields"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "Test event")

        mock_logger.log.assert_called_once_with(logging.INFO, "%s", "Test event")

    def test_log_with_single_field(self, app, mocker):
        """Test logging with event and one field"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "Test event", user_id=123)

        mock_logger.log.assert_called_once_with(logging.INFO, "%s %s", "Test event", "user_id=123")

    def test_log_with_multiple_fields(self, app, mocker):
        """Test logging with event and multiple fields"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "Test event", user_id=123, chat_group_id=456, prompt_len=10)

        # Call should have the event and context string with all fields
        assert mock_logger.log.call_count == 1
        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.INFO
        assert call_args[0][1] == "%s %s"
        assert call_args[0][2] == "Test event"
        # Fields should be in the context string
        assert "user_id=123" in call_args[0][3]
        assert "chat_group_id=456" in call_args[0][3]
        assert "prompt_len=10" in call_args[0][3]

    def test_log_debug_level(self, app, mocker):
        """Test logging at DEBUG level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("debug", "Debug event")

        mock_logger.log.assert_called_once_with(logging.DEBUG, "%s", "Debug event")

    def test_log_info_level(self, app, mocker):
        """Test logging at INFO level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "Info event")

        mock_logger.log.assert_called_once_with(logging.INFO, "%s", "Info event")

    def test_log_warning_level(self, app, mocker):
        """Test logging at WARNING level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("warning", "Warning event")

        mock_logger.log.assert_called_once_with(logging.WARNING, "%s", "Warning event")

    def test_log_error_level(self, app, mocker):
        """Test logging at ERROR level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("error", "Error event")

        mock_logger.log.assert_called_once_with(logging.ERROR, "%s", "Error event")

    def test_log_critical_level(self, app, mocker):
        """Test logging at CRITICAL level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("critical", "Critical event")

        mock_logger.log.assert_called_once_with(logging.CRITICAL, "%s", "Critical event")

    def test_log_case_insensitive_debug(self, app, mocker):
        """Test that log level is case-insensitive for DEBUG"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("DEBUG", "Test event")

        mock_logger.log.assert_called_once_with(logging.DEBUG, "%s", "Test event")

    def test_log_case_insensitive_info(self, app, mocker):
        """Test that log level is case-insensitive for INFO"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("INFO", "Test event")

        mock_logger.log.assert_called_once_with(logging.INFO, "%s", "Test event")

    def test_log_case_insensitive_warning(self, app, mocker):
        """Test that log level is case-insensitive for WARNING"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("WARNING", "Test event")

        mock_logger.log.assert_called_once_with(logging.WARNING, "%s", "Test event")

    def test_log_case_insensitive_error(self, app, mocker):
        """Test that log level is case-insensitive for ERROR"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("ERROR", "Test event")

        mock_logger.log.assert_called_once_with(logging.ERROR, "%s", "Test event")

    def test_log_case_insensitive_critical(self, app, mocker):
        """Test that log level is case-insensitive for CRITICAL"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("CRITICAL", "Test event")

        mock_logger.log.assert_called_once_with(logging.CRITICAL, "%s", "Test event")

    def test_log_case_insensitive_mixed(self, app, mocker):
        """Test that log level is case-insensitive for mixed case"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("WaRnInG", "Test event")

        mock_logger.log.assert_called_once_with(logging.WARNING, "%s", "Test event")

    def test_log_invalid_level_defaults_to_info(self, app, mocker):
        """Test that invalid log level defaults to INFO"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("invalid_level", "Test event")

        mock_logger.log.assert_called_once_with(logging.INFO, "%s", "Test event")

    def test_log_with_string_field_value(self, app, mocker):
        """Test logging with string field values"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "User action", user_email="test@example.com")

        call_args = mock_logger.log.call_args
        assert "user_email=test@example.com" in call_args[0][3]

    def test_log_with_numeric_field_values(self, app, mocker):
        """Test logging with numeric field values"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "Metrics", user_id=123, duration_ms=456, count=789)

        call_args = mock_logger.log.call_args
        context = call_args[0][3]
        assert "user_id=123" in context
        assert "duration_ms=456" in context
        assert "count=789" in context

    def test_log_with_boolean_field_values(self, app, mocker):
        """Test logging with boolean field values"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "Status", is_active=True, is_deleted=False)

        call_args = mock_logger.log.call_args
        context = call_args[0][3]
        assert "is_active=True" in context
        assert "is_deleted=False" in context

    def test_log_with_none_field_value(self, app, mocker):
        """Test logging with None field value"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "Nullable field", value=None)

        call_args = mock_logger.log.call_args
        context = call_args[0][3]
        assert "value=None" in context

    def test_log_with_list_field_value(self, app, mocker):
        """Test logging with list field value"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "List data", ids=[1, 2, 3])

        call_args = mock_logger.log.call_args
        context = call_args[0][3]
        assert "ids=[1, 2, 3]" in context

    def test_log_event_with_special_characters(self, app, mocker):
        """Test logging event message with special characters"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "Special chars: !@#$%^&*()")

        mock_logger.log.assert_called_once_with(logging.INFO, "%s", "Special chars: !@#$%^&*()")

    def test_log_empty_event_message(self, app, mocker):
        """Test logging with empty event message"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "")

        mock_logger.log.assert_called_once_with(logging.INFO, "%s", "")

    def test_log_long_event_message(self, app, mocker):
        """Test logging with long event message"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        long_message = "x" * 1000
        from backend.chat import _log
        with app.app_context():
            _log("info", long_message)

        mock_logger.log.assert_called_once_with(logging.INFO, "%s", long_message)

    def test_log_with_field_name_with_underscores(self, app, mocker):
        """Test logging with field names containing underscores"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "Event", chat_group_id=1, recipe_ingredient_id=2, ai_model_name="gpt4")

        call_args = mock_logger.log.call_args
        context = call_args[0][3]
        assert "chat_group_id=1" in context
        assert "recipe_ingredient_id=2" in context
        assert "ai_model_name=gpt4" in context

    def test_log_field_values_with_special_characters(self, app, mocker):
        """Test logging field values containing special characters"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "Event", reason="error: timeout_or_connection", status="404_not_found")

        call_args = mock_logger.log.call_args
        context = call_args[0][3]
        assert "reason=error: timeout_or_connection" in context
        assert "status=404_not_found" in context

    def test_log_many_fields(self, app, mocker):
        """Test logging with many fields"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "Event",
                 user_id=1, chat_group_id=2, recipe_id=3, ingredient_id=4,
                 status_code=200, duration_ms=100, is_mock=True,
                 reason="success", model_name="gpt4", image_url="http://example.com/img.png")

        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.INFO
        assert call_args[0][1] == "%s %s"
        assert call_args[0][2] == "Event"
        context = call_args[0][3]
        # Verify all fields are present
        assert "user_id=1" in context
        assert "chat_group_id=2" in context
        assert "recipe_id=3" in context
        assert "ingredient_id=4" in context
        assert "status_code=200" in context
        assert "duration_ms=100" in context
        assert "is_mock=True" in context
        assert 'reason=success' in context
        assert 'model_name=gpt4' in context

    def test_log_returns_none(self, app, mocker):
        """Test that _log function returns None"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            result = _log("info", "Test event", user_id=1)

        assert result is None

    def test_log_with_fields_returns_none(self, app, mocker):
        """Test that _log function returns None even with fields"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            result = _log("error", "Error occurred", reason="timeout", duration=5000)

        assert result is None

    def test_log_early_return_when_no_fields(self, app, mocker):
        """Test that function returns early when no fields provided"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "Test event")

        # Should call log only once with event only (no context join)
        assert mock_logger.log.call_count == 1
        call_args = mock_logger.log.call_args
        # Should have 3 arguments: level, format_string, event
        assert len(call_args[0]) == 3

    def test_log_calls_context_join_with_fields(self, app, mocker):
        """Test that function joins fields into context string"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.chat import _log
        with app.app_context():
            _log("info", "Test event", field1="value1", field2="value2")

        # Should call log with 4 arguments: level, format_string, event, context
        call_args = mock_logger.log.call_args
        assert len(call_args[0]) == 4
        # Context should be a string with both fields
        context = call_args[0][3]
        assert isinstance(context, str)
        assert "field1=value1" in context
        assert "field2=value2" in context
