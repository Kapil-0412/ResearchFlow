from unittest.mock import Mock, patch

import requests

from researchflow.downloader import PDFDownloader
from researchflow.models import Paper


def test_pdf_downloader_downloads_public_pdf(tmp_path):
    paper = Paper(
        paper_id="P001",
        title="Counterfactual Cyber Attack Reasoning",
        source="IEEE",
        pdf_url="https://example.com/paper.pdf",
    )

    response = Mock()
    response.status_code = 200
    response.headers = {
        "Content-Type": "application/pdf",
    }
    response.content = b"%PDF-1.4 test pdf content"
    response.raise_for_status.return_value = None

    downloader = PDFDownloader(tmp_path)

    with patch(
        "researchflow.downloader.pdf_downloader.requests.get",
        return_value=response,
    ):
        result = downloader.download(paper)

    assert result is True

    assert paper.download_status == "downloaded"
    assert paper.download_attempts == 1
    assert paper.local_path is not None
    assert paper.download_error is None

    saved_file = tmp_path / "IEEE" / "Counterfactual_Cyber_Attack_Reasoning.pdf"

    assert saved_file.exists()
    assert saved_file.read_bytes() == b"%PDF-1.4 test pdf content"


def test_pdf_downloader_handles_missing_pdf_url(tmp_path):
    paper = Paper(
        paper_id="P002",
        title="Paper Without PDF",
        source="ACM",
        pdf_url=None,
    )

    downloader = PDFDownloader(tmp_path)

    result = downloader.download(paper)

    assert result is False
    assert paper.download_status == "no_public_pdf"
    assert paper.download_attempts == 1
    assert paper.download_error is not None
    assert paper.local_path is None


def test_pdf_downloader_handles_temporary_failure(tmp_path):
    paper = Paper(
        paper_id="P003",
        title="Temporary Failure Paper",
        source="Springer",
        pdf_url="https://example.com/paper.pdf",
    )

    response = Mock()
    response.status_code = 503
    response.headers = {}
    response.raise_for_status.side_effect = Exception(
        "503 Service Unavailable"
    )

    downloader = PDFDownloader(tmp_path)

    with patch(
        "researchflow.downloader.pdf_downloader.requests.get",
        return_value=response,
    ):
        result = downloader.download(paper)

    assert result is False
    assert paper.download_status == "temporary_failure"
    assert paper.download_attempts == 1
    assert paper.download_error is not None


def test_pdf_downloader_rejects_non_pdf_content(tmp_path):
    paper = Paper(
        paper_id="P004",
        title="HTML Instead Of PDF",
        source="ScienceDirect",
        pdf_url="https://example.com/paper",
    )

    response = Mock()
    response.status_code = 200
    response.headers = {
        "Content-Type": "text/html",
    }
    response.content = b"<html>Access denied</html>"
    response.raise_for_status.return_value = None

    downloader = PDFDownloader(tmp_path)

    with patch(
        "researchflow.downloader.pdf_downloader.requests.get",
        return_value=response,
    ):
        result = downloader.download(paper)

    assert result is False
    assert paper.download_status == "no_public_pdf"
    assert paper.download_attempts == 1
    assert paper.local_path is None

def test_pdf_downloader_accepts_pdf_by_file_signature(
    tmp_path,
):
    paper = Paper(
        paper_id="P005",
        title="PDF Without Content Type",
        source="arXiv",
        pdf_url="https://example.com/paper",
    )

    response = Mock()
    response.status_code = 200
    response.headers = {}
    response.content = b"%PDF-1.7 test content"
    response.raise_for_status.return_value = None

    downloader = PDFDownloader(tmp_path)

    with patch(
        "researchflow.downloader.pdf_downloader.requests.get",
        return_value=response,
    ):
        result = downloader.download(paper)

    assert result is True
    assert paper.download_status == "downloaded"
    assert paper.local_path is not None


def test_pdf_downloader_rejects_empty_response(
    tmp_path,
):
    paper = Paper(
        paper_id="P006",
        title="Empty PDF Response",
        source="ACM",
        pdf_url="https://example.com/paper.pdf",
    )

    response = Mock()
    response.status_code = 200
    response.headers = {
        "Content-Type": "application/pdf",
    }
    response.content = b""
    response.raise_for_status.return_value = None

    downloader = PDFDownloader(tmp_path)

    with patch(
        "researchflow.downloader.pdf_downloader.requests.get",
        return_value=response,
    ):
        result = downloader.download(paper)

    assert result is False
    assert paper.download_status == "temporary_failure"
    assert paper.download_attempts == 1
    assert paper.local_path is None


def test_pdf_downloader_handles_authentication_required(
    tmp_path,
):
    paper = Paper(
        paper_id="P007",
        title="Authentication Required Paper",
        source="Springer",
        pdf_url="https://example.com/paper.pdf",
    )

    response = Mock()
    response.status_code = 401
    response.headers = {}
    response.raise_for_status.side_effect = (
        requests.HTTPError("401 Unauthorized")
    )

    downloader = PDFDownloader(tmp_path)

    with patch(
        "researchflow.downloader.pdf_downloader.requests.get",
        return_value=response,
    ):
        result = downloader.download(paper)

    assert result is False
    assert paper.download_status == "authentication_required"
    assert paper.download_attempts == 1


def test_pdf_downloader_handles_institutional_access_required(
    tmp_path,
):
    paper = Paper(
        paper_id="P008",
        title="Institutional Access Paper",
        source="IEEE",
        pdf_url="https://example.com/paper.pdf",
    )

    response = Mock()
    response.status_code = 403
    response.headers = {}
    response.raise_for_status.side_effect = (
        requests.HTTPError("403 Forbidden")
    )

    downloader = PDFDownloader(tmp_path)

    with patch(
        "researchflow.downloader.pdf_downloader.requests.get",
        return_value=response,
    ):
        result = downloader.download(paper)

    assert result is False
    assert (
        paper.download_status
        == "institutional_access_required"
    )
    assert paper.download_attempts == 1


def test_pdf_downloader_does_not_overwrite_existing_file(
    tmp_path,
):
    paper = Paper(
        paper_id="P009",
        title="Existing Paper",
        source="IEEE",
        pdf_url="https://example.com/paper.pdf",
    )

    existing_file = (
        tmp_path
        / "IEEE"
        / "Existing_Paper.pdf"
    )

    existing_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    existing_file.write_bytes(
        b"%PDF-1.4 original content"
    )

    response = Mock()
    response.status_code = 200
    response.headers = {
        "Content-Type": "application/pdf",
    }
    response.content = b"%PDF-1.7 new content"
    response.raise_for_status.return_value = None

    downloader = PDFDownloader(tmp_path)

    with patch(
        "researchflow.downloader.pdf_downloader.requests.get",
        return_value=response,
    ):
        result = downloader.download(paper)

    assert result is True

    assert existing_file.read_bytes() == (
        b"%PDF-1.4 original content"
    )

    assert paper.local_path is not None
    assert paper.local_path != str(existing_file)