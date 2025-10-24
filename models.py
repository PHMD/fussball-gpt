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


class PlayerStats(BaseModel):
    """Player statistics from API-Football."""
    source: DataSource = DataSource.SPORTS_API
    player_name: str
    team: str
    position: str

    # Appearance stats
    appearances: int = 0
    minutes_played: int = 0

    # Performance stats
    goals: int = 0
    assists: int = 0
    shots_total: int = 0
    shots_on_target: int = 0

    # Disciplinary
    yellow_cards: int = 0
    red_cards: int = 0

    # Additional (optional)
    passes_total: Optional[int] = None
    passes_accurate: Optional[int] = None
    dribbles_successful: Optional[int] = None

    # Goalkeeper (if applicable)
    saves: Optional[int] = None
    goals_conceded: Optional[int] = None
    clean_sheets: Optional[int] = None

    # Metadata
    season: str = "2022-2023"
    league: str = "Bundesliga"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AggregatedData(BaseModel):
    """Container for all aggregated data to pass to LLM."""
    news_articles: list[NewsArticle] = Field(default_factory=list)
    sports_events: list[SportsEvent] = Field(default_factory=list)
    player_stats: list[PlayerStats] = Field(default_factory=list)
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

        if self.player_stats:
            lines.append("=== TOP PLAYER STATISTICS (Bundesliga 2022/23 - Letzte vollständige Saison) ===")

            # Group by category for better readability
            top_scorers = sorted(self.player_stats, key=lambda p: p.goals, reverse=True)[:10]
            top_assists = sorted(self.player_stats, key=lambda p: p.assists, reverse=True)[:10]

            lines.append("\nTop Scorers:")
            for i, player in enumerate(top_scorers, 1):
                lines.append(f"{i}. {player.player_name} ({player.team}) - {player.goals} Tore, {player.assists} Vorlagen, {player.minutes_played} Min")

            lines.append("\nTop Assists:")
            for i, player in enumerate(top_assists, 1):
                lines.append(f"{i}. {player.player_name} ({player.team}) - {player.assists} Vorlagen, {player.goals} Tore, {player.appearances} Spiele")

            lines.append("")

        return "\n".join(lines)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
