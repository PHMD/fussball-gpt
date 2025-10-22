"""
Data aggregation module for KSI prototype.

Fetches and normalizes data from:
1. Kicker API (using kickerde-api-client)
2. Kicker RSS feeds
3. TheSportsDB public API
"""

import os
from datetime import datetime
from typing import Optional
import feedparser
import requests
from models import (
    AggregatedData,
    DataSource,
    NewsArticle,
    SportsEvent,
)


class DataAggregator:
    """Aggregates sports data from multiple public sources."""

    def __init__(self):
        self.kicker_rss_url = "https://newsfeed.kicker.de/opml"
        self.sports_db_base_url = "https://www.thesportsdb.com/api/v1/json/3"

    def fetch_kicker_api(self) -> list[NewsArticle]:
        """
        Fetch data from Kicker API using kickerde-api-client.

        Note: The kickerde-api-client package provides league/team data,
        NOT news articles. For news, use fetch_kicker_rss() instead.

        This method is kept for potential future expansion (e.g., team stats,
        league standings) but currently returns empty list.

        Returns:
            List of normalized NewsArticle objects (currently empty)
        """
        articles = []

        # The kickerde-api-client is for league/team data, not news
        # Keeping this as a placeholder for future expansion
        # For news articles, use RSS feeds (fetch_kicker_rss)

        return articles

    def fetch_kicker_rss(self) -> list[NewsArticle]:
        """
        Fetch news from Kicker RSS feeds.

        Returns:
            List of normalized NewsArticle objects
        """
        articles = []

        try:
            # Parse the OPML feed to get individual RSS feeds
            feed = feedparser.parse(self.kicker_rss_url)

            # Get the first few RSS feed URLs from the OPML
            rss_feeds = []
            if hasattr(feed, 'entries'):
                for entry in feed.entries[:3]:  # Limit to first 3 feeds
                    if hasattr(entry, 'xmlUrl'):
                        rss_feeds.append(entry.xmlUrl)

            # If OPML parsing fails, try direct RSS feed URLs
            if not rss_feeds:
                rss_feeds = [
                    "https://newsfeed.kicker.de/news/aktuell",
                    "https://newsfeed.kicker.de/bundesliga/news",
                ]

            # Parse each RSS feed
            for feed_url in rss_feeds:
                try:
                    rss_data = feedparser.parse(feed_url)

                    for entry in rss_data.entries[:5]:  # Get 5 articles per feed
                        # Parse timestamp
                        timestamp = datetime.now()
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            timestamp = datetime(*entry.published_parsed[:6])

                        article = NewsArticle(
                            source=DataSource.KICKER_RSS,
                            title=entry.get("title", "No title"),
                            content=entry.get("summary", entry.get("description", "No content")),
                            url=entry.get("link"),
                            timestamp=timestamp,
                            category=rss_data.feed.get("title"),
                        )
                        articles.append(article)

                except Exception as e:
                    print(f"Error parsing RSS feed {feed_url}: {e}")

        except Exception as e:
            print(f"Error fetching Kicker RSS: {e}")

        return articles

    def fetch_sports_api(self) -> list[SportsEvent]:
        """
        Fetch sports data from TheSportsDB public API.

        Returns:
            List of normalized SportsEvent objects
        """
        events = []

        try:
            # Get recent events for popular leagues
            # Using free tier endpoints (no API key needed for basic access)

            # Example: Get latest events from Bundesliga (league ID: 4331)
            league_ids = [
                "4331",  # Bundesliga
                "4332",  # 2. Bundesliga
            ]

            for league_id in league_ids:
                try:
                    # Get next 15 events
                    url = f"{self.sports_db_base_url}/eventsnextleague.php?id={league_id}"
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    data = response.json()

                    if data.get("events"):
                        for event_data in data["events"][:5]:  # Limit to 5 per league
                            # Parse timestamp
                            event_time = event_data.get("strTimestamp")
                            timestamp = datetime.fromisoformat(event_time) if event_time else datetime.now()

                            event = SportsEvent(
                                source=DataSource.SPORTS_API,
                                event_type="schedule",
                                title=f"{event_data.get('strHomeTeam')} vs {event_data.get('strAwayTeam')}",
                                content=f"Upcoming match in {event_data.get('strLeague', 'Unknown League')}",
                                timestamp=timestamp,
                                home_team=event_data.get("strHomeTeam"),
                                away_team=event_data.get("strAwayTeam"),
                                league=event_data.get("strLeague"),
                            )
                            events.append(event)

                except Exception as e:
                    print(f"Error fetching sports data for league {league_id}: {e}")

        except Exception as e:
            print(f"Error fetching sports API: {e}")

        return events

    def aggregate_all(self) -> AggregatedData:
        """
        Fetch and aggregate data from all sources.

        Returns:
            AggregatedData object containing all normalized data
        """
        print("Fetching data from all sources...")

        # Fetch from all sources
        kicker_api_articles = self.fetch_kicker_api()
        kicker_rss_articles = self.fetch_kicker_rss()
        sports_events = self.fetch_sports_api()

        # Combine all news articles
        all_articles = kicker_api_articles + kicker_rss_articles

        print(f"Fetched {len(all_articles)} news articles and {len(sports_events)} sports events")

        return AggregatedData(
            news_articles=all_articles,
            sports_events=sports_events,
        )


def main():
    """Standalone testing of data aggregation."""
    aggregator = DataAggregator()
    data = aggregator.aggregate_all()

    print("\n" + "="*60)
    print("AGGREGATED DATA SUMMARY")
    print("="*60)
    print(f"Total news articles: {len(data.news_articles)}")
    print(f"Total sports events: {len(data.sports_events)}")
    print("\n" + "="*60)
    print("SAMPLE DATA FOR LLM CONTEXT")
    print("="*60)
    print(data.to_context_string()[:1000])  # Print first 1000 chars
    print("\n... (truncated)")


if __name__ == "__main__":
    main()
