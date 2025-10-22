"""
Data models for KSI prototype.

All data sources are normalized to these schemas for consistent LLM processing.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DataSource(str, Enum):
    """Enumeration of supported data sources."""
    KICKER_API = "kicker_api"
    KICKER_RSS = "kicker_rss"
    SPORTS_API = "sports_api"


class NewsArticle(BaseModel):
    """Normalized news article from any source."""
    source: DataSource
    title: str
    content: str
    url: Optional[str] = None
    timestamp: datetime
    author: Optional[str] = None
    category: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SportsEvent(BaseModel):
    """Normalized sports event data (scores, schedules, stats)."""
    source: DataSource
    event_type: str = Field(..., description="Type of event: match, score, schedule, stat")
    title: str
    content: str  # Human-readable description
    timestamp: datetime

    # Optional structured data
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    score: Optional[str] = None
    league: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AggregatedData(BaseModel):
    """Container for all aggregated data to pass to LLM."""
    news_articles: list[NewsArticle] = Field(default_factory=list)
    sports_events: list[SportsEvent] = Field(default_factory=list)
    aggregation_timestamp: datetime = Field(default_factory=datetime.now)

    def to_context_string(self) -> str:
        """Convert aggregated data to LLM context string."""
        lines = [f"Data aggregated at: {self.aggregation_timestamp.isoformat()}\n"]

        if self.news_articles:
            lines.append("=== NEWS ARTICLES ===")
            for article in self.news_articles:
                lines.append(f"[{article.timestamp.strftime('%Y-%m-%d %H:%M')}] {article.title}")
                lines.append(f"Source: {article.source.value}")
                lines.append(f"Content: {article.content[:500]}...")  # Truncate for context
                lines.append("")

        if self.sports_events:
            lines.append("=== SPORTS EVENTS ===")
            for event in self.sports_events:
                lines.append(f"[{event.timestamp.strftime('%Y-%m-%d %H:%M')}] {event.title}")
                lines.append(f"Source: {event.source.value}")
                lines.append(f"Content: {event.content}")
                if event.score:
                    lines.append(f"Score: {event.score}")
                lines.append("")

        return "\n".join(lines)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
