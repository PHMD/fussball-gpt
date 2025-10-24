"""
Data aggregation module for KSI prototype.

Fetches and normalizes data from:
1. Kicker API (using kickerde-api-client)
2. Kicker RSS feeds
3. TheSportsDB public API
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import feedparser
import requests
from dotenv import load_dotenv
from models import (
    AggregatedData,
    DataSource,
    NewsArticle,
    PlayerStats,
    SportsEvent,
)

load_dotenv()


class DataAggregator:
    """Aggregates sports data from multiple public sources."""

    def __init__(self):
        self.kicker_rss_url = "https://newsfeed.kicker.de/opml"
        self.sports_db_base_url = "https://www.thesportsdb.com/api/v1/json/3"

        # API-Football (direct API, free tier: 100 req/day)
        # Uses RAPIDAPI_KEY but with direct API endpoints (not RapidAPI format)
        # Free tier limitation: 2021-2023 seasons only (current season requires paid plan)
        self.api_football_key = os.getenv("RAPIDAPI_KEY")
        self.has_api_football = bool(self.api_football_key)
        self.api_football_base_url = "https://v3.football.api-sports.io"

        # Cache setup for player stats (6-hour cache to stay within rate limits)
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_duration = timedelta(hours=6)

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

    def fetch_bundesliga_standings(self) -> str:
        """
        Fetch Bundesliga standings from TheSportsDB (FREE TIER).

        Returns:
            Formatted string with standings table
        """
        try:
            url = f"{self.sports_db_base_url}/lookuptable.php?l=4331&s=2024-2025"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("table"):
                return ""

            # Format standings
            lines = ["=== BUNDESLIGA TABELLE (Saison 2024/25) ===\n"]
            for team in data["table"][:10]:  # Top 10 teams
                pos = team.get("intRank", "?")
                name = team.get("strTeam", "Unknown")
                played = team.get("intPlayed", "0")
                points = team.get("intPoints", "0")
                gf = team.get("intGoalsFor", "0")
                ga = team.get("intGoalsAgainst", "0")

                try:
                    gd = int(gf) - int(ga)
                except:
                    gd = 0

                lines.append(
                    f"{pos:2}. {name:25} | {played:2} Sp. | {points:2} Pkt | {gf}:{ga} ({gd:+d})"
                )

            return "\n".join(lines)

        except Exception as e:
            print(f"Error fetching standings: {e}")
            return ""

    def fetch_recent_results(self) -> list[SportsEvent]:
        """
        Fetch recent Bundesliga results from TheSportsDB (FREE TIER).

        Returns:
            List of recent match events
        """
        events = []

        try:
            url = f"{self.sports_db_base_url}/eventspastleague.php?id=4331"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("events"):
                for event_data in data["events"][:5]:  # Last 5 matches
                    home_team = event_data.get("strHomeTeam", "Unknown")
                    away_team = event_data.get("strAwayTeam", "Unknown")
                    home_score = event_data.get("intHomeScore", "")
                    away_score = event_data.get("intAwayScore", "")
                    date_str = event_data.get("dateEvent", "")

                    # Parse date
                    timestamp = datetime.now()
                    if date_str:
                        try:
                            timestamp = datetime.strptime(date_str, "%Y-%m-%d")
                        except:
                            pass

                    event = SportsEvent(
                        source=DataSource.SPORTS_API,
                        event_type="result",
                        title=f"{home_team} {home_score}:{away_score} {away_team}",
                        content=f"Bundesliga - Ergebnis",
                        timestamp=timestamp,
                        home_team=home_team,
                        away_team=away_team,
                        score=f"{home_score}:{away_score}",
                        league="Bundesliga",
                    )
                    events.append(event)

        except Exception as e:
            print(f"Error fetching recent results: {e}")

        return events

    def fetch_player_stats(self, league_id: int = 78, season: str = "2025") -> list[PlayerStats]:
        """
        Fetch top player statistics from API-Football (direct API, paid tier).

        Args:
            league_id: Bundesliga ID = 78
            season: Season year (2025 = 2024/25 current season)

        Returns:
            List of PlayerStats objects for top performers (current season)
        """
        if not self.has_api_football:
            print("API-Football not configured (RAPIDAPI_KEY missing)")
            return []

        players = []

        try:
            # API-Football direct API endpoint
            url = f"{self.api_football_base_url}/players/topscorers"

            headers = {
                "x-apisports-key": self.api_football_key
            }

            params = {
                "league": league_id,
                "season": season
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("response"):
                # Get top 20 players (top scorers)
                for player_data in data["response"][:20]:
                    player_info = player_data.get("player", {})
                    stats = player_data.get("statistics", [{}])[0]

                    player = PlayerStats(
                        player_name=player_info.get("name", "Unknown"),
                        team=stats.get("team", {}).get("name", "Unknown"),
                        position=stats.get("games", {}).get("position", "Unknown"),

                        # Appearance stats
                        appearances=stats.get("games", {}).get("appearences", 0) or 0,
                        minutes_played=stats.get("games", {}).get("minutes", 0) or 0,

                        # Performance stats
                        goals=stats.get("goals", {}).get("total", 0) or 0,
                        assists=stats.get("goals", {}).get("assists", 0) or 0,
                        shots_total=stats.get("shots", {}).get("total", 0) or 0,
                        shots_on_target=stats.get("shots", {}).get("on", 0) or 0,

                        # Disciplinary
                        yellow_cards=stats.get("cards", {}).get("yellow", 0) or 0,
                        red_cards=stats.get("cards", {}).get("red", 0) or 0,

                        # Additional
                        passes_total=stats.get("passes", {}).get("total"),
                        passes_accurate=stats.get("passes", {}).get("accuracy"),
                        dribbles_successful=stats.get("dribbles", {}).get("success"),

                        # Goalkeeper (if applicable)
                        saves=stats.get("goals", {}).get("saves"),

                        season=f"{season}-{int(season)+1}",
                        league="Bundesliga"
                    )

                    players.append(player)

            print(f"Fetched {len(players)} player stats from API-Football")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print("⚠️  API-Football: Invalid API key or quota exceeded (100 req/day limit)")
            else:
                print(f"HTTP Error fetching player stats: {e}")
        except Exception as e:
            print(f"Error fetching player stats: {e}")

        return players

    def fetch_player_stats_cached(self) -> list[PlayerStats]:
        """Fetch player stats with caching to avoid rate limits."""
        cache_file = self.cache_dir / "player_stats.json"

        # Check cache (6 hour duration)
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < self.cache_duration:
                print(f"Using cached player stats ({cache_age.seconds // 3600}h old)")
                try:
                    with open(cache_file) as f:
                        cached_data = json.load(f)
                        return [PlayerStats(**p) for p in cached_data]
                except Exception as e:
                    print(f"Error loading cache: {e}")

        # Fetch fresh data
        player_stats = self.fetch_player_stats()

        # Save to cache
        if player_stats:
            try:
                with open(cache_file, 'w') as f:
                    json.dump([p.dict() for p in player_stats], f)
            except Exception as e:
                print(f"Error saving cache: {e}")

        return player_stats

    def fetch_team_form(self) -> dict[str, dict]:
        """
        Fetch form guide (last 5 matches) for Bundesliga teams.

        Returns:
            Dict mapping team names to form data with format like:
            {"Bayern München": {"form": "W-W-D-W-L", "points": 10, "matches": [...]}}
        """
        team_forms = {}

        try:
            # First, get standings to get team IDs
            url = f"{self.sports_db_base_url}/lookuptable.php?l=4331&s=2024-2025"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("table"):
                return {}

            # Get top 10 teams (most relevant for users)
            for team_data in data["table"][:10]:
                team_name = team_data.get("strTeam")
                team_id = team_data.get("idTeam")

                if not team_id or not team_name:
                    continue

                # Fetch last 5 events for this team
                try:
                    events_url = f"{self.sports_db_base_url}/eventslast.php?id={team_id}"
                    events_response = requests.get(events_url, timeout=10)
                    events_response.raise_for_status()
                    events_data = events_response.json()

                    if events_data.get("results"):
                        # Process last 5 matches
                        matches = []
                        form_letters = []
                        points = 0

                        for match in events_data["results"][:5]:
                            home_team = match.get("strHomeTeam")
                            away_team = match.get("strAwayTeam")
                            home_score = match.get("intHomeScore")
                            away_score = match.get("intAwayScore")

                            # Skip if scores are missing
                            if home_score is None or away_score is None:
                                continue

                            home_score = int(home_score)
                            away_score = int(away_score)

                            # Determine result from team's perspective
                            if home_team == team_name:
                                if home_score > away_score:
                                    form_letters.append("W")
                                    points += 3
                                elif home_score == away_score:
                                    form_letters.append("D")
                                    points += 1
                                else:
                                    form_letters.append("L")
                            elif away_team == team_name:
                                if away_score > home_score:
                                    form_letters.append("W")
                                    points += 3
                                elif away_score == home_score:
                                    form_letters.append("D")
                                    points += 1
                                else:
                                    form_letters.append("L")

                            matches.append({
                                "home": home_team,
                                "away": away_team,
                                "score": f"{home_score}:{away_score}"
                            })

                        if form_letters:
                            team_forms[team_name] = {
                                "form": "-".join(form_letters),
                                "points": points,
                                "matches": matches
                            }

                except Exception as e:
                    print(f"Error fetching form for {team_name}: {e}")
                    continue

        except Exception as e:
            print(f"Error fetching team forms: {e}")

        return team_forms

    def fetch_team_form_cached(self) -> dict[str, dict]:
        """Fetch team form with caching (6-hour cache)."""
        cache_file = self.cache_dir / "team_form.json"

        # Check cache
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < self.cache_duration:
                print(f"Using cached team form ({cache_age.seconds // 3600}h old)")
                try:
                    with open(cache_file) as f:
                        return json.load(f)
                except Exception as e:
                    print(f"Error loading cache: {e}")

        # Fetch fresh data
        team_forms = self.fetch_team_form()

        # Save to cache
        if team_forms:
            try:
                with open(cache_file, 'w') as f:
                    json.dump(team_forms, f)
            except Exception as e:
                print(f"Error saving cache: {e}")

        return team_forms

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
            AggregatedData object containing all normalized data with standings prepended
        """
        print("Fetching data from all sources...")

        # Fetch news
        kicker_api_articles = self.fetch_kicker_api()
        kicker_rss_articles = self.fetch_kicker_rss()
        all_articles = kicker_api_articles + kicker_rss_articles

        # Fetch standings (will be prepended to context)
        standings_text = self.fetch_bundesliga_standings()

        # Fetch sports events
        upcoming_fixtures = self.fetch_sports_api()
        recent_results = self.fetch_recent_results()
        all_events = recent_results + upcoming_fixtures

        # Fetch player stats (cached to stay within rate limits)
        player_stats = self.fetch_player_stats_cached() if self.has_api_football else []

        # Fetch team form guide (cached, 6 hours)
        team_forms = self.fetch_team_form_cached()

        print(f"Fetched {len(all_articles)} articles, {len(all_events)} events, {len(player_stats)} player stats, {len(team_forms)} team forms")

        # Create aggregated data
        data = AggregatedData(
            news_articles=all_articles,
            sports_events=all_events,
            player_stats=player_stats,
        )

        # Prepend standings + form guide to context (monkey-patch for this instance)
        form_guide_text = self._format_form_guide(team_forms)
        original_context = data.to_context_string()

        enhanced_parts = []
        if standings_text:
            enhanced_parts.append(standings_text)
        if form_guide_text:
            enhanced_parts.append(form_guide_text)
        enhanced_parts.append(original_context)

        data._enhanced_context = "\n\n".join(enhanced_parts)

        return data

    def _format_form_guide(self, team_forms: dict[str, dict]) -> str:
        """Format team form data for LLM context."""
        if not team_forms:
            return ""

        lines = ["=== TEAM FORM GUIDE (Last 5 Matches) ==="]
        lines.append("")

        # Sort by current form points (most in-form teams first)
        sorted_teams = sorted(team_forms.items(), key=lambda x: x[1]["points"], reverse=True)

        for team_name, form_data in sorted_teams:
            form_str = form_data["form"]
            points = form_data["points"]
            lines.append(f"{team_name}: {form_str} ({points} Punkte aus letzten 5 Spielen)")

        return "\n".join(lines)


# Monkey-patch to_context_string to use enhanced context if available
_original_to_context_string = AggregatedData.to_context_string

def _enhanced_to_context_string(self) -> str:
    """Use enhanced context (with standings) if available, else original."""
    if hasattr(self, '_enhanced_context'):
        return self._enhanced_context
    return _original_to_context_string(self)

AggregatedData.to_context_string = _enhanced_to_context_string


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
    print("SAMPLE DATA FOR LLM CONTEXT (with standings)")
    print("="*60)
    context = data.to_context_string()
    print(context[:1500])  # Print first 1500 chars
    print("\n... (truncated)")
    print(f"\nTotal context size: {len(context)} characters")


if __name__ == "__main__":
    main()
