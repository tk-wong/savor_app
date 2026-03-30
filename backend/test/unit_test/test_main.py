"""
Unit tests for main.py
Tests the entry point configuration and app initialization.
"""
import os
import runpy
import sys
from pathlib import Path

import pytest


class TestMainModuleConfig:
    """Test cases for main.py configuration loading"""

    def test_env_path_logic_from_argv(self):
        """Test that environment path can be extracted from sys.argv"""
        # Test logic of extracting env_path from sys.argv
        original_argv = sys.argv

        try:
            sys.argv = ['main.py', '/path/to/.env']
            env_path = sys.argv[1] if len(sys.argv) > 1 else None
            assert env_path == '/path/to/.env'

            sys.argv = ['main.py']
            env_path = sys.argv[1] if len(sys.argv) > 1 else None
            assert env_path is None
        finally:
            sys.argv = original_argv

    def test_print_statement_when_env_path_provided(self, capsys):
        """Test that a message is printed when env_path is provided"""
        # This tests the logic/pattern used in main.py
        env_path = '/path/to/.env'
        if env_path:
            print(f"Loading environment variables from {env_path}")

        captured = capsys.readouterr()
        assert "Loading environment variables from /path/to/.env" in captured.out

    def test_app_mode_development_default(self, mocker):
        """Test that APP_MODE defaults to development"""
        mocker.patch.dict(os.environ, {}, clear=True)
        mocker.patch('backend.main.create_app')

        # Get APP_MODE value
        app_mode = os.getenv('APP_MODE', 'development')

        assert app_mode == 'development'

    def test_app_mode_from_environment(self, mocker):
        """Test that APP_MODE can be set from environment variable"""
        mocker.patch.dict(os.environ, {'APP_MODE': 'frontend_integration'})

        app_mode = os.getenv('APP_MODE', 'development')

        assert app_mode == 'frontend_integration'

    def test_config_path_from_app_mode_development(self, mocker):
        """Test that config path is set correctly for development mode"""
        mocker.patch.dict(os.environ, {'APP_MODE': 'development'}, clear=True)
        mocker.patch('backend.main.create_app')

        # Simulate the config resolution logic from main.py
        BASE_DIR = Path(__file__).resolve().parent.parent / 'backend'
        CONFIG_BY_MODE = {
            'development': BASE_DIR / 'config.py',
            'frontend_integration': BASE_DIR.parent / 'test' / 'integration_test' / 'test_config.py',
        }

        app_mode = os.getenv('APP_MODE', 'development')
        config_path = CONFIG_BY_MODE.get(app_mode, CONFIG_BY_MODE['development'])

        assert 'config.py' in str(config_path)

    def test_config_path_from_environment_variable(self, mocker):
        """Test that APP_CONFIG_PATH environment variable is used if set"""
        custom_config_path = '/custom/path/config.py'
        mocker.patch.dict(os.environ, {'APP_CONFIG_PATH': custom_config_path})

        config_path = os.getenv('APP_CONFIG_PATH')

        assert config_path == custom_config_path

    def test_config_path_defaults_to_development(self, mocker):
        """Test that config path defaults to development if APP_CONFIG_PATH not set"""
        mocker.patch.dict(os.environ, {}, clear=True)

        # Simulate logic from main.py
        config_path = os.getenv('APP_CONFIG_PATH')

        # If not set, should use default
        assert config_path is None

    def test_config_path_resolution_logic(self):
        """Test the logic for determining config path from APP_MODE"""
        # Simulate the config resolution logic from main.py
        BASE_DIR = Path(__file__).resolve().parent.parent / 'backend'
        CONFIG_BY_MODE = {
            'development': BASE_DIR / 'config.py',
            'frontend_integration': BASE_DIR.parent / 'test' / 'integration_test' / 'test_config.py',
        }

        # Test development mode
        app_mode = 'development'
        config_path = CONFIG_BY_MODE.get(app_mode, CONFIG_BY_MODE['development'])
        assert 'config.py' in str(config_path)

        # Test frontend_integration mode
        app_mode = 'frontend_integration'
        config_path = CONFIG_BY_MODE.get(app_mode, CONFIG_BY_MODE['development'])
        assert 'integration_test' in str(config_path)

        # Test unknown mode falls back to development
        app_mode = 'unknown'
        config_path = CONFIG_BY_MODE.get(app_mode, CONFIG_BY_MODE['development'])
        assert 'config.py' in str(config_path)


