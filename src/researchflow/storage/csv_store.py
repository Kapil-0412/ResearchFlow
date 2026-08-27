import json
from pathlib import Path

import pandas as pd

from researchflow.models import Paper


class CSVStore:
    """Store and retrieve research papers using CSV files."""

    LIST_FIELDS = {"authors", "keywords"}

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def save(self, papers: list[Paper]) -> None:
        """Save papers to the CSV file."""

        if not papers:
            return

        self.path.parent.mkdir(parents=True, exist_ok=True)

        records = []

        for paper in papers:
            record = paper.model_dump(mode="json")

            for field in self.LIST_FIELDS:
                record[field] = json.dumps(
                    record[field],
                    ensure_ascii=False,
                )

            records.append(record)

        dataframe = pd.DataFrame(records)

        dataframe.to_csv(
            self.path,
            index=False,
            encoding="utf-8",
        )

    def load(self) -> list[Paper]:
        """Load papers from the CSV file."""

        if not self.path.exists():
            return []

        dataframe = pd.read_csv(
            self.path,
            keep_default_na=False,
        )

        records = dataframe.to_dict(orient="records")

        for record in records:
            for field in self.LIST_FIELDS:
                value = record.get(field, "")

                if value:
                    record[field] = json.loads(value)
                else:
                    record[field] = []

            for field, value in record.items():
                if value == "":
                    record[field] = None

        return [
            Paper.model_validate(record)
            for record in records
        ]