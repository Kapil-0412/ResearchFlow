from collections.abc import Iterator
from typing import Any

from researchflow.http import HTTPClient
from researchflow.models import Paper
from researchflow.processing import normalize_paper
from researchflow.sources.base import PaperSource


SEMANTIC_SCHOLAR_API_URL = (
    "https://api.semanticscholar.org/graph/v1/paper/search"
)


class SemanticScholarSource(PaperSource):
    """Search research papers using the Semantic Scholar API."""

    name = "Semantic Scholar"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
    ):
        self.api_key = api_key
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
        """Search Semantic Scholar and yield normalized Paper objects."""

        if max_results <= 0:
            return

        limit = min(max_results, 100)

        params: dict[str, Any] = {
            "query": query,
            "limit": limit,
            "offset": 0,
            "fields": (
                "paperId,title,authors,abstract,year,"
                "externalIds,url,openAccessPdf,venue,"
                "publicationDate"
            ),
        }

        headers: dict[str, str] = {}

        if self.api_key:
            headers["x-api-key"] = self.api_key

        collected = 0

        with self.http_client:
            while collected < max_results:
                response = self.http_client.get(
                    SEMANTIC_SCHOLAR_API_URL,
                    params=params,
                    headers=headers or None,
                )

                data = response.json()

                results = data.get(
                    "data",
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

                # Semantic Scholar returns the total number of
                # matching papers in "total".
                total = data.get("total")

                if total is not None:
                    if params["offset"] + len(results) >= total:
                        break

                # If fewer papers than requested were returned,
                # there is normally no next page.
                if len(results) < limit:
                    break

                params["offset"] += len(results)

    def _parse_result(
        self,
        result: dict[str, Any],
        *,
        query: str,
    ) -> Paper:
        """Convert a Semantic Scholar result into a Paper."""

        authors = []

        for author in result.get(
            "authors",
            [],
        ):
            if not isinstance(author, dict):
                continue

            name = author.get("name")

            if name:
                authors.append(
                    {
                        "display_name": name,
                    }
                )

        external_ids = result.get(
            "externalIds"
        ) or {}

        doi = external_ids.get("DOI")

        paper_id = result.get(
            "paperId"
        )

        if not paper_id:
            paper_id = (
                doi
                or result.get("url")
                or ""
            )

        open_access_pdf = result.get(
            "openAccessPdf"
        )

        pdf_url = None

        if isinstance(
            open_access_pdf,
            dict,
        ):
            pdf_url = open_access_pdf.get(
                "url"
            )
        elif isinstance(
            open_access_pdf,
            str,
        ):
            pdf_url = open_access_pdf

        paper_url = result.get(
            "url"
        )

        return normalize_paper(
            paper_id=paper_id,
            title=result.get("title"),
            authors=authors,
            abstract=result.get("abstract"),
            keywords=[],
            year=result.get("year"),
            source=self.name,
            doi=doi,
            paper_url=paper_url,
            pdf_url=pdf_url,
            search_query=query,
        )