from datetime import datetime

import pandas as pd
from pydantic import BaseModel

from db import engine
from config import TRADEMARKS_STATUS_FQN, TRADEMARKS_FAILED_FQN


class TrademarkWithStatus(BaseModel):
    application_number: str
    wordmark: str | None
    class_name: str | None
    status: str
    timestamp: datetime
    
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
            print(f"An error occurred while getting all trademarks with status: {str(e)}")
            df = pd.DataFrame()
        
        print(f"Found {df.shape[0]} trademarks with status")
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
            print(f"An error occurred while getting trademark for application number {application_number}: {str(e)}")
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
            print(f"An error occurred while getting trademark for wordmark {wordmark} and class {class_name}: {str(e)}")
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
            print(f"An error occurred while deleting trademark for application number {self.application_number}: {str(e)}")
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
            print(f"An error occurred while deleting failed trademark for application number {self.application_number}: {str(e)}")
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
            print(f"An error occurred while getting trademark history for application number {application_number}: {str(e)}")
            return []

    def get_history(self):
        return self.get_history_by_application_number(self.application_number)
