from pathlib import Path

import duckdb
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATABASE_FILE = PROJECT_ROOT / "data" / "analytics.duckdb"

COMPANY_NAMES = {
    "INFY.NS": "Infosys",
    "RELIANCE.NS": "Reliance Industries",
    "HDFCBANK.NS": "HDFC Bank",
    "AAPL": "Apple",
    "NVDA": "NVIDIA",
}


def load_processed_duckdb(database_file: Path = DATABASE_FILE) -> pd.DataFrame:
    """Read staging candles from DuckDB and derive reusable row metrics."""
    connection = duckdb.connect(str(database_file), read_only=True)
    try:
        frame = connection.execute("SELECT * FROM staging.candles").df()
    finally:
        connection.close()
    frame["date"] = pd.to_datetime(frame["date"])
    required = {"symbol", "date", "high", "low", "close", "volume"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"DuckDB staging.candles is missing columns: {sorted(missing)}")
    frame["company"] = frame["symbol"].map(COMPANY_NAMES).fillna(frame["symbol"])
    frame["intraday_range_pct"] = (frame["high"] - frame["low"]) / frame["close"] * 100
    frame["previous_close"] = frame.groupby("symbol")["close"].shift(1)
    frame["daily_return_pct"] = (frame["close"] / frame["previous_close"] - 1) * 100
    return frame


def summarize_by_company(frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate distinct descriptive metrics from an already-loaded frame."""
    ordered = frame.sort_values(["symbol", "date"])
    summary = (
        ordered.groupby(["symbol", "company"], as_index=False)
        .agg(
            trading_days=("date", "nunique"),
            total_volume=("volume", "sum"),
            average_volume=("volume", "mean"),
            average_intraday_range_pct=("intraday_range_pct", "mean"),
            daily_return_volatility=("daily_return_pct", "std"),
            positive_close_days=("daily_return_pct", lambda values: (values > 0).sum()),
            start_close=("close", "first"),
            end_close=("close", "last"),
        )
    )
    summary["period_change_pct"] = (summary["end_close"] / summary["start_close"] - 1) * 100
    return summary.reset_index(drop=True)


def date_range(frame: pd.DataFrame) -> tuple[str, str]:
    return frame["date"].min().strftime("%Y-%m-%d"), frame["date"].max().strftime("%Y-%m-%d")
