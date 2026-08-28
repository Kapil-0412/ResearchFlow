from collections.abc import Iterator
from typing import Any

import httpx

from researchflow.models import Paper
from researchflow.processing import normalize_paper
from researchflow.sources.base import PaperSource


OPENALEX_API_URL = "https://api.openalex.org/works"


class OpenAlexSource(PaperSource):
    """Search research papers using the OpenAlex API."""

    name = "OpenAlex"

    def __init__(
        self,
        *,
        mailto: str | None = None,
        timeout: float = 30.0,
    ):
        self.mailto = mailto
        self.timeout = timeout

    def search(
        self,
        query: str,
        *,
        max_results: int = 100,
    ) -> Iterator[Paper]:
        """Search OpenAlex and yield normalized Paper objects."""

        if max_results <= 0:
            return

        params: dict[str, Any] = {
            "search": query,
            "per-page": min(max_results, 100),
            "page": 1,
        }

        if self.mailto:
            params["mailto"] = self.mailto

        with httpx.Client(timeout=self.timeout) as client:
            while True:
                response = client.get(
                    OPENALEX_API_URL,
                    params=params,
                )

                response.raise_for_status()

                data = response.json()

                results = data.get("results", [])

                if not results:
                    break

                for result in results:
                    yield self._parse_result(
                        result,
                        query=query,
                    )

                    if (
                        params["page"] * params["per-page"]
                        >= max_results
                    ):
                        return

                params["page"] += 1

    def _parse_result(
        self,
        result: dict[str, Any],
        *,
        query: str,
    ) -> Paper:
        """Convert an OpenAlex result into a Paper."""

        authors = []

        for authorship in result.get("authorships", []):
            author = authorship.get("author", {})

            if author:
                authors.append(
                    {
                        "display_name": author.get(
                            "display_name"
                        )
                    }
                )

        primary_location = result.get(
            "primary_location"
        ) or {}

        landing_page_url = primary_location.get(
            "landing_page_url"
        )

        pdf_url = (
            primary_location
            .get("pdf_url")
            or {}
        ).get("url")

        return normalize_paper(
            paper_id=result.get("id", ""),
            title=result.get("title"),
            authors=authors,
            abstract=self._reconstruct_abstract(
                result.get("abstract_inverted_index")
            ),
            keywords=[
                keyword.get("display_name")
                for keyword in result.get("keywords", [])
                if keyword.get("display_name")
            ],
            year=result.get("publication_year"),
            source=self.name,
            doi=result.get("doi"),
            paper_url=landing_page_url,
            pdf_url=pdf_url,
            search_query=query,
        )

    @staticmethod
    def _reconstruct_abstract(
        inverted_index: dict[str, list[int]] | None,
    ) -> str | None:
        """Reconstruct an abstract from OpenAlex's inverted index."""

        if not inverted_index:
            return None

        words = []

        for word, positions in inverted_index.items():
            for position in positions:
                words.append((position, word))

        words.sort(key=lambda item: item[0])

        return " ".join(
            word
            for _, word in words
        )