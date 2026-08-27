from .extract import extract
from .transform import clean_data
from .load import load_csv


def run_pipeline():

    print(
        "Starting pipeline"
    )


    # Extract API data
    extract()


    # Transform raw JSON into dataframe
    df = clean_data()


    # Load dataframe into CSV
    load_csv(df)


    print(
        "Pipeline completed successfully"
    )



if __name__ == "__main__":

    run_pipeline()