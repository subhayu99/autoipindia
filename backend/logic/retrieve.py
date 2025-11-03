from datetime import datetime

import pandas as pd
from pydantic import BaseModel, field_validator
from sqlalchemy import text

from db import engine
from config import TRADEMARKS_STATUS_FQN, TRADEMARKS_FAILED_FQN, LOG_LEVEL
from logger import setup_logger

# Set up logger for this module
logger = setup_logger(__name__, LOG_LEVEL)


class TrademarkWithStatus(BaseModel):
    application_number: str
    wordmark: str | None
    class_name: str | None
    status: str
    timestamp: datetime
    
    @field_validator("status")
    def keep_only_first_word(cls, v: str):
        return v.split()[0]
    
    @classmethod
    def from_dict(cls, d: dict) -> 'TrademarkWithStatus':
        return cls(
            application_number=d.get("application_number"),
            wordmark=d.get("wordmark"),
            class_name=d.get("class_name"),
            status=d.get("status"),
            timestamp=d.get("timestamp")
        )
        
    def to_dict(self) -> dict:
        return {
            "application_number": self.application_number,
            "wordmark": self.wordmark,
            "class_name": self.class_name,
            "status": self.status,
            "timestamp": self.timestamp
        }

    @classmethod
    def get_all(cls, as_df=False):
        query = f"""
            SELECT * FROM {TRADEMARKS_STATUS_FQN}
            QUALIFY ROW_NUMBER() OVER (PARTITION BY application_number ORDER BY timestamp DESC) = 1
        """
        try:
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
        except Exception as e:
            logger.error(f"Error while getting all trademarks with status: {str(e)}", exc_info=True)
            df = pd.DataFrame()

        logger.info(f"Found {df.shape[0]} trademarks with status")
        return df if as_df else [cls.from_dict(x) for x in df.to_dict(orient="records")]

    @classmethod
    def get_by_application_number(cls, application_number: str):
        query = f"""
            SELECT * FROM {TRADEMARKS_STATUS_FQN}
            WHERE CAST(application_number AS STRING) = '{application_number}'
            QUALIFY ROW_NUMBER() OVER (PARTITION BY application_number ORDER BY timestamp DESC) = 1
        """
        try:
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
        except Exception as e:
            logger.error(f"Error while getting trademark for application number {application_number}: {str(e)}", exc_info=True)
            df = pd.DataFrame()
        
        if not df.empty:
            return cls.from_dict(df.iloc[0].to_dict())
        else:
            return None

    @classmethod
    def get_by_wordmark_and_class(cls, wordmark: str, class_name: str):
        query = f"""
            SELECT * FROM {TRADEMARKS_STATUS_FQN}
            WHERE CAST(wordmark AS STRING) = '{wordmark}' AND CAST(class_name AS STRING) = '{class_name}'
            QUALIFY ROW_NUMBER() OVER (PARTITION BY application_number ORDER BY timestamp DESC) = 1
        """
        try:
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
        except Exception as e:
            logger.error(f"Error while getting trademark for wordmark {wordmark} and class {class_name}: {str(e)}", exc_info=True)
            df = pd.DataFrame()
        
        if not df.empty:
            return cls.from_dict(df.iloc[0].to_dict())
        else:
            return None
    
    def delete_by_application_number(self):
        d = {}
        query = f"""
            DELETE FROM {TRADEMARKS_STATUS_FQN}
            WHERE CAST(application_number AS STRING) = '{self.application_number}'
        """
        try:
            with engine.connect() as conn:
                conn.execute(query)
            d[TRADEMARKS_STATUS_FQN] = True
        except Exception as e:
            logger.error(f"Error while deleting trademark for application number {self.application_number}: {str(e)}", exc_info=True)
            d[TRADEMARKS_STATUS_FQN] = False

        query = f"""
            DELETE FROM {TRADEMARKS_FAILED_FQN}
            WHERE CAST(application_number AS STRING) = '{self.application_number}'
        """
        try:
            with engine.connect() as conn:
                conn.execute(query)
            d[TRADEMARKS_FAILED_FQN] = True
        except Exception as e:
            logger.error(f"Error while deleting failed trademark for application number {self.application_number}: {str(e)}", exc_info=True)
            d[TRADEMARKS_FAILED_FQN] = False
        
        return d
    
    @classmethod
    def get_history_by_application_number(cls, application_number: str) -> list['TrademarkWithStatus']:
        query = f"""
            WITH combined AS (
                SELECT application_number, wordmark, class_name, status, timestamp FROM {TRADEMARKS_STATUS_FQN}
                UNION ALL
                SELECT application_number, wordmark, class_name, '!FAILED' AS status, timestamp FROM {TRADEMARKS_FAILED_FQN}
            )
            SELECT * FROM combined
            WHERE application_number = '{application_number}'
            ORDER BY timestamp DESC
        """
        try:
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
            return [cls.from_dict(x) for x in df.to_dict(orient="records")]
        except Exception as e:
            logger.error(f"Error while getting trademark history for application number {application_number}: {str(e)}", exc_info=True)
            return []

    def get_history(self):
        return self.get_history_by_application_number(self.application_number)

    @classmethod
    def get_paginated_with_filters(
        cls,
        page: int = 1,
        page_size: int = 50,
        wordmark: str = None,
        class_name: str = None,
        status: str = None,
        application_number: str = None,
        as_df: bool = False
    ):
        """
        Get paginated trademarks with optional filters.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            wordmark: Filter by wordmark (partial match)
            class_name: Filter by class name (exact match)
            status: Filter by status (partial match)
            application_number: Filter by application number (partial match)
            as_df: Return as DataFrame if True, else list of objects

        Returns:
            Dictionary with paginated results and metadata
        """
        # Build WHERE clauses
        where_clauses = []
        if wordmark:
            where_clauses.append(f"LOWER(CAST(wordmark AS STRING)) LIKE LOWER('%{wordmark}%')")
        if class_name:
            where_clauses.append(f"CAST(class_name AS STRING) = '{class_name}'")
        if status:
            where_clauses.append(f"LOWER(CAST(status AS STRING)) LIKE LOWER('%{status}%')")
        if application_number:
            where_clauses.append(f"CAST(application_number AS STRING) LIKE '%{application_number}%'")

        where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Calculate offset
        offset = (page - 1) * page_size

        # Get total count
        count_query = f"""
            WITH deduped AS (
                SELECT * FROM {TRADEMARKS_STATUS_FQN}
                QUALIFY ROW_NUMBER() OVER (PARTITION BY application_number ORDER BY timestamp DESC) = 1
            )
            SELECT COUNT(*) as total FROM deduped
            {where_clause}
        """

        # Get paginated data
        data_query = f"""
            WITH deduped AS (
                SELECT * FROM {TRADEMARKS_STATUS_FQN}
                QUALIFY ROW_NUMBER() OVER (PARTITION BY application_number ORDER BY timestamp DESC) = 1
            )
            SELECT * FROM deduped
            {where_clause}
            ORDER BY timestamp DESC
            LIMIT {page_size} OFFSET {offset}
        """

        try:
            with engine.connect() as conn:
                # Get total count
                count_df = pd.read_sql(count_query, conn)
                total = int(count_df.iloc[0]['total']) if not count_df.empty else 0

                # Get paginated data
                df = pd.read_sql(data_query, conn)

            logger.info(f"Retrieved page {page} with {len(df)} trademarks (total: {total})")

            total_pages = (total + page_size - 1) // page_size if total > 0 else 0

            result = {
                "data": df if as_df else [cls.from_dict(x) for x in df.to_dict(orient="records")],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }

            return result

        except Exception as e:
            logger.error(f"Error while getting paginated trademarks: {str(e)}", exc_info=True)
            return {
                "data": [] if not as_df else pd.DataFrame(),
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_prev": False
                }
            }

    @classmethod
    def bulk_delete_by_application_numbers(cls, application_numbers: list[str]) -> dict:
        """
        Bulk delete trademarks by application numbers.

        Args:
            application_numbers: List of application numbers to delete

        Returns:
            Dictionary with success/failure counts
        """
        if not application_numbers:
            return {"deleted": 0, "failed": 0, "errors": []}

        logger.info(f"Bulk deleting {len(application_numbers)} trademarks")

        deleted_count = 0
        failed_count = 0
        errors = []

        # Use parameterized query to prevent SQL injection
        app_numbers_str = "', '".join([str(num).replace("'", "''") for num in application_numbers])

        # Delete from trademark_status table
        query_status = text(f"""
            DELETE FROM {TRADEMARKS_STATUS_FQN}
            WHERE CAST(application_number AS STRING) IN ('{app_numbers_str}')
        """)

        # Delete from failed_trademarks table
        query_failed = text(f"""
            DELETE FROM {TRADEMARKS_FAILED_FQN}
            WHERE CAST(application_number AS STRING) IN ('{app_numbers_str}')
        """)

        try:
            with engine.connect() as conn:
                # Delete from both tables
                result_status = conn.execute(query_status)
                result_failed = conn.execute(query_failed)
                conn.commit()

                deleted_count = len(application_numbers)
                logger.info(f"Successfully deleted {deleted_count} trademarks")

        except Exception as e:
            failed_count = len(application_numbers)
            error_msg = f"Error during bulk delete: {str(e)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)

        return {
            "deleted": deleted_count,
            "failed": failed_count,
            "errors": errors
        }
