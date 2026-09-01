from collections.abc import Iterator

from researchflow.models import Paper
from researchflow.search import SearchEngine
from researchflow.sources.base import PaperSource


class FakeSource(PaperSource):
    """Fake source used for testing the search engine."""

    name = "FakeSource"

    def search(
        self,
        query: str,
        *,
        max_results: int = 100,
    ) -> Iterator[Paper]:
        yield Paper(
            paper_id="FAKE001",
            title=f"Result for {query}",
            authors=["Test Author"],
            year=2026,
            source=self.name,
            search_query=query,
        )


def test_search_engine_searches_registered_source():
    source = FakeSource()

    engine = SearchEngine([source])

    papers = engine.search(
        "counterfactual cyber attack",
        max_results_per_source=5,
    )

    assert len(papers) == 1

    assert papers[0].title == (
        "Result for counterfactual cyber attack"
    )

    assert papers[0].source == "FakeSource"

    assert papers[0].search_query == (
        "counterfactual cyber attack"
    )


def test_search_engine_supports_multiple_sources():
    source_one = FakeSource()
    source_two = FakeSource()

    engine = SearchEngine(
        [
            source_one,
            source_two,
        ]
    )

    papers = engine.search(
        "knowledge graph",
        max_results_per_source=5,
    )

    assert len(papers) == 2


def test_empty_query_returns_no_results():
    source = FakeSource()

    engine = SearchEngine([source])

    papers = engine.search("   ")

    assert papers == []