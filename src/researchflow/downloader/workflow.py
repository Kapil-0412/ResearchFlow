from collections.abc import Iterable

from researchflow.models import Paper

from .pdf_downloader import PDFDownloader
from .pending_store import PendingDownloadStore


class DownloadWorkflow:
    """Coordinate PDF downloads and pending-download persistence."""

    def __init__(
        self,
        *,
        downloader: PDFDownloader,
        pending_store: PendingDownloadStore,
    ):
        self.downloader = downloader
        self.pending_store = pending_store

    def download(
        self,
        papers: Iterable[Paper],
    ) -> list[bool]:
        """Download papers and persist unsuccessful downloads."""

        papers = list(papers)
        results = []

        for paper in papers:
            result = self.downloader.download(paper)
            results.append(result)

        self.pending_store.save(papers)

        return results

    def download_pending(self) -> list[bool]:
        """Retry only papers currently stored as pending."""

        papers = self.pending_store.load()

        if not papers:
            return []

        results = []

        for paper in papers:
            result = self.downloader.download(paper)
            results.append(result)

            if result:
                paper.download_status = "downloaded"

        self.pending_store.save(papers)

        return results