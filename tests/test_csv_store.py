from researchflow.models import Paper
from researchflow.storage import CSVStore


def test_save_and_load_papers(tmp_path):
    csv_path = tmp_path / "papers.csv"

    store = CSVStore(csv_path)

    papers = [
        Paper(
            paper_id="P001",
            title="Test Research Paper",
            authors=["Author One", "Author Two"],
            abstract="This is a test research abstract.",
            keywords=["cybersecurity", "attack graph"],
            year=2026,
            source="OpenAlex",
            doi="10.1234/example",
            paper_url="https://example.com/paper",
            pdf_url="https://example.com/paper.pdf",
            search_query="cybersecurity AND attack graph",
            query_id="Q01",
            found_in_keywords=[
                "cybersecurity",
                "attack graph",
            ],
            found_in_sources=[
                "OpenAlex",
                "Crossref",
            ],
            relevance_score=94.5,
            relevance_category="HIGH",
            relevance_reason="Strong research alignment.",
            user_decision="PENDING",
            pdf_status="available",
            download_status="not_downloaded",
            download_attempts=0,
            last_download_attempt=None,
            download_error=None,
            local_path=None,
        ),
        Paper(
            paper_id="P002",
            title="Another Research Paper",
            authors=["Author Three"],
            year=2025,
            source="Crossref",
        ),
    ]

    store.save(papers)

    assert csv_path.exists()

    loaded_papers = store.load()

    assert len(loaded_papers) == 2

    first = loaded_papers[0]

    assert first.paper_id == "P001"
    assert first.title == "Test Research Paper"
    assert first.authors == ["Author One", "Author Two"]
    assert first.abstract == "This is a test research abstract."
    assert first.keywords == ["cybersecurity", "attack graph"]
    assert first.year == 2026
    assert first.source == "OpenAlex"
    assert first.doi == "10.1234/example"
    assert first.paper_url == "https://example.com/paper"
    assert first.pdf_url == "https://example.com/paper.pdf"
    assert first.search_query == "cybersecurity AND attack graph"
    assert first.query_id == "Q01"

    assert first.found_in_keywords == [
        "cybersecurity",
        "attack graph",
    ]

    assert first.found_in_sources == [
        "OpenAlex",
        "Crossref",
    ]

    assert first.relevance_score == 94.5
    assert first.relevance_category == "HIGH"
    assert first.relevance_reason == "Strong research alignment."
    assert first.user_decision == "PENDING"
    assert first.pdf_status == "available"
    assert first.download_status == "not_downloaded"
    assert first.download_attempts == 0
    assert first.last_download_attempt is None
    assert first.download_error is None
    assert first.local_path is None

    second = loaded_papers[1]

    assert second.paper_id == "P002"
    assert second.authors == ["Author Three"]
    assert second.keywords == []
    assert second.found_in_keywords == []
    assert second.found_in_sources == []
    assert second.abstract is None
    assert second.doi is None