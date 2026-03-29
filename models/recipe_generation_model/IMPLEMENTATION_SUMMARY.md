# Integration Testing Table Dropping - Implementation Summary

## Changes Made

### 1. New Utility Module: `db_utils.py`
Created a new module that provides database utilities for table management during testing:

**Key Functions:**
- `should_drop_tables()` - Checks the environment variable
- `drop_tables(db_connection, table_names)` - Generic table dropping with CASCADE
- `drop_pgvector_collection(db_connection, collection_name)` - Drops vector embeddings
- `drop_chat_history_tables(db_connection, table_name)` - Drops chat history tables

### 2. Updated Files

#### `.env_dev` (Development Environment)
- Added `DROP_TABLES_ON_INIT=false` (default, no table dropping)

#### `.env_test` (New Test Environment)
- Created new configuration file with `DROP_TABLES_ON_INIT=true`
- Uses separate test database (`savor_db_test`)

#### `recipe_retriever.py`
- Added imports for database utilities
- Added logic to drop pgvector collection during `__init__` if `DROP_TABLES_ON_INIT=true`
- Re-creates embeddings after dropping

#### `recipe_assistant.py`
- Added imports for database utilities
- Added logic to drop chat history tables during `__init__` if `DROP_TABLES_ON_INIT=true`

#### `main.py`
- Added loading of `DROP_TABLES_ON_INIT` environment variable
- Variable available for passing to components if needed

#### `tests/conftest.py`
- Initialized pytest configuration with session-scoped fixture
- Sets `DROP_TABLES_ON_INIT=true` for all tests by default
- Provides `enable_table_dropping` and `disable_table_dropping` fixtures for fine-grained control

### 3. Documentation

#### `TABLE_DROPPING.md`
Comprehensive documentation covering:
- Overview and purpose
- Environment variable configuration
- Usage patterns (production vs testing)
- Implementation details
- Test setup instructions
- Safety considerations
- Troubleshooting guide

## How It Works

### Automatic Table Dropping

When `DROP_TABLES_ON_INIT=true`:

1. **RecipeRetriever initialization**:
   - Connects to database
   - Drops the pgvector collection "recipes" if it exists
   - Creates new empty PGVector instance
   - Re-populates embeddings from the dataset

2. **RecipeAssistant initialization**:
   - Drops chat history tables if they exist
   - New tables are created automatically as needed

### Environment Configuration

```
Development:      DROP_TABLES_ON_INIT=false (or unset)
Testing:          DROP_TABLES_ON_INIT=true
Production:       DROP_TABLES_ON_INIT=false
```

## Testing

### Running Tests with Table Dropping

```bash
# Tests automatically enable table dropping via conftest.py
pytest tests/

# Or explicitly with environment variable
DROP_TABLES_ON_INIT=true pytest tests/
```

### Per-Test Control

```python
# Drop tables for this test
def test_with_clean_db(enable_table_dropping):
    pass

# Don't drop tables for this test
def test_keep_data(disable_table_dropping):
    pass
```

## Safety Features

- ✅ Only drops tables when explicitly enabled via environment variable
- ✅ Default is `false` (no dropping) for safety
- ✅ Uses `CASCADE` to handle dependencies
- ✅ Catches and logs errors gracefully
- ✅ Separates test database from development/production

## Integration Points

All components integrate seamlessly:
- Environment variables control behavior
- Logging shows when tables are being dropped
- Error handling prevents crashes on drop failures
- Clean database state ensured for each test run

