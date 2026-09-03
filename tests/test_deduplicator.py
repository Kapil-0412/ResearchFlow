from researchflow.models import Paper
from researchflow.processing import PaperDeduplicator


def test_deduplicates_same_doi():
    papers = [
        Paper(
            paper_id="P001",
            title="Counterfactual Cyber Attack Reasoning",
            source="IEEE",
            doi="10.1234/example",
            found_in_keywords=["counterfactual cybersecurity"],
        ),
        Paper(
            paper_id="P002",
            title="Counterfactual Cyber Attack Reasoning",
            source="ACM",
            doi="https://doi.org/10.1234/example",
            found_in_keywords=["attack path reasoning"],
        ),
    ]

    deduplicator = PaperDeduplicator()

    result = deduplicator.deduplicate(papers)

    assert len(result) == 1

    paper = result[0]

    assert paper.found_in_keywords == [
        "counterfactual cybersecurity",
        "attack path reasoning",
    ]

    assert paper.found_in_sources == [
        "IEEE",
        "ACM",
    ]


def test_deduplicates_same_title_without_doi():
    papers = [
        Paper(
            paper_id="P001",
            title="Cyber Attack Path Analysis",
            source="IEEE",
        ),
        Paper(
            paper_id="P002",
            title="CYBER ATTACK PATH ANALYSIS!",
            source="Springer",
        ),
    ]

    deduplicator = PaperDeduplicator()

    result = deduplicator.deduplicate(papers)

    assert len(result) == 1


def test_does_not_merge_different_papers():
    papers = [
        Paper(
            paper_id="P001",
            title="Cyber Attack Path Analysis",
            source="IEEE",
        ),
        Paper(
            paper_id="P002",
            title="Knowledge Graph Based Malware Detection",
            source="ACM",
        ),
    ]

    deduplicator = PaperDeduplicator()

    result = deduplicator.deduplicate(papers)

    assert len(result) == 2


def test_deduplicator_preserves_search_query():
    papers = [
        Paper(
            paper_id="P001",
            title="Shared Paper",
            source="IEEE",
            search_query="counterfactual attack",
        ),
        Paper(
            paper_id="P002",
            title="Shared Paper",
            source="ACM",
            search_query="cyber attack reasoning",
        ),
    ]

    deduplicator = PaperDeduplicator()

    result = deduplicator.deduplicate(papers)

    assert len(result) == 1

    assert result[0].found_in_keywords == [
        "counterfactual attack",
        "cyber attack reasoning",
    ]