from collections.abc import Iterator
from typing import Any

from researchflow.http import HTTPClient
from researchflow.models import Paper
from researchflow.processing import normalize_paper
from researchflow.sources.base import PaperSource


CROSSREF_API_URL = "https://api.crossref.org/works"


class CrossrefSource(PaperSource):
    """Search research papers using the Crossref API."""

    name = "Crossref"

    def __init__(
        self,
        *,
        mailto: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
    ):
        self.mailto = mailto
        self.timeout = timeout

        self.http_client = HTTPClient(
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )

    def search(
        self,
        query: str,
        *,
        max_results: int = 100,
    ) -> Iterator[Paper]:
        """Search Crossref and yield normalized Paper objects."""

        if max_results <= 0:
            return

        rows = min(max_results, 1000)

        params: dict[str, Any] = {
            "query.bibliographic": query,
            "rows": rows,
            "offset": 0,
        }

        if self.mailto:
            params["mailto"] = self.mailto

        collected = 0

        with self.http_client:
            while collected < max_results:
                response = self.http_client.get(
                    CROSSREF_API_URL,
                    params=params,
                )

                data = response.json()

                message = data.get(
                    "message",
                    {},
                )

                results = message.get(
                    "items",
                    [],
                )

                if not results:
                    break

                for result in results:
                    if collected >= max_results:
                        return

                    yield self._parse_result(
                        result,
                        query=query,
                    )

                    collected += 1

                if len(results) < rows:
                    break

                params["offset"] += rows

    def _parse_result(
        self,
        result: dict[str, Any],
        *,
        query: str,
    ) -> Paper:
        """Convert a Crossref result into a Paper."""

        authors = result.get(
            "author",
            [],
        )

        title_data = result.get(
            "title",
            [],
        )

        title = (
            title_data[0]
            if title_data
            else None
        )

        published = (
            result.get("published-print")
            or result.get("published-online")
            or result.get("published")
            or result.get("issued")
            or {}
        )

        date_parts = published.get(
            "date-parts",
            [],
        )

        year = None

        if date_parts and date_parts[0]:
            year = date_parts[0][0]

        doi = result.get("DOI")

        paper_url = result.get(
            "URL"
        )

        abstract = result.get(
            "abstract"
        )

        pdf_url = self._extract_pdf_url(
            result
        )

        return normalize_paper(
            paper_id=doi or result.get(
                "URL",
                "",
            ),
            title=title,
            authors=authors,
            abstract=abstract,
            keywords=[],
            year=year,
            source=self.name,
            doi=doi,
            paper_url=paper_url,
            pdf_url=pdf_url,
            search_query=query,
        )

    @staticmethod
    def _extract_pdf_url(
        result: dict[str, Any],
    ) -> str | None:
        """Extract a PDF URL from Crossref link metadata."""

        links = result.get(
            "link",
            [],
        )

        for link in links:
            if not isinstance(link, dict):
                continue

            content_type = link.get(
                "content-type",
                "",
            )

            url = link.get(
                "URL"
            )

            if (
                url
                and content_type.lower()
                == "application/pdf"
            ):
                return url

        return None