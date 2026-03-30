"""Pytest configuration for recipe generation model tests."""

import os
import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables for integration testing."""
    # Load test-specific environment variables
    env_test_path = os.path.join(os.path.dirname(__file__), "..", ".env_test")
    if os.path.exists(env_test_path):
        load_dotenv(env_test_path)
    
    # Enable table dropping for integration tests
    os.environ["DROP_TABLES_ON_INIT"] = "true"
    yield
    # Cleanup can be added here if needed


@pytest.fixture
def enable_table_dropping(monkeypatch):
    """Fixture to enable table dropping for a specific test."""
    monkeypatch.setenv("DROP_TABLES_ON_INIT", "true")


@pytest.fixture
def disable_table_dropping(monkeypatch):
    """Fixture to disable table dropping for a specific test."""
    monkeypatch.setenv("DROP_TABLES_ON_INIT", "false")

