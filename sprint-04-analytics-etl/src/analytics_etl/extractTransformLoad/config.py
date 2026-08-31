import os

from dotenv import load_dotenv


load_dotenv()


SYMBOLS = [
    "INFY.NS",
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "AAPL",
    "NVDA",
]


# Date range for the candle fetch.
# apifetch.py uses these to fetch only what is missing from cache.
FROM_DATE = os.getenv("FAUXNANCE_FROM_DATE", "2025-08-27")
TO_DATE   = os.getenv("FAUXNANCE_TO_DATE",   "2026-08-27")


API_URL = os.getenv("FAUXNANCE_API_URL")
API_KEY = os.getenv("FAUXNANCE_API_KEY")


if not API_URL:
    raise ValueError("FAUXNANCE_API_URL is missing. Check your .env file.")


if not API_KEY:
    raise ValueError("FAUXNANCE_API_KEY is missing. Check your .env file.")