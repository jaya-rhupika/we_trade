import os

from dotenv import load_dotenv


# Load variables from .env file
load_dotenv()


# Stock symbols to extract
SYMBOLS = [
    "INFY.NS",
    "RELIANCE.NS",
    "TATASTEEL.BO"
]


# Date range for analytics
START_DATE = "2026-07-01"

END_DATE = "2026-07-31"


# Fauxnance API configuration
API_URL = os.getenv(
    "FAUXNANCE_API_URL"
)


API_KEY = os.getenv(
    "FAUXNANCE_API_KEY"
)


# Validate environment variables

if not API_URL:
    raise ValueError(
        "FAUXNANCE_API_URL is missing. Check your .env file."
    )


if not API_KEY:
    raise ValueError(
        "FAUXNANCE_API_KEY is missing. Check your .env file."
    )