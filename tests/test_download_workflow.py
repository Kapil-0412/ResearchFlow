from unittest.mock import Mock

from researchflow.downloader import (
    DownloadWorkflow,
    PDFDownloader,
    PendingDownloadStore,
)
from researchflow.models import Paper


def test_workflow_downloads_successful_papers(
    tmp_path,
):
    pending_path = tmp_path / "pending.csv"

    downloader = Mock(spec=PDFDownloader)
    downloader.download.return_value = True

    store = PendingDownloadStore(pending_path)

    workflow = DownloadWorkflow(
        downloader=downloader,
        pending_store=store,
    )

    paper = Paper(
        paper_id="P001",
        title="Public PDF",
        source="arXiv",
        pdf_url="https://example.com/paper.pdf",
    )

    results = workflow.download([paper])

    assert results == [True]
    downloader.download.assert_called_once_with(paper)
    assert not pending_path.exists()


def test_workflow_persists_failed_downloads(
    tmp_path,
):
    pending_path = tmp_path / "pending.csv"

    downloader = Mock(spec=PDFDownloader)
    downloader.download.return_value = False

    store = PendingDownloadStore(pending_path)

    workflow = DownloadWorkflow(
        downloader=downloader,
        pending_store=store,
    )

    paper = Paper(
        paper_id="P002",
        title="Restricted Paper",
        source="IEEE",
        pdf_url="https://example.com/paper.pdf",
        download_status="institutional_access_required",
    )

    results = workflow.download([paper])

    assert results == [False]
    downloader.download.assert_called_once_with(paper)

    loaded = store.load()

    assert len(loaded) == 1
    assert loaded[0].paper_id == "P002"


def test_workflow_processes_multiple_papers(
    tmp_path,
):
    pending_path = tmp_path / "pending.csv"

    downloader = Mock(spec=PDFDownloader)
    downloader.download.side_effect = [
        True,
        False,
        True,
    ]

    store = PendingDownloadStore(pending_path)

    workflow = DownloadWorkflow(
        downloader=downloader,
        pending_store=store,
    )

    papers = [
        Paper(
            paper_id="P001",
            title="Paper One",
            source="IEEE",
            pdf_url="https://example.com/one.pdf",
        ),
        Paper(
            paper_id="P002",
            title="Paper Two",
            source="ACM",
            pdf_url="https://example.com/two.pdf",
            download_status="temporary_failure",
        ),
        Paper(
            paper_id="P003",
            title="Paper Three",
            source="arXiv",
            pdf_url="https://example.com/three.pdf",
        ),
    ]

    results = workflow.download(papers)

    assert results == [True, False, True]

    assert downloader.download.call_count == 3

    loaded = store.load()

    assert [
        paper.paper_id
        for paper in loaded
    ] == ["P002"]


def test_workflow_can_retry_pending_papers(
    tmp_path,
):
    pending_path = tmp_path / "pending.csv"

    store = PendingDownloadStore(pending_path)

    pending_paper = Paper(
        paper_id="P004",
        title="Pending Paper",
        source="Springer",
        pdf_url="https://example.com/paper.pdf",
        download_status="temporary_failure",
    )

    store.save([pending_paper])

    downloader = Mock(spec=PDFDownloader)
    downloader.download.return_value = True

    workflow = DownloadWorkflow(
        downloader=downloader,
        pending_store=store,
    )

    results = workflow.download_pending()

    assert results == [True]
    downloader.download.assert_called_once()

    assert store.load() == []