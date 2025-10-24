"""
Test user config integration with LLM.

This demonstrates how user preferences (language + detail level)
modify the system prompt and affect response quality.
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv
from data_aggregator import DataAggregator
from user_config import UserConfigManager, DetailLevel, Language

load_dotenv()

def test_user_config():
    """Test that user config correctly modifies LLM responses."""

    print("\n" + "="*70)
    print("  Testing User Config Integration")
    print("="*70)

    # Initialize
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    aggregator = DataAggregator()
    config = UserConfigManager()

    # Fetch data
    print("\nFetching latest data...")
    data = aggregator.aggregate_all()
    context = data.to_context_string()

    # Test query
    test_query_de = "Wer führt die Bundesliga-Tabelle an?"
    test_query_en = "Who is leading the Bundesliga table?"

    # Test Case 1: Check current config
    print("\n" + "="*70)
    print("CURRENT USER CONFIGURATION")
    print("="*70)
    print(f"Language: {config.profile.language}")
    print(f"Detail Level: {config.profile.detail_level}")
    print(f"Name: {config.profile.name}")
    if config.profile.favorite_team:
        print(f"Favorite Team: {config.profile.favorite_team}")

    # Build system prompt with user preferences
    system_prompt = config.get_base_system_prompt()
    system_prompt += "\n" + config.get_system_prompt_modifier()
    system_prompt += f"\n\nHier sind die aktuellen Daten:\n\n{context}" if config.profile.language == Language.GERMAN else f"\n\nHere is the current data:\n\n{context}"

    # Query LLM
    query = test_query_de if config.profile.language == Language.GERMAN else test_query_en

    print("\n" + "="*70)
    print(f"QUERY: {query}")
    print("="*70)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": query}]
    )

    answer = response.content[0].text
    word_count = len(answer.split())

    print(f"\nRESPONSE ({word_count} words):")
    print(answer)

    # Provide guidance
    print("\n" + "="*70)
    print("CONFIGURATION COMMANDS")
    print("="*70)
    print("\nTo change settings:")
    print("  python onboarding.py          - Run full setup again")
    print("\nOr manually edit .fussballgpt_config.json:")
    print("  language: 'de' or 'en'")
    print("  detail_level: 'quick', 'balanced', or 'detailed'")
    print("\n" + "="*70)

if __name__ == "__main__":
    test_user_config()
