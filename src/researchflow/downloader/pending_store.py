import json
from pathlib import Path

import pandas as pd

from researchflow.models import Paper


class PendingDownloadStore:
    """Persist papers that need a later PDF download attempt."""

    LIST_FIELDS = {
        "authors",
        "keywords",
        "found_in_keywords",
        "found_in_sources",
    }

    PENDING_STATUSES = {
        "institutional_access_required",
        "authentication_required",
        "temporary_failure",
        "no_public_pdf",
    }

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def save(self, papers: list[Paper]) -> None:
        """Save only papers that are currently pending download."""

        pending = [
            paper
            for paper in papers
            if paper.download_status in self.PENDING_STATUSES
        ]

        if not pending:
            if self.path.exists():
                self.path.unlink()
            return

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        records = []

        for paper in pending:
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
        """Load pending papers from the CSV file."""

        if not self.path.exists():
            return []

        dataframe = pd.read_csv(
            self.path,
            keep_default_na=False,
        )

        records = dataframe.to_dict(
            orient="records",
        )

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