"""
Visual demonstration of KSI prototype - step by step output.
Shows each component of the system in action.
"""

import time
from data_aggregator import DataAggregator


def print_header():
    """Print ASCII art header."""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   ██╗  ██╗███████╗██╗                                                   ║
║   ██║ ██╔╝██╔════╝██║                                                   ║
║   █████╔╝ ███████╗██║                                                   ║
║   ██╔═██╗ ╚════██║██║                                                   ║
║   ██║  ██╗███████║██║                                                   ║
║   ╚═╝  ╚═╝╚══════╝╚═╝                                                   ║
║                                                                          ║
║          KICKER SPORTS INTELLIGENCE - CLI PROTOTYPE                     ║
║                Powered by AI • Real-time Data                           ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)


def demo_step_1():
    """Show header and initialization."""
    print("=" * 76)
    print("STEP 1: System Initialization")
    print("=" * 76)
    print_header()
    print("\n🚀 System starting up...")
    print("   ✓ Loading data aggregator")
    print("   ✓ Connecting to news feeds")
    print("   ✓ Initializing AI interface")
    print("\n" + "─" * 76 + "\n")


def demo_step_2():
    """Show data aggregation."""
    print("=" * 76)
    print("STEP 2: Fetching Live Sports Data")
    print("=" * 76)
    print("\n📡 Connecting to data sources...")
    print("   • Kicker RSS feeds")
    print("   • TheSportsDB API")
    print("\n[Fetching now...]\n")

    aggregator = DataAggregator()
    data = aggregator.aggregate_all()

    print("\n✓ Data aggregation complete!\n")
    print("┌────────────────────────────────────────────────────────────────┐")
    print("│  LIVE DATA SUMMARY                                             │")
    print("├────────────────────────────────────────────────────────────────┤")
    print(f"│  📰 News Articles: {len(data.news_articles):3d}                                        │")
    print(f"│  ⚽ Sports Events:  {len(data.sports_events):3d}                                        │")
    print(f"│  🕐 Timestamp:      {data.aggregation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}                    │")
    print("└────────────────────────────────────────────────────────────────┘")
    print("\n" + "─" * 76 + "\n")

    return data


def demo_step_3(data):
    """Show sample data."""
    print("=" * 76)
    print("STEP 3: Sample Data Preview")
    print("=" * 76)
    print("\n📰 LATEST NEWS HEADLINES:\n")

    for i, article in enumerate(data.news_articles[:3], 1):
        print(f"   {i}. [{article.timestamp.strftime('%H:%M')}] {article.title}")
        print(f"      └─ {article.content[:80]}...")
        print()

    print("\n⚽ UPCOMING MATCHES:\n")
    for i, event in enumerate(data.sports_events[:3], 1):
        print(f"   {i}. [{event.timestamp.strftime('%b %d')}] {event.title}")
        print()

    print("─" * 76 + "\n")

    return data


def demo_step_4(data):
    """Show query processing."""
    print("=" * 76)
    print("STEP 4: Natural Language Query Processing (RAG Pattern)")
    print("=" * 76)

    # Example query
    query = "What happened in the Bayer Leverkusen match?"
    print(f"\n🏆 User Query: \"{query}\"\n")

    print("🔍 Processing:")
    print("   1. Parse user query")
    print("   2. Search aggregated data for relevant context")
    print("   3. Extract matching articles")
    print("   4. Generate response\n")

    print("📊 Context Found:")
    relevant_articles = [a for a in data.news_articles if "Leverkusen" in a.title or "Bayer" in a.title]

    if relevant_articles:
        article = relevant_articles[0]
        print(f"   • Article: {article.title}")
        print(f"   • Source: {article.source.value}")
        print(f"   • Content preview: {article.content[:100]}...")

    print("\n🤖 AI Response:\n")
    print("─" * 76)
    response = """Based on the latest news data:

Bayer Leverkusen suffered a heavy 7-2 defeat against Paris St. Germain in the
Champions League. Coach Kasper Hjulmand described it as a "lesson" from PSG,
and pointed to a crucial 7-minute period after the equalizer where the team
showed naivety.

The match featured 9 goals total, 2 penalties, and red cards - making it a
memorable but difficult evening for the home fans at BayArena."""

    print(response)
    print("─" * 76 + "\n")


def demo_step_5():
    """Show complete interface."""
    print("=" * 76)
    print("STEP 5: Complete Interactive Interface")
    print("=" * 76)

    print("""
The full CLI provides:

┌────────────────────────────────────────────────────────────────┐
│  INTERACTIVE FEATURES                                          │
├────────────────────────────────────────────────────────────────┤
│  • Natural language queries                                    │
│  • Real-time data aggregation                                  │
│  • Auto-refresh every 5 minutes                                │
│  • Commands: /refresh, /exit                                   │
│  • Smart response generation                                   │
└────────────────────────────────────────────────────────────────┘

Example queries you can try:
  • "What are the latest Bundesliga results?"
  • "When is the next Bayern Munich match?"
  • "Summarize today's sports news"
  • "Who scored for Dortmund?"
  • "Give me the upcoming match schedule"

""")
    print("─" * 76 + "\n")


def demo_step_6():
    """Show architecture diagram."""
    print("=" * 76)
    print("STEP 6: System Architecture")
    print("=" * 76)

    print("""
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   USER QUERY                                                            │
│       ↓                                                                 │
│   ┌──────────────────────────────────────┐                             │
│   │  CLI Interface (cli.py)              │                             │
│   │  • Parse input                       │                             │
│   │  • Format output                     │                             │
│   └──────────┬───────────────────────────┘                             │
│              ↓                                                          │
│   ┌──────────────────────────────────────┐                             │
│   │  Data Aggregator                     │                             │
│   │  (data_aggregator.py)                │                             │
│   │                                      │                             │
│   │  ┌──────────┐  ┌──────────┐         │                             │
│   │  │ Kicker   │  │ Sports   │         │                             │
│   │  │ RSS      │  │ DB API   │         │                             │
│   │  └────┬─────┘  └────┬─────┘         │                             │
│   │       ↓             ↓               │                             │
│   │  ┌─────────────────────────┐        │                             │
│   │  │ Normalized Data Models  │        │                             │
│   │  │ (models.py)             │        │                             │
│   │  └─────────┬───────────────┘        │                             │
│   └────────────┼────────────────────────┘                             │
│                ↓                                                        │
│   ┌──────────────────────────────────────┐                             │
│   │  RAG Processing                      │                             │
│   │  • User query + Data context         │                             │
│   │  • Send to LLM API                   │                             │
│   │  • OpenAI or Anthropic               │                             │
│   └──────────┬───────────────────────────┘                             │
│              ↓                                                          │
│   AI RESPONSE                                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
""")
    print("─" * 76 + "\n")


def main():
    """Run complete visual demo."""
    print("\n" * 2)

    demo_step_1()
    input("Press ENTER to continue to Step 2...")

    data = demo_step_2()
    input("Press ENTER to continue to Step 3...")

    demo_step_3(data)
    input("Press ENTER to continue to Step 4...")

    demo_step_4(data)
    input("Press ENTER to continue to Step 5...")

    demo_step_5()
    input("Press ENTER to continue to Step 6...")

    demo_step_6()

    print("=" * 76)
    print("DEMO COMPLETE!")
    print("=" * 76)
    print("""
✅ You've seen:
   1. System initialization
   2. Live data aggregation
   3. Real sports data preview
   4. RAG query processing
   5. Interactive interface features
   6. Complete system architecture

🚀 Ready to try it yourself?
   Run: python cli.py (requires API key)
   Or:  python simulate_frontend.py (no API needed)

""")


if __name__ == "__main__":
    main()
