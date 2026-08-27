import pandas as pd
import plotly.express as px


df = pd.read_csv(
    "data/processed/metrics.csv"
)


names = {

"INFY.NS":
"Infosys Ltd",

"RELIANCE.NS":
"Reliance Industries Ltd",

"TATASTEEL.BO":
"Tata Steel Ltd"

}


df["company"] = (
    df["symbol"]
    .map(names)
)



# Chart 1

fig = px.line(
    df,
    x="date",
    y="volume",
    color="company",

    title=
    "Tata Steel Recorded the Highest Daily Trading Volume",

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
    "artefacts/chart_1.html"
)



# Chart 2


fig = px.line(
    df,
    x="date",
    y="close",
    color="company",

    title=
    "Reliance Industries Closing Price During July 2026",

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
    "artefacts/chart_2.html"
)



# Chart 3


fig = px.bar(
    df.groupby(
        "company"
    )
    ["traded_value"]
    .sum()
    .reset_index(),

    x="company",

    y="traded_value",

    title=
    "Reliance Industries Accounted for the Highest Traded Value",

    labels={

    "company":
    "Company",

    "traded_value":
    "Traded Value (INR)"

    }

)


fig.write_html(
    "artefacts/chart_3.html"
)


print(
    "Charts created"
)
