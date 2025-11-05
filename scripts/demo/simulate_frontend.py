"""
ASCII Front-End Simulation for KSI Prototype.

Simulates the CLI interface with visual elements and pre-programmed responses
to demonstrate the RAG pattern without requiring LLM API access.
"""

import time
import sys
from datetime import datetime
from data_aggregator import DataAggregator


def print_slow(text, delay=0.02):
    """Print text with typing effect."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def print_header():
    """Print ASCII art header."""
    header = """
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
"""
    print(header)


def print_loading_bar(message, duration=2):
    """Show a loading bar animation."""
    bar_length = 50
    print(f"\n{message}")
    for i in range(bar_length + 1):
        percent = int((i / bar_length) * 100)
        filled = '█' * i
        empty = '░' * (bar_length - i)
        print(f'\r[{filled}{empty}] {percent}%', end='', flush=True)
        time.sleep(duration / bar_length)
    print("\n")


def print_data_summary(data):
    """Print summary of fetched data."""
    box = f"""
┌────────────────────────────────────────────────────────────────┐
│  DATA AGGREGATION COMPLETE                                     │
├────────────────────────────────────────────────────────────────┤
│  📰 News Articles: {len(data.news_articles):3d}                                        │
│  ⚽ Sports Events:  {len(data.sports_events):3d}                                        │
│  🕐 Last Updated:   {data.aggregation_timestamp.strftime('%H:%M:%S')}                              │
└────────────────────────────────────────────────────────────────┘
"""
    print(box)


def simulate_llm_response(query, data):
    """
    Simulate LLM responses based on query patterns.
    In real system, this would call OpenAI/Anthropic API.
    """
    query_lower = query.lower()

    # Pattern matching for different query types
    if "leverkusen" in query_lower or "bayer" in query_lower:
        return """Based on the latest news data:

Bayer Leverkusen suffered a heavy 7-2 defeat against Paris St. Germain in the
Champions League. Coach Kasper Hjulmand described it as a "lesson" from PSG,
and pointed to a crucial 7-minute period after the equalizer where the team
showed naivety.

The match featured 9 goals total, 2 penalties, and red cards - making it a
memorable but difficult evening for the home fans at BayArena."""

    elif "dortmund" in query_lower or "bvb" in query_lower:
        return """According to the aggregated data:

Borussia Dortmund won 4-2 away at FC Copenhagen. The highlights include:

• Felix Nmecha scored twice (double pack)
• Fabio Silva scored his first goal for the club (premiere)
• Coach Niko Kovac praised the team's second-half performance, saying they
  "shifted up at least one gear" after the halftime break
• This marks another strong attacking performance with 4 goals scored"""

    elif "upcoming" in query_lower or "next" in query_lower or "schedule" in query_lower:
        events_text = "\n".join([
            f"  • {event.title} ({event.timestamp.strftime('%b %d, %H:%M')})"
            for event in data.sports_events[:5]
        ])
        return f"""Here are the upcoming matches from the data:

{events_text}

Note: The current data shows English League 1 matches. For Bundesliga-specific
schedules, the league ID in the sports API may need adjustment."""

    elif "summary" in query_lower or "latest" in query_lower or "news" in query_lower:
        return f"""Here's a summary of the latest sports news:

🏆 CHAMPIONS LEAGUE:
• PSG demolishes Bayer Leverkusen 7-2 in a high-scoring thriller
• Borussia Dortmund wins 4-2 at Copenhagen with Nmecha's brace

🎾 TENNIS:
• Alexander Zverev advances in Vienna despite a "catastrophic" second set

📊 Data includes {len(data.news_articles)} articles and {len(data.sports_events)} upcoming events
Last updated: {data.aggregation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"""

    elif "nmecha" in query_lower or "who scored" in query_lower:
        return """From the match reports:

Felix Nmecha scored twice (a "Doppelpack") for Borussia Dortmund in their
4-2 victory over FC Copenhagen. Additionally, new signing Fabio Silva scored
his first goal for BVB, marking a successful debut contribution."""

    else:
        return f"""I've analyzed the available sports data, which includes:

• {len(data.news_articles)} news articles from Kicker
• {len(data.sports_events)} upcoming matches

Key topics in the data:
- Champions League results (PSG vs Leverkusen, Dortmund vs Copenhagen)
- Tennis updates (Alexander Zverev in Vienna)
- Upcoming English League 1 matches

Could you ask a more specific question about these topics?"""


def run_simulation():
    """Run the complete simulation."""
    print_header()
    print("\n🚀 Initializing system...\n")

    # Simulate loading
    time.sleep(0.5)
    print("✓ Loading data aggregator")
    time.sleep(0.3)
    print("✓ Connecting to news feeds")
    time.sleep(0.3)
    print("✓ Loading AI model")
    time.sleep(0.3)

    # Fetch real data
    print_loading_bar("📡 Aggregating sports data from sources...", duration=2)

    aggregator = DataAggregator()
    data = aggregator.aggregate_all()

    print_data_summary(data)

    # Commands help
    print("""
┌────────────────────────────────────────────────────────────────┐
│  COMMANDS                                                      │
├────────────────────────────────────────────────────────────────┤
│  Ask any sports question in natural language                  │
│  /demo   - Run automated demo with sample queries             │
│  /exit   - Exit the simulation                                │
└────────────────────────────────────────────────────────────────┘
""")

    # Demo queries
    demo_queries = [
        "What happened in the Bayer Leverkusen match?",
        "How did Borussia Dortmund do?",
        "Who scored for Dortmund?",
        "Give me a summary of the latest sports news",
        "What matches are coming up?"
    ]

    while True:
        print("\n" + "─" * 70)
        user_input = input("\n🏆 You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['/exit', '/quit']:
            print("\n")
            print_slow("Thank you for using KSI! Goodbye! 👋", delay=0.03)
            print()
            break

        if user_input.lower() == '/demo':
            print("\n📺 Running automated demo with sample queries...\n")
            time.sleep(1)

            for i, query in enumerate(demo_queries, 1):
                print("\n" + "─" * 70)
                print(f"\n🏆 Demo Query {i}/{len(demo_queries)}: {query}")
                time.sleep(0.5)

                # Simulate processing
                print("\n🤖 KSI: ", end="", flush=True)
                for _ in range(3):
                    print(".", end="", flush=True)
                    time.sleep(0.3)
                print("\n")

                # Get response
                response = simulate_llm_response(query, data)
                print_slow(response, delay=0.01)

                time.sleep(1.5)

            print("\n" + "─" * 70)
            print("\n✓ Demo complete! Now try your own queries.\n")
            continue

        # Process user query
        print("\n🤖 KSI: ", end="", flush=True)
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(0.2)
        print("\n")

        response = simulate_llm_response(user_input, data)
        print_slow(response, delay=0.01)


if __name__ == "__main__":
    try:
        run_simulation()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
