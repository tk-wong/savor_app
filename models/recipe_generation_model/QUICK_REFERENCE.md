# Quick Reference: Table Dropping Feature

## What Was Added

A complete table dropping mechanism for integration testing with environment variable control.

## Files Created/Modified

### New Files:
- ✅ `db_utils.py` - Database utility module with dropping functions
- ✅ `.env_test` - Test environment configuration
- ✅ `TABLE_DROPPING.md` - Comprehensive documentation
- ✅ `IMPLEMENTATION_SUMMARY.md` - Implementation details
- ✅ `tests/test_table_dropping_example.py` - Example tests

### Modified Files:
- ✅ `.env_dev` - Added `DROP_TABLES_ON_INIT=false`
- ✅ `recipe_retriever.py` - Added table dropping logic
- ✅ `recipe_assistant.py` - Added table dropping logic
- ✅ `main.py` - Added environment variable loading
- ✅ `tests/conftest.py` - Added pytest fixtures

## Quick Start

### Development (No Table Dropping)
```bash
# Use .env_dev (default)
python main.py
```

### Integration Testing (With Table Dropping)
```bash
# Tables are automatically dropped during test initialization
pytest tests/

# Or explicitly enable
export DROP_TABLES_ON_INIT=true
pytest tests/
```

### Production
```bash
# Make sure DROP_TABLES_ON_INIT=false
export DROP_TABLES_ON_INIT=false
gunicorn main:app
```

## Environment Variable

**`DROP_TABLES_ON_INIT`** (String: "true" or "false")

- Default: `"false"`
- When `"true"`: Drops pgvector collection and chat history tables on initialization
- When `"false"`: Preserves existing tables

## Core Functions (db_utils.py)

```python
# Check if tables should be dropped
from db_utils import should_drop_tables
if should_drop_tables():
    print("Tables will be dropped")

# Drop specific tables
from db_utils import drop_tables
drop_tables(db_connection, ["table1", "table2"])

# Drop pgvector collection
from db_utils import drop_pgvector_collection
drop_pgvector_collection(db_connection, "recipes")

# Drop chat history
from db_utils import drop_chat_history_tables
drop_chat_history_tables(db_connection, "llm_chat_history")
```

## Using Fixtures in Tests

```python
# Enable table dropping for this test
def test_fresh_data(enable_table_dropping):
    # DROP_TABLES_ON_INIT=true for this test
    pass

# Disable table dropping for this test
def test_preserve_data(disable_table_dropping):
    # DROP_TABLES_ON_INIT=false for this test
    pass

# All tests automatically enable table dropping via session fixture
def test_any_integration_test():
    # DROP_TABLES_ON_INIT=true (from conftest.py)
    pass
```

## What Gets Dropped

1. **PGVector Collection** (`recipes`)
   - All vector embeddings
   - Metadata associated with embeddings
   - Automatically recreated from dataset

2. **Chat History Table** (`llm_chat_history`)
   - All message history
   - Session information
   - Recreated as needed

## Safety Features

✅ Defaults to `false` (safe)
✅ Requires explicit enable
✅ Separate test database configuration
✅ Error handling and logging
✅ Idempotent operations (safe to run multiple times)

## Troubleshooting

### Tables not being dropped
1. Check: `echo $DROP_TABLES_ON_INIT`
2. Verify database connection
3. Check application logs for errors

### Connection refused
1. Ensure PostgreSQL is running
2. Verify database credentials in .env file
3. Check database host and port

### Permission denied
1. Verify database user has DROP privileges
2. Check database role permissions

## See Also

- `TABLE_DROPPING.md` - Full documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `tests/test_table_dropping_example.py` - Example tests
- `db_utils.py` - Source code

