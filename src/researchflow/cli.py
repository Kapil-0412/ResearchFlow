import argparse
from pathlib import Path

from researchflow.downloader import (
    DownloadWorkflow,
    PDFDownloader,
    PendingDownloadStore,
)


DEFAULT_DOWNLOAD_DIRECTORY = Path("data/papers")
DEFAULT_PENDING_FILE = Path("data/pending_downloads.csv")


def build_parser() -> argparse.ArgumentParser:
    """Build the ResearchFlow command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="researchflow",
        description=(
            "ResearchFlow research paper discovery "
            "and PDF management tool."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
    )

    download_pending_parser = subparsers.add_parser(
        "download-pending",
        help="Retry downloading papers saved in the pending list.",
    )

    download_pending_parser.add_argument(
        "--download-directory",
        type=Path,
        default=DEFAULT_DOWNLOAD_DIRECTORY,
        help=(
            "Directory where downloaded PDFs are stored."
        ),
    )

    download_pending_parser.add_argument(
        "--pending-file",
        type=Path,
        default=DEFAULT_PENDING_FILE,
        help=(
            "CSV file containing papers waiting for download."
        ),
    )

    return parser


def main(args: list[str] | None = None) -> int:
    """Run the ResearchFlow command-line interface."""

    parser = build_parser()
    parsed_args = parser.parse_args(args)

    if parsed_args.command is None:
        parser.print_help()
        return 0

    if parsed_args.command == "download-pending":
        workflow = DownloadWorkflow(
            downloader=PDFDownloader(
                parsed_args.download_directory,
            ),
            pending_store=PendingDownloadStore(
                parsed_args.pending_file,
            ),
        )

        results = workflow.download_pending()

        if not results:
            print("No pending papers to download.")
            return 0

        successful = sum(results)
        failed = len(results) - successful

        print(
            f"Download complete: "
            f"{successful} succeeded, "
            f"{failed} failed."
        )

        return 0 if failed == 0 else 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())