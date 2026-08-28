from researchflow.sources import OpenAlexSource


def test_openalex_source_name():
    source = OpenAlexSource()

    assert source.name == "OpenAlex"


def test_reconstruct_abstract():
    inverted_index = {
        "Cybersecurity": [0],
        "research": [1],
        "is": [2],
        "important": [3],
    }

    abstract = OpenAlexSource._reconstruct_abstract(
        inverted_index
    )

    assert abstract == "Cybersecurity research is important"


def test_reconstruct_empty_abstract():
    assert (
        OpenAlexSource._reconstruct_abstract(None)
        is None
    )


def test_parse_openalex_result():
    source = OpenAlexSource()

    result = {
        "id": "https://openalex.org/W123456789",
        "title": "Counterfactual Cyber Attack Reasoning",
        "publication_year": 2026,
        "doi": "https://doi.org/10.1234/example",
        "authorships": [
            {
                "author": {
                    "display_name": "John Smith"
                }
            },
            {
                "author": {
                    "display_name": "Jane Doe"
                }
            },
        ],
        "keywords": [
            {
                "display_name": "cybersecurity"
            },
            {
                "display_name": "knowledge graph"
            },
        ],
        "abstract_inverted_index": {
            "Cyber": [0],
            "attack": [1],
            "reasoning": [2],
            "is": [3],
            "important": [4],
        },
        "primary_location": {
            "landing_page_url": (
                "https://example.com/paper"
            ),
            "pdf_url": {
                "url": (
                    "https://example.com/paper.pdf"
                )
            },
        },
    }

    paper = source._parse_result(
        result,
        query="counterfactual cyber attack",
    )

    assert paper.paper_id == (
        "https://openalex.org/W123456789"
    )

    assert paper.title == (
        "Counterfactual Cyber Attack Reasoning"
    )

    assert paper.authors == [
        "John Smith",
        "Jane Doe",
    ]

    assert paper.keywords == [
        "cybersecurity",
        "knowledge graph",
    ]

    assert paper.abstract == (
        "Cyber attack reasoning is important"
    )

    assert paper.year == 2026

    assert paper.source == "OpenAlex"

    assert paper.doi == (
        "https://doi.org/10.1234/example"
    )

    assert paper.paper_url == (
        "https://example.com/paper"
    )

    assert paper.pdf_url == (
        "https://example.com/paper.pdf"
    )

    assert paper.search_query == (
        "counterfactual cyber attack"
    )