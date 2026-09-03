import pytest

from researchflow.models import Paper
from researchflow.sources import PaperSource


def test_paper_source_requires_search_implementation():
    with pytest.raises(TypeError):
        PaperSource()


def test_source_implementation():

    class TestSource(PaperSource):
        name = "TestSource"

        def search(
            self,
            query: str,
            *,
            max_results: int = 100,
        ):
            yield Paper(
                paper_id="TEST001",
                title="Test Paper",
                source=self.name,
            )

    source = TestSource()

    papers = list(
        source.search(
            "test query",
            max_results=10,
        )
    )

    assert len(papers) == 1
    assert papers[0].paper_id == "TEST001"
    assert papers[0].source == "TestSource"