import json
import os
from pathlib import Path
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv


load_dotenv()

CACHE_DIR = Path(".cache")


def get_api_key():
    key = os.getenv("key")  # use FAUXNANCE_API_KEY if that is your env name

    if not key:
        raise RuntimeError("API key is not set")

    return key


def quotes_cache_path(symbol):

    CACHE_DIR.mkdir(exist_ok=True)

    today = datetime.utcnow().strftime("%Y-%m-%d")

    return CACHE_DIR / f"quotes_{symbol}_{today}.json"


def get_cached_quote(symbol):
    path = quotes_cache_path(symbol)

    if not path.exists():
        return None

    with path.open("r") as f:
        return json.load(f)


def fetch_quotes(symbols):

    if isinstance(symbols, str):
        symbols = [symbols]

    results = {}
    missing_symbols = []


    for symbol in symbols:
        cached = get_cached_quote(symbol)

        if cached is not None:
            print(f"{symbol}: loaded from cache")
            results[symbol] = cached
        else:
            missing_symbols.append(symbol)

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

        quotes = raw["data"]["quotes"]

        for item in quotes:
            symbol = item["symbol"]

            results[symbol] = item

            cache_file = quotes_cache_path(symbol)

            with cache_file.open("w") as f:
                json.dump(item, f, indent=2)

    return results


def candles_cache_path(symbol, interval):

    CACHE_DIR.mkdir(exist_ok=True)

    filename = f"candles_{symbol}_{interval}.json"

    return CACHE_DIR / filename


def get_cached_candles(symbol, interval):
    """
    Load candle cache.
    """

    path = candles_cache_path(
        symbol,
        interval
    )

    if not path.exists():
        return None

    with path.open("r") as f:
        return json.load(f)


def save_cached_candles(symbol, interval, data):

    cache_file = candles_cache_path(
        symbol,
        interval
    )

    with cache_file.open("w") as f:
        json.dump(data, f, indent=2)


def _extract_candles(raw):


    return raw["data"]["candles"]


def _get_candle_date(candle):

    return candle["date"]


def _merge_candles(existing, new):

    candles_by_date = {}

    for candle in existing:
        date = _get_candle_date(candle)
        candles_by_date[date] = candle

    for candle in new:
        date = _get_candle_date(candle)
        candles_by_date[date] = candle

    return [
        candles_by_date[date]
        for date in sorted(candles_by_date)
    ]


def _filter_candles(candles, from_date, to_date):
    """
    Return candles inside requested date range.
    """

    result = []

    for candle in candles:

        candle_date = _get_candle_date(candle)

        if from_date <= candle_date <= to_date:
            result.append(candle)

    return result


def _fetch_candles_from_api(
    symbol,
    from_date,
    to_date,
    interval
):
    """
    Fetch candles directly from API.
    """

    print(
        f"{symbol}: API fetch "
        f"{from_date} -> {to_date}"
    )

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

    return response.json()


