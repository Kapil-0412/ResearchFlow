from unittest.mock import Mock, patch

from researchflow.models import Paper


def test_search_command_runs_search_pipeline(tmp_path):
    config_path = tmp_path / "search.json"
    output_path = tmp_path / "papers.csv"

    config_path.write_text(
        """
        {
            "research_topic": "cybersecurity knowledge graph",
            "search_strings": [
                "cybersecurity knowledge graph"
            ],
            "max_results_per_query": 5,
            "headless": true
        }
        """,
        encoding="utf-8",
    )

    paper = Paper(
        paper_id="P001",
        title="Cybersecurity Knowledge Graph",
        source="OpenAlex",
    )

    mock_engine = Mock()
    mock_engine.search_many.return_value = [paper]

    with patch(
        "researchflow.cli.build_search_engine",
        return_value=mock_engine,
    ):
        from researchflow.cli import main

        result = main(
            [
                "search",
                "--config",
                str(config_path),
                "--output",
                str(output_path),
            ]
        )

    assert result == 0

    mock_engine.search_many.assert_called_once_with(
        ["cybersecurity knowledge graph"],
        max_results_per_source=5,
    )

    assert output_path.exists()