import json
from pathlib import Path

from pydantic import BaseModel, Field


class SearchConfig(BaseModel):
    """Configuration used by ResearchFlow for paper discovery."""

    research_topic: str

    search_strings: list[str] = Field(default_factory=list)

    max_results_per_query: int = 100

    headless: bool = False


def load_search_config(path: str | Path) -> SearchConfig:
    """Load and validate a ResearchFlow search configuration."""

    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    with config_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return SearchConfig.model_validate(data)