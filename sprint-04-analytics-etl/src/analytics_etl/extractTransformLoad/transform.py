import json
from pathlib import Path

import pandas as pd

from candle_validator import (
    validate_candle
)


RAW_FILE = Path(
    "data/raw/fauxnance.json"
)



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