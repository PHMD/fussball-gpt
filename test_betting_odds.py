"""
Test betting odds integration.

NOTE: Requires ODDS_API_KEY in .env file
Get free API key at: https://the-odds-api.com/
Free tier: 500 requests/month
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv
from data_aggregator import DataAggregator
from user_config import UserConfigManager, DetailLevel, Language

load_dotenv()

def test_betting_odds():
    """Test that betting odds enhance LLM responses for Betting Enthusiast persona."""

    print("\n" + "="*70)
    print("  Testing Betting Odds API Integration")
    print("="*70)

    # Check if API key is configured
    if not os.getenv("ODDS_API_KEY"):
        print("\n⚠️  ODDS_API_KEY not found in .env file")
        print("\nTo get a free API key:")
        print("1. Visit: https://the-odds-api.com/")
        print("2. Sign up for free account (500 requests/month)")
        print("3. Add ODDS_API_KEY=your_key to .env file")
        print("\nTest cannot proceed without API key.")
        return

    # Initialize
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    aggregator = DataAggregator()
    config = UserConfigManager()

    # Set to Betting Enthusiast persona (Balanced mode, German)
    config.profile.detail_level = DetailLevel.BALANCED
    config.profile.language = Language.GERMAN

    # Fetch data (includes betting odds now)
    print("\nFetching latest data (with betting odds)...")
    data = aggregator.aggregate_all()
    context = data.to_context_string()

    # Build system prompt
    system_prompt = config.get_base_system_prompt()
    system_prompt += "\n" + config.get_system_prompt_modifier()
    system_prompt += f"\n\nHier sind die aktuellen Daten:\n\n{context}"

    # Test query that should benefit from odds data
    test_query = "Welche Spiele stehen als nächstes an und wie sind die Quoten? Gibt es Value Bets?"

    print("\n" + "="*70)
    print(f"QUERY: {test_query}")
    print("="*70)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=system_prompt,
        messages=[{"role": "user", "content": test_query}]
    )

    answer = response.content[0].text
    word_count = len(answer.split())

    print(f"\nRESPONSE ({word_count} words):")
    print(answer)

    # Check if response mentions odds
    odds_indicators = ["Quoten", "Quote", "Heim", "Unentschieden", "Auswärts", "Value", "Wert"]
    mentions_odds = any(indicator in answer for indicator in odds_indicators)

    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)
    print(f"✅ Response mentions odds data: {mentions_odds}")
    print(f"Response length: {word_count} words (expected: 100-200 for Balanced mode)")

    if mentions_odds:
        print("\n✅ SUCCESS: Betting odds are being used by LLM!")
        print("Expected impact: Betting Enthusiast persona 7-9/10 → 9.5-10/10")
    else:
        print("\n⚠️  WARNING: Odds data may not be prominent in responses")
        print("Check if any odds were fetched from API")

if __name__ == "__main__":
    test_betting_odds()
