from pathlib import Path

import plotly.graph_objects as go
from plotly.io import to_html

from .metrics import DATABASE_FILE, date_range, load_processed_duckdb, summarize_by_company


OUTPUT_FILE = Path(__file__).resolve().parents[3] / "charts" / "analytics_dashboard.html"


def _period(frame) -> str:
    start, end = date_range(frame)
    return f"{start} to {end}"


def _chart(title: str, x, y, x_title: str, y_title: str) -> go.Figure:
    figure = go.Figure()
    figure.add_trace(go.Bar(x=x, y=y))
    figure.update_layout(title=title, xaxis_title=x_title, yaxis_title=y_title, template="plotly_white")
    return figure


def create_dashboard(database_file: Path = DATABASE_FILE, output_file: Path = OUTPUT_FILE) -> Path:
    frame = load_processed_duckdb(database_file)
    summary = summarize_by_company(frame)
    period = _period(frame)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    company = summary["company"]
    total_volume = summary["total_volume"].sum()
    volume_leader = summary.loc[summary["total_volume"].idxmax()]
    change_leader = summary.loc[summary["period_change_pct"].idxmax()]
    common = frame.groupby("date")["symbol"].nunique()
    common_dates = common[common == summary["symbol"].nunique()].index
    daily = frame[frame["date"].isin(common_dates)]
    daily_volume = daily.dropna(subset=["volume"])
    daily_range = daily.dropna(subset=["intraday_range_pct"])
    daily_volume_leaders = daily_volume.loc[daily_volume.groupby("date")["volume"].idxmax(), "company"].value_counts()
    daily_range_leaders = daily_range.loc[daily_range.groupby("date")["intraday_range_pct"].idxmax(), "company"].value_counts()

    figures = [
        _chart(
            f"{volume_leader['company']} Recorded {volume_leader['total_volume'] / total_volume * 100:.2f}% of Total Volume ({period})",
            company, summary["total_volume"] / 1e9, "Company", "Total traded volume (billion shares)"),
        _chart(
            f"{summary.loc[summary['average_intraday_range_pct'].idxmin(), 'company']} Had the Lowest Average Intraday Range ({period})",
            company, summary["average_intraday_range_pct"], "Company", "Average high-to-low range (% of closing price)"),
        _chart(
            f"{change_leader['company']} Had the Highest Closing Price Increase ({period})",
            company, summary["period_change_pct"], "Company", "Closing price change (%)"),
        _chart(
            f"NVIDIA Led Daily Volume on {int(daily_volume_leaders.get('NVIDIA', 0))} of {len(common_dates)} Common Trading Dates",
            daily_volume_leaders.index, daily_volume_leaders.values, "Company", "Common dates led (count)"),
        _chart(
            f"NVIDIA Had the Highest Daily-Return Volatility ({period})",
            company, summary["daily_return_volatility"], "Company", "Daily-return volatility (percentage points)"),
        _chart(
            f"Infosys Led Intraday Range on {int(daily_range_leaders.get('Infosys', 0))} of {len(common_dates)} Common Trading Dates",
            daily_range_leaders.index, daily_range_leaders.values, "Company", "Common dates led (count)"),
    ]
    sections = []
    for index, figure in enumerate(figures):
        sections.append(to_html(figure, full_html=False, include_plotlyjs="inline" if index == 0 else False))
    html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Sprint 4 Analytics Dashboard</title>
<style>body{font-family:Arial,sans-serif;margin:2rem;color:#17202a;background:#f4f6f7}main{max-width:1200px;margin:auto}h1{margin-bottom:.25rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:1rem}.chart{background:white;padding:1rem;border-radius:8px;box-shadow:0 1px 5px #ccd}p{color:#52606d}</style></head>
<body><main><h1>Sprint 4 Analytics Dashboard</h1><p>DuckDB source: staging.candles | Analysis period: %s | Five selected companies</p><div class="grid">%s</div></main></body></html>""" % (period, "".join(f'<section id="claim-{index + 1}" class="chart">{section}</section>' for index, section in enumerate(sections)))
    output_file.write_text(html, encoding="utf-8")
    return output_file


if __name__ == "__main__":
    print(create_dashboard())
