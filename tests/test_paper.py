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