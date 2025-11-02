from datetime import datetime

import pandas as pd
from pytz import timezone
from sqlalchemy import text

from db import engine
from helpers.utils import run_parallel_exec
from logic.trademark_search import TrademarkSearchParams
from config import CAPTCHA_MAX_RETRIES, TRADEMARKS_FAILED_FQN, TRADEMARKS_STATUS_FQN, TRADEMARKS_STATUS_TABLE_NAME, TRADEMARKS_FAILED_TABLE_NAME


def create_tables_if_not_exists():
    with engine.connect() as conn:
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {TRADEMARKS_STATUS_TABLE_NAME} (
                application_number VARCHAR, 
                wordmark VARCHAR, 
                class_name VARCHAR, 
                status VARCHAR, 
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {TRADEMARKS_FAILED_TABLE_NAME} (
                wordmark VARCHAR, 
                class_name VARCHAR, 
                application_number VARCHAR, 
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

# Create tables if they don't exist
create_tables_if_not_exists()


def _write_failed_to_db(trademark: TrademarkSearchParams):
    print(f"Writing failed trademark search to database: {trademark.to_dict()}")
    failed_df = pd.DataFrame([trademark.to_dict()])
    failed_df["timestamp"] = datetime.now(tz=timezone("Asia/Kolkata"))
    with engine.connect() as conn:
        failed_df.to_sql("failed_trademarks", conn, index=False, if_exists="append")
    print("Wrote failed trademark search to database successfully")


def get_trademark_status(trademark: TrademarkSearchParams, headless: bool = True, write_to_db: bool = True) -> dict | None:
    """
    Get trademark status from database or online search
    """
    try:
        df = trademark.search(headless=headless, max_retries=CAPTCHA_MAX_RETRIES)
        
        if df is not None and not df.empty:
            if not write_to_db:
                print(f"Returning trademark status: {df.iloc[0].to_dict()}")
                return df.iloc[0].to_dict()
    
            if isinstance(df, str):
                _write_failed_to_db(trademark)
                return None
            
            print(f"Writing trademark status to database: {df}")
            df["timestamp"] = datetime.now(tz=timezone("Asia/Kolkata"))
            with engine.connect() as conn:
                df.to_sql("trademark_status", conn, index=False, if_exists="append")
            print("Wrote trademark status to database successfully")
            return df.iloc[0].to_dict()
    
    except Exception as e:
        print(f"An error occurred while searching for trademark status: {str(e)}")
        
        if write_to_db:
            _write_failed_to_db(trademark)
        
        return None


def ingest_trademark_status(trademarks: list[TrademarkSearchParams], max_workers: int = 10, headless: bool = True, write_each_to_db: bool = True):
    """Ingest trademarks into database"""
    
    if not trademarks:
        raise ValueError("trademarks list cannot be empty")
    
    tm_status_map: list[tuple[TrademarkSearchParams, dict | None]] = []
    
    try:
        print(f"Starting ingestion of {len(trademarks)} trademarks with {max_workers} workers")
        tm_status_map = run_parallel_exec(
            get_trademark_status, trademarks, headless, write_each_to_db, max_workers=max_workers,
        )
    except Exception as e:
        print(f"An error occurred while ingesting trademarks: {str(e)}")
        return {"success": 0, "failed": len(trademarks)}
    
    successful: list[dict] = []
    failed_tms: list[dict] = []
    
    for tm_status in tm_status_map:
        if tm_status[1] is not None:
            successful.append(tm_status[1])
        else:
            failed_tms.append(tm_status[0].to_dict())
    
    print(f"Finished ingestion of {len(trademarks)} trademarks")
    print(f"✅ Successfully ingested {len(successful)} trademarks")
    print(f"❌ Failed to ingest {len(failed_tms)} trademarks")
    
    if not write_each_to_db:
        current_time = datetime.now(tz=timezone("Asia/Kolkata"))

        df_success = pd.DataFrame(successful)
        df_success["timestamp"] = current_time

        df_failed = pd.DataFrame(failed_tms)
        df_failed["timestamp"] = current_time
        
        with engine.connect() as conn:
            if not df_success.empty:
                print(f"Writing {len(successful)} trademarks to database")
                df_success.to_sql("trademark_status", conn, index=False, if_exists="append")
            if not df_failed.empty:
                print(f"Writing {len(failed_tms)} failed trademarks to database")
                df_failed.to_sql("failed_trademarks", conn, index=False, if_exists="append")

    return {"success": len(successful), "failed": len(failed_tms)}


def get_trademarks_to_ingest(stale_since_days: int = 15) -> list[TrademarkSearchParams]:
    """
    Retrieves trademarks that need to be ingested, i.e. trademarks that have not been ingested in the last {stale_since_days} days.
    
    This function first deduplicates the trademark_status table by selecting the latest entry for each application number.
    Then, it selects trademarks that have not been ingested in the last {stale_since_days} days.
    Finally, it deduplicates the failed_trademarks table and coalesces the result with the deduplicated trademark_status table.
    
    :param stale_since_days: The number of days since which trademarks should not have been ingested.
    :return: A list of TrademarkSearchParams objects
    """
    print(f"Retrieving trademarks to ingest that have not been ingested in the last {stale_since_days} days")
    query = f"""
      WITH succeeded_deduped AS (
        -- Select the latest entry for each application_number from the trademark_status table
        SELECT * FROM {TRADEMARKS_STATUS_FQN}
        QUALIFY ROW_NUMBER() OVER (PARTITION BY application_number ORDER BY timestamp DESC) = 1
      ),
      newly_ingested AS (
        -- Select trademarks that have not been ingested in the last {stale_since_days} days
        SELECT * FROM succeeded_deduped
        WHERE DATE_DIFF('day', timestamp, current_timestamp) < {stale_since_days}
      ),
      failed_deduped AS (
        -- Select the latest entry for each application_number from the failed_trademarks table
        SELECT
          CAST(application_number AS STRING) AS application_number,
          LAST_VALUE (wordmark IGNORE NULLS) OVER (PARTITION BY application_number ORDER BY timestamp) AS wordmark,
          CAST(LAST_VALUE (class_name IGNORE NULLS) OVER (PARTITION BY application_number ORDER BY timestamp) AS STRING) AS class_name,
          timestamp,
        FROM {TRADEMARKS_FAILED_FQN}
        QUALIFY ROW_NUMBER() OVER (PARTITION BY application_number ORDER BY timestamp DESC) = 1
      ),
      failed_coalesced AS (
        -- Coalesce the failed_deduped table with the succeeded_deduped table
        SELECT
          f.application_number,
          COALESCE(s.wordmark, f.wordmark) AS wordmark,
          COALESCE(s.class_name, f.class_name) AS class_name,
          -- f.timestamp,
        FROM failed_deduped f
        LEFT JOIN succeeded_deduped s
          ON f.application_number = s.application_number
      )
      SELECT * FROM failed_coalesced
      WHERE application_number NOT IN (SELECT application_number FROM newly_ingested)
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
    except Exception as e:
        print(f"An error occurred while getting trademarks to ingest: {str(e)}")
        df = pd.DataFrame()
    
    if df.empty:
        print("No trademarks to ingest")
        return []
    
    print(f"Found {df.shape[0]} trademarks to ingest")
    return [TrademarkSearchParams.from_dict(x) for x in df.to_dict(orient="records")]
