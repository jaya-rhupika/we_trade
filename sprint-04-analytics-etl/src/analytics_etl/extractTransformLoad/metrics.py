import pandas as pd


INPUT = "data/processed/candles.csv"

OUTPUT = "data/processed/metrics.csv"



df = pd.read_csv(INPUT)



df["date"] = pd.to_datetime(
    df["date"]
)



df["daily_return"] = (
    df.groupby("symbol")
    ["close"]
    .pct_change()
    * 100
)



df["traded_value"] = (
    df["close"]
    *
    df["volume"]
)



df["price_range"] = (
    df["high"]
    -
    df["low"]
)



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

        total_traded_value=(
            "traded_value",
            "sum"
        )
    )
)



print(summary)



df.to_csv(
    OUTPUT,
    index=False
)
