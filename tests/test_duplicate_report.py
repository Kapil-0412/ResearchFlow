from researchflow.models import Paper
from researchflow.processing.duplicate_report import DuplicateReport


def test_duplicate_report_contains_only_duplicates(tmp_path):
    papers = [
        Paper(
            paper_id="P001",
            title="Shared Research Paper",
            source="IEEE",
            doi="10.1234/shared",
            found_in_keywords=[
                "counterfactual cybersecurity",
                "cyber attack reasoning",
            ],
            found_in_sources=[
                "IEEE",
                "ACM",
            ],
        ),
        Paper(
            paper_id="P002",
            title="Unique Research Paper",
            source="arXiv",
            doi="10.1234/unique",
            found_in_keywords=[
                "knowledge graph",
            ],
            found_in_sources=[
                "arXiv",
            ],
        ),
    ]

    output = tmp_path / "duplicate_report.csv"

    report = DuplicateReport()

    report.generate(
        papers,
        output,
    )

    rows = report.load(output)

    assert len(rows) == 1

    row = rows[0]

    assert row["title"] == "Shared Research Paper"
    assert row["doi"] == "10.1234/shared"
    assert row["found_count"] == 2
    assert row["found_in_keywords"] == (
        "counterfactual cybersecurity; "
        "cyber attack reasoning"
    )
    assert row["found_in_sources"] == "IEEE; ACM"


def test_duplicate_report_counts_discovery_sources_and_keywords(
    tmp_path,
):
    papers = [
        Paper(
            paper_id="P001",
            title="Research Paper",
            source="IEEE",
            found_in_keywords=["keyword one"],
            found_in_sources=["IEEE"],
        ),
        Paper(
            paper_id="P001",
            title="Research Paper",
            source="ACM",
            found_in_keywords=["keyword two"],
            found_in_sources=["ACM"],
        ),
        Paper(
            paper_id="P001",
            title="Research Paper",
            source="Springer",
            found_in_keywords=["keyword three"],
            found_in_sources=["Springer"],
        ),
    ]

    output = tmp_path / "duplicate_report.csv"

    report = DuplicateReport()

    report.generate(
        papers,
        output,
    )

    rows = report.load(output)

    assert len(rows) == 1

    row = rows[0]

    assert row["found_count"] == 3
    assert row["found_in_keywords"] == (
        "keyword one; keyword two; keyword three"
    )
    assert row["found_in_sources"] == (
        "IEEE; ACM; Springer"
    )