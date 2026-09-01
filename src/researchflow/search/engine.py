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