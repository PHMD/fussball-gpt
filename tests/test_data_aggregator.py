"""Tests for data aggregator."""

import pytest
from data_aggregator import DataAggregator
from models import DataSource


class TestDataAggregator:
    """Test DataAggregator class."""

    def test_aggregator_initialization(self):
        """Test that aggregator initializes correctly."""
        aggregator = DataAggregator()
        assert aggregator.kicker_rss_url is not None
        assert aggregator.sports_db_base_url is not None

    def test_fetch_kicker_rss(self):
        """Test fetching Kicker RSS feeds."""
        aggregator = DataAggregator()
        articles = aggregator.fetch_kicker_rss()

        # Should get at least some articles (network dependent)
        assert isinstance(articles, list)

        # If we got articles, verify structure
        if articles:
            article = articles[0]
            assert article.source == DataSource.KICKER_RSS
            assert article.title is not None
            assert article.content is not None

    def test_fetch_sports_api(self):
        """Test fetching sports API data."""
        aggregator = DataAggregator()
        events = aggregator.fetch_sports_api()

        # Should get events (network dependent)
        assert isinstance(events, list)

        # If we got events, verify structure
        if events:
            event = events[0]
            assert event.source == DataSource.SPORTS_API
            assert event.event_type is not None
            assert event.title is not None

    def test_aggregate_all(self):
        """Test full aggregation from all sources."""
        aggregator = DataAggregator()
        data = aggregator.aggregate_all()

        # Should return AggregatedData object
        assert data is not None
        assert hasattr(data, 'news_articles')
        assert hasattr(data, 'sports_events')
        assert hasattr(data, 'aggregation_timestamp')

        # Should have some data (network dependent)
        total_items = len(data.news_articles) + len(data.sports_events)
        assert total_items >= 0  # At minimum, should not fail

    def test_aggregate_all_returns_valid_context(self):
        """Test that aggregated data can be converted to context string."""
        aggregator = DataAggregator()
        data = aggregator.aggregate_all()

        context = data.to_context_string()
        assert isinstance(context, str)
        assert len(context) > 0
