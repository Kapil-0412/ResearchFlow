from unittest.mock import Mock, patch

from researchflow.models import Paper


def test_download_pending_command_runs_workflow():
    paper = Paper(
        paper_id="P001",
        title="Pending Paper",
        source="IEEE",
        download_status="institutional_access_required",
    )

    mock_workflow = Mock()
    mock_workflow.download_pending.return_value = [True]

    with patch(
        "researchflow.cli.DownloadWorkflow",
        return_value=mock_workflow,
    ):
        from researchflow.cli import main

        result = main(["download-pending"])

    assert result == 0
    mock_workflow.download_pending.assert_called_once()


def test_download_pending_command_returns_failure_code():
    mock_workflow = Mock()
    mock_workflow.download_pending.return_value = [False]

    with patch(
        "researchflow.cli.DownloadWorkflow",
        return_value=mock_workflow,
    ):
        from researchflow.cli import main

        result = main(["download-pending"])

    assert result == 1


def test_cli_without_command_returns_help_code():
    from researchflow.cli import main

    result = main([])

    assert result == 0