from datetime import datetime, UTC
from typing import Optional

from pydantic import BaseModel, Field


class Paper(BaseModel):
    """Represents a research paper collected by ResearchFlow."""

    # ------------------------------------------------------------------
    # Paper identity and bibliographic metadata
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Search and discovery information
    # ------------------------------------------------------------------

    search_query: Optional[str] = None
    query_id: Optional[str] = None

    # All keywords that have discovered this paper.
    #
    # Example:
    # [
    #     "counterfactual cybersecurity",
    #     "cyber attack reasoning",
    #     "attack path analysis"
    # ]
    found_in_keywords: list[str] = Field(default_factory=list)

    # All scholarly sources/databases where this paper was found.
    #
    # Example:
    # [
    #     "IEEE",
    #     "ACM",
    #     "OpenAlex"
    # ]
    found_in_sources: list[str] = Field(default_factory=list)

    # ------------------------------------------------------------------
    # Relevance and screening information
    # ------------------------------------------------------------------

    relevance_score: Optional[float] = None
    relevance_category: Optional[str] = None
    relevance_reason: Optional[str] = None

    user_decision: Optional[str] = None

    # ------------------------------------------------------------------
    # PDF and download information
    # ------------------------------------------------------------------

    pdf_status: str = "unknown"
    download_status: str = "not_downloaded"

    # Number of times ResearchFlow has attempted to download the PDF.
    download_attempts: int = 0

    # Timestamp of the most recent download attempt.
    last_download_attempt: Optional[datetime] = None

    # Human-readable reason for the most recent download failure.
    #
    # Example:
    # "Institutional access required"
    download_error: Optional[str] = None

    # Local path of the downloaded PDF, if available.
    local_path: Optional[str] = None

    # ------------------------------------------------------------------
    # Collection metadata
    # ------------------------------------------------------------------

    collected_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )