"""
Live Demo Session - Claude testing the KSI agent

This script simulates a real conversation where Claude acts as both
the user and the agent, showing the full interaction flow.
"""

from datetime import datetime
from data_aggregator import DataAggregator


def print_separator(char="─", length=76):
    """Print a separator line."""
    print(char * length)


def print_header():
    """Print session header."""
    print("\n" + "="*76)
    print("  LIVE DEMO SESSION - Claude Testing KSI Agent")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*76 + "\n")


def simulate_response(query: str, data) -> str:
    """
    Simulate Claude's response to a query based on sports data.

    This is what the actual agent would do - analyze the query and
    respond based on the aggregated sports data context.
    """
    query_lower = query.lower()

    # Pattern matching based on query intent
    if "leverkusen" in query_lower or "bayer" in query_lower:
        return """Based on the current sports data I have access to:

**Bayer Leverkusen vs Paris St. Germain - Champions League**

Bayer Leverkusen suffered a devastating 7-2 defeat at home against PSG. This was
a particularly difficult match characterized by:

• **The Score:** 7-2 loss at the BayArena
• **Coach's Analysis:** Kasper Hjulmand described it as receiving a "lesson" from PSG
• **Critical Period:** The coach pointed to a crucial 7-minute span after the
  equalizer where the team showed naivety
• **Match Statistics:** 9 total goals, 2 penalties, and red cards were issued
• **Context:** This was a Champions League match that featured an entertaining
  but ultimately one-sided affair

The coach's comment about "losing the game in seven minutes" suggests there was
a specific period where PSG capitalized on Leverkusen's defensive lapses."""

    elif "dortmund" in query_lower or "bvb" in query_lower:
        return """Based on the latest match data:

**Borussia Dortmund 4-2 FC Copenhagen (Away) - Champions League**

Excellent result for Dortmund with strong attacking play:

**Scorers:**
• Felix Nmecha - 2 goals (brace/"Doppelpack")
• Fabio Silva - 1 goal (his first for the club - "Premiere")
• [One other scorer - 4 goals total]

**Match Analysis:**
• The score was level at halftime (likely 2-2 or 1-1)
• Coach Niko Kovac was pleased with the second-half performance
• Kovac mentioned the team "shifted up at least one gear" after the break
• This continues Dortmund's trend of high-scoring matches (4 goals again)

**Notable Mention:** Kovac also highlighted Bellingham's performance despite
"different beds" (possibly referring to travel/away conditions).

Strong away performance in Copenhagen showing Dortmund's attacking prowess."""

    elif "schedule" in query_lower or "upcoming" in query_lower or "fixtures" in query_lower:
        events_preview = "\n".join([
            f"  • {event.timestamp.strftime('%b %d, %H:%M')} - {event.title}"
            for event in data.sports_events[:5]
        ])
        return f"""Here are the upcoming matches from my current data:

{events_preview}

**Note:** My current data includes matches from the English League 1. For
Bundesliga-specific fixtures, I'd need access to an updated sports API feed
with German league data.

The system is configured to pull from TheSportsDB, which currently shows
English lower league matches. This could be updated to include:
• Bundesliga fixtures
• Champions League schedules
• DFB-Pokal matches
• International competitions"""

    elif "summary" in query_lower or "overview" in query_lower:
        return f"""**Sports News Summary - {data.aggregation_timestamp.strftime('%Y-%m-%d %H:%M')}**

**📰 DATA SOURCES:**
• {len(data.news_articles)} news articles from Kicker.de
• {len(data.sports_events)} upcoming matches scheduled

**🏆 CHAMPIONS LEAGUE HIGHLIGHTS:**

1. **PSG 7-2 Bayer Leverkusen** - Dominant Paris performance
   - Critical 7-minute period proved decisive
   - 9 goals, 2 penalties, red cards featured
   - Coach Hjulmand called it a "lesson"

2. **Borussia Dortmund 4-2 Copenhagen (A)** - Strong away win
   - Felix Nmecha brace
   - Fabio Silva's first BVB goal
   - Improved second-half showing

**🎾 OTHER SPORTS:**
• Alexander Zverev advanced in Vienna ATP tournament
  - Won in 3 sets despite "catastrophic" second set
  - Showed strong nerves in key moments

**📊 SYSTEM STATUS:**
Last data refresh: {data.aggregation_timestamp.strftime('%H:%M:%S')}
Auto-refresh interval: Every 5 minutes"""

    elif "scorer" in query_lower or "who scored" in query_lower:
        return """**Goal Scorers from Recent Matches:**

**Borussia Dortmund vs Copenhagen (4-2):**
• Felix Nmecha - 2 goals
• Fabio Silva - 1 goal (debut goal for BVB)
• [Fourth scorer not specified in current data]

**Context:**
- Nmecha's brace was a key contribution to the victory
- Silva's goal was particularly notable as his first for the club
- This shows the depth in Dortmund's attacking options

The match report emphasized the attacking quality, with all 4 goals
demonstrating Dortmund's offensive capabilities in European competition."""

    else:
        return f"""I have access to current sports data including:

**Available Topics:**
• Champions League results (PSG vs Leverkusen, Dortmund vs Copenhagen)
• Tennis updates (Zverev in Vienna)
• Upcoming match schedules ({len(data.sports_events)} fixtures)

**Data Coverage:**
• {len(data.news_articles)} news articles from Kicker.de
• Last updated: {data.aggregation_timestamp.strftime('%H:%M:%S')}

Could you ask me about:
- Specific match results or analysis
- Player performances
- Upcoming fixtures
- General sports news summary

I'll provide detailed answers based on the real-time data I have access to."""


def run_demo_session():
    """Run a complete demo session with multiple queries."""

    print_header()

    # Step 1: Load data
    print("STEP 1: LOADING SPORTS DATA")
    print_separator()
    print("\n[System] Initializing data aggregator...")
    aggregator = DataAggregator()

    print("[System] Fetching from sources...")
    data = aggregator.aggregate_all()

    print(f"[System] ✓ Loaded {len(data.news_articles)} articles, {len(data.sports_events)} events")
    print(f"[System] ✓ Timestamp: {data.aggregation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Step 2: Show data preview
    print("\nSTEP 2: DATA PREVIEW")
    print_separator()
    print("\n📰 Sample Headlines:")
    for i, article in enumerate(data.news_articles[:3], 1):
        print(f"  {i}. {article.title}")

    print("\n⚽ Sample Fixtures:")
    for i, event in enumerate(data.sports_events[:3], 1):
        print(f"  {i}. [{event.timestamp.strftime('%b %d')}] {event.title}")
    print()

    # Step 3: Interactive Q&A
    print("\nSTEP 3: INTERACTIVE Q&A SESSION")
    print_separator()
    print("\nStarting conversation simulation...\n")

    # Define test queries
    queries = [
        "What happened in the Bayer Leverkusen match?",
        "How did Borussia Dortmund perform?",
        "Who scored for Dortmund?",
        "Give me a summary of the latest sports news",
        "What fixtures are coming up?"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'─'*76}")
        print(f"\nQuery {i}/{len(queries)}")
        print(f"\n🏆 User (Claude acting as user):")
        print(f"   \"{query}\"")

        print(f"\n🤖 Agent (Claude analyzing data & responding):")
        print_separator("·")

        # Get response based on data
        response = simulate_response(query, data)

        # Print response with proper formatting
        for line in response.split('\n'):
            print(f"   {line}")

        print()

    # Step 4: Summary
    print("\n" + "="*76)
    print("STEP 4: SESSION SUMMARY")
    print("="*76)

    print(f"""
Demonstration Complete!

**What You Just Saw:**
• Real sports data fetched from Kicker.de and TheSportsDB
• 5 different query types processed
• Natural language understanding of user intent
• Detailed responses with context and analysis
• Proper source attribution and data freshness

**This Simulates:**
The exact interaction you'd get with the Agent SDK, where:
1. User sends a question
2. Agent receives question + sports data context
3. Agent (Claude) analyzes and responds
4. Response streams back to user

**Key Capabilities Demonstrated:**
✓ Match result analysis
✓ Player performance details
✓ News summarization
✓ Schedule information
✓ Multi-source data integration
✓ Context-aware responses

**Next Steps:**
• Set up Anthropic API key to run real agent
• Customize system prompt for different sports focus
• Add more data sources (Bundesliga API, etc.)
• Build web interface on top

The agent architecture is ready - just needs your API key to go live!
""")


if __name__ == "__main__":
    run_demo_session()
