from .deduplicator import PaperDeduplicator
from .duplicate_report import DuplicateReport
from .normalize import (
    normalize_authors,
    normalize_keywords,
    normalize_paper,
    normalize_text,
)

__all__ = [
    "PaperDeduplicator",
    "DuplicateReport",
    "normalize_authors",
    "normalize_keywords",
    "normalize_paper",
    "normalize_text",
]