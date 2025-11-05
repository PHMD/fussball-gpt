"""
Test form guide integration with LLM.

This tests if the form guide data improves response quality for betting/analyst personas.
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv
from data_aggregator import DataAggregator
from user_config import UserConfigManager, DetailLevel, Language

load_dotenv()

def test_form_guide():
    """Test that form guide enhances LLM responses."""

    print("\n" + "="*70)
    print("  Testing Form Guide Impact on LLM Responses")
    print("="*70)

    # Initialize
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    aggregator = DataAggregator()
    config = UserConfigManager()

    # Set to Detailed mode for Expert Analyst persona
    config.profile.detail_level = DetailLevel.DETAILED
    config.profile.language = Language.GERMAN

    # Fetch data (includes form guide now)
    print("\nFetching latest data (with form guide)...")
    data = aggregator.aggregate_all()
    context = data.to_context_string()

    # Build system prompt
    system_prompt = config.get_base_system_prompt()
    system_prompt += "\n" + config.get_system_prompt_modifier()
    system_prompt += f"\n\nHier sind die aktuellen Daten:\n\n{context}"

    # Test query that should benefit from form guide
    test_query = "Welche Mannschaften haben gerade eine gute Form? Wer ist in Form und wer kämpft?"

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

    # Check if response mentions form data
    form_indicators = ["Form", "letzten 5", "letzte Spiele", "Siegesserie", "punktlos"]
    mentions_form = any(indicator in answer for indicator in form_indicators)

    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)
    print(f"✅ Response mentions form data: {mentions_form}")
    print(f"Response length: {word_count} words (expected: 150-300 for Detailed mode)")

    if mentions_form:
        print("\n✅ SUCCESS: Form guide is being used by LLM to enhance responses!")
    else:
        print("\n⚠️  WARNING: Form guide data may not be prominent enough in responses")

if __name__ == "__main__":
    test_form_guide()
