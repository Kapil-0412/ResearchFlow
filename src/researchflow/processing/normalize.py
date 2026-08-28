from typing import Any

from researchflow.models import Paper


def normalize_text(value: Any) -> str | None:
    """Convert a value into clean text."""

    if value is None:
        return None

    text = str(value).strip()

    return text if text else None


def normalize_authors(authors: Any) -> list[str]:
    """Normalize different author formats into a list of names."""

    if not authors:
        return []

    if isinstance(authors, str):
        return [authors.strip()] if authors.strip() else []

    normalized = []

    for author in authors:
        if isinstance(author, str):
            name = author.strip()

        elif isinstance(author, dict):
            name = (
                author.get("name")
                or author.get("display_name")
                or _build_crossref_author_name(author)
            )

        else:
            name = None

        if name:
            normalized.append(name.strip())

    return normalized


def _build_crossref_author_name(author: dict) -> str | None:
    """Build an author name from Crossref-style metadata."""

    given = author.get("given", "")
    family = author.get("family", "")

    name = f"{given} {family}".strip()

    return name if name else None


def normalize_keywords(keywords: Any) -> list[str]:
    """Normalize keywords into a clean list."""

    if not keywords:
        return []

    if isinstance(keywords, str):
        return [
            keyword.strip()
            for keyword in keywords.split(",")
            if keyword.strip()
        ]

    return [
        str(keyword).strip()
        for keyword in keywords
        if str(keyword).strip()
    ]


def normalize_paper(
    *,
    paper_id: str,
    title: Any,
    authors: Any = None,
    abstract: Any = None,
    keywords: Any = None,
    year: Any = None,
    source: str,
    doi: Any = None,
    paper_url: Any = None,
    pdf_url: Any = None,
    search_query: Any = None,
    query_id: Any = None,
) -> Paper:
    """Create a standardized Paper object from source metadata."""

    normalized_year = None

    if year is not None:
        try:
            normalized_year = int(year)
        except (TypeError, ValueError):
            normalized_year = None

    return Paper(
        paper_id=str(paper_id),
        title=normalize_text(title) or "Untitled",
        authors=normalize_authors(authors),
        abstract=normalize_text(abstract),
        keywords=normalize_keywords(keywords),
        year=normalized_year,
        source=source,
        doi=normalize_text(doi),
        paper_url=normalize_text(paper_url),
        pdf_url=normalize_text(pdf_url),
        search_query=normalize_text(search_query),
        query_id=normalize_text(query_id),
    )