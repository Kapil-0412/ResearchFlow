from datetime import UTC, datetime

from researchflow.downloader import DownloadManager
from researchflow.models import Paper


def test_new_paper_has_not_downloaded_status():
    paper = Paper(
        paper_id="P001",
        title="Test Paper",
        source="IEEE",
    )

    assert paper.download_status == "not_downloaded"
    assert paper.download_attempts == 0
    assert paper.last_download_attempt is None
    assert paper.download_error is None


def test_download_manager_marks_successful_download(tmp_path):
    paper = Paper(
        paper_id="P001",
        title="Test Paper",
        source="IEEE",
        pdf_url="https://example.com/paper.pdf",
    )

    manager = DownloadManager(tmp_path)

    manager.mark_downloaded(
        paper,
        tmp_path / "P001.pdf",
    )

    assert paper.download_status == "downloaded"
    assert paper.local_path == str(tmp_path / "P001.pdf")
    assert paper.download_attempts == 1
    assert paper.last_download_attempt is not None
    assert paper.download_error is None


def test_download_manager_marks_pending_download(tmp_path):
    paper = Paper(
        paper_id="P002",
        title="Restricted Paper",
        source="IEEE",
        pdf_url="https://example.com/restricted.pdf",
    )

    manager = DownloadManager(tmp_path)

    manager.mark_pending(
        paper,
        status="institutional_access_required",
        error="Institutional access is required.",
    )

    assert paper.download_status == "institutional_access_required"
    assert paper.download_attempts == 1
    assert paper.last_download_attempt is not None
    assert paper.download_error == (
        "Institutional access is required."
    )


def test_download_manager_identifies_pending_papers(tmp_path):
    downloaded = Paper(
        paper_id="P001",
        title="Downloaded Paper",
        source="IEEE",
        download_status="downloaded",
    )

    pending = Paper(
        paper_id="P002",
        title="Pending Paper",
        source="ACM",
        download_status="institutional_access_required",
    )

    not_attempted = Paper(
        paper_id="P003",
        title="Not Attempted",
        source="Springer",
        download_status="not_downloaded",
    )

    manager = DownloadManager(tmp_path)

    result = manager.pending_papers(
        [
            downloaded,
            pending,
            not_attempted,
        ]
    )

    assert len(result) == 1
    assert result[0].paper_id == "P002"


def test_download_manager_records_failed_attempt(tmp_path):
    paper = Paper(
        paper_id="P004",
        title="Failed Paper",
        source="ACM",
    )

    manager = DownloadManager(tmp_path)

    manager.mark_pending(
        paper,
        status="temporary_failure",
        error="Connection timed out.",
    )

    assert paper.download_status == "temporary_failure"
    assert paper.download_attempts == 1
    assert paper.download_error == "Connection timed out."


def test_download_attempt_timestamp_is_utc(tmp_path):
    paper = Paper(
        paper_id="P005",
        title="Timestamp Test",
        source="arXiv",
    )

    manager = DownloadManager(tmp_path)

    manager.mark_pending(
        paper,
        status="temporary_failure",
        error="Test failure.",
    )

    assert isinstance(
        paper.last_download_attempt,
        datetime,
    )

    assert paper.last_download_attempt.tzinfo == UTC