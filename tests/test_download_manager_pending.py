from researchflow.downloader import (
    DownloadManager,
    PendingDownloadStore,
)
from researchflow.models import Paper


def test_download_manager_saves_pending_papers(
    tmp_path,
):
    pending_path = tmp_path / "pending_downloads.csv"

    manager = DownloadManager(
        tmp_path / "papers"
    )
    store = PendingDownloadStore(
        pending_path
    )

    papers = [
        Paper(
            paper_id="P001",
            title="Restricted Paper",
            source="IEEE",
            download_status="institutional_access_required",
        ),
        Paper(
            paper_id="P002",
            title="Downloaded Paper",
            source="ACM",
            download_status="downloaded",
        ),
    ]

    pending = manager.pending_papers(papers)

    store.save(pending)

    loaded = store.load()

    assert len(loaded) == 1
    assert loaded[0].paper_id == "P001"
    assert (
        loaded[0].download_status
        == "institutional_access_required"
    )


def test_download_manager_loads_pending_papers(
    tmp_path,
):
    pending_path = tmp_path / "pending_downloads.csv"

    store = PendingDownloadStore(
        pending_path
    )

    paper = Paper(
        paper_id="P001",
        title="Restricted Paper",
        source="IEEE",
        download_status="authentication_required",
    )

    store.save([paper])

    manager = DownloadManager(
        tmp_path / "papers"
    )

    loaded = store.load()
    pending = manager.pending_papers(loaded)

    assert len(pending) == 1
    assert pending[0].paper_id == "P001"


def test_downloaded_papers_are_not_returned_for_retry(
    tmp_path,
):
    manager = DownloadManager(
        tmp_path / "papers"
    )

    papers = [
        Paper(
            paper_id="P001",
            title="Already Downloaded",
            source="IEEE",
            download_status="downloaded",
        ),
        Paper(
            paper_id="P002",
            title="Needs Retry",
            source="ACM",
            download_status="temporary_failure",
        ),
    ]

    pending = manager.pending_papers(papers)

    assert [
        paper.paper_id
        for paper in pending
    ] == ["P002"]