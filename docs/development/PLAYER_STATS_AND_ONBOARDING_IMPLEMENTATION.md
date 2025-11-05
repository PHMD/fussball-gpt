# Player Stats & User Onboarding Implementation Guide

**Status:** Ready to implement
**Date:** October 23, 2025

---

## Part 1: Adding Player Stats (Fantasy Player Fix)

### Research Summary

**Good News:** API-Football (which you already have integrated) includes comprehensive player stats in the **free tier** (100 req/day):

✅ **Available Stats:**
- Goals, assists, minutes played, appearances
- Yellow cards, red cards
- Shots on target, shots total
- Passes, dribbles
- Penalty stats, substitutions
- Goalkeeper: saves, conceded goals, clean sheets

❌ **NOT in Free Tier:**
- xG (expected goals) - requires paid tier ($49+/month)
- Real-time in-match updates - post-match only
- Detailed heatmaps/pass networks

**Cost:** $0/month (free tier) → $10/month (Basic, 3,000 req/day)

---

### Implementation Steps

#### Step 1: Add PlayerStats Model

**File:** `models.py`

```python
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
    season: str = "2024-2025"
    league: str = "Bundesliga"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**Update AggregatedData:**

```python
class AggregatedData(BaseModel):
    """Container for all aggregated data to pass to LLM."""
    news_articles: list[NewsArticle] = Field(default_factory=list)
    sports_events: list[SportsEvent] = Field(default_factory=list)
    player_stats: list[PlayerStats] = Field(default_factory=list)  # NEW
    aggregation_timestamp: datetime = Field(default_factory=datetime.now)

    def to_context_string(self) -> str:
        """Convert aggregated data to LLM context string."""
        lines = [f"Data aggregated at: {self.aggregation_timestamp.isoformat()}\n"]

        # ... existing code for news and events ...

        # NEW: Add player stats section
        if self.player_stats:
            lines.append("=== TOP PLAYER STATISTICS (Bundesliga 2024/25) ===")

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
```

---

#### Step 2: Add Player Stats Fetching to DataAggregator

**File:** `data_aggregator.py`

```python
def fetch_player_stats(self, league_id: int = 78, season: str = "2024") -> list[PlayerStats]:
    """
    Fetch top player statistics from API-Football.

    Args:
        league_id: Bundesliga ID = 78
        season: Season year (2024 for 2024/25 season)

    Returns:
        List of PlayerStats objects for top performers
    """
    if not self.has_api_football:
        print("API-Football not configured (RAPIDAPI_KEY missing)")
        return []

    players = []

    try:
        # API-Football endpoint for player statistics
        url = "https://api-football-v1.p.rapidapi.com/v3/players/topscorers"

        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
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

    except Exception as e:
        print(f"Error fetching player stats: {e}")

    return players


