import httpx

from researchflow.sources.semantic_scholar import (
    SemanticScholarSource,
)


def make_response(
    status_code: int,
    *,
    json_data=None,
):
    response = httpx.Response(
        status_code,
        json=json_data,
        request=httpx.Request(
            "GET",
            "https://api.semanticscholar.org",
        ),
    )

    return response


def test_semantic_scholar_search():
    source = SemanticScholarSource()

    response_data = {
        "total": 1,
        "data": [
            {
                "paperId": "abc123",
                "title": "Cybersecurity Knowledge Graph",
                "authors": [
                    {
                        "authorId": "1",
                        "name": "John Doe",
                    }
                ],
                "abstract": "A cybersecurity research paper.",
                "year": 2025,
                "externalIds": {
                    "DOI": "10.1234/example",
                },
                "url": (
                    "https://www.semanticscholar.org/"
                    "paper/abc123"
                ),
                "openAccessPdf": {
                    "url": (
                        "https://example.com/paper.pdf"
                    )
                },
            }
        ],
    }

    class FakeHTTPClient:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            pass

        def get(
            self,
            *args,
            **kwargs,
        ):
            return make_response(
                200,
                json_data=response_data,
            )

    source.http_client = FakeHTTPClient()

    papers = list(
        source.search(
            "cybersecurity knowledge graph",
            max_results=5,
        )
    )

    assert len(papers) == 1

    paper = papers[0]

    assert paper.title == (
        "Cybersecurity Knowledge Graph"
    )

    assert paper.authors == [
        "John Doe"
    ]

    assert paper.year == 2025

    assert paper.source == (
        "Semantic Scholar"
    )

    assert paper.doi == (
        "10.1234/example"
    )

    assert paper.paper_url == (
        "https://www.semanticscholar.org/"
        "paper/abc123"
    )

    assert paper.pdf_url == (
        "https://example.com/paper.pdf"
    )


def test_semantic_scholar_empty_results():
    source = SemanticScholarSource()

    response_data = {
        "total": 0,
        "data": [],
    }

    class FakeHTTPClient:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            pass

        def get(
            self,
            *args,
            **kwargs,
        ):
            return make_response(
                200,
                json_data=response_data,
            )

    source.http_client = FakeHTTPClient()

    papers = list(
        source.search(
            "some nonexistent query",
            max_results=5,
        )
    )

    assert papers == []


def test_semantic_scholar_max_results_zero():
    source = SemanticScholarSource()

    papers = list(
        source.search(
            "cybersecurity",
            max_results=0,
        )
    )

    assert papers == []