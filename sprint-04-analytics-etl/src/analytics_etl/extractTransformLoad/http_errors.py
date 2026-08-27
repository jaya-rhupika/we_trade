"""
HTTP error handling for the Fauxnance API.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import requests


logger = logging.getLogger(__name__)


class QuotaExhausted(Exception):
    """Raised when Fauxnance returns HTTP 429."""

    def __init__(self, message: str, retry_after: str | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class BadRequest(Exception):
    """Raised for HTTP 4xx responses other than 429."""

    def __init__(self, status_code: int, reason: str) -> None:
        super().__init__(f"HTTP {status_code}: {reason}")
        self.status_code = status_code
        self.reason = reason


class ConnectionFailed(Exception):
    """Raised when network/timeout retries are exhausted."""

    def __init__(self, message: str, retry_count: int) -> None:
        super().__init__(message)
        self.retry_count = retry_count


def fetch_with_retry(
    url: str,
    api_key: str,
    symbol: str,
    timeout: int = 10,
    max_retries: int = 3,
    backoff_seconds: float = 1.0,
) -> dict[str, Any]:
    """
    HTTP 200 -> return decoded JSON unchanged.
    HTTP 429: Log the quota failure and raise QuotaExhausted. Retry-After is captured but the function does not sleep until the quota resets.
    Other HTTP 4xx: Log the bad request and raise BadRequest. These errors are not retried.
    HTTP 5xx: Treat as a retryable connection-style failure.
    """

    if not api_key:
        raise ValueError("api_key must not be empty")

    headers = {
        "X-Api-Key": api_key,
    }

    backoff = backoff_seconds

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout,
            )

            # ---------------------------------------------------------
            # 429: quota exhausted
            # ---------------------------------------------------------
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")

                logger.error(
                    "QUOTA_EXHAUSTED | symbol=%s | status=429 | "
                    "retry_after=%s | action=stop",
                    symbol,
                    retry_after if retry_after is not None else "unknown",
                )

                raise QuotaExhausted(
                    "Fauxnance API quota exhausted",
                    retry_after=retry_after,
                )

            # ---------------------------------------------------------
            # Other 4xx: request is bad; don't retry
            # ---------------------------------------------------------
            if 400 <= response.status_code < 500:
                reason = response.text[:200]

                logger.warning(
                    "BAD_REQUEST | symbol=%s | status=%s | "
                    "reason=%s | action=skip_symbol",
                    symbol,
                    response.status_code,
                    reason,
                )

                raise BadRequest(
                    status_code=response.status_code,
                    reason=reason,
                )

            # ---------------------------------------------------------
            # 200: successful HTTP request.
            #
            # IMPORTANT:
            # We return the raw JSON unchanged. Validation belongs
            # to transform/candle_validator.py.
            # ---------------------------------------------------------
            if response.status_code == 200:
                logger.info(
                    "EXTRACTED | symbol=%s | status=200 | "
                    "response_bytes=%s",
                    symbol,
                    len(response.content),
                )

                return response.json()

            # ---------------------------------------------------------
            # 5xx: server-side failure.
            #
            # Treat it as retryable.
            # ---------------------------------------------------------
            if 500 <= response.status_code < 600:
                raise requests.ConnectionError(
                    f"Fauxnance returned HTTP {response.status_code}"
                )

            # Unexpected status code.
            raise requests.ConnectionError(
                f"Unexpected HTTP status {response.status_code}"
            )

        except QuotaExhausted:
            # Never retry a quota exhaustion.
            raise

        except BadRequest:
            # Never retry a bad request.
            raise

        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt < max_retries:
                logger.debug(
                    "RETRY | symbol=%s | attempt=%s/%s | "
                    "error=%s | backoff_seconds=%s",
                    symbol,
                    attempt,
                    max_retries,
                    type(exc).__name__,
                    backoff,
                )

                time.sleep(backoff)
                backoff *= 2
                continue

            logger.warning(
                "CONNECTION_FAILED | symbol=%s | attempts=%s | "
                "error=%s | action=skip_symbol",
                symbol,
                max_retries,
                type(exc).__name__,
            )

            raise ConnectionFailed(
                str(exc),
                retry_count=max_retries,
            ) from exc

    # This is unreachable, but keeps the function explicit.
    raise ConnectionFailed(
        "Request failed after all retry attempts",
        retry_count=max_retries,
    )