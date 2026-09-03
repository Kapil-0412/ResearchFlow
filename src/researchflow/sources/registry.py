from researchflow.search import SearchEngine

from .arxiv import ArxivSource
from .crossref import CrossrefSource
from .openalex import OpenAlexSource


def build_search_engine() -> SearchEngine:
    """Build a SearchEngine with all currently supported sources."""

    return SearchEngine(
        [
            OpenAlexSource(),
            CrossrefSource(),
            ArxivSource(),
        ]
    )