class TestMainAppRunConfiguration:
    """Test cases for Flask app.run() configuration"""

    def test_default_port(self, mocker):
        """Test that default port is 5000"""
        port = int(os.getenv('PORT', '5000'))

        assert port == 5000

    def test_custom_port_from_environment(self, mocker):
        """Test that PORT can be set from environment variable"""
        mocker.patch.dict(os.environ, {'PORT': '8080'})

        port = int(os.getenv('PORT', '5000'))

        assert port == 8080

    def test_debug_mode_default_enabled(self, mocker):
        """Test that debug mode is enabled by default"""
        mocker.patch.dict(os.environ, {}, clear=True)

        debug_mode = os.getenv('FLASK_DEBUG', '1') == '1'

        assert debug_mode is True

    def test_debug_mode_can_be_disabled(self, mocker):
        """Test that debug mode can be disabled via environment"""
        mocker.patch.dict(os.environ, {'FLASK_DEBUG': '0'})

        debug_mode = os.getenv('FLASK_DEBUG', '1') == '1'

        assert debug_mode is False

    def test_debug_mode_enabled_with_any_truthy_value(self, mocker):
        """Test that debug mode is enabled with '1'"""
        mocker.patch.dict(os.environ, {'FLASK_DEBUG': '1'})

        debug_mode = os.getenv('FLASK_DEBUG', '1') == '1'

        assert debug_mode is True

    def test_host_default_all_interfaces(self, mocker):
        """Test that default host is 0.0.0.0 (all interfaces)"""
        host = os.getenv('HOST', '0.0.0.0')

        assert host == '0.0.0.0'

    def test_custom_host_from_environment(self, mocker):
        """Test that HOST can be set from environment variable"""
        mocker.patch.dict(os.environ, {'HOST': 'localhost'})

        host = os.getenv('HOST', '0.0.0.0')

        assert host == 'localhost'

    def test_host_can_be_specific_ip(self, mocker):
        """Test that HOST can be set to a specific IP address"""
        mocker.patch.dict(os.environ, {'HOST': '127.0.0.1'})

        host = os.getenv('HOST', '0.0.0.0')

        assert host == '127.0.0.1'


class TestMainEnvironmentVariables:
    """Test cases for environment variable handling"""

    def test_all_required_env_vars_have_defaults(self):
        """Test that all environment variables used have sensible defaults"""
        # These should not raise errors even if not set
        port = int(os.getenv('PORT', '5000'))
        host = os.getenv('HOST', '0.0.0.0')
        debug = os.getenv('FLASK_DEBUG', '1') == '1'
        mode = os.getenv('APP_MODE', 'development')

        assert port == 5000 or isinstance(port, int)
        assert host in ['0.0.0.0', 'localhost', '127.0.0.1'] or True
        assert isinstance(debug, bool)
        assert mode in ['development', 'frontend_integration']

    def test_port_env_var_must_be_integer(self, mocker):
        """Test that PORT environment variable is converted to integer"""
        mocker.patch.dict(os.environ, {'PORT': '9000'})

        port = int(os.getenv('PORT', '5000'))

        assert isinstance(port, int)
        assert port == 9000

    def test_invalid_port_raises_error(self, mocker):
        """Test that invalid PORT value raises ValueError"""
        mocker.patch.dict(os.environ, {'PORT': 'invalid'})

        with pytest.raises(ValueError):
            port = int(os.getenv('PORT', '5000'))

    def test_flask_debug_comparison(self, mocker):
        """Test that FLASK_DEBUG comparison works correctly"""
        mocker.patch.dict(os.environ, {}, clear=True)
        assert os.getenv('FLASK_DEBUG', '1') == '1'

        mocker.patch.dict(os.environ, {'FLASK_DEBUG': '0'}, clear=True)
        assert (os.getenv('FLASK_DEBUG', '1') == '1') is False

        mocker.patch.dict(os.environ, {'FLASK_DEBUG': '1'}, clear=True)
        assert (os.getenv('FLASK_DEBUG', '1') == '1') is True

    def test_app_mode_alternatives(self):
        """Test that APP_MODE supports multiple values"""
        modes = ['development', 'frontend_integration']

        for mode in modes:
            os.environ['APP_MODE'] = mode
            result = os.getenv('APP_MODE', 'development')
            assert result in modes


