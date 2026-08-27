import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from .candle_validator import (
    validate_candle
)


RAW_FILE = Path("data/raw/fauxnance.json")
NUMERIC_FIELDS = ("open", "high", "low", "close", "adjclose", "volume")


def parse_date(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None
    return parsed.strftime("%Y-%m-%d")


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def extract_candles(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    data = payload.get("data")
    if isinstance(data, dict) and isinstance(data.get("candles"), list):
        return data["candles"]
    if isinstance(payload.get("candles"), list):
        return payload["candles"]
    return []


def _symbol(payload: dict[str, Any]) -> str | None:
    data = payload.get("data")
    if isinstance(data, dict):
        return data.get("symbol")
    return payload.get("symbol")


def _validate_candle(candle: Any) -> tuple[bool, str]:
    if not isinstance(candle, dict):
        return False, "candle is not an object"
    if "close" not in candle or candle["close"] is None:
        return False, "missing close"
    for field in NUMERIC_FIELDS:
        value = candle.get(field)
        if field == "volume" and value is None:
            continue
        if value is not None and not is_number(value):
            return False, f"invalid numeric value for {field}"
    if is_number(candle.get("high")) and is_number(candle.get("low")):
        if candle["high"] < candle["low"]:
            return False, "high is below low"
    if is_number(candle.get("volume")) and candle["volume"] < 0:
        return False, "negative volume"
    if parse_date(candle.get("date")) is None:
        return False, "invalid ISO date"
    return True, ""


def transform(raw_response: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Return loadable candle rows and terminal rejection records."""
    candles = extract_candles(raw_response)
    symbol = _symbol(raw_response)
    dates: dict[str, list[dict[str, Any]]] = {}
    rejected: list[dict[str, Any]] = []

    for candle in candles:
        date = candle.get("date") if isinstance(candle, dict) else None
        if isinstance(date, str):
            dates.setdefault(date, []).append(candle)

    conflicting_dates = {
        date
        for date, rows in dates.items()
        if len(rows) > 1 and len({row.get("close") for row in rows}) > 1
    }
    valid_rows: list[dict[str, Any]] = []
    for candle in candles:
        date = candle.get("date") if isinstance(candle, dict) else None
        if date in conflicting_dates:
            rejected.append({"symbol": symbol, "date": date, "reason": "conflicting duplicate"})
            continue
        valid, reason = _validate_candle(candle)
        if not valid:
            rejected.append({"symbol": symbol, "date": date, "reason": reason})
            continue
        normalized_date = parse_date(date)
        valid_rows.append(
            {
                "symbol": symbol,
                "date": normalized_date,
                "open": candle.get("open"),
                "high": candle.get("high"),
                "low": candle.get("low"),
                "close": candle.get("close"),
                "adjclose": candle.get("adjclose"),
                "volume": candle.get("volume"),
            }
        )
    return {"valid_rows": valid_rows, "rejected_rows": rejected}


def clean_data() -> pd.DataFrame:
    with RAW_FILE.open(encoding="utf-8") as raw_file:
        raw = json.load(raw_file)
    rows: list[dict[str, Any]] = []
    for symbol, payload in raw.items():
        response = payload if isinstance(payload, dict) else {"candles": payload}
        response.setdefault("data", {})
        response["data"].setdefault("symbol", symbol)
        rows.extend(transform(response)["valid_rows"])
    dataframe = pd.DataFrame(rows).drop_duplicates(subset=["symbol", "date"])
    if dataframe.empty:
        raise ValueError("No valid candle data found after transformation")
    return dataframe
