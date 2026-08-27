import json
import logging
import os
from pathlib import Path

from config import (
    SYMBOLS,
    API_URL,
)

from http_errors import (
    fetch_with_retry,
    QuotaExhausted,
    BadRequest,
    ConnectionFailed,
)

from logging_config import configure_logging


logger = logging.getLogger(__name__)


OUTPUT = Path(
    "data/raw/fauxnance.json"
)


def extract():

    configure_logging()

    api_key = os.getenv(
        "FAUXNANCE_API_KEY"
    )

    if not api_key:
        raise EnvironmentError(
            "FAUXNANCE_API_KEY is not set"
        )


    results = {}


    for symbol in SYMBOLS:

        logger.info(
            "FETCHING_SYMBOL | symbol=%s",
            symbol
        )


        url = (
            f"{API_URL}/candles/{symbol}"
        )


        try:

            response = fetch_with_retry(
                url=url,
                api_key=api_key,
                symbol=symbol,
            )


            # Keep raw response unchanged
            results[symbol] = response


        except QuotaExhausted as error:

            logger.error(
                "BATCH_STOPPED | symbol=%s | reason=%s",
                symbol,
                error,
            )

            # Quota affects every remaining request.
            # Continuing would waste time.
            raise


        except BadRequest as error:

            logger.warning(
                "SYMBOL_SKIPPED | symbol=%s | reason=%s",
                symbol,
                error,
            )

            # Bad symbol/request should not kill whole batch.
            continue


        except ConnectionFailed as error:

            logger.warning(
                "SYMBOL_FAILED | symbol=%s | reason=%s",
                symbol,
                error,
            )

            # Move to next symbol.
            continue



    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    with open(
        OUTPUT,
        "w"
    ) as file:

        json.dump(
            results,
            file,
            indent=2
        )


    logger.info(
        "RAW_DATA_SAVED | path=%s | symbols=%s",
        OUTPUT,
        len(results),
    )


    return results



if __name__ == "__main__":

    extract()