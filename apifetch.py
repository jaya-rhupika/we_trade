import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv
 
load_dotenv()


CACHE_DIR = Path(".cache")

def get_api_key():
    key = os.getenv("key")
    print(key)
    if not key:
        raise RuntimeError("FAUXNANCE_API_KEY is not set")
    return key


def cache_path(symbol):
    CACHE_DIR.mkdir(exist_ok=True)
    return CACHE_DIR / f"{symbol}.json"


def get_cached_candles(symbol):
    path = cache_path(symbol)

    if path.exists():
        with path.open() as f:
            return json.load(f)

    return None


def fetch_candles(symbol):
    cached = get_cached_candles(symbol)

    if cached is not None:
        return cached
    print("12")
    headers = {
        "X-Api-Key": get_api_key(),
        "Accept": "application/json"
    }
    response = requests.get(
        f"https://y4t9nq2bqf.execute-api.eu-west-2.amazonaws.com/v1/symbols/{symbol}",
        headers=headers,
        timeout=30,
    )
    print(response)

    response.raise_for_status()

    raw = response.json()

    path = cache_path(symbol)
    with path.open("w") as f:
        json.dump(raw, f)

    return raw


fetch_candles("NVDA")