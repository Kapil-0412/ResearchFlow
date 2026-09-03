import csv
import re
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from researchflow.models import Paper


class DuplicateReport:
    """Generate CSV reports for papers discovered multiple times."""

    FIELDNAMES = [
        "paper_id",
        "title",
        "doi",
        "found_count",
        "found_in_keywords",
        "found_in_sources",
    ]

    def generate(
        self,
        papers: Iterable[Paper],
        output_path: str | Path,
    ) -> None:
        """Generate a CSV report containing duplicate papers."""

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        grouped: dict[str, list[Paper]] = defaultdict(list)

        for paper in papers:
            grouped[self._paper_key(paper)].append(paper)

        rows = []

        for group in grouped.values():
            discovery_count = max(
                len(paper.found_in_keywords)
                for paper in group
            )

            if len(group) > 1:
                discovery_count = max(
                    discovery_count,
                    len(group),
                )

            if discovery_count <= 1:
                continue

            representative = group[0]

            keywords = []
            sources = []

            for paper in group:
                for keyword in paper.found_in_keywords:
                    if keyword not in keywords:
                        keywords.append(keyword)

                if paper.search_query:
                    if paper.search_query not in keywords:
                        keywords.append(paper.search_query)

                for source in paper.found_in_sources:
                    if source not in sources:
                        sources.append(source)

                if paper.source not in sources:
                    sources.append(paper.source)

            rows.append(
                {
                    "paper_id": representative.paper_id,
                    "title": representative.title,
                    "doi": representative.doi or "",
                    "found_count": discovery_count,
                    "found_in_keywords": "; ".join(keywords),
                    "found_in_sources": "; ".join(sources),
                }
            )

        with output_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.FIELDNAMES,
            )

            writer.writeheader()
            writer.writerows(rows)

    @classmethod
    def load(
        cls,
        input_path: str | Path,
    ) -> list[dict[str, str | int]]:
        """Load a duplicate report CSV."""

        input_path = Path(input_path)

        with input_path.open(
            "r",
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)

            rows = []

            for row in reader:
                row["found_count"] = int(
                    row["found_count"]
                )

                rows.append(row)

        return rows

    @classmethod
    def _paper_key(cls, paper: Paper) -> str:
        """Generate a key used to group the same paper."""

        if paper.doi:
            return f"doi:{cls._normalize_doi(paper.doi)}"

        return f"title:{cls._normalize_title(paper.title)}"

    @staticmethod
    def _normalize_doi(doi: str) -> str:
        """Normalize a DOI for comparison."""

        value = doi.strip().lower()

        value = re.sub(
            r"^https?://doi\.org/",
            "",
            value,
        )

        value = re.sub(
            r"^doi:",
            "",
            value,
        )

        return value.rstrip("/")

    @staticmethod
    def _normalize_title(title: str) -> str:
        """Normalize a title for comparison."""

        value = title.strip().lower()

        value = re.sub(
            r"[^a-z0-9\s]",
            " ",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()