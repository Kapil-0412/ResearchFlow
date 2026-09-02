import re
from datetime import UTC, datetime
from pathlib import Path

import requests

from researchflow.models import Paper


class PDFDownloader:
    """Download legitimate publicly accessible research PDFs."""

    def __init__(
        self,
        download_directory: str | Path,
        *,
        timeout: int = 30,
    ):
        self.download_directory = Path(download_directory)
        self.timeout = timeout

    def download(self, paper: Paper) -> bool:
        """Download a paper's public PDF."""

        paper.download_attempts += 1
        paper.last_download_attempt = datetime.now(UTC)

        if not paper.pdf_url:
            paper.download_status = "no_public_pdf"
            paper.download_error = "No public PDF URL is available."
            return False

        try:
            response = requests.get(
                paper.pdf_url,
                timeout=self.timeout,
                allow_redirects=True,
            )
            response.raise_for_status()

        except requests.HTTPError as exc:
            if response.status_code == 401:
                paper.download_status = (
                    "authentication_required"
                )
            elif response.status_code == 403:
                paper.download_status = (
                    "institutional_access_required"
                )
            else:
                paper.download_status = "temporary_failure"

            paper.download_error = str(exc)
            return False

        except requests.RequestException as exc:
            paper.download_status = "temporary_failure"
            paper.download_error = str(exc)
            return False

        except Exception as exc:
            paper.download_status = "temporary_failure"
            paper.download_error = str(exc)
            return False

        content = response.content

        if not content:
            paper.download_status = "temporary_failure"
            paper.download_error = "The response contained no data."
            return False

        content_type = response.headers.get(
            "Content-Type",
            "",
        ).lower()

        is_pdf = (
            "application/pdf" in content_type
            or content.startswith(b"%PDF-")
        )

        if not is_pdf:
            paper.download_status = "no_public_pdf"
            paper.download_error = (
                "The URL did not return a PDF."
            )
            return False

        output_path = self._build_unique_output_path(
            paper
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_bytes(content)

        paper.download_status = "downloaded"
        paper.download_error = None
        paper.local_path = str(output_path)

        return True

    def _build_output_path(
        self,
        paper: Paper,
    ) -> Path:
        """Build the default source-specific PDF path."""

        source_directory = self.download_directory / (
            self._sanitize_filename(paper.source)
        )

        filename = self._sanitize_filename(
            paper.title
        )

        return source_directory / f"{filename}.pdf"

    def _build_unique_output_path(
        self,
        paper: Paper,
    ) -> Path:
        """Build a PDF path without overwriting an existing file."""

        output_path = self._build_output_path(paper)

        if not output_path.exists():
            return output_path

        stem = output_path.stem
        suffix = output_path.suffix
        parent = output_path.parent

        counter = 2

        while True:
            candidate = (
                parent
                / f"{stem}_{counter}{suffix}"
            )

            if not candidate.exists():
                return candidate

            counter += 1

    @staticmethod
    def _sanitize_filename(value: str) -> str:
        """Convert text into a safe filesystem filename."""

        value = value.strip()

        value = re.sub(
            r'[<>:"/\\|?*]',
            "_",
            value,
        )

        value = re.sub(
            r"\s+",
            "_",
            value,
        )

        value = re.sub(
            r"_+",
            "_",
            value,
        )

        value = value.strip("._")

        return value or "untitled"