from researchflow.models import Paper


def test_create_paper():
    paper = Paper(
        paper_id="P001",
        title="Test Research Paper",
        authors=["Author One", "Author Two"],
        year=2026,
        source="OpenAlex",
    )

    assert paper.paper_id == "P001"
    assert paper.title == "Test Research Paper"
    assert len(paper.authors) == 2
    assert paper.year == 2026
    assert paper.source == "OpenAlex"


def test_paper_tracks_discovery_and_download_state():
    paper = Paper(
        paper_id="P002",
        title="Counterfactual Cyber Attack Reasoning",
        source="IEEE",
        found_in_keywords=[
            "counterfactual cybersecurity",
            "cyber attack reasoning",
        ],
        found_in_sources=[
            "IEEE",
            "OpenAlex",
        ],
    )

    assert paper.found_in_keywords == [
        "counterfactual cybersecurity",
        "cyber attack reasoning",
    ]

    assert paper.found_in_sources == [
        "IEEE",
        "OpenAlex",
    ]

    assert paper.download_attempts == 0
    assert paper.last_download_attempt is None
    assert paper.download_error is None