import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

CACHE_DIR = Path(".cache")


def get_api_key():
    key = os.getenv("key")

    if not key:
        raise RuntimeError("API key is not set")

    return key


# -------------------------
# Quotes cache
# -------------------------

def quotes_cache_path(symbol):
    """
    Example:
    .cache/quotes_TCS.NS_2026-08-27.json
    """

    CACHE_DIR.mkdir(exist_ok=True)

    from datetime import datetime
    today = datetime.utcnow().strftime("%Y-%m-%d")

    return CACHE_DIR / f"quotes_{symbol}_{today}.json"


def get_cached_quote(symbol):
    path = quotes_cache_path(symbol)

    if not path.exists():
        return None

    with path.open("r") as f:
        return json.load(f)


def fetch_quotes(symbols):
    """
    Fetch quotes.
    API limit: 25 symbols per request.
    """

    if isinstance(symbols, str):
        symbols = [symbols]

    results = {}
    missing_symbols = []

    # Check cache
    for symbol in symbols:
        cached = get_cached_quote(symbol)

        if cached is not None:
            print(f"{symbol} from cache")
            results[symbol] = cached
        else:
            missing_symbols.append(symbol)

    # Fetch missing symbols in batches of 25
    for i in range(0, len(missing_symbols), 25):
        batch = missing_symbols[i:i + 25]

        response = requests.get(
            "https://y4t9nq2bqf.execute-api.eu-west-2.amazonaws.com/v1/quotes",
            headers={
                "X-Api-Key": get_api_key(),
                "Accept": "application/json"
            },
            params={
                "symbols": ",".join(batch)
            },
            timeout=30,
        )

        print(response.url)

        response.raise_for_status()

        raw = response.json()

        for item in raw["data"]["quotes"]:
            symbol = item["symbol"]

            results[symbol] = item

            with quotes_cache_path(symbol).open("w") as f:
                json.dump(item, f, indent=2)

    return results


# -------------------------
# Candles cache
# -------------------------

def candles_cache_path(symbol, from_date, to_date, interval):
    """
    Example:
    .cache/candles_TCS.NS_2026-01-01_2026-08-27_1d.json
    """

    CACHE_DIR.mkdir(exist_ok=True)

    filename = (
        f"candles_{symbol}_"
        f"{from_date}_"
        f"{to_date}_"
        f"{interval}.json"
    )

    return CACHE_DIR / filename


def get_cached_candles(symbol, from_date, to_date, interval):
    path = candles_cache_path(
        symbol,
        from_date,
        to_date,
        interval
    )

    if not path.exists():
        return None

    with path.open("r") as f:
        return json.load(f)


def fetch_candles(symbol, from_date, to_date, interval="1d"):
    """
    Fetch historical candles.
    """

    cached = get_cached_candles(
        symbol,
        from_date,
        to_date,
        interval
    )

    if cached is not None:
        print(f"{symbol} candles from cache")
        return cached

    response = requests.get(
        f"https://y4t9nq2bqf.execute-api.eu-west-2.amazonaws.com/v1/candles/{symbol}",
        headers={
            "X-Api-Key": get_api_key(),
            "Accept": "application/json"
        },
        params={
            "from": from_date,
            "to": to_date,
            "interval": interval
        },
        timeout=30,
    )

    print(response.url)

    response.raise_for_status()

    raw = response.json()

    with candles_cache_path(
        symbol,
        from_date,
        to_date,
        interval
    ).open("w") as f:
        json.dump(raw, f, indent=2)

    return raw


# -------------------------
# Example usage
# -------------------------

quotes = fetch_quotes([
    "TATASTEEL.NS",
    "TCS.NS",
    "INFY.NS"
])

print(json.dumps(quotes, indent=2))


candles = fetch_candles(
    "TCS.NS",
    "2026-01-01",
    "2026-08-27",
    "1d"
)

print(json.dumps(candles, indent=2)) 

