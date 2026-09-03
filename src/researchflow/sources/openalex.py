from collections.abc import Iterator
from typing import Any

from researchflow.http import HTTPClient
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
        """Search OpenAlex and yield normalized Paper objects."""

        if max_results <= 0:
            return

        per_page = min(max_results, 100)

        params: dict[str, Any] = {
            "search": query,
            "per-page": per_page,
            "page": 1,
        }

        if self.mailto:
            params["mailto"] = self.mailto

        collected = 0

        with self.http_client:
            while collected < max_results:
                response = self.http_client.get(
                    OPENALEX_API_URL,
                    params=params,
                )

                data = response.json()

                results = data.get(
                    "results",
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

                # If OpenAlex returned fewer results than requested,
                # there are no more results on the next page.
                if len(results) < per_page:
                    break

                params["page"] += 1

    def _parse_result(
        self,
        result: dict[str, Any],
        *,
        query: str,
    ) -> Paper:
        """Convert an OpenAlex result into a Paper."""

        authors = []

        for authorship in result.get(
            "authorships",
            [],
        ):
            author = authorship.get(
                "author",
                {},
            )

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

        # OpenAlex may return pdf_url as either:
        # 1. a dictionary: {"url": "..."}
        # 2. a string: "https://..."
        # 3. None
        pdf_data = primary_location.get(
            "pdf_url"
        )

        if isinstance(pdf_data, dict):
            pdf_url = pdf_data.get(
                "url"
            )
        elif isinstance(pdf_data, str):
            pdf_url = pdf_data
        else:
            pdf_url = None

        return normalize_paper(
            paper_id=result.get(
                "id",
                "",
            ),
            title=result.get(
                "title"
            ),
            authors=authors,
            abstract=self._reconstruct_abstract(
                result.get(
                    "abstract_inverted_index"
                )
            ),
            keywords=[
                keyword.get(
                    "display_name"
                )
                for keyword in result.get(
                    "keywords",
                    [],
                )
                if keyword.get(
                    "display_name"
                )
            ],
            year=result.get(
                "publication_year"
            ),
            source=self.name,
            doi=result.get(
                "doi"
            ),
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
                words.append(
                    (
                        position,
                        word,
                    )
                )

        words.sort(
            key=lambda item: item[0]
        )

        return " ".join(
            word
            for _, word in words
        )