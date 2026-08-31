import json
import logging
from pathlib import Path

import requests

from .config import (
    SYMBOLS,
    FROM_DATE,
    TO_DATE,
)

from .apifetch import fetch_candles

from .http_errors import (
    QuotaExhausted,
    BadRequest,
    ConnectionFailed,
    InvalidResponse,
)

from .logging_config import configure_logging


logger = logging.getLogger(__name__)


OUTPUT = Path(
    "data/raw/fauxnance.json"
)


def extract():

    configure_logging()

    results = {}

    for symbol in SYMBOLS:

        logger.info(
            "FETCHING_SYMBOL | symbol=%s | from=%s | to=%s",
            symbol,
            FROM_DATE,
            TO_DATE,
        )

        try:

            response = fetch_candles(
                symbol=symbol,
                from_date=FROM_DATE,
                to_date=TO_DATE,
            )

            # Keep raw response unchanged
            results[symbol] = response

            candle_count = len(
                response.get("data", {}).get("candles", [])
            )

            logger.info(
                "SYMBOL_FETCHED | symbol=%s | candles=%s",
                symbol,
                candle_count,
            )

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

        except InvalidResponse as error:

            logger.warning(
                "SYMBOL_SKIPPED | symbol=%s | reason=%s",
                symbol,
                error,
            )

            # A 200 response with a non-JSON body is not loadable data.
            continue

        except requests.HTTPError as error:

            status = error.response.status_code if error.response is not None else "unknown"

            # 429 from apifetch — treat same as QuotaExhausted
            if status == 429:
                logger.error(
                    "BATCH_STOPPED | symbol=%s | reason=quota_exhausted | status=429",
                    symbol,
                )
                raise QuotaExhausted(
                    "Fauxnance API quota exhausted",
                ) from error

            # Other 4xx — skip symbol
            if isinstance(status, int) and 400 <= status < 500:
                logger.warning(
                    "SYMBOL_SKIPPED | symbol=%s | reason=http_%s",
                    symbol,
                    status,
                )
                continue

            # 5xx or unknown — skip symbol
            logger.warning(
                "SYMBOL_FAILED | symbol=%s | reason=http_%s",
                symbol,
                status,
            )
            continue

        except requests.RequestException as error:

            logger.warning(
                "SYMBOL_FAILED | symbol=%s | reason=%s",
                symbol,
                error,
            )

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