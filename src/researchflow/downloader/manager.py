from datetime import UTC, datetime
from collections.abc import Iterable
from pathlib import Path

from researchflow.models import Paper


class DownloadManager:
    """Manage paper PDF download state."""

    PENDING_STATUSES = {
        "institutional_access_required",
        "authentication_required",
        "temporary_failure",
        "no_public_pdf",
    }

    def __init__(self, download_directory: str | Path):
        self.download_directory = Path(download_directory)

    def mark_downloaded(
        self,
        paper: Paper,
        local_path: str | Path,
    ) -> None:
        """Mark a paper as successfully downloaded."""

        paper.download_status = "downloaded"
        paper.local_path = str(Path(local_path))
        paper.download_attempts += 1
        paper.last_download_attempt = datetime.now(UTC)
        paper.download_error = None

    def mark_pending(
        self,
        paper: Paper,
        *,
        status: str,
        error: str,
    ) -> None:
        """Record a failed or deferred download attempt."""

        if status not in self.PENDING_STATUSES:
            raise ValueError(
                f"Unsupported pending download status: {status}"
            )

        paper.download_status = status
        paper.download_attempts += 1
        paper.last_download_attempt = datetime.now(UTC)
        paper.download_error = error

    def pending_papers(
        self,
        papers: Iterable[Paper],
    ) -> list[Paper]:
        """Return papers that should be retried later."""

        return [
            paper
            for paper in papers
            if paper.download_status in self.PENDING_STATUSES
        ]