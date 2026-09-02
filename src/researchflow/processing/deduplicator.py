import re
from collections.abc import Iterable

from researchflow.models import Paper


class PaperDeduplicator:
    """Deduplicate research papers across sources."""

    def deduplicate(
        self,
        papers: Iterable[Paper],
    ) -> list[Paper]:
        """Return unique papers while preserving discovery information."""

        merged: dict[str, Paper] = {}

        for paper in papers:
            self._initialize_discovery_information(paper)

            key = self._paper_key(paper)

            if key not in merged:
                merged[key] = paper
                continue

            self._merge_paper(
                merged[key],
                paper,
            )

        return list(merged.values())

    @staticmethod
    def _initialize_discovery_information(
        paper: Paper,
    ) -> None:
        """Ensure the paper contains its own discovery information."""

        if paper.search_query:
            if paper.search_query not in paper.found_in_keywords:
                paper.found_in_keywords.append(
                    paper.search_query
                )

        if paper.source:
            if paper.source not in paper.found_in_sources:
                paper.found_in_sources.append(
                    paper.source
                )

    @staticmethod
    def _merge_paper(
        existing: Paper,
        duplicate: Paper,
    ) -> None:
        """Merge discovery information from a duplicate paper."""

        for keyword in duplicate.found_in_keywords:
            if keyword not in existing.found_in_keywords:
                existing.found_in_keywords.append(keyword)

        for source in duplicate.found_in_sources:
            if source not in existing.found_in_sources:
                existing.found_in_sources.append(source)

    @classmethod
    def _paper_key(cls, paper: Paper) -> str:
        """
        Generate a key for identifying the same paper.

        DOI is preferred. If DOI is unavailable, a normalized
        title is used as a fallback.
        """

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