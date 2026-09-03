from researchflow.models import Paper
from researchflow.processing import (
    normalize_authors,
    normalize_keywords,
    normalize_paper,
)


def test_normalize_authors_from_strings():
    authors = normalize_authors(
        ["John Smith", "Jane Doe"]
    )

    assert authors == [
        "John Smith",
        "Jane Doe",
    ]


def test_normalize_authors_from_dictionaries():
    authors = normalize_authors(
        [
            {"display_name": "John Smith"},
            {"display_name": "Jane Doe"},
        ]
    )

    assert authors == [
        "John Smith",
        "Jane Doe",
    ]


def test_normalize_crossref_authors():
    authors = normalize_authors(
        [
            {
                "given": "John",
                "family": "Smith",
            }
        ]
    )

    assert authors == ["John Smith"]


def test_normalize_keywords():
    keywords = normalize_keywords(
        "cybersecurity, attack graph, knowledge graph"
    )

    assert keywords == [
        "cybersecurity",
        "attack graph",
        "knowledge graph",
    ]


def test_normalize_paper():
    paper = normalize_paper(
        paper_id="OA001",
        title="  Cyber Attack Research  ",
        authors=[
            {"display_name": "John Smith"},
            {"display_name": "Jane Doe"},
        ],
        abstract="A research abstract.",
        keywords="cybersecurity, attack graph",
        year="2026",
        source="OpenAlex",
        doi="10.1234/example",
        paper_url="https://example.com/paper",
    )

    assert isinstance(paper, Paper)

    assert paper.paper_id == "OA001"
    assert paper.title == "Cyber Attack Research"

    assert paper.authors == [
        "John Smith",
        "Jane Doe",
    ]

    assert paper.keywords == [
        "cybersecurity",
        "attack graph",
    ]

    assert paper.year == 2026
    assert paper.source == "OpenAlex"
    assert paper.doi == "10.1234/example"