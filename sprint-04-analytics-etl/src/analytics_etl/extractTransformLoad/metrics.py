from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "candles.csv"

COMPANY_NAMES = {
    "INFY.NS": "Infosys",
    "RELIANCE.NS": "Reliance Industries",
    "HDFCBANK.NS": "HDFC Bank",
}


def load_processed_csv(input_file: Path = INPUT_FILE) -> pd.DataFrame:
    """Load processed candles; calculations accept a DataFrame separately."""
    frame = pd.read_csv(input_file, parse_dates=["date"])
    required = {"symbol", "date", "close", "volume"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Processed CSV is missing columns: {sorted(missing)}")
    frame["company"] = frame["symbol"].map(COMPANY_NAMES).fillna(frame["symbol"])
    frame["traded_value"] = frame["close"] * frame["volume"]
    frame["intraday_range_pct"] = (frame["high"] - frame["low"]) / frame["close"] * 100
    return frame


def summarize_by_company(frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate descriptive trading metrics from an already-loaded frame."""
    ordered = frame.sort_values(["symbol", "date"])
    return (
        ordered.groupby(["symbol", "company"], as_index=False)
        .agg(
            trading_days=("date", "nunique"),
            total_volume=("volume", "sum"),
            total_traded_value=("traded_value", "sum"),
            average_traded_value=("traded_value", "mean"),
            average_intraday_range_pct=("intraday_range_pct", "mean"),
            start_close=("close", "first"),
            end_close=("close", "last"),
        )
        .sort_values("total_traded_value", ascending=False)
        .reset_index(drop=True)
    )


def date_range(frame: pd.DataFrame) -> tuple[str, str]:
    return frame["date"].min().strftime("%Y-%m-%d"), frame["date"].max().strftime("%Y-%m-%d")