def aggregate_all(self) -> AggregatedData:
    """
    Fetch and aggregate data from all sources.

    Returns:
        AggregatedData object with news, events, standings, AND player stats
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

    # NEW: Fetch player stats
    player_stats = self.fetch_player_stats() if self.has_api_football else []

    print(f"Fetched {len(all_articles)} articles, {len(all_events)} events, {len(player_stats)} player stats")

    # Create aggregated data
    data = AggregatedData(
        news_articles=all_articles,
        sports_events=all_events,
        player_stats=player_stats,  # NEW
    )

    # Prepend standings to context (existing monkey-patch)
    original_context = data.to_context_string()
    data._enhanced_context = f"{standings_text}\n\n{original_context}" if standings_text else original_context

    return data
```

---

#### Step 3: Test Player Stats

```bash
# Test the player stats fetching
source venv/bin/activate
python -c "
from data_aggregator import DataAggregator

agg = DataAggregator()
data = agg.aggregate_all()

print(f'Player stats count: {len(data.player_stats)}')
if data.player_stats:
    print('\nTop 5 scorers:')
    for p in sorted(data.player_stats, key=lambda x: x.goals, reverse=True)[:5]:
        print(f'  {p.player_name} ({p.team}): {p.goals} goals, {p.assists} assists')
"
```

---

### Rate Limit Management

**Free Tier: 100 requests/day**

**Strategy to stay within limits:**

1. **Cache player stats** (update once per day)
2. **Smart fetching:**
   - Standings: 1 request
   - Recent results: 1 request
   - Player stats (top scorers): 1 request
   - **Total: 3 requests per full data refresh**

3. **Implementation:**

```python
import json
from datetime import datetime, timedelta
from pathlib import Path

class DataAggregator:
    def __init__(self):
        # ... existing init ...
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_duration = timedelta(hours=6)  # Cache for 6 hours

    def fetch_player_stats_cached(self) -> list[PlayerStats]:
        """Fetch player stats with caching to avoid rate limits."""
        cache_file = self.cache_dir / "player_stats.json"

        # Check cache
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < self.cache_duration:
                print(f"Using cached player stats ({cache_age.seconds // 3600}h old)")
                with open(cache_file) as f:
                    cached_data = json.load(f)
                    return [PlayerStats(**p) for p in cached_data]

        # Fetch fresh data
        player_stats = self.fetch_player_stats()

        # Save to cache
        if player_stats:
            with open(cache_file, 'w') as f:
                json.dump([p.dict() for p in player_stats], f)

        return player_stats
```

---

## Part 2: User Onboarding & Detail Levels

### Problem Statement

Different user personas need different response lengths:
- **Casual Fan:** Short, highlight-focused answers
- **Expert Analyst:** Detailed, tactical analysis
- **Betting/Fantasy:** Data-heavy, stats-focused

### Solution: 3-Tier Detail System

**Detail Levels:**
1. **Quick** (Casual fans) - 1-2 sentences, highlights only
2. **Balanced** (Default) - Current behavior, 2-3 paragraphs
3. **Detailed** (Experts) - Comprehensive, tactical depth

---

### Implementation: User Profile System

#### Step 1: Create User Config

**File:** `user_config.py`

```python
"""User configuration and preference management."""
import json
from pathlib import Path
from enum import Enum
from pydantic import BaseModel


class DetailLevel(str, Enum):
    """Response detail level preferences."""
    QUICK = "quick"
    BALANCED = "balanced"
    DETAILED = "detailed"


class UserProfile(BaseModel):
    """User preferences and profile."""
    detail_level: DetailLevel = DetailLevel.BALANCED
    name: str = "User"
    persona: str = "balanced"  # casual, analyst, betting, fantasy
    language: str = "de"  # German

    # Personalization
    favorite_team: str = ""
    interests: list[str] = []  # ["tactics", "transfers", "stats", etc.]

    class Config:
        use_enum_values = True


class UserConfigManager:
    """Manages user configuration persistence."""

    def __init__(self, config_path: str = ".ksi_config.json"):
        self.config_path = Path(config_path)
        self.profile = self.load_profile()

    def load_profile(self) -> UserProfile:
        """Load user profile from config file."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = json.load(f)
                return UserProfile(**data)
        return UserProfile()

    def save_profile(self):
        """Save user profile to config file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.profile.dict(), f, indent=2)

    def update_detail_level(self, level: DetailLevel):
        """Update and save detail level preference."""
        self.profile.detail_level = level
        self.save_profile()

    def get_system_prompt_modifier(self) -> str:
        """Get system prompt modifier based on detail level."""
        modifiers = {
            DetailLevel.QUICK: """
WICHTIG: Dieser Nutzer bevorzugt KURZE Antworten.
- Maximal 2-3 Sätze
- Nur die wichtigsten Highlights
- Keine taktischen Details
- Einfache Sprache
- Direkte Antworten ohne Kontext
Beispiel: "Bayern führt die Tabelle mit 82 Punkten an, 13 Punkte vor Leverkusen."
""",
            DetailLevel.BALANCED: """
WICHTIG: Dieser Nutzer bevorzugt AUSGEWOGENE Antworten.
- 2-3 Absätze
- Wichtige Fakten + etwas Kontext
- Gelegentliche taktische Einblicke
- Professioneller Ton
- Journalistischer Stil (aktuelles Verhalten)
""",
            DetailLevel.DETAILED: """
