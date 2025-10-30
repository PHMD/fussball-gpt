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

        # The Odds API (free tier: 500 req/month)
        self.odds_api_key = os.getenv("ODDS_API_KEY")
        self.has_odds_api = bool(self.odds_api_key)
        self.odds_api_base_url = "https://api.the-odds-api.com/v4"

        # Brave Search API (free tier: 2K req/month, 1 req/sec)
        self.brave_search_key = os.getenv("BRAVE_SEARCH_API_KEY")
        self.has_brave_search = bool(self.brave_search_key)
        self.brave_search_base_url = "https://api.search.brave.com/res/v1/web/search"

        # Cache setup
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_duration = timedelta(hours=6)  # Player stats, team form
        self.odds_cache_duration = timedelta(hours=24)  # Odds update less frequently

        # Session-level cache for Brave Search (in-memory, 5-minute TTL)
        self.brave_search_session_cache = {}  # {query_hash: (articles, timestamp)}
        self.brave_cache_ttl = timedelta(minutes=5)

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

    def _is_bundesliga_content(self, title: str, content: str) -> bool:
        """
        Check if article content is Bundesliga-related.

        Returns True if content is about Bundesliga (German soccer).
        Returns False for other sports (NFL, NBA, etc.) or other leagues.
        """
        text = f"{title} {content}".lower()

        # Exclude non-soccer sports
        excluded_sports = ['nfl', 'quarterback', 'vikings', 'nba', 'baseball', 'hockey', 'tennis']
        if any(sport in text for sport in excluded_sports):
            return False

        # Bundesliga team names (major clubs)
        bundesliga_teams = [
            'bayern', 'münchen', 'dortmund', 'bvb', 'leipzig', 'leverkusen',
            'frankfurt', 'freiburg', 'union berlin', 'köln', 'hoffenheim',
            'wolfsburg', 'gladbach', 'stuttgart', 'bremen', 'augsburg',
            'bochum', 'mainz', 'heidenheim', 'darmstadt'
        ]

        # Bundesliga keywords
        bundesliga_keywords = ['bundesliga', '1. bundesliga', 'dfl']

        # Check for matches
        has_team = any(team in text for team in bundesliga_teams)
        has_keyword = any(keyword in text for keyword in bundesliga_keywords)

        return has_team or has_keyword

    def fetch_kicker_rss(self) -> list[NewsArticle]:
        """
        Fetch news from Kicker RSS feeds.

        Returns:
            List of normalized NewsArticle objects
        """
        articles = []
        seen_urls = set()  # Track duplicates across feeds

        try:
            # Parse the OPML feed to get individual RSS feeds
            feed = feedparser.parse(self.kicker_rss_url)

            # Use multiple feeds to maximize Bundesliga coverage (Oct 2025)
            # Combining these gives ~7 unique Bundesliga articles vs 5 from single feed
            rss_feeds = [
                "https://newsfeed.kicker.de/news/aktuell",   # General news (5 Bundesliga)
                "https://newsfeed.kicker.de/news/fussball",  # Soccer-specific (7 Bundesliga, some overlap)
            ]

            # Parse each RSS feed
            for feed_url in rss_feeds:
                try:
                    rss_data = feedparser.parse(feed_url)

                    # Fetch more articles since we're filtering (get 20, filter to ~5-10 Bundesliga)
                    for entry in rss_data.entries[:20]:
                        title = entry.get("title", "No title")
                        content = entry.get("summary", entry.get("description", "No content"))
                        url = entry.get("link")

                        # Skip duplicates (same article in multiple feeds)
                        if url in seen_urls:
                            continue

                        # Filter: Only include Bundesliga-related content
                        if not self._is_bundesliga_content(title, content):
                            continue

                        # Mark as seen
                        seen_urls.add(url)

                        # Parse timestamp
                        timestamp = datetime.now()
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            timestamp = datetime(*entry.published_parsed[:6])

                        article = NewsArticle(
                            source=DataSource.KICKER_RSS,
                            title=title,
                            content=content,
                            url=url,
                            timestamp=timestamp,
                            category=rss_data.feed.get("title"),
                        )
                        articles.append(article)

                except Exception as e:
                    print(f"Error parsing RSS feed {feed_url}: {e}")

        except Exception as e:
            print(f"Error fetching Kicker RSS: {e}")

        return articles

    def _extract_entities(self, title: str, description: str, snippets: list[str]) -> dict:
        """
        Extract entities (teams, players, keywords) from article text.

        Args:
            title: Article title
            description: Article description
            snippets: Additional text snippets

        Returns:
            Dict with teams, players, and keywords found
        """
        text = f"{title} {description} {' '.join(snippets)}".lower()

        # Bundesliga teams
        teams = [
            'bayern', 'münchen', 'dortmund', 'bvb', 'leipzig', 'rb leipzig',
            'leverkusen', 'bayer leverkusen', 'frankfurt', 'eintracht',
            'freiburg', 'union berlin', 'köln', 'fc köln', 'hoffenheim',
            'wolfsburg', 'vfl wolfsburg', 'gladbach', 'borussia', 'stuttgart',
            'bremen', 'werder', 'augsburg', 'bochum', 'mainz', 'heidenheim'
        ]

        # Topic keywords
        keywords = {
            'match': ['spiel', 'match', 'sieg', 'niederlage', 'unentschieden', 'tor', 'goal'],
            'injury': ['verletzung', 'injury', 'ausfall', 'gesperrt', 'suspended'],
            'transfer': ['transfer', 'wechsel', 'verpflichtet', 'signing'],
            'tactics': ['taktik', 'tactics', 'formation', 'strategie'],
            'stats': ['statistik', 'stats', 'zahlen', 'rekord', 'record']
        }

        found_teams = [team for team in teams if team in text]
        found_keywords = {}
        for category, words in keywords.items():
            if any(word in text for word in words):
                found_keywords[category] = True

        return {
            'teams': list(set(found_teams)),
            'topics': list(found_keywords.keys())
        }

    def _classify_article_type(self, entities: dict) -> str:
        """
        Classify article type based on extracted entities.

        Args:
            entities: Dict with teams and topics

        Returns:
            Article type classification
        """
        topics = entities.get('topics', [])

        if 'match' in topics:
            return "Match Report"
        elif 'injury' in topics:
            return "Injury Update"
        elif 'transfer' in topics:
            return "Transfer News"
        elif 'tactics' in topics:
            return "Tactical Analysis"
        elif 'stats' in topics:
            return "Performance Stats"
        else:
            return "General News"

    def _combine_snippets(self, result: dict) -> str:
        """
        Combine description and extra_snippets for richer content.

        Args:
            result: Brave Search result dict

        Returns:
            Combined text content
        """
        parts = [result.get("description", "")]
        extra_snippets = result.get("extra_snippets", [])
        if extra_snippets:
            parts.extend(extra_snippets)
        return "\n\n".join(parts)

    def fetch_kicker_articles_brave(self, query: str, max_results: int = 5) -> list[NewsArticle]:
        """
        Search kicker.de using Brave Search API for relevant Bundesliga articles.

        Enhanced with:
        - Session-level caching (5-minute TTL)
        - Entity extraction (teams, topics)
        - Article type classification
        - Extra snippets for richer content

        Used as fallback when RSS feeds have insufficient coverage for user queries.

        Args:
            query: Search query (will be prepended with "site:kicker.de Bundesliga")
            max_results: Maximum number of results to return (default: 5)

        Returns:
            List of NewsArticle objects from Brave Search results
        """
        if not self.has_brave_search:
            return []

        # Check session cache
        query_key = hash(query.lower().strip())

        if query_key in self.brave_search_session_cache:
            articles, cached_at = self.brave_search_session_cache[query_key]
            age = datetime.now() - cached_at

            if age < self.brave_cache_ttl:
                print(f"[Using cached Brave Search results ({age.seconds}s old)]")
                return articles

        articles = []

        try:
            # Search kicker.de specifically for Bundesliga content
            search_query = f"site:kicker.de Bundesliga {query}"

            response = requests.get(
                self.brave_search_base_url,
                headers={
                    "Accept": "application/json",
                    "X-Subscription-Token": self.brave_search_key,
                },
                params={
                    "q": search_query,
                    "count": max_results,
                    "freshness": "pw",  # Past week for recency
                },
                timeout=2  # Fast timeout (2 seconds)
            )

            response.raise_for_status()
            data = response.json()

            # Extract web results
            results = data.get("web", {}).get("results", [])

            for result in results:
                # Extract metadata
                title = result.get("title", "No title")
                description = result.get("description", "")
                extra_snippets = result.get("extra_snippets", [])

                # Combine all content (description + extra_snippets)
                full_content = self._combine_snippets(result)

                # Extract entities and classify
                entities = self._extract_entities(title, description, extra_snippets)
                article_type = self._classify_article_type(entities)

                # Create enhanced NewsArticle
                article = NewsArticle(
                    source=DataSource.KICKER_RSS,  # Keep same source type for consistency
                    title=title,
                    content=full_content,  # Now includes extra_snippets (~1700 chars)
                    url=result.get("url"),
                    timestamp=datetime.now(),  # Brave doesn't provide publish date
                    category=f"{article_type} (via Brave Search)",
                )
                articles.append(article)

            if articles:
                print(f"Brave Search found {len(articles)} additional Bundesliga articles")

            # Cache results for session
            self.brave_search_session_cache[query_key] = (articles, datetime.now())

        except requests.exceptions.Timeout:
            print("Brave Search timeout (2s limit exceeded)")
        except requests.exceptions.HTTPError as e:
            print(f"Brave Search API error: {e}")
        except Exception as e:
            print(f"Brave Search failed: {e}")

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

    def fetch_betting_odds(self) -> dict[str, dict]:
        """
        Fetch pre-match betting odds for Bundesliga fixtures from The Odds API.

        Returns:
            Dict mapping match IDs to odds data like:
            {"match_id": {"home": "Bayern", "away": "Dortmund", "odds": {"home": 1.50, "draw": 4.20, "away": 7.00}}}
        """
        if not self.has_odds_api:
            print("The Odds API not configured (ODDS_API_KEY missing)")
            return {}

        odds_data = {}

        try:
            # Fetch odds for German Bundesliga
            url = f"{self.odds_api_base_url}/sports/soccer_germany_bundesliga/odds/"

            params = {
                "apiKey": self.odds_api_key,
                "regions": "eu",  # European bookmakers
                "markets": "h2h",  # Head-to-head (match winner)
                "oddsFormat": "decimal"  # European decimal format
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Process odds data
            for event in data:
                match_id = event.get("id")
                home_team = event.get("home_team")
                away_team = event.get("away_team")
                commence_time = event.get("commence_time")

                # Get average odds from first bookmaker (or average if multiple)
                bookmakers = event.get("bookmakers", [])
                if not bookmakers:
                    continue

                # Use first bookmaker's odds (could average multiple in future)
                first_bookmaker = bookmakers[0]
                markets = first_bookmaker.get("markets", [])

                # Find h2h market
                h2h_market = next((m for m in markets if m.get("key") == "h2h"), None)
                if not h2h_market:
                    continue

                outcomes = h2h_market.get("outcomes", [])

                # Extract odds for home, draw, away
                odds = {}
                for outcome in outcomes:
                    name = outcome.get("name")
                    price = outcome.get("price")

                    if name == home_team:
                        odds["home"] = price
                    elif name == away_team:
                        odds["away"] = price
                    elif name.lower() == "draw":
                        odds["draw"] = price

                if odds:
                    odds_data[match_id] = {
                        "home": home_team,
                        "away": away_team,
                        "commence_time": commence_time,
                        "odds": odds,
                        "bookmaker": first_bookmaker.get("title", "Unknown")
                    }

            print(f"Fetched odds for {len(odds_data)} Bundesliga fixtures")

            # Check remaining quota
            remaining = response.headers.get("x-requests-remaining")
            if remaining:
                print(f"Odds API requests remaining: {remaining}")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("⚠️  The Odds API: Invalid API key")
            elif e.response.status_code == 429:
                print("⚠️  The Odds API: Rate limit exceeded (500 req/month on free tier)")
            else:
                print(f"HTTP Error fetching odds: {e}")
        except Exception as e:
            print(f"Error fetching betting odds: {e}")

        return odds_data

    def fetch_betting_odds_cached(self) -> dict[str, dict]:
        """Fetch betting odds with caching (24-hour cache)."""
        cache_file = self.cache_dir / "betting_odds.json"

        # Check cache
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < self.odds_cache_duration:
                print(f"Using cached betting odds ({cache_age.seconds // 3600}h old)")
                try:
                    with open(cache_file) as f:
                        return json.load(f)
                except Exception as e:
                    print(f"Error loading cache: {e}")

        # Fetch fresh data
        odds_data = self.fetch_betting_odds()

        # Save to cache
        if odds_data:
            try:
                with open(cache_file, 'w') as f:
                    json.dump(odds_data, f)
            except Exception as e:
                print(f"Error saving cache: {e}")

        return odds_data

    def fetch_head_to_head(self, team_id1: str, team_id2: str, limit: int = 10) -> dict:
        """
        Fetch head-to-head record between two teams.

        Args:
            team_id1: First team ID
            team_id2: Second team ID
            limit: Number of recent matches to analyze (default 10)

        Returns:
            Dict with H2H record like:
            {"team1_name": "Bayern", "team2_name": "Dortmund",
             "team1_wins": 7, "draws": 2, "team2_wins": 1, "matches": [...]}
        """
        try:
            # Fetch recent events for team1
            url = f"{self.sports_db_base_url}/eventslast.php?id={team_id1}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("results"):
                return {}

            # Filter for matches against team2
            h2h_matches = []
            for match in data["results"]:
                home_id = match.get("idHomeTeam")
                away_id = match.get("idAwayTeam")

                # Check if this match involved both teams
                if (home_id == team_id1 and away_id == team_id2) or \
                   (home_id == team_id2 and away_id == team_id1):
                    h2h_matches.append(match)

            # If we don't have enough matches, try team2's history
            if len(h2h_matches) < limit:
                url2 = f"{self.sports_db_base_url}/eventslast.php?id={team_id2}"
                response2 = requests.get(url2, timeout=10)
                response2.raise_for_status()
                data2 = response2.json()

                if data2.get("results"):
                    for match in data2["results"]:
                        home_id = match.get("idHomeTeam")
                        away_id = match.get("idAwayTeam")

                        # Avoid duplicates
                        match_id = match.get("idEvent")
                        if match_id not in [m.get("idEvent") for m in h2h_matches]:
                            if (home_id == team_id1 and away_id == team_id2) or \
                               (home_id == team_id2 and away_id == team_id1):
                                h2h_matches.append(match)

            # Limit to most recent matches
            h2h_matches = h2h_matches[:limit]

            if not h2h_matches:
                return {}

            # Calculate record
            team1_wins = 0
            team2_wins = 0
            draws = 0
            team1_name = ""
            team2_name = ""

            for match in h2h_matches:
                home_id = match.get("idHomeTeam")
                away_id = match.get("idAwayTeam")
                home_score = match.get("intHomeScore")
                away_score = match.get("intAwayScore")

                # Skip if scores are missing
                if home_score is None or away_score is None:
                    continue

                home_score = int(home_score)
                away_score = int(away_score)

                # Get team names
                if not team1_name:
                    team1_name = match.get("strHomeTeam") if home_id == team_id1 else match.get("strAwayTeam")
                if not team2_name:
                    team2_name = match.get("strAwayTeam") if home_id == team_id1 else match.get("strHomeTeam")

                # Determine result
                if home_score == away_score:
                    draws += 1
                elif (home_id == team_id1 and home_score > away_score) or \
                     (away_id == team_id1 and away_score > home_score):
                    team1_wins += 1
                else:
                    team2_wins += 1

            return {
                "team1_name": team1_name,
                "team2_name": team2_name,
                "team1_wins": team1_wins,
                "draws": draws,
                "team2_wins": team2_wins,
                "total_matches": len([m for m in h2h_matches if m.get("intHomeScore") is not None]),
                "matches": h2h_matches
            }

        except Exception as e:
            print(f"Error fetching H2H for teams {team_id1} vs {team_id2}: {e}")
            return {}

    def fetch_h2h_for_upcoming_fixtures(self) -> dict[str, dict]:
        """
        Fetch H2H records for upcoming Bundesliga fixtures.

        Returns:
            Dict mapping fixture keys to H2H records
        """
        h2h_data = {}

        try:
            # Get upcoming fixtures to know which H2H to fetch
            url = f"{self.sports_db_base_url}/eventsnextleague.php?id=4331"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("events"):
                # Get H2H for next 5 fixtures
                for event in data["events"][:5]:
                    home_team = event.get("strHomeTeam")
                    away_team = event.get("strAwayTeam")
                    home_id = event.get("idHomeTeam")
                    away_id = event.get("idAwayTeam")

                    if home_id and away_id:
                        fixture_key = f"{home_team}_vs_{away_team}"
                        h2h = self.fetch_head_to_head(home_id, away_id)

                        if h2h:
                            h2h_data[fixture_key] = h2h

            print(f"Fetched H2H for {len(h2h_data)} upcoming fixtures")

        except Exception as e:
            print(f"Error fetching H2H for fixtures: {e}")

        return h2h_data

    def fetch_h2h_cached(self) -> dict[str, dict]:
        """Fetch H2H records with caching (24-hour cache)."""
        cache_file = self.cache_dir / "head_to_head.json"

        # Check cache
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < self.odds_cache_duration:
                print(f"Using cached H2H records ({cache_age.seconds // 3600}h old)")
                try:
                    with open(cache_file) as f:
                        return json.load(f)
                except Exception as e:
                    print(f"Error loading cache: {e}")

        # Fetch fresh data
        h2h_data = self.fetch_h2h_for_upcoming_fixtures()

        # Save to cache
        if h2h_data:
            try:
                with open(cache_file, 'w') as f:
                    # Remove 'matches' field to reduce cache size
                    h2h_summary = {}
                    for key, value in h2h_data.items():
                        h2h_summary[key] = {k: v for k, v in value.items() if k != "matches"}
                    json.dump(h2h_summary, f)
            except Exception as e:
                print(f"Error saving cache: {e}")

        return h2h_data

    def fetch_injuries(self, league_id: int = 78, season: str = "2025") -> dict[str, list]:
        """
        Fetch injury/suspension data for Bundesliga from API-Football.

        Args:
            league_id: Bundesliga ID = 78
            season: Season year (2025 = 2024/25 current season)

        Returns:
            Dict mapping team names to lists of injured/suspended players
        """
        if not self.has_api_football:
            print("API-Football not configured for injuries (RAPIDAPI_KEY missing)")
            return {}

        injuries_by_team = {}

        try:
            # API-Football injuries endpoint
            url = f"{self.api_football_base_url}/injuries"

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
                # Group injuries by team
                for injury_data in data["response"]:
                    player = injury_data.get("player", {})
                    team = injury_data.get("team", {})
                    fixture = injury_data.get("fixture", {})

                    player_name = player.get("name", "Unknown")
                    team_name = team.get("name", "Unknown")
                    injury_type = player.get("type", "Unknown")  # Injury or Missing Roster
                    injury_reason = player.get("reason", "Unknown")

                    # Add to team's injury list
                    if team_name not in injuries_by_team:
                        injuries_by_team[team_name] = []

                    injuries_by_team[team_name].append({
                        "player": player_name,
                        "type": injury_type,
                        "reason": injury_reason
                    })

            print(f"Fetched injury data for {len(injuries_by_team)} teams")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print("⚠️  API-Football: Injuries endpoint not available on current plan")
            elif e.response.status_code == 404:
                print("⚠️  API-Football: No injury data for current season/league")
            else:
                print(f"HTTP Error fetching injuries: {e}")
        except Exception as e:
            print(f"Error fetching injuries: {e}")

        return injuries_by_team

    def fetch_injuries_cached(self) -> dict[str, list]:
        """Fetch injuries with caching (6-hour cache)."""
        cache_file = self.cache_dir / "injuries.json"

        # Check cache
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < self.cache_duration:
                print(f"Using cached injury data ({cache_age.seconds // 3600}h old)")
                try:
                    with open(cache_file) as f:
                        return json.load(f)
                except Exception as e:
                    print(f"Error loading cache: {e}")

        # Fetch fresh data
        injuries = self.fetch_injuries()

        # Save to cache
        if injuries:
            try:
                with open(cache_file, 'w') as f:
                    json.dump(injuries, f)
            except Exception as e:
                print(f"Error saving cache: {e}")

        return injuries

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

        # Fetch betting odds (cached, 24 hours)
        betting_odds = self.fetch_betting_odds_cached() if self.has_odds_api else {}

        # Fetch head-to-head records for upcoming fixtures (cached, 24 hours)
        h2h_records = self.fetch_h2h_cached()

        # Fetch injury/suspension data (cached, 6 hours)
        injuries = self.fetch_injuries_cached() if self.has_api_football else {}

        print(f"Fetched {len(all_articles)} articles, {len(all_events)} events, {len(player_stats)} player stats, {len(team_forms)} team forms, {len(betting_odds)} odds, {len(h2h_records)} H2H, {len(injuries)} teams with injuries")

        # Create aggregated data
        data = AggregatedData(
            news_articles=all_articles,
            sports_events=all_events,
            player_stats=player_stats,
        )

        # Prepend standings + form guide + injuries + H2H + odds to context (monkey-patch for this instance)
        form_guide_text = self._format_form_guide(team_forms)
        injuries_text = self._format_injuries(injuries)
        h2h_text = self._format_h2h_records(h2h_records)
        betting_odds_text = self._format_betting_odds(betting_odds)
        original_context = data.to_context_string()

        enhanced_parts = []
        if standings_text:
            enhanced_parts.append(standings_text)
        if form_guide_text:
            enhanced_parts.append(form_guide_text)
        if injuries_text:
            enhanced_parts.append(injuries_text)
        if h2h_text:
            enhanced_parts.append(h2h_text)
        if betting_odds_text:
            enhanced_parts.append(betting_odds_text)
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

    def _format_injuries(self, injuries: dict[str, list]) -> str:
        """Format injury/suspension data for LLM context."""
        if not injuries:
            return ""

        lines = ["=== INJURIES & SUSPENSIONS ==="]
        lines.append("")

        # Sort teams alphabetically
        sorted_teams = sorted(injuries.items())

        for team_name, injury_list in sorted_teams:
            if not injury_list:
                continue

            # Group by type (Injury vs Missing Roster/Suspension)
            injuries_only = [i for i in injury_list if i.get("type") == "Injury"]
            other = [i for i in injury_list if i.get("type") != "Injury"]

            players = []
            for inj in injuries_only:
                player = inj.get("player", "Unknown")
                reason = inj.get("reason", "Unknown")
                players.append(f"{player} ({reason})")

            for inj in other:
                player = inj.get("player", "Unknown")
                reason = inj.get("reason", "Unknown")
                players.append(f"{player} ({reason})")

            if players:
                lines.append(f"{team_name}: {', '.join(players[:5])}")  # Limit to 5 per team

        if len(lines) == 2:  # Only header, no data
            return ""

        return "\n".join(lines)

    def _format_h2h_records(self, h2h_records: dict[str, dict]) -> str:
        """Format head-to-head records for LLM context."""
        if not h2h_records:
            return ""

        lines = ["=== HEAD-TO-HEAD RECORDS (Upcoming Fixtures) ==="]
        lines.append("")

        for fixture_key, h2h_data in h2h_records.items():
            team1 = h2h_data.get("team1_name", "Unknown")
            team2 = h2h_data.get("team2_name", "Unknown")
            team1_wins = h2h_data.get("team1_wins", 0)
            draws = h2h_data.get("draws", 0)
            team2_wins = h2h_data.get("team2_wins", 0)
            total = h2h_data.get("total_matches", 0)

            if total > 0:
                lines.append(
                    f"{team1} vs {team2}: {team1_wins}S-{draws}U-{team2_wins}N "
                    f"(letzte {total} Spiele, {team1} Perspektive)"
                )

        if len(lines) == 2:  # Only header, no data
            return ""

        return "\n".join(lines)

    def _format_betting_odds(self, betting_odds: dict[str, dict]) -> str:
        """Format betting odds for LLM context."""
        if not betting_odds:
            return ""

        lines = ["=== BETTING ODDS (Upcoming Fixtures) ==="]
        lines.append("⚠️  Odds are for entertainment purposes only")
        lines.append("")

        # Group by commence time to show upcoming fixtures in order
        fixtures = []
        for match_id, odds_data in betting_odds.items():
            home = odds_data["home"]
            away = odds_data["away"]
            odds = odds_data["odds"]
            commence_time = odds_data.get("commence_time", "")
            bookmaker = odds_data.get("bookmaker", "Unknown")

            # Parse commence time for sorting
            try:
                commence_dt = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
            except:
                commence_dt = datetime.now()

            # Format odds display
            home_odds = odds.get("home", "N/A")
            draw_odds = odds.get("draw", "N/A")
            away_odds = odds.get("away", "N/A")

            fixtures.append({
                "time": commence_dt,
                "home": home,
                "away": away,
                "home_odds": home_odds,
                "draw_odds": draw_odds,
                "away_odds": away_odds,
                "bookmaker": bookmaker
            })

        # Sort by commence time (earliest first)
        fixtures.sort(key=lambda x: x["time"])

        # Format output
        for fixture in fixtures[:10]:  # Show next 10 fixtures
            time_str = fixture["time"].strftime("%d.%m %H:%M")
            lines.append(
                f"{fixture['home']} vs {fixture['away']} ({time_str})"
            )
            lines.append(
                f"  Quoten: Heim {fixture['home_odds']:.2f} | Unentschieden {fixture['draw_odds']:.2f} | Auswärts {fixture['away_odds']:.2f}"
            )
            lines.append(f"  Quelle: {fixture['bookmaker']}")
            lines.append("")

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
