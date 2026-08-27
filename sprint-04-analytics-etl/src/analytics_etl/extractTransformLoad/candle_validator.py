"""
Validation of individual OHLCV candle records.

It only determines whether an individual candle is valid
and explains why it is invalid.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


REQUIRED_FIELDS = (
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
)

PRICE_FIELDS = (
    "open",
    "high",
    "low",
    "close",
)


def validate_candle(
    candle: dict[str, Any],
) -> tuple[bool, str | None]:
    """
    Validate one OHLCV candle.

    Returns:
        (True, None)
            Candle is valid.

        (False, reason)
            Candle is invalid and should not be loaded as-is.
    """

    # ---------------------------------------------------------
    # Required fields
    # ---------------------------------------------------------
    for field in REQUIRED_FIELDS:
        if field not in candle:
            return False, f"missing required field: {field}"

    # ---------------------------------------------------------
    # Date
    # ---------------------------------------------------------
    date_value = candle["date"]

    if not isinstance(date_value, str):
        return False, "date is not a string"

    try:
        datetime.strptime(date_value, "%Y-%m-%d")
    except ValueError:
        return False, f"date is not ISO format: {date_value!r}"

    # ---------------------------------------------------------
    # OHLC numeric values
    # ---------------------------------------------------------
    numeric_values: dict[str, float] = {}

    for field in PRICE_FIELDS:
        value = candle[field]

        try:
            numeric_values[field] = float(value)
        except (TypeError, ValueError):
            return False, f"{field} is not numeric: {value!r}"

    # ---------------------------------------------------------
    # Candle geometry
    #
    # A candle cannot have a high lower than its low.
    # ---------------------------------------------------------
    high = numeric_values["high"]
    low = numeric_values["low"]

    if high < low:
        return False, f"high {high} is below low {low}"

    # ---------------------------------------------------------
    # Volume
    # ---------------------------------------------------------
    volume = candle["volume"]

    try:
        volume_value = float(volume)
    except (TypeError, ValueError):
        return False, f"volume is not numeric: {volume!r}"

    if volume_value < 0:
        return False, f"volume is negative: {volume}"

    return True, None