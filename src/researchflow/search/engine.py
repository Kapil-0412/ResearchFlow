from collections.abc import Iterable

from researchflow.models import Paper
from researchflow.sources.base import PaperSource


class SearchEngine:
    """Coordinate searches across registered paper sources."""

    def __init__(
        self,
        sources: Iterable[PaperSource],
    ):
        self.sources = list(sources)

    def search(
        self,
        query: str,
        *,
        max_results_per_source: int = 100,
    ) -> list[Paper]:
        """Search all registered sources for one query."""

        if not query.strip():
            return []

        papers: list[Paper] = []

        for source in self.sources:
            papers.extend(
                source.search(
                    query,
                    max_results=max_results_per_source,
                )
            )

        return papers

    def search_many(
        self,
        queries: Iterable[str],
        *,
        max_results_per_source: int = 100,
    ) -> list[Paper]:
        """
        Search all registered sources for multiple queries.

        Duplicate papers are merged into a single Paper record while
        preserving the queries and sources that discovered the paper.
        """

        merged_papers: dict[str, Paper] = {}

        for query in queries:
            query = query.strip()

            if not query:
                continue

            papers = self.search(
                query,
                max_results_per_source=max_results_per_source,
            )

            for paper in papers:
                self._merge_paper(
                    merged_papers,
                    paper,
                    query=query,
                )

        return list(merged_papers.values())

    @staticmethod
    def _merge_paper(
        merged_papers: dict[str, Paper],
        paper: Paper,
        *,
        query: str,
    ) -> None:
        """Merge a paper into the accumulated search results."""

        paper_key = SearchEngine._paper_key(paper)

        if paper_key not in merged_papers:
            paper.found_in_keywords = [query]
            paper.found_in_sources = [paper.source]

            merged_papers[paper_key] = paper
            return

        existing = merged_papers[paper_key]

        if query not in existing.found_in_keywords:
            existing.found_in_keywords.append(query)

        if paper.source not in existing.found_in_sources:
            existing.found_in_sources.append(paper.source)

    @staticmethod
    def _paper_key(paper: Paper) -> str:
        """
        Return a stable key used for basic duplicate detection.

        DOI is preferred because it is generally a stronger identifier
        than title. When DOI is unavailable, paper_id is used.
        """

        if paper.doi:
            return f"doi:{paper.doi.strip().lower()}"

        return f"id:{paper.paper_id.strip().lower()}"