from pathlib import Path
import pandas as pd


OUTPUT_FILE = Path(
    "data/processed/candles.csv"
)



def load_csv(df: pd.DataFrame):

    """
    Load transformed dataframe into CSV file.

    Parameters:
        df (pd.DataFrame): Cleaned market data dataframe
    """


    if df.empty:
        raise ValueError(
            "Cannot load empty dataframe"
        )


    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    print(
        f"Data loaded successfully into {OUTPUT_FILE}"
    )



if __name__ == "__main__":

    print(
        "load.py is ready. Call load_csv(df) from pipeline.py"
    )