import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")

# Database Configuration
DATABASE_NAME = os.getenv("DATABASE_NAME", "autoipindia")
DATABASE_PROTOCOL = os.getenv("DATABASE_PROTOCOL", "duckdb:///")
DATABASE_URL = f"md:{DATABASE_NAME}?motherduck_token={MOTHERDUCK_TOKEN}"

TRADEMARKS_STATUS_TABLE_NAME = os.getenv("TRADEMARKS_STATUS_TABLE_NAME", "trademark_status")
TRADEMARKS_FAILED_TABLE_NAME = os.getenv("TRADEMARKS_FAILED_TABLE_NAME", "failed_trademarks")

TRADEMARKS_STATUS_FQN = f"{DATABASE_NAME}.{TRADEMARKS_STATUS_TABLE_NAME}"
TRADEMARKS_FAILED_FQN = f"{DATABASE_NAME}.{TRADEMARKS_FAILED_TABLE_NAME}"

# Scraping Configuration
CAPTCHA_MAX_RETRIES = int(os.getenv("CAPTCHA_MAX_RETRIES", 5))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
DELAY_BETWEEN_REQUESTS = int(os.getenv("DELAY_BETWEEN_REQUESTS", 5))

# Sample Captcha Configuration
SAMPLE_CAPTCHA_DIR = Path("sample_captchas")
CAPTCHA_EXAMPLES = [
    ("sample0.jpeg", "372006"),
    ("sample1.jpeg", "820019"),
    ("sample2.jpeg", "785407"),
    ("sample3.jpeg", "810721"),
    ("sample4.jpeg", "881558"),
    ("sample5.jpeg", "276230"),
    ("sample6.jpeg", "351958"),
    ("sample7.jpeg", "142874"),
    ("sample8.jpeg", "003127"),
    ("sample9.jpeg", "911844"),
]

CAPTCHA_EXAMPLES = [
    (SAMPLE_CAPTCHA_DIR / filename, code) for filename, code in CAPTCHA_EXAMPLES
]


# Prefect Configuration
PREFECT_API_URL = os.getenv("PREFECT_API_URL", "https://api.prefect.cloud")
PREFECT_WORKSPACE = os.getenv("PREFECT_WORKSPACE")
