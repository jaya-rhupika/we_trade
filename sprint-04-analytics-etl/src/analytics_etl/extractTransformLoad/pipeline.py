from .extract import extract
from .transform import clean_data
from .load import load_to_duckdb


def run_pipeline():

    print(
        "Starting pipeline"
    )


    # Extract API data
    extract()


    # Transform raw JSON into dataframe
    df = clean_data()


    # Load dataframe into CSV
    load_to_duckdb(df)


    print(
        "Pipeline completed successfully"
    )



if __name__ == "__main__":

    run_pipeline()