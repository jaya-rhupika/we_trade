from pathlib import Path

import duckdb


DATABASE_FILE = Path(
    "data/analytics.duckdb"
)

SCHEMA_FILE = Path(
    "../../../contracts/analytics-schema.sql"
)

PROCESSED_FILE = Path(
    "data/processed/candles.csv"
)


def create_database():

    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = duckdb.connect(
        str(DATABASE_FILE)
    )

    schema_sql = SCHEMA_FILE.read_text(
        encoding="utf-8"
    )

    connection.execute(
        schema_sql.replace(
            "CREATE TABLE",
            "CREATE TABLE IF NOT EXISTS"
        )
    )

    return connection


def create_staging_schema(connection):

    connection.execute(
        """
        CREATE SCHEMA IF NOT EXISTS staging
        """
    )

    print(
        "Staging schema created successfully."
    )


def load_processed_csv(connection):

    if not PROCESSED_FILE.exists():

        raise FileNotFoundError(
            f"Processed file not found: {PROCESSED_FILE}"
        )

    connection.execute(
        """
        CREATE OR REPLACE TABLE staging.candles AS
        SELECT *
        FROM read_csv_auto(?)
        """,
        [
            str(PROCESSED_FILE)
        ]
    )

    print(
        f"Processed CSV loaded successfully into "
        f"staging.candles"
    )


def show_staging_data(connection):

    print(
        "\nStaging table:"
    )

    print(
        connection.sql(
            """
            SELECT *
            FROM staging.candles
            LIMIT 10
            """
        )
    )

    print(
        "\nNumber of rows:"
    )

    print(
        connection.sql(
            """
            SELECT COUNT(*)
            FROM staging.candles
            """
        )
    )


def fill_dim_account(connection):

    """
    Placeholder for the future DIM_ACCOUNT load.

    This function will populate DIM_ACCOUNT once
    account data becomes available.
    """

    pass


def fill_dim_instrument(connection):

    """
    Placeholder for the future DIM_INSTRUMENT load.

    This function will populate DIM_INSTRUMENT once
    instrument data becomes available.
    """

    pass


def fill_dim_date(connection):

    """
    Placeholder for the future DIM_DATE load.

    This function will populate DIM_DATE once
    the required analytical date data becomes available.
    """

    pass


def fill_fact_trades(connection):

    """
    Placeholder for the future FACT_TRADES load.

    This function will populate FACT_TRADES once
    account, instrument, date, and trade data becomes available.
    """

    pass


if __name__ == "__main__":

    connection = create_database()

    print(
        "\nAnalytical tables:"
    )

    print(
        connection.sql(
            "SHOW TABLES"
        )
    )

    create_staging_schema(
        connection
    )

    load_processed_csv(
        connection
    )

    show_staging_data(
        connection
    )

    print(
        "\nStar schema load functions:"
    )

    print(
        "DIM_ACCOUNT      -> placeholder"
    )

    print(
        "DIM_INSTRUMENT   -> placeholder"
    )

    print(
        "DIM_DATE         -> placeholder"
    )

    print(
        "FACT_TRADES      -> placeholder"
    )

    connection.close()