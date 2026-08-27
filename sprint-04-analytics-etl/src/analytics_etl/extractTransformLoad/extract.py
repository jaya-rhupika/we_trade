import json
from pathlib import Path

import requests

from config import (
    SYMBOLS,
    API_URL,
    API_KEY
)


OUTPUT = Path(
    "data/raw/fauxnance.json"
)



def fetch_symbol(symbol):

    headers = {
        "X-Api-Key": API_KEY
    }


    url = f"{API_URL}/candles/{symbol}"


    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )


    print(
        "Request URL:",
        response.url
    )

    print(
        "Status:",
        response.status_code
    )


    # Useful for debugging API responses
    if response.status_code != 200:
        print(
            "Response:",
            response.text
        )


    response.raise_for_status()


    return response.json()



def extract():

    results = {}


    for symbol in SYMBOLS:

        print(
            f"Downloading {symbol}"
        )


        results[symbol] = fetch_symbol(
            symbol
        )



    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    with open(
        OUTPUT,
        "w"
    ) as file:

        json.dump(
            results,
            file,
            indent=2
        )


    print(
        "Raw data saved to",
        OUTPUT
    )



if __name__ == "__main__":

    extract()