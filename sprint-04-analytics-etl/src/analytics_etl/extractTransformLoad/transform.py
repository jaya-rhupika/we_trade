import json
from pathlib import Path
from typing import Any

import pandas as pd

from .candle_validator import (
    validate_candle
)


RAW_FILE = Path(
    "data/raw/fauxnance.json"
)


def extract_candles(payload: Any) -> list[dict[str, Any]]:

    """
    Extract candle list from Fauxnance API response.
    Handles different possible JSON structures.
    """

    if isinstance(payload, list):

        return payload

    if not isinstance(payload, dict):

        return []

    data = payload.get("data")

    if (
        isinstance(data, dict)
        and isinstance(data.get("candles"), list)
    ):

        return data["candles"]

    if isinstance(
        payload.get("candles"),
        list
    ):

        return payload["candles"]

    return []


def _symbol(payload: dict[str, Any]) -> str | None:

    data = payload.get("data")

    if isinstance(data, dict):

        return data.get("symbol")

    return payload.get("symbol")


def transform(
    raw_response: dict[str, Any]
) -> dict[str, list[dict[str, Any]]]:

    """
    Transform one raw Fauxnance response into valid
    candle rows and rejected records.
    """

    candles = extract_candles(
        raw_response
    )

    symbol = _symbol(
        raw_response
    )

    dates: dict[
        str,
        list[dict[str, Any]]
    ] = {}

    rejected: list[
        dict[str, Any]
    ] = []


    # Collect candles by date so that conflicting
    # duplicate records can be identified.

    for candle in candles:

        date = (
            candle.get("date")
            if isinstance(candle, dict)
            else None
        )

        if isinstance(date, str):

            dates.setdefault(
                date,
                []
            ).append(candle)


    conflicting_dates = {
        date
        for date, rows in dates.items()
        if (
            len(rows) > 1
            and len(
                {
                    row.get("close")
                    for row in rows
                }
            ) > 1
        )
    }


    valid_rows: list[
        dict[str, Any]
    ] = []


    for candle in candles:

        date = (
            candle.get("date")
            if isinstance(candle, dict)
            else None
        )


        # Conflicting duplicate records are rejected
        # before normal candle validation.

        if date in conflicting_dates:

            rejected.append(
                {
                    "symbol": symbol,
                    "date": date,
                    "reason": "conflicting duplicate"
                }
            )

            continue


        # Validation is handled by the separate
        # candle_validator module.

        valid, result = validate_candle(
            candle
        )


        if not valid:

            rejected.append(
                {
                    "symbol": symbol,
                    "date": date,
                    "reason": result
                }
            )

            continue


        valid_rows.append(
            {
                "symbol": symbol,
                "date": result,
                "open": candle.get("open"),
                "high": candle.get("high"),
                "low": candle.get("low"),
                "close": candle.get("close"),
                "adjclose": candle.get("adjclose"),
                "volume": candle.get("volume"),
            }
        )


    return {
        "valid_rows": valid_rows,
        "rejected_rows": rejected
    }


def clean_data() -> pd.DataFrame:

    with RAW_FILE.open(
        encoding="utf-8"
    ) as raw_file:

        raw = json.load(
            raw_file
        )


    rows: list[
        dict[str, Any]
    ] = []


    for symbol, payload in raw.items():

        response = (
            payload
            if isinstance(payload, dict)
            else {
                "candles": payload
            }
        )


        if not isinstance(
            response.get("data"),
            dict
        ):

            response["data"] = {}


        response["data"].setdefault(
            "symbol",
            symbol
        )


        transformed = transform(
            response
        )


        rows.extend(
            transformed["valid_rows"]
        )


    dataframe = pd.DataFrame(
        rows
    )


    if not dataframe.empty:

        dataframe = dataframe.drop_duplicates(
            subset=[
                "symbol",
                "date"
            ]
        )


    if dataframe.empty:

        raise ValueError(
            "No valid candle data found after transformation"
        )


    return dataframe


if __name__ == "__main__":

    dataframe = clean_data()

    print(
        dataframe.head()
    )