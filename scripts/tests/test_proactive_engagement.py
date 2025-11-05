"""
Test proactive engagement (Issue #19).

Validates that the LLM provides context-aware follow-up suggestions
based on query type: player, team, match, standings, news.
"""
import os
from dotenv import load_dotenv

from data_aggregator import DataAggregator
from cli import LLMClient

load_dotenv()

def test_follow_ups():
    """Test that every response includes context-aware follow-ups."""

    print("=" * 70)
    print("  PROACTIVE ENGAGEMENT TESTING - Issue #19")
    print("=" * 70)

    # Fetch real data once
    print("\n[Fetching data...]")
    aggregator = DataAggregator()
    data = aggregator.aggregate_all()

    # Initialize LLM
    llm = LLMClient(provider="openai")

    # Test cases: (query, query_type, expected_context)
    test_cases = [
        (
            "Tell me about Harry Kane",
            "PLAYER",
            ["team", "match", "compare", "performers"]
        ),
        (
            "How is Bayern doing?",
            "TEAM",
            ["player", "form", "fixtures", "upcoming", "match"]
        ),
        (
            "When is Bayern's next game?",
            "MATCH/FIXTURE",
            ["head-to-head", "form", "odds", "record"]
        ),
        (
            "Show me the Bundesliga table",
            "STANDINGS",
            ["top scorer", "performer", "fixtures", "upcoming"]
        ),
        (
            "What's the latest news?",
            "NEWS/GENERAL",
            ["team", "feed", "personalized", "deeper"]
        ),
    ]

    passed = 0
    failed = 0

    for i, (query, query_type, expected_keywords) in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/5: {query_type} Query")
        print(f"{'='*70}")
        print(f"Query: \"{query}\"")
        print(f"Expected context: {', '.join(expected_keywords)}")
        print("-" * 70)

        # Get response
        response = llm.query(query, data, conversation_history=[])
        print(f"\nResponse:\n{response}")

        # Validation
        print(f"\n{'─'*70}")
        print("VALIDATION:")
        print(f"{'─'*70}")

        # Check 1: Has follow-up section (💬)
        has_follow_up = "💬" in response
        print(f"  {'✅' if has_follow_up else '❌'} Has follow-up section (💬)")

        # Check 2: Context-aware keywords present
        response_lower = response.lower()
        found_keywords = [kw for kw in expected_keywords if kw in response_lower]
        context_aware = len(found_keywords) > 0

        print(f"  {'✅' if context_aware else '❌'} Context-aware follow-up")
        if found_keywords:
            print(f"     → Found: {', '.join(found_keywords)}")
        else:
            print(f"     → Missing expected keywords: {', '.join(expected_keywords)}")

        # Check 3: Multiple options (2-3 suggestions)
        bullet_count = response.count("•")
        has_multiple_options = bullet_count >= 2
        print(f"  {'✅' if has_multiple_options else '⚠️'} Multiple options ({bullet_count} bullets)")

        # Check 4: Not generic ("anything else?", "what else?")
        generic_phrases = ["anything else", "what else", "something else", "help you with something"]
        is_specific = not any(phrase in response_lower for phrase in generic_phrases)
        print(f"  {'✅' if is_specific else '⚠️'} Specific (not generic 'anything else?')")

        # Overall pass/fail
        test_passed = has_follow_up and context_aware
        if test_passed:
            passed += 1
            print(f"\n✅ TEST PASSED")
        else:
            failed += 1
            print(f"\n❌ TEST FAILED")

    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"Tests passed: {passed}/5")
    print(f"Tests failed: {failed}/5")

    if passed == 5:
        print("\n🎉 All tests passed! Proactive engagement working as expected.")
    elif passed >= 3:
        print(f"\n⚠️  Most tests passed ({passed}/5). Review failures above.")
    else:
        print(f"\n❌ Many tests failed ({failed}/5). LLM not following context-aware rules.")

    print(f"\n{'='*70}")
    print("KEY BEHAVIORS TO LOOK FOR:")
    print("  1. EVERY response ends with follow-up (💬)")
    print("  2. Follow-ups are context-aware (player→team, team→players, etc.)")
    print("  3. Offer 2-3 specific options (not 'anything else?')")
    print("  4. Natural and conversational tone")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    test_follow_ups()