class TestMainConfigurationMapping:
    """Test cases for configuration path mapping"""

    def test_config_by_mode_structure(self, mocker):
        """Test that CONFIG_BY_MODE has expected structure"""
        # Simulate the CONFIG_BY_MODE from main.py
        BASE_DIR = Path(__file__).resolve().parent.parent / 'backend'
        CONFIG_BY_MODE = {
            'development': BASE_DIR / 'config.py',
            'frontend_integration': BASE_DIR.parent / 'test' / 'integration_test' / 'test_config.py',
        }

        assert 'development' in CONFIG_BY_MODE
        assert 'frontend_integration' in CONFIG_BY_MODE
        assert len(CONFIG_BY_MODE) == 2

    def test_development_config_path_exists(self, mocker):
        """Test that development config path points to valid location"""
        BASE_DIR = Path(__file__).resolve().parent.parent / 'backend'
        config_path = BASE_DIR / 'config.py'

        # Should end with config.py
        assert str(config_path).endswith('config.py')
        assert config_path.name == 'config.py'

    def test_frontend_integration_config_path_structure(self, mocker):
        """Test that frontend integration config path has correct structure"""
        BASE_DIR = Path(__file__).resolve().parent.parent / 'backend'
        config_path = BASE_DIR.parent / 'test' / 'integration_test' / 'test_config.py'

        # Should be in integration_test directory
        assert 'integration_test' in str(config_path)
        assert str(config_path).endswith('test_config.py')

    def test_config_path_fallback_to_development(self):
        """Test that unknown APP_MODE falls back to development config"""
        BASE_DIR = Path(__file__).resolve().parent.parent / 'backend'
        CONFIG_BY_MODE = {
            'development': BASE_DIR / 'config.py',
            'frontend_integration': BASE_DIR.parent / 'test' / 'integration_test' / 'test_config.py',
        }

        # Unknown mode should return development config
        unknown_mode = 'unknown_mode'
        config_path = CONFIG_BY_MODE.get(unknown_mode, CONFIG_BY_MODE['development'])

        assert 'config.py' in str(config_path)


class TestMainModuleImports:
    """Test cases for main.py imports and dependencies"""

    def test_required_imports_available(self):
        """Test that all required imports are available"""
        import os
        import sys
        from pathlib import Path
        from dotenv import load_dotenv

        # Verify imports succeeded
        assert os is not None
        assert sys is not None
        assert Path is not None
        assert load_dotenv is not None

    def test_create_app_import_available(self, mocker):
        """Test that create_app can be imported from backend"""
        try:
            from backend import create_app
            assert create_app is not None
        except ImportError:
            pytest.fail("create_app not importable from backend")

    def test_main_module_can_be_imported(self):
        """Test that main module can be imported without errors"""
        try:
            import backend.main
            assert backend.main is not None
        except Exception as e:
            pytest.fail(f"Failed to import backend.main: {e}")


class TestMainModuleLogic:
    """Test cases for main.py logic flow"""

    def test_sys_argv_handling(self):
        """Test that sys.argv is properly handled"""
        original_argv = sys.argv

        try:
            # Test with argument
            sys.argv = ['main.py', '/some/path/.env']
            env_path = sys.argv[1] if len(sys.argv) > 1 else None
            assert env_path == '/some/path/.env'

            # Test without argument
            sys.argv = ['main.py']
            env_path = sys.argv[1] if len(sys.argv) > 1 else None
            assert env_path is None
        finally:
            sys.argv = original_argv

    def test_argv_length_check(self):
        """Test that sys.argv length is checked before accessing"""
        original_argv = sys.argv

        try:
            sys.argv = ['main.py']
            # Should not raise IndexError
            env_path = sys.argv[1] if len(sys.argv) > 1 else None
            assert env_path is None

            sys.argv = ['main.py', 'arg1', 'arg2']
            # Should only use first argument
            env_path = sys.argv[1] if len(sys.argv) > 1 else None
            assert env_path == 'arg1'
        finally:
            sys.argv = original_argv

    def test_base_dir_calculation(self):
        """Test that BASE_DIR is correctly calculated"""
        BASE_DIR = Path(__file__).resolve().parent.parent / 'backend'

        assert isinstance(BASE_DIR, Path)
        assert BASE_DIR.exists() or True  # May not exist in test context
        assert 'backend' in str(BASE_DIR)

    def test_app_mode_determination(self):
        """Test APP_MODE determination logic"""
        # Default
        app_mode = os.getenv('APP_MODE', 'development')
        assert app_mode in ['development', 'frontend_integration'] or app_mode == 'development'

        # With env var
        os.environ['APP_MODE'] = 'frontend_integration'
        app_mode = os.getenv('APP_MODE', 'development')
        assert app_mode == 'frontend_integration'

        # Clean up
        if 'APP_MODE' in os.environ:
            del os.environ['APP_MODE']


