from pathlib import Path

from researchflow.cli import build_parser


def test_cli_parser_accepts_download_directory():
    parser = build_parser()

    args = parser.parse_args(
        [
            "download-pending",
            "--download-directory",
            "data/papers",
        ]
    )

    assert args.download_directory == Path("data/papers")


def test_cli_parser_accepts_pending_file():
    parser = build_parser()

    args = parser.parse_args(
        [
            "download-pending",
            "--pending-file",
            "data/pending_downloads.csv",
        ]
    )

    assert args.pending_file == Path(
        "data/pending_downloads.csv"
    )


def test_cli_parser_has_default_download_configuration():
    parser = build_parser()

    args = parser.parse_args(
        ["download-pending"]
    )

    assert args.download_directory == Path(
        "data/papers"
    )

    assert args.pending_file == Path(
        "data/pending_downloads.csv"
    )