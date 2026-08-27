from researchflow.config import SearchConfig, load_search_config


def test_load_search_config():
    config = load_search_config("config/search_strings.json")

    assert isinstance(config, SearchConfig)

    assert config.research_topic != ""

    assert len(config.search_strings) > 0

    assert config.max_results_per_query == 100

    assert config.headless is False