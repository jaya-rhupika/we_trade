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


    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    # Load metrics data
    df = pd.read_csv(
        INPUT_FILE
    )


    # Load summary metrics
    summary = pd.read_csv(
        SUMMARY_FILE
    )


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


    # Ensure chronological order
    df["date"] = pd.to_datetime(
        df["date"]
    )


    df = df.sort_values(
        [
            "company",
            "date"
        ]
    )


    # -------------------------------
    # Chart 1:
    # Daily trading volume trend
    # -------------------------------

    fig = px.line(

        df,

        x="date",

        y="volume",

        color="company",

        title=
        "Daily Trading Volume Comparison",

        labels={

            "date":
            "Trading Date",

            "volume":
            "Shares Traded",

            "company":
            "Company"

        }

    )


    fig.write_html(
        OUTPUT_DIR / "chart_1.html"
    )



    # -------------------------------
    # Chart 2:
    # Closing price movement
    # -------------------------------

    fig = px.line(

        df,

        x="date",

        y="close",

        color="company",

        title=
        "Closing Price Movement During Selected Period",

        labels={

            "date":
            "Trading Date",

            "close":
            "Closing Price (INR)",

            "company":
            "Company"

        }

    )


    fig.write_html(
        OUTPUT_DIR / "chart_2.html"
    )



    # -------------------------------
    # Chart 3:
    # Total traded value comparison
    # -------------------------------

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

        }

    )


    fig.write_html(
        OUTPUT_DIR / "chart_3.html"
    )


    print(
        "Charts created successfully"
    )


    print(
        f"Saved charts in {OUTPUT_DIR}"
    )



if __name__ == "__main__":

    create_charts()






















