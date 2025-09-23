import duckdb
from sqlalchemy import create_engine
from contextlib import contextmanager

from config import DATABASE_URL, DATABASE_PROTOCOL


engine = create_engine(f"{DATABASE_PROTOCOL}{DATABASE_URL}")


class DatabaseConnection:
    """Singleton database connection manager"""
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def get_connection(self):
        """Get database connection"""
        if self._connection is None:
            self._connection = duckdb.connect(DATABASE_URL)
            # Install and load httpfs for potential remote operations
            try:
                self._connection.execute("INSTALL httpfs;")
                self._connection.execute("LOAD httpfs;")
            except Exception:
                pass  # httpfs might already be installed
        return self._connection
    
    def close_connection(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    db_manager = DatabaseConnection()
    conn = db_manager.get_connection()
    try:
        yield conn
    finally:
        # Don't close connection here as it's managed by singleton
        pass
