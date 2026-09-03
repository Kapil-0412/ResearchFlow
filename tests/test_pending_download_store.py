from researchflow.downloader import PendingDownloadStore
from researchflow.models import Paper


def test_pending_download_store_saves_pending_papers(tmp_path):
    path = tmp_path / "pending_downloads.csv"

    papers = [
        Paper(
            paper_id="P001",
            title="Restricted Paper",
            source="IEEE",
            doi="10.1234/restricted",
            pdf_url="https://example.com/restricted.pdf",
            download_status="institutional_access_required",
            download_attempts=1,
            download_error="Institutional access is required.",
            found_in_keywords=["counterfactual cybersecurity"],
            found_in_sources=["IEEE"],
        )
    ]

    store = PendingDownloadStore(path)

    store.save(papers)

    loaded = store.load()

    assert len(loaded) == 1

    paper = loaded[0]

    assert paper.paper_id == "P001"
    assert paper.title == "Restricted Paper"
    assert paper.source == "IEEE"
    assert paper.doi == "10.1234/restricted"
    assert paper.download_status == "institutional_access_required"
    assert paper.download_attempts == 1
    assert paper.download_error == (
        "Institutional access is required."
    )
    assert paper.found_in_keywords == [
        "counterfactual cybersecurity",
    ]
    assert paper.found_in_sources == [
        "IEEE",
    ]


def test_pending_download_store_loads_only_pending_papers(tmp_path):
    path = tmp_path / "pending_downloads.csv"

    papers = [
        Paper(
            paper_id="P001",
            title="Pending Paper",
            source="IEEE",
            download_status="institutional_access_required",
        ),
        Paper(
            paper_id="P002",
            title="Downloaded Paper",
            source="ACM",
            download_status="downloaded",
        ),
        Paper(
            paper_id="P003",
            title="Temporary Failure",
            source="Springer",
            download_status="temporary_failure",
        ),
    ]

    store = PendingDownloadStore(path)

    store.save(papers)

    loaded = store.load()

    assert len(loaded) == 2

    assert [
        paper.paper_id
        for paper in loaded
    ] == [
        "P001",
        "P003",
    ]


def test_pending_download_store_returns_empty_when_file_missing(
    tmp_path,
):
    path = tmp_path / "pending_downloads.csv"

    store = PendingDownloadStore(path)

    assert store.load() == []


def test_pending_download_store_does_not_save_downloaded_papers(
    tmp_path,
):
    path = tmp_path / "pending_downloads.csv"

    papers = [
        Paper(
            paper_id="P001",
            title="Downloaded Paper",
            source="IEEE",
            download_status="downloaded",
        )
    ]

    store = PendingDownloadStore(path)

    store.save(papers)

    assert store.load() == []