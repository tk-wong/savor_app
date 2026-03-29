# Table Dropping for Integration Testing

This document describes the functionality for dropping tables during integration testing.

## Overview

The recipe generation model includes a configurable mechanism to automatically drop database tables during initialization. This is useful for integration testing scenarios where you want a clean database state before each test run.

## Environment Variable

### `DROP_TABLES_ON_INIT`

Controls whether tables should be dropped when the application initializes.

- **Type**: Boolean (string: `"true"` or `"false"`)
- **Default**: `"false"`
- **Location**: Set in your `.env` file

**Example:**
```bash
DROP_TABLES_ON_INIT=true
```

## Affected Tables

When `DROP_TABLES_ON_INIT=true`, the following tables/collections are dropped during initialization:

1. **Vector Collection (recipes)**: The LangChain pgvector collection for recipe embeddings
2. **Chat History Table**: The PostgreSQL chat message history table (`llm_chat_history` by default)

## Usage

### Production (Default)

In production, set the environment variable to `false` or leave it unset:

```bash
# .env_prod
DROP_TABLES_ON_INIT=false
```

### Integration Testing

When running integration tests, enable table dropping:

```bash
# .env_test
DROP_TABLES_ON_INIT=true
```

## Configuration Files

- **`.env_dev`**: Development environment with `DROP_TABLES_ON_INIT=false`
- **`.env_test`**: Test environment with `DROP_TABLES_ON_INIT=true`

## Implementation Details

### Core Module: `db_utils.py`

The `db_utils.py` module provides utility functions for table management:

#### Functions

- **`should_drop_tables()`**: Checks if tables should be dropped based on the environment variable
- **`drop_tables(db_connection, table_names)`**: Drops specified tables with CASCADE support
- **`drop_pgvector_collection(db_connection, collection_name)`**: Drops the vector collection and associated embeddings
- **`drop_chat_history_tables(db_connection, table_name)`**: Drops chat history tables

### Integration Points

1. **RecipeRetriever (`recipe_retriever.py`)**:
   - Drops the vector collection during `__init__` if `DROP_TABLES_ON_INIT=true`
   - Re-creates embeddings when tables are dropped

2. **RecipeAssistant (`recipe_assistant.py`)**:
   - Drops chat history tables during `__init__` if `DROP_TABLES_ON_INIT=true`
   - Creates new tables as needed

3. **Main Application (`main.py`)**:
   - Loads the `DROP_TABLES_ON_INIT` environment variable
   - Passes configuration to components during initialization

## Test Setup

### Using pytest

The `tests/conftest.py` provides fixtures for controlling table dropping in tests:

```python
import pytest

# Enable table dropping for a specific test
def test_something(enable_table_dropping):
    # Tables will be dropped at initialization
    pass

# Disable table dropping for a specific test
def test_another(disable_table_dropping):
    # Tables will NOT be dropped at initialization
    pass
```

### Automatic Setup

By default, all tests in the test suite will have `DROP_TABLES_ON_INIT=true` set automatically via the session-scoped fixture in `conftest.py`.

## Safety Considerations

⚠️ **WARNING**: When `DROP_TABLES_ON_INIT=true`, all data in the affected tables will be permanently deleted!

- **Only use this in testing environments**
- Never enable in production
- Always verify your environment before running tests
- Consider using separate test databases

## Example Workflow

```bash
# Development (no table dropping)
export DROP_TABLES_ON_INIT=false
python main.py

# Integration Testing (with table dropping)
export DROP_TABLES_ON_INIT=true
pytest tests/

# Production (no table dropping)
export DROP_TABLES_ON_INIT=false
gunicorn main:app
```

## Troubleshooting

### Tables not being dropped

1. **Check the environment variable**: Ensure `DROP_TABLES_ON_INIT=true` is set
2. **Verify connectivity**: Ensure the database connection is working
3. **Check logs**: Look for error messages indicating why tables weren't dropped
4. **Manual verification**: Query the database to verify table status

### Connection errors during table dropping

If you see connection errors:

1. Verify database credentials in the environment file
2. Ensure the database server is running
3. Check database permissions for the connecting user

## See Also

- `db_utils.py`: Database utility functions
- `.env_dev`: Development environment configuration
- `.env_test`: Test environment configuration
- `tests/conftest.py`: Pytest configuration and fixtures

