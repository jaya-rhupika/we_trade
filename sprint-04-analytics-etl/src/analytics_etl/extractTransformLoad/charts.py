from pathlib import Path

import pandas as pd
import plotly.express as px


INPUT_FILE = Path(
    "data/processed/metrics.csv"
)

SUMMARY_FILE = Path(
    "data/processed/summary_metrics.csv"
)

OUTPUT_DIR = Path(
    "artefacts"
)


def create_charts():

    # Create output directory
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    # Load data
    df = pd.read_csv(
        INPUT_FILE
    )

    summary = pd.read_csv(
        SUMMARY_FILE
    )


    if df.empty:
        raise ValueError(
            "metrics.csv is empty"
        )


    # Company name mapping
    company_names = {

        "INFY.NS":
        "Infosys Ltd",

        "RELIANCE.NS":
        "Reliance Industries Ltd",

        "TATASTEEL.BO":
        "Tata Steel Ltd"

    }


    df["company"] = (
        df["symbol"]
        .map(company_names)
    )


    summary["company"] = (
        summary["symbol"]
        .map(company_names)
    )


    # Convert date to datetime
    df["date"] = pd.to_datetime(
        df["date"]
    )


    # Sort data chronologically
    df = df.sort_values(
        [
            "company",
            "date"
        ]
    )


    # =====================================================
    # CHART 1
    # Daily Trading Volume
    # =====================================================

    fig = px.line(

        df,

        x="date",

        y="volume",

        color="company",

        markers=True,

        title=
        "Daily Trading Volume Comparison",

        labels={

            "date":
            "Trading Date",

            "volume":
            "Shares Traded",

            "company":
            "Company"

        },

        hover_data={
            "symbol": True,
            "volume": ":,.0f",
            "date": "|%d %b %Y"
        }

    )


    fig.update_traces(
        marker=dict(
            size=7
        )
    )


    fig.update_layout(

        xaxis_title="Trading Date",

        yaxis_title="Shares Traded",

        legend_title="Company",

        hovermode="x unified",

        template="plotly_white"

    )


    fig.write_html(
        OUTPUT_DIR / "chart_1.html"
    )


    # =====================================================
    # CHART 2
    # Closing Price
    # =====================================================

    fig = px.line(

        df,

        x="date",

        y="close",

        color="company",

        markers=True,

        title=
        "Closing Price Movement During July 2026",

        labels={

            "date":
            "Trading Date",

            "close":
            "Closing Price (INR)",

            "company":
            "Company"

        },

        hover_data={
            "symbol": True,
            "close": ":.2f",
            "date": "|%d %b %Y"
        }

    )


    fig.update_traces(
        marker=dict(
            size=7
        )
    )


    fig.update_layout(

        xaxis_title="Trading Date",

        yaxis_title="Closing Price (INR)",

        legend_title="Company",

        hovermode="x unified",

        template="plotly_white"

    )


    fig.write_html(
        OUTPUT_DIR / "chart_2.html"
    )


    # =====================================================
    # CHART 3
    # Total Traded Value
    # =====================================================

    fig = px.bar(

        summary,

        x="company",

        y="total_traded_value",

        title=
        "Total Traded Value Comparison",

        labels={

            "company":
            "Company",

            "total_traded_value":
            "Total Traded Value (INR)"

        },

        text="total_traded_value"

    )


    fig.update_traces(

        texttemplate="%{text:,.0f}",

        textposition="outside",

        hovertemplate=
        "<b>%{x}</b><br>"
        "Total Traded Value: ₹%{y:,.0f}"
        "<extra></extra>"

    )


    fig.update_layout(

        xaxis_title="Company",

        yaxis_title="Total Traded Value (INR)",

        template="plotly_white",

        uniformtext_minsize=8,

        uniformtext_mode="hide"

    )


    fig.write_html(
        OUTPUT_DIR / "chart_3.html"
    )


    print(
        "Charts created successfully."
    )

    print(
        f"Charts saved to: {OUTPUT_DIR}"
    )


if __name__ == "__main__":

    create_charts()