"""Tests for data models."""

import pytest
from datetime import datetime
from models import DataSource, NewsArticle, SportsEvent, AggregatedData


class TestNewsArticle:
    """Test NewsArticle model."""

    def test_create_valid_article(self):
        """Test creating a valid news article."""
        article = NewsArticle(
            source=DataSource.KICKER_RSS,
            title="Test Article",
            content="Test content",
            timestamp=datetime.now()
        )
        assert article.title == "Test Article"
        assert article.source == DataSource.KICKER_RSS

    def test_article_with_optional_fields(self):
        """Test article with all optional fields."""
        article = NewsArticle(
            source=DataSource.KICKER_API,
            title="Test",
            content="Content",
            timestamp=datetime.now(),
            url="https://example.com",
            author="Test Author",
            category="Sports"
        )
        assert article.url == "https://example.com"
        assert article.author == "Test Author"


class TestSportsEvent:
    """Test SportsEvent model."""

    def test_create_valid_event(self):
        """Test creating a valid sports event."""
        event = SportsEvent(
            source=DataSource.SPORTS_API,
            event_type="match",
            title="Bayern vs Dortmund",
            content="Bundesliga match",
            timestamp=datetime.now()
        )
        assert event.event_type == "match"
        assert event.title == "Bayern vs Dortmund"

    def test_event_with_score(self):
        """Test event with score information."""
        event = SportsEvent(
            source=DataSource.SPORTS_API,
            event_type="score",
            title="Bayern vs Dortmund",
            content="Match finished",
            timestamp=datetime.now(),
            home_team="Bayern",
            away_team="Dortmund",
            score="3-1"
        )
        assert event.score == "3-1"
        assert event.home_team == "Bayern"


class TestAggregatedData:
    """Test AggregatedData model."""

    def test_empty_aggregation(self):
        """Test creating empty aggregated data."""
        data = AggregatedData()
        assert len(data.news_articles) == 0
        assert len(data.sports_events) == 0

    def test_to_context_string(self):
        """Test conversion to LLM context string."""
        article = NewsArticle(
            source=DataSource.KICKER_RSS,
            title="Test News",
            content="Test content",
            timestamp=datetime.now()
        )
        data = AggregatedData(news_articles=[article])
        context = data.to_context_string()

        assert "Test News" in context
        assert "NEWS ARTICLES" in context

    def test_aggregation_with_multiple_sources(self):
        """Test aggregation with news and events."""
        article = NewsArticle(
            source=DataSource.KICKER_RSS,
            title="News",
            content="Content",
            timestamp=datetime.now()
        )
        event = SportsEvent(
            source=DataSource.SPORTS_API,
            event_type="match",
            title="Match",
            content="Match info",
            timestamp=datetime.now()
        )
        data = AggregatedData(
            news_articles=[article],
            sports_events=[event]
        )

        assert len(data.news_articles) == 1
        assert len(data.sports_events) == 1

        context = data.to_context_string()
        assert "NEWS ARTICLES" in context
        assert "SPORTS EVENTS" in context
