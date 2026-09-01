from collections.abc import Iterator
from typing import Any
import urllib.parse
import xml.etree.ElementTree as ET

from researchflow.http import HTTPClient
from researchflow.models import Paper
from researchflow.processing import normalize_paper
from researchflow.sources.base import PaperSource


ARXIV_API_URL = "https://export.arxiv.org/api/query"

ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
}


class ArxivSource(PaperSource):
    """Search research papers using the arXiv API."""

    name = "arXiv"

    def __init__(
        self,
        *,
        timeout: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
    ):
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
        """Search arXiv and yield normalized Paper objects."""

        if max_results <= 0:
            return

        batch_size = min(max_results, 100)

        start = 0

        with self.http_client:
            while start < max_results:

                params = {
                    "search_query": f"all:{query}",
                    "start": start,
                    "max_results": batch_size,
                    "sortBy": "relevance",
                    "sortOrder": "descending",
                }

                response = self.http_client.get(
                    ARXIV_API_URL,
                    params=params,
                )

                root = ET.fromstring(
                    response.text
                )

                entries = root.findall(
                    "atom:entry",
                    ATOM_NS,
                )

                if not entries:
                    break

                for entry in entries:
                    if start >= max_results:
                        return

                    paper = self._parse_result(
                        entry,
                        query=query,
                    )

                    yield paper

                    start += 1

                if len(entries) < batch_size:
                    break

    def _parse_result(
        self,
        entry: ET.Element,
        *,
        query: str,
    ) -> Paper:
        """Convert an arXiv entry into a Paper."""

        id_element = entry.find(
            "atom:id",
            ATOM_NS,
        )

        title_element = entry.find(
            "atom:title",
            ATOM_NS,
        )

        summary_element = entry.find(
            "atom:summary",
            ATOM_NS,
        )

        published_element = entry.find(
            "atom:published",
            ATOM_NS,
        )

        paper_id = (
            id_element.text.strip()
            if id_element is not None
            and id_element.text
            else ""
        )

        title = (
            title_element.text.strip()
            if title_element is not None
            and title_element.text
            else None
        )

        abstract = (
            summary_element.text.strip()
            if summary_element is not None
            and summary_element.text
            else None
        )

        year = None

        if (
            published_element is not None
            and published_element.text
        ):
            try:
                year = int(
                    published_element.text[:4]
                )
            except ValueError:
                year = None

        authors = []

        for author in entry.findall(
            "atom:author",
            ATOM_NS,
        ):
            name_element = author.find(
                "atom:name",
                ATOM_NS,
            )

            if (
                name_element is not None
                and name_element.text
            ):
                authors.append(
                    {
                        "display_name": (
                            name_element.text.strip()
                        )
                    }
                )

        doi = None

        for identifier in entry.findall(
            "atom:link",
            ATOM_NS,
        ):
            rel = identifier.get("rel")
            href = identifier.get("href")

            if (
                rel == "related"
                and href
                and "doi.org" in href
            ):
                doi = href.replace(
                    "https://doi.org/",
                    "",
                )
                break

        paper_url = paper_id

        pdf_url = None

        for link in entry.findall(
            "atom:link",
            ATOM_NS,
        ):
            href = link.get("href")
            link_type = link.get("type")

            if (
                href
                and link_type == "application/pdf"
            ):
                pdf_url = href
                break

        categories = []

        for category in entry.findall(
            "atom:category",
            ATOM_NS,
        ):
            term = category.get("term")

            if term:
                categories.append(term)

        return normalize_paper(
            paper_id=paper_id,
            title=title,
            authors=authors,
            abstract=abstract,
            keywords=categories,
            year=year,
            source=self.name,
            doi=doi,
            paper_url=paper_url,
            pdf_url=pdf_url,
            search_query=query,
        )