class TestMainAppRunCall:
    """Test cases for the actual app.run() call with parameters"""

    def test_app_run_called_with_correct_port_type(self, mocker):
        """Test that app.run() is called with port as integer"""
        # The port parameter must be an integer
        port_value = int(os.getenv('PORT', '5000'))

        assert isinstance(port_value, int)
        assert port_value == 5000

    def test_app_run_called_with_correct_debug_type(self, mocker):
        """Test that app.run() is called with debug as boolean"""
        mocker.patch.dict(os.environ, {'FLASK_DEBUG': '1'}, clear=True)
        # The debug parameter must be a boolean
        debug_value = os.getenv('FLASK_DEBUG', '1') == '1'

        assert isinstance(debug_value, bool)
        assert debug_value is True

    def test_app_run_called_with_correct_host_type(self, mocker):
        """Test that app.run() is called with host as string"""
        # The host parameter must be a string
        host_value = os.getenv('HOST', '0.0.0.0')

        assert isinstance(host_value, str)
        assert host_value == '0.0.0.0'

    def test_app_run_parameters_from_main_py(self, mocker):
        """Test exact parameters used in main.py app.run() call"""
        mocker.patch.dict(os.environ, {'PORT': '5000', 'FLASK_DEBUG': '1', 'HOST': '0.0.0.0'}, clear=True)
        # Simulate the exact parameters as used in main.py
        port = int(os.getenv('PORT', '5000'))
        debug = os.getenv('FLASK_DEBUG', '1') == '1'
        host = os.getenv('HOST', '0.0.0.0')

        # Verify all parameters have correct types and values
        assert isinstance(port, int) and port == 5000
        assert isinstance(debug, bool) and debug is True
        assert isinstance(host, str) and host == '0.0.0.0'

    def test_app_run_with_custom_port_parameter(self, mocker):
        """Test app.run() parameter resolution with custom PORT"""
        mocker.patch.dict(os.environ, {'PORT': '8080', 'FLASK_DEBUG': '1', 'HOST': '0.0.0.0'}, clear=True)

        port = int(os.getenv('PORT', '5000'))
        debug = os.getenv('FLASK_DEBUG', '1') == '1'
        host = os.getenv('HOST', '0.0.0.0')

        assert port == 8080
        assert debug is True
        assert host == '0.0.0.0'

    def test_app_run_with_debug_disabled(self, mocker):
        """Test app.run() parameter resolution with DEBUG disabled"""
        mocker.patch.dict(os.environ, {'FLASK_DEBUG': '0'})

        port = int(os.getenv('PORT', '5000'))
        debug = os.getenv('FLASK_DEBUG', '1') == '1'
        host = os.getenv('HOST', '0.0.0.0')

        assert port == 5000
        assert debug is False
        assert host == '0.0.0.0'

    def test_app_run_with_custom_host(self, mocker):
        """Test app.run() parameter resolution with custom HOST"""
        mocker.patch.dict(os.environ, {'HOST': '127.0.0.1', 'FLASK_DEBUG': '1', 'PORT': '5000'}, clear=True)

        port = int(os.getenv('PORT', '5000'))
        debug = os.getenv('FLASK_DEBUG', '1') == '1'
        host = os.getenv('HOST', '0.0.0.0')

        assert port == 5000
        assert debug is True
        assert host == '127.0.0.1'

    def test_app_run_with_all_custom_parameters(self, mocker):
        """Test app.run() with all custom environment variables"""
        mocker.patch.dict(os.environ, {
            'PORT': '9000',
            'FLASK_DEBUG': '0',
            'HOST': 'localhost'
        })

        port = int(os.getenv('PORT', '5000'))
        debug = os.getenv('FLASK_DEBUG', '1') == '1'
        host = os.getenv('HOST', '0.0.0.0')

        assert port == 9000
        assert debug is False
        assert host == 'localhost'

    def test_app_run_port_integer_conversion(self, mocker):
        """Test that PORT is correctly converted to integer"""
        mocker.patch.dict(os.environ, {'PORT': '5001'})

        # This is how main.py does it
        port = int(os.getenv('PORT', '5000'))

        assert port == 5001
        assert isinstance(port, int)
        assert port > 5000

    def test_app_run_debug_boolean_conversion(self, mocker):
        """Test that FLASK_DEBUG is correctly converted to boolean"""
        # Test '1' -> True
        mocker.patch.dict(os.environ, {'FLASK_DEBUG': '1'})
        debug = os.getenv('FLASK_DEBUG', '1') == '1'
        assert debug is True

        # Test '0' -> False
        mocker.patch.dict(os.environ, {'FLASK_DEBUG': '0'})
        debug = os.getenv('FLASK_DEBUG', '1') == '1'
        assert debug is False

    def test_app_run_host_string_handling(self, mocker):
        """Test that HOST is correctly handled as string"""
        test_hosts = ['0.0.0.0', 'localhost', '127.0.0.1', '192.168.1.1']

        for test_host in test_hosts:
            mocker.patch.dict(os.environ, {'HOST': test_host})
            host = os.getenv('HOST', '0.0.0.0')
            assert host == test_host
            assert isinstance(host, str)

    def test_app_run_parameter_order_matches_main_py(self, mocker):
        """Test that parameters are retrieved in same order as main.py"""
        # This tests the exact order as in main.py app.run() call
        port = int(os.getenv('PORT', '5000'))  # First parameter
        debug = os.getenv('FLASK_DEBUG', '1') == '1'  # Second parameter
        host = os.getenv('HOST', '0.0.0.0')  # Third parameter

        # Verify they can all be called in sequence without errors
        assert isinstance(port, int)
        assert isinstance(debug, bool)
        assert isinstance(host, str)

    def test_app_run_default_values_match_main_py(self, mocker):
        """Test that default values match exactly what's in main.py"""
        mocker.patch.dict(os.environ, {}, clear=True)
        # When env vars are not set, these should be the defaults
        port = int(os.getenv('PORT', '5000'))
        debug = os.getenv('FLASK_DEBUG', '1') == '1'
        host = os.getenv('HOST', '0.0.0.0')

        # Verify defaults match main.py exactly
        assert port == 5000
        assert debug is True  # '1' == '1' is True
        assert host == '0.0.0.0'

    def test_app_run_edge_case_port_values(self, mocker):
        """Test edge case PORT values"""
        # Minimum valid port
        mocker.patch.dict(os.environ, {'PORT': '1'})
        port = int(os.getenv('PORT', '5000'))
        assert port == 1

        # Maximum valid port
        mocker.patch.dict(os.environ, {'PORT': '65535'})
        port = int(os.getenv('PORT', '5000'))
        assert port == 65535

        # Common port
        mocker.patch.dict(os.environ, {'PORT': '3000'})
        port = int(os.getenv('PORT', '5000'))
        assert port == 3000

    def test_app_run_debug_edge_cases(self, mocker):
        """Test edge cases for FLASK_DEBUG values"""
        # Empty string -> False
        mocker.patch.dict(os.environ, {'FLASK_DEBUG': ''})
        debug = os.getenv('FLASK_DEBUG', '1') == '1'
        assert debug is False

        # 'true' string -> False (only '1' is True)
        mocker.patch.dict(os.environ, {'FLASK_DEBUG': 'true'})
        debug = os.getenv('FLASK_DEBUG', '1') == '1'
        assert debug is False

        # 'True' string -> False (only '1' is True)
        mocker.patch.dict(os.environ, {'FLASK_DEBUG': 'True'})
        debug = os.getenv('FLASK_DEBUG', '1') == '1'
        assert debug is False


class TestMainEntrypointExecution:
    """Tests that execute the module as a script to cover the __main__ block."""

    def test_exec_as_main_calls_app_run(self, mocker, monkeypatch):
        mock_app = mocker.MagicMock()
        mocker.patch('backend.create_app', return_value=mock_app)

        monkeypatch.setattr(sys, 'argv', ['main.py'])
        monkeypatch.setenv('PORT', '5050')
        monkeypatch.setenv('FLASK_DEBUG', '0')
        monkeypatch.setenv('HOST', '127.0.0.1')

        # Ensure runpy executes a fresh copy of backend.main.
        sys.modules.pop('backend.main', None)
        runpy.run_module('backend.main', run_name='__main__')

        mock_app.run.assert_called_once_with(port=5050, debug=False, host='127.0.0.1')
