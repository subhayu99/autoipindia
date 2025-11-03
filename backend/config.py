import os
from pathlib import Path
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")
API_TOKEN = os.getenv("API_TOKEN")  # Static token for API authentication

# Database Configuration
DATABASE_NAME = os.getenv("DATABASE_NAME", "autoipindia")
DATABASE_PROTOCOL = os.getenv("DATABASE_PROTOCOL", "duckdb:///")
DATABASE_URL = f"md:{DATABASE_NAME}?motherduck_token={MOTHERDUCK_TOKEN}"

TRADEMARKS_STATUS_TABLE_NAME = os.getenv("TRADEMARKS_STATUS_TABLE_NAME", "trademark_status")
TRADEMARKS_FAILED_TABLE_NAME = os.getenv("TRADEMARKS_FAILED_TABLE_NAME", "failed_trademarks")

TRADEMARKS_STATUS_FQN = f"{DATABASE_NAME}.{TRADEMARKS_STATUS_TABLE_NAME}"
TRADEMARKS_FAILED_FQN = f"{DATABASE_NAME}.{TRADEMARKS_FAILED_TABLE_NAME}"

MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", 1))

# Captcha Configurations
CAPTCHA_MAX_RETRIES = int(os.getenv("CAPTCHA_MAX_RETRIES", 5))
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

# CORS Configuration
# Allow multiple origins separated by comma
# Set CORS_ORIGINS environment variable to override defaults
CORS_ORIGINS_STR = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:8050,http://127.0.0.1:3000,http://127.0.0.1:8050,https://subhayu99.github.io"
)
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_STR.split(",") if origin.strip()]

# Validate required environment variables
def validate_config():
    """Validate that all required environment variables are set."""
    required_vars = {
        "API_TOKEN": API_TOKEN,
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "MOTHERDUCK_TOKEN": MOTHERDUCK_TOKEN,
    }

    missing_vars = [var for var, value in required_vars.items() if not value]

    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        print("Please set these variables in your .env file", file=sys.stderr)
        sys.exit(1)

# Run validation on import
validate_config()
