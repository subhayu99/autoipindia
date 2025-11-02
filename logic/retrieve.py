from datetime import datetime
from dataclasses import dataclass

import pandas as pd

from db import engine


@dataclass
class TrademarkWithStatus:
    application_number: str
    wordmark: str
    class_name: str
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
        query = """
            SELECT * FROM autoipindia.trademark_status
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
