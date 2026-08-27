import json
from pathlib import Path
from datetime import datetime

import pandas as pd


RAW_FILE = Path(
    "data/raw/fauxnance.json"
)


NUMERIC_FIELDS = [
    "open",
    "high",
    "low",
    "close",
    "adjclose",
    "volume"
]



def parse_date(value):

    if value is None:
        return None


    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%Y-%m-%dT%H:%M:%S"
    ]


    for fmt in formats:

        try:

            return datetime.strptime(
                value,
                fmt
            ).strftime(
                "%Y-%m-%d"
            )

        except ValueError:
            continue


    return None




def is_number(value):

    return isinstance(
        value,
        (int, float)
    )




def validate_candle(candle):


    if candle.get("close") is None:

        return False, "missing_close"



    for field in NUMERIC_FIELDS:

        if field in candle:

            if not is_number(
                candle[field]
            ):

                return False, f"invalid_{field}"



    if (
        "high" in candle
        and "low" in candle
    ):

        if candle["high"] < candle["low"]:

            return False, "high_less_than_low"



    if (
        "volume" in candle
        and candle["volume"] < 0
    ):

        return False, "negative_volume"



    date = parse_date(
        candle.get("date")
    )


    if date is None:

        return False, "invalid_date"



    return True, date




def extract_candles(payload):

    """
    Extract candle list from Fauxnance API response.
    Handles different possible JSON structures.
    """


    if isinstance(payload, list):

        return payload



    if "data" in payload:

        if isinstance(
            payload["data"],
            dict
        ):

            if "candles" in payload["data"]:

                return payload["data"]["candles"]



    if "candles" in payload:

        return payload["candles"]



    return []




def clean_data():


    with open(
        RAW_FILE,
        "r"
    ) as file:

        raw = json.load(file)



    rows = []

    rejected = []



    for symbol, payload in raw.items():


        candles = extract_candles(
            payload
        )


        for candle in candles:


            valid, result = validate_candle(
                candle
            )


            if not valid:


                rejected.append(
                    {
                        "symbol": symbol,
                        "date": candle.get("date"),
                        "reason": result
                    }
                )

                continue



            rows.append(
                {
                    "symbol": symbol,
                    "date": result,
                    "open": candle.get("open"),
                    "high": candle.get("high"),
                    "low": candle.get("low"),
                    "close": candle.get("close"),
                    "adjclose": candle.get("adjclose"),
                    "volume": candle.get("volume")
                }
            )



    df = pd.DataFrame(
        rows
    )



    if df.empty:

        raise ValueError(
            "No valid candle data found after transformation"
        )



    # Remove duplicate symbol/date records

    df = df.drop_duplicates(
        subset=[
            "symbol",
            "date"
        ],
        keep="first"
    )



    print(
        "Rejected records:"
    )


    for item in rejected:

        print(item)



    print(
        "Transformation completed"
    )


    return df




if __name__ == "__main__":

    dataframe = clean_data()

    print(
        dataframe.head()
    )