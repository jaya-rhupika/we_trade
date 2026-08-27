from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "data/processed/candles.csv"
)


OUTPUT_FILE = Path(
    "data/processed/metrics.csv"
)


SUMMARY_FILE = Path(
    "data/processed/summary_metrics.csv"
)



def calculate_metrics():

    # Load cleaned candle data
    df = pd.read_csv(
        INPUT_FILE
    )


    if df.empty:
        raise ValueError(
            "Input candles.csv is empty"
        )


    # Convert date column
    df["date"] = pd.to_datetime(
        df["date"]
    )


    # Sort before calculating returns
    df = df.sort_values(
        [
            "symbol",
            "date"
        ]
    )


    # Daily percentage return
    df["daily_return"] = (
        df.groupby("symbol")["close"]
        .pct_change()
        * 100
    )


    # Value traded each day
    df["traded_value"] = (
        df["close"]
        *
        df["volume"]
    )


    # Daily high-low movement
    df["price_range"] = (
        df["high"]
        -
        df["low"]
    )


    # Summary metrics per stock
    summary = (
        df.groupby("symbol")
        .agg(
            average_volume=(
                "volume",
                "mean"
            ),

            total_volume=(
                "volume",
                "sum"
            ),

            average_closing_price=(
                "close",
                "mean"
            ),

            highest_price=(
                "high",
                "max"
            ),

            lowest_price=(
                "low",
                "min"
            ),

            total_traded_value=(
                "traded_value",
                "sum"
            ),

            average_daily_return=(
                "daily_return",
                "mean"
            )
        )
        .reset_index()
    )


    # Create output folder
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    # Save row-level metrics
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    # Save summary metrics
    summary.to_csv(
        SUMMARY_FILE,
        index=False
    )


    print(
        "Metrics calculated successfully"
    )


    print(
        "\nSummary:"
    )

    print(summary)



if __name__ == "__main__":

    calculate_metrics()
