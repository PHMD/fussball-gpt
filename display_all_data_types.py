"""
Display All Data Types - Shell Client Format

Shows every type of data the KSI agent can display, formatted exactly
as it would appear in the terminal/shell interface.
"""

from datetime import datetime
from data_aggregator import DataAggregator


def print_section_header(title: str):
    """Print a section header."""
    print("\n" + "="*76)
    print(f"  {title}")
    print("="*76 + "\n")


def display_news_articles(data):
    """Display all news article formats."""
    print_section_header("📰 NEWS ARTICLES - Full Format")

    for i, article in enumerate(data.news_articles[:5], 1):
        print(f"Article {i}/{len(data.news_articles)}")
        print("─" * 76)
        print(f"Title:     {article.title}")
        print(f"Source:    {article.source.value}")
        print(f"Published: {article.timestamp.strftime('%Y-%m-%d %H:%M')}")
        if article.url:
            print(f"URL:       {article.url}")
        if article.author:
            print(f"Author:    {article.author}")
        if article.category:
            print(f"Category:  {article.category}")
        print(f"\nContent:")
        print(f"  {article.content}")
        print("\n" + "─" * 76 + "\n")


def display_sports_events(data):
    """Display all sports event formats."""
    print_section_header("⚽ SPORTS EVENTS - Full Format")

    for i, event in enumerate(data.sports_events[:5], 1):
        print(f"Event {i}/{len(data.sports_events)}")
        print("─" * 76)
        print(f"Title:      {event.title}")
        print(f"Type:       {event.event_type}")
        print(f"Date/Time:  {event.timestamp.strftime('%Y-%m-%d %H:%M')}")
        print(f"Source:     {event.source.value}")

        if event.home_team and event.away_team:
            print(f"\nMatch Details:")
            print(f"  Home:     {event.home_team}")
            print(f"  Away:     {event.away_team}")

        if event.score:
            print(f"  Score:    {event.score}")

        if event.league:
            print(f"  League:   {event.league}")

        print(f"\nDescription:")
        print(f"  {event.content}")
        print("\n" + "─" * 76 + "\n")


def display_headlines_compact(data):
    """Display headlines in compact format."""
    print_section_header("📋 NEWS HEADLINES - Compact Format")

    for i, article in enumerate(data.news_articles, 1):
        timestamp = article.timestamp.strftime('%H:%M')
        print(f"{i:2d}. [{timestamp}] {article.title}")
    print()


def display_fixtures_compact(data):
    """Display fixtures in compact format."""
    print_section_header("📅 UPCOMING FIXTURES - Compact Format")

    for i, event in enumerate(data.sports_events, 1):
        date = event.timestamp.strftime('%b %d, %H:%M')
        print(f"{i:2d}. [{date}] {event.title}")
    print()


def display_match_result_format(data):
    """Display match result format."""
    print_section_header("🏆 MATCH RESULT - Detailed Format")

    # Simulate a match result display
    print("CHAMPIONS LEAGUE - Matchday 3")
    print("─" * 76)
    print()
    print("  Bayer Leverkusen  2  -  7  Paris St. Germain")
    print("  Venue: BayArena, Leverkusen")
    print("  Date: October 21, 2025")
    print()
    print("  Match Report:")
    print("  • Critical 7-minute period after equalizer proved decisive")
    print("  • 9 total goals, 2 penalties, red cards issued")
    print("  • Coach Hjulmand: 'We lost the game in seven minutes'")
    print()
    print("  Statistics:")
    print("  • Total Goals:        9")
    print("  • Penalties:          2")
    print("  • Disciplinary:       Red cards")
    print()
    print("─" * 76 + "\n")


def display_player_stats_format(data):
    """Display player statistics format."""
    print_section_header("👤 PLAYER STATISTICS - Detailed Format")

    print("Player: Felix Nmecha")
    print("Team:   Borussia Dortmund")
    print("─" * 76)
    print()
    print("Latest Performance:")
    print("  Match:        FC Copenhagen 2-4 Borussia Dortmund")
    print("  Date:         October 21, 2025")
    print("  Position:     Midfielder")
    print()
    print("  Statistics:")
    print("  • Goals:      2 (Brace/Doppelpack)")
    print("  • Assists:    -")
    print("  • Minutes:    90'")
    print("  • Rating:     ⭐⭐⭐⭐")
    print()
    print("  Context:")
    print("  Nmecha's double helped Dortmund secure an important away victory")
    print("  in Copenhagen, continuing the team's strong attacking form.")
    print()
    print("─" * 76 + "\n")


