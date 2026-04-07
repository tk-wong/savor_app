"""Database utility functions for managing tables during testing."""

import os
import psycopg
from typing import Optional


def should_drop_tables() -> bool:
    """Check if tables should be dropped on initialization.

    Returns:
        bool: True if DROP_TABLES_ON_INIT environment variable is set to 'true'
    """
    return os.getenv("DROP_TABLES_ON_INIT", "false").lower() == "true"


def drop_tables(db_connection: psycopg.Connection, table_names: list[str]) -> None:
    """Drop specified tables from the database.

    Args:
        db_connection: PostgreSQL connection object
        table_names: List of table names to drop
    """
    if not should_drop_tables():
        return

    try:
        cursor = db_connection.cursor()
        for table_name in table_names:
            # Use CASCADE to drop dependent objects
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        raise Exception(f"Error dropping tables: {e}")


def drop_pgvector_collection(db_connection: psycopg.Connection, collection_name: str = "recipes") -> None:
    """Drop the pgvector collection table if DROP_TABLES_ON_INIT is enabled.

    Args:
        db_connection: PostgreSQL connection object
        collection_name: Name of the collection to drop
    """
    if not should_drop_tables():
        return

    try:
        cursor = db_connection.cursor()
        # Remove vector rows tied to the target collection, then remove collection metadata.
        cursor.execute(f"""
            DELETE FROM langchain_pg_embedding 
            WHERE collection_id IN (
                SELECT uuid FROM langchain_pg_collection WHERE name = %s
            );
        """, (collection_name,))
        cursor.execute(
            "DELETE FROM langchain_pg_collection WHERE name = %s;",
            (collection_name,),
        )
        db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        raise Exception(f"Error dropping pgvector collection: {e}")


def drop_chat_history_tables(db_connection: psycopg.Connection, table_name: str = "llm_chat_history") -> None:
    """Drop chat history related tables if DROP_TABLES_ON_INIT is enabled.

    Args:
        db_connection: PostgreSQL connection object
        table_name: Name of the chat history table to drop
    """
    if not should_drop_tables():
        return

    try:
        cursor = db_connection.cursor()
        # Drop the chat history table
        cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        raise Exception(f"Error dropping chat history tables: {e}")
