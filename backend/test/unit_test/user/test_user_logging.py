"""
Unit tests for the _log function in user.py.
Tests structured logging with various log levels and field combinations.
"""
import logging
from unittest.mock import MagicMock


class TestUserLogFunction:
    """Test cases for _log function in user module"""

    def test_log_with_no_fields(self, app, mocker):
        """Test logging with event only, no fields"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("info", "Test event")

        mock_logger.log.assert_called_once_with(logging.INFO, "%s", "Test event")

    def test_log_with_single_field(self, app, mocker):
        """Test logging with event and one field"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("info", "Test event", user_id=123)

        mock_logger.log.assert_called_once_with(logging.INFO, "%s %s", "Test event", "user_id=123")

    def test_log_with_multiple_fields(self, app, mocker):
        """Test logging with event and multiple fields"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("info", "Test event", user_id=123, status_code=200, duration_ms=50)

        assert mock_logger.log.call_count == 1
        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.INFO
        assert call_args[0][1] == "%s %s"
        assert call_args[0][2] == "Test event"
        assert "user_id=123" in call_args[0][3]
        assert "status_code=200" in call_args[0][3]
        assert "duration_ms=50" in call_args[0][3]

    def test_log_debug_level(self, app, mocker):
        """Test logging at DEBUG level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("debug", "Debug event")

        mock_logger.log.assert_called_once_with(logging.DEBUG, "%s", "Debug event")

    def test_log_info_level(self, app, mocker):
        """Test logging at INFO level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("info", "Info event")

        mock_logger.log.assert_called_once_with(logging.INFO, "%s", "Info event")

    def test_log_warning_level(self, app, mocker):
        """Test logging at WARNING level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("warning", "Warning event")

        mock_logger.log.assert_called_once_with(logging.WARNING, "%s", "Warning event")

    def test_log_error_level(self, app, mocker):
        """Test logging at ERROR level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("error", "Error event")

        mock_logger.log.assert_called_once_with(logging.ERROR, "%s", "Error event")

    def test_log_critical_level(self, app, mocker):
        """Test logging at CRITICAL level"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("critical", "Critical event")

        mock_logger.log.assert_called_once_with(logging.CRITICAL, "%s", "Critical event")

    def test_log_case_insensitive(self, app, mocker):
        """Test that log level is case-insensitive"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("ERROR", "Test event")

        mock_logger.log.assert_called_once_with(logging.ERROR, "%s", "Test event")

    def test_log_invalid_level_defaults_to_info(self, app, mocker):
        """Test that invalid log level defaults to INFO"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("invalid_level", "Test event")

        mock_logger.log.assert_called_once_with(logging.INFO, "%s", "Test event")

    def test_log_with_email_field(self, app, mocker):
        """Test logging with email field"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("info", "User action", email="test@example.com")

        call_args = mock_logger.log.call_args
        assert "email=test@example.com" in call_args[0][3]

    def test_log_receive_login_request(self, app, mocker):
        """Test logging of receive login request event"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("info", "Receive request for /user/login", email="user@example.com")

        call_args = mock_logger.log.call_args
        assert "Receive request for /user/login" in call_args[0][2]
        assert "email=user@example.com" in call_args[0][3]

    def test_log_failed_login_validation(self, app, mocker):
        """Test logging of failed login validation"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("warning", "Fail to validate login parameters", has_email=False, has_password=True,
                 status_code=400, duration_ms=5)

        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.WARNING
        context = call_args[0][3]
        assert "has_email=False" in context
        assert "has_password=True" in context
        assert "status_code=400" in context

    def test_log_login_failed_nonexistent_email(self, app, mocker):
        """Test logging of login failure with non-existent email"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("warning", "Login failed with non-existent email", email="unknown@example.com")

        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.WARNING
        assert "Login failed with non-existent email" in call_args[0][2]

    def test_log_login_failed_invalid_password(self, app, mocker):
        """Test logging of login failure with invalid password"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("warning", "Login failed with invalid password", email="user@example.com")

        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.WARNING
        assert "Login failed with invalid password" in call_args[0][2]

    def test_log_login_successful(self, app, mocker):
        """Test logging of successful login"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("info", "Login successful", user_id=42, email="user@example.com")

        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.INFO
        context = call_args[0][3]
        assert "user_id=42" in context
        assert "email=user@example.com" in context

    def test_log_completed_login_request(self, app, mocker):
        """Test logging of completed login request"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("info", "Completed login request", user_id=1, status_code=200, duration_ms=50)

        call_args = mock_logger.log.call_args
        context = call_args[0][3]
        assert "user_id=1" in context
        assert "status_code=200" in context
        assert "duration_ms=50" in context

    def test_log_receive_create_user_request(self, app, mocker):
        """Test logging of receive create user request event"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("info", "Receive request for /user/create", email="newuser@example.com", username="newuser")

        call_args = mock_logger.log.call_args
        assert "Receive request for /user/create" in call_args[0][2]
        context = call_args[0][3]
        assert "email=newuser@example.com" in context
        assert "username=newuser" in context

    def test_log_failed_user_creation_validation(self, app, mocker):
        """Test logging of failed user creation validation"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("warning", "Fail to validate user creation parameters", has_email=True,
                 has_username=False, has_password=True, status_code=400, duration_ms=5)

        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.WARNING
        context = call_args[0][3]
        assert "has_email=True" in context
        assert "has_username=False" in context
        assert "has_password=True" in context
        assert "status_code=400" in context

    def test_log_email_already_exists_warning(self, app, mocker):
        """Test logging of email already exists warning"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("warning", "User creation failed because email already exists", email="existing@example.com",
                 status_code=409, duration_ms=20)

        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.WARNING
        context = call_args[0][3]
        assert "email=existing@example.com" in context
        assert "status_code=409" in context

    def test_log_user_created_successfully(self, app, mocker):
        """Test logging of successful user creation"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("info", "User created successfully", user_id=99, email="newuser@example.com",
                 status_code=201, duration_ms=100)

        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.INFO
        context = call_args[0][3]
        assert "user_id=99" in context
        assert "email=newuser@example.com" in context
        assert "status_code=201" in context

    def test_log_with_boolean_fields(self, app, mocker):
        """Test logging with boolean field values"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("warning", "Validation failed", has_email=True, has_password=False)

        call_args = mock_logger.log.call_args
        context = call_args[0][3]
        assert "has_email=True" in context
        assert "has_password=False" in context

    def test_log_returns_none(self, app, mocker):
        """Test that _log function returns None"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            result = _log("info", "Test event", user_id=1)

        assert result is None

    def test_log_early_return_when_no_fields(self, app, mocker):
        """Test that function returns early when no fields provided"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("info", "Test event")

        assert mock_logger.log.call_count == 1
        call_args = mock_logger.log.call_args
        assert len(call_args[0]) == 3

    def test_log_calls_context_join_with_fields(self, app, mocker):
        """Test that function joins fields into context string"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("info", "Test event", field1="value1", field2="value2")

        call_args = mock_logger.log.call_args
        assert len(call_args[0]) == 4
        context = call_args[0][3]
        assert isinstance(context, str)
        assert "field1=value1" in context
        assert "field2=value2" in context

    def test_log_with_numeric_status_codes(self, app, mocker):
        """Test logging with different HTTP status codes"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("info", "Request completed", status_code=200)

        call_args = mock_logger.log.call_args
        assert "status_code=200" in call_args[0][3]

    def test_log_with_all_login_fields(self, app, mocker):
        """Test logging with all login-related fields"""
        mock_logger = MagicMock()
        mocker.patch.object(app, 'logger', mock_logger)

        from backend.user import _log
        with app.app_context():
            _log("info", "Login event", user_id=5, email="test@example.com", status_code=200, duration_ms=75)

        call_args = mock_logger.log.call_args
        context = call_args[0][3]
        assert "user_id=5" in context
        assert "email=test@example.com" in context
        assert "status_code=200" in context
        assert "duration_ms=75" in context
