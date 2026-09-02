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

        if query == "first keyword":
            yield Paper(
                paper_id="P001",
                title="Shared Research Paper",
                authors=["Test Author"],
                year=2026,
                source=self.name,
                doi="10.1234/shared",
                search_query=query,
            )

        elif query == "second keyword":
            yield Paper(
                paper_id="P001",
                title="Shared Research Paper",
                authors=["Test Author"],
                year=2026,
                source=self.name,
                doi="10.1234/shared",
                search_query=query,
            )

        else:
            yield Paper(
                paper_id=f"FAKE-{query}",
                title=f"Result for {query}",
                authors=["Test Author"],
                year=2026,
                source=self.name,
                search_query=query,
            )


class SecondFakeSource(PaperSource):
    """Second fake source used to test cross-source duplicates."""

    name = "SecondFakeSource"

    def search(
        self,
        query: str,
        *,
        max_results: int = 100,
    ) -> Iterator[Paper]:

        if query == "first keyword":
            yield Paper(
                paper_id="SECOND001",
                title="Shared Research Paper",
                authors=["Test Author"],
                year=2026,
                source=self.name,
                doi="10.1234/shared",
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


def test_search_many_tracks_multiple_keywords():
    source = FakeSource()

    engine = SearchEngine([source])

    papers = engine.search_many(
        [
            "first keyword",
            "second keyword",
        ],
        max_results_per_source=5,
    )

    assert len(papers) == 1

    paper = papers[0]

    assert paper.paper_id == "P001"

    assert paper.title == "Shared Research Paper"

    assert paper.found_in_keywords == [
        "first keyword",
        "second keyword",
    ]

    assert paper.found_in_sources == [
        "FakeSource",
    ]


def test_search_many_tracks_multiple_sources():
    source_one = FakeSource()
    source_two = SecondFakeSource()

    engine = SearchEngine(
        [
            source_one,
            source_two,
        ]
    )

    papers = engine.search_many(
        ["first keyword"],
        max_results_per_source=5,
    )

    assert len(papers) == 1

    paper = papers[0]

    assert paper.title == "Shared Research Paper"

    assert paper.found_in_keywords == [
        "first keyword",
    ]

    assert paper.found_in_sources == [
        "FakeSource",
        "SecondFakeSource",
    ]


def test_search_many_ignores_empty_queries():
    source = FakeSource()

    engine = SearchEngine([source])

    papers = engine.search_many(
        [
            "   ",
            "",
        ]
    )

    assert papers == []