WICHTIG: Dieser Nutzer bevorzugt DETAILLIERTE Antworten.
- Umfassende Analysen
- Taktische Tiefe (Formationen, Systeme, Strategien)
- Statistische Belege
- Fachterminologie erwünscht
- Vergleiche und historischer Kontext
- 3-5 Absätze oder mehr bei Bedarf
"""
        }
        return modifiers.get(self.profile.detail_level, modifiers[DetailLevel.BALANCED])
```

---

#### Step 2: Interactive Onboarding Flow

**File:** `onboarding.py`

```python
"""Interactive user onboarding."""
from user_config import UserConfigManager, DetailLevel


def run_onboarding():
    """Interactive onboarding to set up user preferences."""

    print("\n" + "="*70)
    print("  🏆 Willkommen bei KSI - Kicker Sports Intelligence")
    print("="*70)
    print("\nLass uns ein paar Fragen klären, um KSI für dich zu optimieren.\n")

    config = UserConfigManager()

    # Question 1: Name (optional)
    name = input("Wie sollen wir dich nennen? (Enter für 'User'): ").strip()
    if name:
        config.profile.name = name

    # Question 2: Detail Level (CRITICAL)
    print(f"\n{config.profile.name}, wie detailliert sollen meine Antworten sein?\n")
    print("1. 🚀 SCHNELL - Kurze Highlights (1-2 Sätze)")
    print("   Beispiel: 'Bayern führt mit 82 Punkten, 13 vor Leverkusen.'")
    print()
    print("2. ⚖️  AUSGEWOGEN - Standard-Journalismus (2-3 Absätze) [EMPFOHLEN]")
    print("   Beispiel: Bayern-Analyse + Kontext + ein bisschen Taktik")
    print()
    print("3. 📊 DETAILLIERT - Tiefe Analysen (3-5+ Absätze)")
    print("   Beispiel: Formationen, Systeme, Statistiken, Vergleiche")
    print()

    while True:
        choice = input("Deine Wahl (1-3): ").strip()
        if choice == "1":
            config.profile.detail_level = DetailLevel.QUICK
            print("✅ Eingestellt: Schnelle, prägnante Antworten")
            break
        elif choice == "2":
            config.profile.detail_level = DetailLevel.BALANCED
            print("✅ Eingestellt: Ausgewogene Antworten (Standard)")
            break
        elif choice == "3":
            config.profile.detail_level = DetailLevel.DETAILED
            print("✅ Eingestellt: Detaillierte, analytische Antworten")
            break
        else:
            print("Bitte 1, 2 oder 3 wählen.")

    # Question 3: Favorite Team (optional)
    print("\nHast du ein Lieblingsteam? (Enter zum Überspringen)")
    team = input("Team: ").strip()
    if team:
        config.profile.favorite_team = team
        print(f"✅ Lieblingsteam: {team}")

    # Question 4: Interests (optional)
    print("\nWas interessiert dich besonders? (Enter zum Überspringen)")
    print("Optionen: taktik, transfers, statistiken, news, international")
    interests_input = input("Interessen (komma-getrennt): ").strip()
    if interests_input:
        interests = [i.strip() for i in interests_input.split(",")]
        config.profile.interests = interests
        print(f"✅ Interessen: {', '.join(interests)}")

    # Save profile
    config.save_profile()

    print("\n" + "="*70)
    print("✅ Einrichtung abgeschlossen!")
    print(f"Deine Einstellungen wurden in '.ksi_config.json' gespeichert.")
    print()
    print("Du kannst diese jederzeit ändern mit: python onboarding.py")
    print("="*70 + "\n")

    return config.profile


if __name__ == "__main__":
    run_onboarding()
```

---

#### Step 3: Integrate with CLI

**File:** `cli.py` (modify existing)

```python
from user_config import UserConfigManager

# At the start of main()
def main():
    # Check if user has completed onboarding
    config = UserConfigManager()

    if not config.config_path.exists():
        print("Sieht aus, als wärst du neu hier!")
        print("Starte Onboarding mit: python onboarding.py")
        print("Oder fahre fort mit Standard-Einstellungen...\n")

    print(f"Hallo {config.profile.name}! Detail-Level: {config.profile.detail_level.value}")

    # ... rest of existing code ...

    # When building LLM prompt:
    system_prompt = f"""Du bist KSI (Kicker Sports Intelligence)...

    {config.get_system_prompt_modifier()}

    ... rest of prompt ..."""
```

---

#### Step 4: Quick Settings Command

**Add to CLI:**

```python
# In the main CLI loop
if user_input.startswith("/settings"):
    print("\nAktuelle Einstellungen:")
    print(f"  Detail-Level: {config.profile.detail_level.value}")
    print(f"  Name: {config.profile.name}")
    if config.profile.favorite_team:
        print(f"  Lieblingsteam: {config.profile.favorite_team}")

    print("\nÄndern:")
    print("  /detail quick      - Kurze Antworten")
    print("  /detail balanced   - Ausgewogene Antworten")
    print("  /detail detailed   - Detaillierte Antworten")
    print("  /onboarding        - Komplett neu einrichten")
    continue

if user_input.startswith("/detail"):
    parts = user_input.split()
    if len(parts) == 2 and parts[1] in ["quick", "balanced", "detailed"]:
        config.update_detail_level(DetailLevel(parts[1]))
        print(f"✅ Detail-Level geändert zu: {parts[1]}")
    else:
        print("Verwendung: /detail [quick|balanced|detailed]")
    continue

if user_input == "/onboarding":
    from onboarding import run_onboarding
    run_onboarding()
    config = UserConfigManager()  # Reload config
    continue
```

---

### Testing the Detail Levels

**Test Script:** `test_detail_levels.py`

```python
"""Test different detail levels with same question."""
from user_config import UserConfigManager, DetailLevel
from data_aggregator import DataAggregator
# ... (rest of your LLM setup)

question = "Wer führt die Bundesliga-Tabelle an?"

for level in [DetailLevel.QUICK, DetailLevel.BALANCED, DetailLevel.DETAILED]:
    print(f"\n{'='*70}")
    print(f"Testing: {level.value.upper()}")
    print(f"{'='*70}\n")

    config = UserConfigManager()
    config.profile.detail_level = level

    system_prompt = f"""... {config.get_system_prompt_modifier()} ..."""

    # Query LLM
    response = query_ksi(question, system_prompt)

    print(f"Response ({len(response)} chars):")
    print(response)
    print()
```

---

## Summary

### Part 1: Player Stats ✅
- **Cost:** $0 (uses existing API-Football)
- **Effort:** ~2 hours implementation
- **Impact:** Fixes Fantasy Player persona (2/10 → 8+/10)
- **Rate limits:** 100 req/day free (3 requests per refresh = 30+ refreshes/day)

### Part 2: Detail Levels ✅
- **Cost:** $0 (configuration only)
- **Effort:** ~3 hours implementation
- **Impact:** Fixes Casual Fan persona (5/10 → 8+/10)
- **UX:** Onboarding flow + runtime settings commands

### Combined Impact

**Before:**
- Casual Fan: 5/10
- Expert Analyst: 8-9/10
- Betting Enthusiast: 6-9/10
- Fantasy Player: 2-8/10

**After (Projected):**
- Casual Fan: 8/10 (with Quick mode)
- Expert Analyst: 9/10 (with Detailed mode)
- Betting Enthusiast: 8-9/10 (same, but benefits from player stats)
- Fantasy Player: 8-9/10 (with player stats!)

---

## Next Steps

1. **Add PlayerStats model** to `models.py`
2. **Add player stats fetching** to `data_aggregator.py`
3. **Test player stats** with API-Football
4. **Create user_config.py** for profile management
5. **Create onboarding.py** for interactive setup
6. **Integrate with CLI** for runtime settings
7. **Run multi-persona test again** to validate improvements

**Estimated total time:** 5-6 hours
**Beta impact:** Major improvement for Fantasy and Casual personas
