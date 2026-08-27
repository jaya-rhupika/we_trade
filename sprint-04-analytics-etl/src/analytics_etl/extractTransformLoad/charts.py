from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .metrics import INPUT_FILE, date_range, load_processed_csv, summarize_by_company


OUTPUT_DIR = Path(__file__).resolve().parents[3] / "charts"


def _period(frame: pd.DataFrame) -> str:
    start, end = date_range(frame)
    return f"{start} to {end}"


def create_charts(input_file: Path = INPUT_FILE, output_dir: Path = OUTPUT_DIR) -> list[Path]:
    frame = load_processed_csv(input_file)
    summary = summarize_by_company(frame)
    period = _period(frame)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    leader = summary.iloc[summary["total_volume"].argmax()]
    total_volume = summary["total_volume"].sum()
    volume_share = leader["total_volume"] / total_volume * 100
    fig, axis = plt.subplots(figsize=(9, 6))
    axis.bar(summary["company"], summary["total_volume"] / 1e9)
    axis.set_title(f"{leader['company']} Recorded {volume_share:.2f}% of Total Traded Volume ({period})")
    axis.set_xlabel("Company")
    axis.set_ylabel("Total traded volume (billion shares)")
    axis.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    path = output_dir / "total_traded_volume_by_company.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    paths.append(path)

    fig, axis = plt.subplots(figsize=(9, 6))
    range_leader = summary.iloc[summary["average_intraday_range_pct"].argmax()]
    axis.bar(summary["company"], summary["average_intraday_range_pct"])
    axis.set_title(f"{range_leader['company']} Had the Highest Average Intraday Price Range ({period})")
    axis.set_xlabel("Company")
    axis.set_ylabel("Average intraday high-to-low range (% of closing price)")
    axis.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    path = output_dir / "average_intraday_range_by_company.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    paths.append(path)

    summary["period_change_pct"] = (summary["end_close"] / summary["start_close"] - 1) * 100
    change_leader = summary.iloc[summary["period_change_pct"].argmax()]
    fig, axis = plt.subplots(figsize=(9, 6))
    axis.bar(summary["company"], summary["period_change_pct"])
    axis.set_title(f"{change_leader['company']} Had the Smallest Closing Price Decline ({period})")
    axis.set_xlabel("Company")
    axis.set_ylabel("Closing price change (%)")
    axis.axhline(0, color="black", linewidth=0.8)
    axis.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    path = output_dir / "period_close_change_by_company.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    paths.append(path)
    return paths


if __name__ == "__main__":
    for chart_path in create_charts():
        print(chart_path)
