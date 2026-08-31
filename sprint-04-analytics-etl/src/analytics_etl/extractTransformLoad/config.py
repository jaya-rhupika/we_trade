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



API_URL = os.getenv("FAUXNANCE_API_URL")
API_KEY = os.getenv("FAUXNANCE_API_KEY")


if not API_URL:
    raise ValueError("FAUXNANCE_API_URL is missing. Check your .env file.")


if not API_KEY:
    raise ValueError("FAUXNANCE_API_KEY is missing. Check your .env file.")
