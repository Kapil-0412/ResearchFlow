import time
from types import TracebackType
from typing import Self

import httpx


class HTTPClient:
    """Reusable HTTP client with retry and rate-limit handling."""

    RETRY_STATUS_CODES = {
        429,
        500,
        502,
        503,
        504,
    }

    def __init__(
        self,
        *,
        timeout: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        self._client = httpx.Client(
            timeout=self.timeout,
        )

    def __enter__(self) -> Self:
        """Enter the HTTP client context."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the underlying HTTP client."""
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def get(
        self,
        url: str,
        *,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> httpx.Response:
        """Perform a GET request with retry handling."""

        for attempt in range(
            self.max_retries + 1
        ):
            try:
                response = self._client.get(
                    url,
                    params=params,
                    headers=headers,
                )

            except httpx.RequestError:
                if attempt >= self.max_retries:
                    raise

                self._sleep(attempt)
                continue

            if (
                response.status_code
                not in self.RETRY_STATUS_CODES
            ):
                response.raise_for_status()
                return response

            if attempt >= self.max_retries:
                response.raise_for_status()

            self._sleep(
                attempt,
                response=response,
            )

        raise RuntimeError(
            "HTTP request failed after retries."
        )

    def _sleep(
        self,
        attempt: int,
        *,
        response: httpx.Response | None = None,
    ) -> None:
        """Wait before retrying a request."""

        retry_after = None

        if response is not None:
            retry_after = response.headers.get(
                "Retry-After"
            )

        if retry_after is not None:
            try:
                delay = float(retry_after)
            except ValueError:
                delay = None
        else:
            delay = None

        if delay is None:
            delay = self.backoff_factor * (
                2 ** attempt
            )

        time.sleep(delay)