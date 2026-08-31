from pathlib import Path
import logging

import duckdb
import pandas as pd


DATABASE_FILE = Path(
    "data/analytics.duckdb"
)

PROCESSED_CSV = Path(
    "data/processed/candles.csv"
)


logger = logging.getLogger(__name__)


def create_database():

    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = duckdb.connect(
        str(DATABASE_FILE)
    )

    logger.info(
        "DATABASE_CONNECTED | destination=%s",
        DATABASE_FILE
    )

    return connection


def create_staging_schema(connection):

    connection.execute(
        """
        CREATE SCHEMA IF NOT EXISTS staging
        """
    )

    logger.info(
        "STAGING_SCHEMA_READY"
    )


def save_processed_csv(df: pd.DataFrame):

    """
    Write the cleaned DataFrame to data/processed/candles.csv
    so the processed data is visible without opening DuckDB.
    """

    PROCESSED_CSV.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        PROCESSED_CSV,
        index=False
    )

    logger.info(
        "PROCESSED_CSV_SAVED | path=%s | rows=%s",
        PROCESSED_CSV,
        len(df),
    )


def load_to_duckdb(df: pd.DataFrame):

    """
    Load transformed market data into DuckDB and save
    a processed CSV alongside it.

    The transformed market data is stored in
    staging.candles.

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
        DATABASE_FILE
    )

    # Save processed CSV so data is inspectable without DuckDB
    save_processed_csv(df)

    connection = None

    try:

        connection = create_database()

        create_staging_schema(
            connection
        )

        connection.register(
            "transformed_candles",
            df
        )

        connection.execute(
            """
            CREATE OR REPLACE TABLE staging.candles AS
            SELECT *
            FROM transformed_candles
            """
        )

        connection.unregister(
            "transformed_candles"
        )

        loaded_rows = connection.execute(
            """
            SELECT COUNT(*)
            FROM staging.candles
            """
        ).fetchone()[0]

        logger.info(
            "LOAD_COMPLETED | rows=%s | destination=%s",
            loaded_rows,
            DATABASE_FILE
        )

    except Exception as error:

        logger.error(
            "LOAD_FAILED | reason=%s",
            error
        )

        raise

    finally:

        if connection is not None:

            connection.close()

            logger.info(
                "DATABASE_CONNECTION_CLOSED"
            )


def load_dim_account(connection, data=None):

    """
    Placeholder for loading DIM_ACCOUNT.

    Account data will be loaded when the required
    account source data becomes available.
    """

    pass


def load_dim_instrument(connection, data=None):

    """
    Placeholder for loading DIM_INSTRUMENT.

    Instrument data will be loaded when the required
    instrument source data becomes available.
    """

    pass


def load_dim_date(connection, data=None):

    """
    Placeholder for loading DIM_DATE.

    Date dimension data will be loaded when the
    required analytical source data becomes available.
    """

    pass


def load_fact_trades(connection, data=None):

    """
    Placeholder for loading FACT_TRADES.

    Trade data will be loaded after the required
    account, instrument, date, and trade data
    becomes available.
    """

    pass


if __name__ == "__main__":

    logger.info(
        "load.py is ready. "
        "Use load_to_duckdb(df) from pipeline.py"
    )