from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from typing import List, Dict, Any

# Create a sync SQLAlchemy engine connection pool
# pool_pre_ping=True automatically tests connections before using them to prevent dead drops
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

def execute_read_only_query(sql_string: str) -> List[Dict[str, Any]]:
    """
    Executes an AI-generated SQL string against the database safely.
    Converts result rows automatically into standard dictionaries.
    """
    # Wrap execution inside a context manager to guarantee connection closing
    with engine.connect() as connection:
        try:
            # Bind the raw string to a secure, text-executable object
            result = connection.execute(text(sql_string))
            
            # If the query yields row outputs (like a SELECT statement)
            if result.returns_rows:
                # Convert rows into clear key-value dictionaries mapping: column_name -> value
                return [dict(row._mapping) for row in result.fetchall()]
            
            return []
            
        except SQLAlchemyError as db_error:
            # Re-raise the exact Postgres engine error so our agent's self-healing loop can read it
            raise db_error