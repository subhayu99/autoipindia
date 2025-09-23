from datetime import datetime

import pandas as pd
from pytz import timezone
from sqlalchemy import text

from db import engine
from config import CAPTCHA_MAX_RETRIES
from helpers.utils import run_parallel_exec
from logic.trademark_search import TrademarkSearchParams


def create_tables_if_not_exists():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS trademark_status (
                application_number VARCHAR, 
                wordmark VARCHAR, 
                class_name VARCHAR, 
                status VARCHAR, 
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS failed_trademarks (
                wordmark VARCHAR, 
                class_name VARCHAR, 
                application_number VARCHAR, 
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))


def get_trademark_status(trademark: TrademarkSearchParams) -> dict | None:
    df = trademark.search(max_retries=CAPTCHA_MAX_RETRIES)
    if df is not None and not df.empty:
        return df.iloc[0].to_dict()
    return None


def ingest_trademark_status(trademarks: list[TrademarkSearchParams]):
    """Ingest trademarks into database"""
    # create_tables_if_not_exists()
    
    tm_status_map: list[tuple[TrademarkSearchParams, dict | None]] = run_parallel_exec(
        get_trademark_status, trademarks
    )

    successful: list[dict] = [
        tm_status[1] for tm_status in tm_status_map if tm_status[1] is not None
    ]
    failed_tms: list[dict] = [
        tm_status[0].to_dict() for tm_status in tm_status_map if tm_status[1] is None
    ]

    current_time = datetime.now(tz=timezone("Asia/Kolkata"))

    df_success = pd.DataFrame(successful)
    df_success["timestamp"] = current_time

    df_failed = pd.DataFrame(failed_tms)
    df_failed["timestamp"] = current_time
    
    with engine.connect() as conn:
        if not df_success.empty:
            df_success.to_sql("trademark_status", conn, index=False, if_exists="append")
        if not df_failed.empty:
            df_failed.to_sql("failed_trademarks", conn, index=False, if_exists="append")

    print(f"✅ Successfully ingested {len(successful)} trademarks")
    print(f"❌ Failed to ingest {len(failed_tms)} trademarks")

    return len(successful), len(failed_tms)
