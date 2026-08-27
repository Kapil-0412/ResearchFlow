from datetime import datetime, UTC
from typing import Optional

from pydantic import BaseModel, Field


class Paper(BaseModel):
    """Represents a research paper collected by ResearchFlow."""

    paper_id: str

    title: str
    authors: list[str] = Field(default_factory=list)

    abstract: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)

    year: Optional[int] = None

    source: str

    doi: Optional[str] = None
    paper_url: Optional[str] = None
    pdf_url: Optional[str] = None

    search_query: Optional[str] = None
    query_id: Optional[str] = None

    relevance_score: Optional[float] = None
    relevance_category: Optional[str] = None
    relevance_reason: Optional[str] = None

    user_decision: Optional[str] = None

    pdf_status: str = "unknown"
    download_status: str = "not_downloaded"
    local_path: Optional[str] = None

    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))