def display_summary_dashboard(data):
    """Display summary dashboard format."""
    print_section_header("📊 SUMMARY DASHBOARD")

    print("KSI Sports Intelligence - Data Summary")
    print("─" * 76)
    print(f"Last Updated: {data.aggregation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│  DATA SOURCES                                                       │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    print(f"│  📰 News Articles:       {len(data.news_articles):3d}                                         │")
    print(f"│  ⚽ Sports Events:        {len(data.sports_events):3d}                                         │")
    print(f"│  🔄 Refresh Interval:    5 minutes                                 │")
    print(f"│  ✓  Status:              All sources operational                  │")
    print("└─────────────────────────────────────────────────────────────────────┘")
    print()

    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│  TOP STORIES                                                        │")
    print("├─────────────────────────────────────────────────────────────────────┤")

    for i, article in enumerate(data.news_articles[:3], 1):
        title = article.title[:65] + "..." if len(article.title) > 65 else article.title
        print(f"│  {i}. {title:<66} │")

    print("└─────────────────────────────────────────────────────────────────────┘")
    print()

    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│  UPCOMING MATCHES                                                   │")
    print("├─────────────────────────────────────────────────────────────────────┤")

    for i, event in enumerate(data.sports_events[:3], 1):
        date = event.timestamp.strftime('%b %d')
        match = f"{event.title[:50]}"
        print(f"│  {i}. [{date}] {match:<55} │")

    print("└─────────────────────────────────────────────────────────────────────┘")
    print()


def display_raw_data_format(data):
    """Display raw data format (for debugging)."""
    print_section_header("🔧 RAW DATA - JSON-like Format")

    print("Sample Article (NewsArticle object):")
    print("─" * 76)
    if data.news_articles:
        article = data.news_articles[0]
        print("{")
        print(f'  "source": "{article.source.value}",')
        print(f'  "title": "{article.title}",')
        print(f'  "content": "{article.content[:80]}...",')
        print(f'  "url": "{article.url}",')
        print(f'  "timestamp": "{article.timestamp.isoformat()}",')
        print(f'  "author": "{article.author}",')
        print(f'  "category": "{article.category}"')
        print("}")
    print()

    print("Sample Event (SportsEvent object):")
    print("─" * 76)
    if data.sports_events:
        event = data.sports_events[0]
        print("{")
        print(f'  "source": "{event.source.value}",')
        print(f'  "event_type": "{event.event_type}",')
        print(f'  "title": "{event.title}",')
        print(f'  "content": "{event.content}",')
        print(f'  "timestamp": "{event.timestamp.isoformat()}",')
        print(f'  "home_team": "{event.home_team}",')
        print(f'  "away_team": "{event.away_team}",')
        print(f'  "score": "{event.score}",')
        print(f'  "league": "{event.league}"')
        print("}")
    print()


def display_conversation_format(data):
    """Display conversational Q&A format."""
    print_section_header("💬 CONVERSATIONAL FORMAT - Agent Response")

    print("🏆 User: What's the latest on Borussia Dortmund?")
    print()
    print("🤖 KSI:")
    print("─" * 76)
    print()
    print("Great question! Based on the latest data, here's what's happening")
    print("with Borussia Dortmund:")
    print()
    print("**Champions League Victory**")
    print("Dortmund secured a strong 4-2 away win at FC Copenhagen on October 21.")
    print()
    print("**Goal Scorers:**")
    print("• Felix Nmecha - 2 goals (brace)")
    print("• Fabio Silva - 1 goal (his first for BVB!)")
    print()
    print("**Coach's Take:**")
    print('Niko Kovac was pleased with the second-half performance, saying the')
    print('team "shifted up at least one gear" after the halftime break.')
    print()
    print("**What This Means:**")
    print("This continues Dortmund's strong attacking form, with another")
    print("high-scoring performance. The team looks sharp in European competition.")
    print()
    print("Would you like to know more about specific players or upcoming matches?")
    print()
    print("─" * 76 + "\n")


def main():
    """Display all data type formats."""

    print("\n" + "="*76)
    print("  KSI PROTOTYPE - ALL DATA TYPE DISPLAY FORMATS")
    print("  Shell Client Visualization")
    print("="*76)
    print()
    print("Loading real sports data...")

    # Fetch real data
    aggregator = DataAggregator()
    data = aggregator.aggregate_all()

    print(f"✓ Loaded {len(data.news_articles)} articles, {len(data.sports_events)} events")

    # Display all formats
    display_news_articles(data)
    display_sports_events(data)
    display_headlines_compact(data)
    display_fixtures_compact(data)
    display_match_result_format(data)
    display_player_stats_format(data)
    display_summary_dashboard(data)
    display_conversation_format(data)
    display_raw_data_format(data)

    # Final summary
    print_section_header("✅ ALL DATA FORMATS DISPLAYED")
    print("Formats Shown:")
    print("  1. News Articles (Full Format)")
    print("  2. Sports Events (Full Format)")
    print("  3. Headlines (Compact Format)")
    print("  4. Fixtures (Compact Format)")
    print("  5. Match Results (Detailed Format)")
    print("  6. Player Statistics (Detailed Format)")
    print("  7. Summary Dashboard")
    print("  8. Conversational Format (Agent Response)")
    print("  9. Raw Data Format (JSON-like)")
    print()
    print("These are the formats the KSI agent can display in the shell client.")
    print()


if __name__ == "__main__":
    main()
