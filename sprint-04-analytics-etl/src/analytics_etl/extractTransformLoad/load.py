from pathlib import Path
import logging

import pandas as pd


OUTPUT_FILE = Path(
    "data/processed/candles.csv"
)


logger = logging.getLogger(__name__)



def load_csv(df: pd.DataFrame):

    """
    Load transformed dataframe into CSV file.

    Parameters:
        df (pd.DataFrame): Cleaned market data dataframe
    """


    if df.empty:

        logger.error(
            "LOAD_FAILED | reason=empty_dataframe"
        )

        raise ValueError(
            "Cannot load empty dataframe"
        )


    logger.info(
        "LOAD_STARTED | rows=%s | destination=%s",
        len(df),
        OUTPUT_FILE
    )


    try:

        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        df.to_csv(
            OUTPUT_FILE,
            index=False
        )


        logger.info(
            "LOAD_COMPLETED | rows=%s | destination=%s",
            len(df),
            OUTPUT_FILE
        )


    except Exception as error:

        logger.error(
            "LOAD_FAILED | reason=%s",
            error
        )

        raise



if __name__ == "__main__":

    logger.info(
        "load.py is ready. Call load_csv(df) from pipeline.py"
    )