def fetch_candles(
    symbol,
    from_date,
    to_date,
    interval="1d"
):
    """
    Fetch historical candles using range-aware caching.

    Behaviour:

    1. No cache:
       Fetch entire requested range.

    2. Requested range is completely inside cache:
       Return from cache without API call.

    3. Requested range extends before cache:
       Fetch only missing beginning.

    4. Requested range extends after cache:
       Fetch only missing ending.

    5. Requested range surrounds cache:
       Fetch missing beginning + ending.

    6. Newly fetched candles are merged into cache.

    The cache grows over time.
    """

    from_date = str(from_date)
    to_date = str(to_date)

    # -------------------------
    # Validate dates
    # -------------------------

    if from_date > to_date:
        raise ValueError(
            f"from_date ({from_date}) cannot be "
            f"after to_date ({to_date})"
        )

    # =====================================================
    # LOAD CACHE
    # =====================================================

    cached_raw = get_cached_candles(
        symbol,
        interval
    )

    # =====================================================
    # CASE 1:
    # NO CACHE
    # =====================================================

    if cached_raw is None:

        print(
            f"{symbol}: no cache found"
        )

        raw = _fetch_candles_from_api(
            symbol,
            from_date,
            to_date,
            interval
        )

        save_cached_candles(
            symbol,
            interval,
            raw
        )

        return raw

    # =====================================================
    # EXTRACT CACHED CANDLES
    # =====================================================

    cached_candles = _extract_candles(
        cached_raw
    )

    # =====================================================
    # CASE 2:
    # CACHE EXISTS BUT IS EMPTY
    # =====================================================

    if not cached_candles:

        print(
            f"{symbol}: cache is empty"
        )

        raw = _fetch_candles_from_api(
            symbol,
            from_date,
            to_date,
            interval
        )

        save_cached_candles(
            symbol,
            interval,
            raw
        )

        return raw

    # =====================================================
    # FIND CACHE RANGE
    # =====================================================

    cached_dates = [
        _get_candle_date(candle)
        for candle in cached_candles
    ]

    cached_from = min(cached_dates)
    cached_to = max(cached_dates)

    print(
        f"{symbol}: cached range "
        f"{cached_from} -> {cached_to}"
    )

    print(
        f"{symbol}: requested range "
        f"{from_date} -> {to_date}"
    )

    # =====================================================
    # CASE 3:
    # REQUEST IS COMPLETELY INSIDE CACHE
    # =====================================================

    if (
        from_date >= cached_from
        and to_date <= cached_to
    ):

        print(
            f"{symbol}: loaded requested range "
            f"entirely from cache"
        )

        requested_candles = _filter_candles(
            cached_candles,
            from_date,
            to_date
        )

        # Create a copy of the cached response
        result = dict(cached_raw)

        result["data"] = dict(
            cached_raw["data"]
        )

        result["data"]["candles"] = (
            requested_candles
        )

        return result

    # =====================================================
    # DETERMINE MISSING RANGES
    # =====================================================

    missing_ranges = []

    # -----------------------------------------------------
    # Missing data BEFORE cached range
    # -----------------------------------------------------

    if from_date < cached_from:

        cached_from_date = datetime.strptime(
            cached_from,
            "%Y-%m-%d"
        )

        missing_to = (
            cached_from_date - timedelta(days=1)
        ).strftime("%Y-%m-%d")

        missing_from = from_date

        if missing_from <= missing_to:

            missing_ranges.append(
                (
                    missing_from,
                    missing_to
                )
            )

    # -----------------------------------------------------
    # Missing data AFTER cached range
    # -----------------------------------------------------

    if to_date > cached_to:

        cached_to_date = datetime.strptime(
            cached_to,
            "%Y-%m-%d"
        )

        missing_from = (
            cached_to_date + timedelta(days=1)
        ).strftime("%Y-%m-%d")

        missing_to = to_date

        if missing_from <= missing_to:

            missing_ranges.append(
                (
                    missing_from,
                    missing_to
                )
            )

    # =====================================================
    # FETCH MISSING RANGES
    # =====================================================

    all_candles = list(cached_candles)

    for missing_from, missing_to in missing_ranges:

        print(
            f"{symbol}: missing range "
            f"{missing_from} -> {missing_to}"
        )

        raw = _fetch_candles_from_api(
            symbol,
            missing_from,
            missing_to,
            interval
        )

        new_candles = _extract_candles(
            raw
        )

        all_candles = _merge_candles(
            all_candles,
            new_candles
        )

    # =====================================================
    # UPDATE CACHE
    # =====================================================

    all_candles = _merge_candles(
        [],
        all_candles
    )

    cached_raw["data"]["candles"] = (
        all_candles
    )

    save_cached_candles(
        symbol,
        interval,
        cached_raw
    )

    # =====================================================
    # RETURN ONLY REQUESTED RANGE
    # =====================================================

    requested_candles = _filter_candles(
        all_candles,
        from_date,
        to_date
    )

    result = dict(cached_raw)

    result["data"] = dict(
        cached_raw["data"]
    )

    result["data"]["candles"] = (
        requested_candles
    )

    return result


# =========================================================
# EXAMPLE USAGE
# =========================================================

if __name__ == "__main__":

    # -------------------------
    # Quotes
    # -------------------------

    quotes = fetch_quotes([
        "TATASTEEL.NS",
        "TCS.NS",
        "INFY.NS"
    ])

    print(
        json.dumps(
            quotes,
            indent=2
        )
    )

    # -------------------------
    # Candles
    # -------------------------

    candles = fetch_candles(
        "TCS.NS",
        "2026-01-01",
        "2026-08-27",
        "1d"
    )

    print(
        json.dumps(
            candles,
            indent=2
        )
    )

 