"""
Test off-topic question handling with three-tier system.

Tests data-driven scope management to ensure:
1. Tier 1: Bundesliga-related questions are answered fully
2. Tier 2: Bundesliga-adjacent questions get partial answer + redirect
3. Tier 3: Off-topic questions get polite redirect
"""

import os
import time
from dotenv import load_dotenv

from data_aggregator import DataAggregator
from cli import LLMClient

load_dotenv()


def test_off_topic_handling():
    """Test three-tier scope management system."""

    print("\n" + "="*80)
    print("  OFF-TOPIC HANDLING TEST - Three-Tier System")
    print("="*80)

    # Initialize components
    aggregator = DataAggregator()
    llm = LLMClient(provider="anthropic")  # Using Claude for consistency

    # Fetch data for context
    print("\n[Fetching Bundesliga data...]")
    data = aggregator.aggregate_all()
    print(f"[Data loaded: {len(data.news_articles)} articles, {len(data.sports_events)} events]")

    # Test cases organized by tier
    test_cases = {
        "Tier 1: Bundesliga-Related (Should Answer Fully)": [
            "Who is the top scorer?",
            "When is Dortmund's next match?",
            "Show me the current standings",
            "Are there any injured players for Bayern?",
            "What's the latest Bundesliga news?",
        ],
        "Tier 2: Bundesliga-Adjacent (Should Acknowledge + Redirect)": [
            "How much do Bundesliga tickets cost?",
            "What do Bundesliga players earn?",
            "Is Bundesliga popular in Asia?",
        ],
        "Tier 3: Off-Topic (Should Politely Redirect)": [
            "What's the best restaurant in Munich?",
            "How do I learn German?",
            "Tell me about Formula 1",
            "What movies are playing this weekend?",
        ],
    }

    results = {
        "tier_1_pass": 0,
        "tier_1_fail": 0,
        "tier_2_pass": 0,
        "tier_2_fail": 0,
        "tier_3_pass": 0,
        "tier_3_fail": 0,
    }

    # Run tests for each tier
    for tier_name, questions in test_cases.items():
        print(f"\n{'='*80}")
        print(f"  {tier_name}")
        print("="*80)

        for question in questions:
            print(f"\n📋 Testing: \"{question}\"")
            print("-" * 80)

            # Query LLM
            response = llm.query(question, data)
            print(f"\n🤖 Response:\n{response}")
            print("-" * 80)

            # Add delay to respect rate limits
            time.sleep(5)

            # Validate response based on tier
            if "Tier 1" in tier_name:
                # Should answer with Bundesliga data or context
                passed = validate_tier_1(response)
                results["tier_1_pass" if passed else "tier_1_fail"] += 1
            elif "Tier 2" in tier_name:
                # Should acknowledge + redirect to Bundesliga content
                passed = validate_tier_2(response)
                results["tier_2_pass" if passed else "tier_2_fail"] += 1
            else:  # Tier 3
                # Should politely redirect to Bundesliga capabilities
                passed = validate_tier_3(response)
                results["tier_3_pass" if passed else "tier_3_fail"] += 1

            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"\n{status}")

    # Print summary
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80)
    print(f"\nTier 1 (Bundesliga-Related):")
    print(f"  ✅ Pass: {results['tier_1_pass']}")
    print(f"  ❌ Fail: {results['tier_1_fail']}")

    print(f"\nTier 2 (Bundesliga-Adjacent):")
    print(f"  ✅ Pass: {results['tier_2_pass']}")
    print(f"  ❌ Fail: {results['tier_2_fail']}")

    print(f"\nTier 3 (Off-Topic):")
    print(f"  ✅ Pass: {results['tier_3_pass']}")
    print(f"  ❌ Fail: {results['tier_3_fail']}")

    total_pass = results['tier_1_pass'] + results['tier_2_pass'] + results['tier_3_pass']
    total_fail = results['tier_1_fail'] + results['tier_2_fail'] + results['tier_3_fail']
    total = total_pass + total_fail

    print(f"\n{'='*80}")
    print(f"  OVERALL: {total_pass}/{total} tests passed ({total_pass/total*100:.0f}%)")
    print("="*80)

    return total_pass == total


def validate_tier_1(response: str) -> bool:
    """
    Validate Tier 1 response (should answer with Bundesliga data/context).

    Checks:
    - Response contains actual information (not just redirects)
    - Mentions Bundesliga entities (teams, players, leagues)
    - Does NOT just redirect without answering
    """
    response_lower = response.lower()

    # Should contain Bundesliga entities or data
    bundesliga_indicators = [
        "bayern", "dortmund", "bundesliga", "kane", "kompany", "allianz",
        "goals", "matches", "scorer", "stats", "form", "league"
    ]

    has_bundesliga_content = any(indicator in response_lower for indicator in bundesliga_indicators)

    # Should NOT be a pure redirect (should actually answer)
    redirect_phrases = [
        "i focus on",
        "i specialize in",
        "i'm your bundesliga assistant",
        "i don't have information about"
    ]

    is_pure_redirect = any(phrase in response_lower for phrase in redirect_phrases) and not has_bundesliga_content

    return has_bundesliga_content and not is_pure_redirect


def validate_tier_2(response: str) -> bool:
    """
    Validate Tier 2 response (should acknowledge + redirect).

    Checks:
    - Response acknowledges the question
    - Explains what data IS available
    - Offers Bundesliga alternatives
    - Maintains friendly tone
    """
    response_lower = response.lower()

    # Should acknowledge limitation but offer alternatives
    acknowledgment_indicators = [
        "i focus on",
        "i don't have",
        "i specialize in",
        "rather than"
    ]

    has_acknowledgment = any(indicator in response_lower for indicator in acknowledgment_indicators)

    # Should offer Bundesliga alternatives
    alternative_indicators = [
        "but", "however", "i can", "would you like", "interested",
        "want to", "about", "bayern", "bundesliga"
    ]

    has_alternatives = any(indicator in response_lower for indicator in alternative_indicators)

    return has_acknowledgment and has_alternatives


def validate_tier_3(response: str) -> bool:
    """
    Validate Tier 3 response (should politely redirect).

    Checks:
    - Response is friendly (not robotic)
    - Briefly explains scope/focus
    - Suggests Bundesliga capabilities
    - Does NOT attempt to answer off-topic question
    """
    response_lower = response.lower()

    # Should explain scope
    scope_indicators = [
        "bundesliga",
        "specialize",
        "focus on",
        "german football",
        "football assistant"
    ]

    has_scope_explanation = any(indicator in response_lower for indicator in scope_indicators)

    # Should suggest capabilities
    capability_indicators = [
        "i can", "want to", "would you like", "interested",
        "matches", "stats", "news", "fixtures", "standings"
    ]

    has_capability_suggestion = any(indicator in response_lower for indicator in capability_indicators)

    # Should NOT answer off-topic content directly (allow mentioning the topic for context)
    # Updated to be less strict - it's OK to mention "Super Bowl" while redirecting
    off_topic_answers = [
        "celsius", "fahrenheit", "recipe", "ingredients", "capital of france is",
        "paris is the capital", "stocks work by", "basketball rules"
    ]

    answers_off_topic = any(answer in response_lower for answer in off_topic_answers)

    return has_scope_explanation and has_capability_suggestion and not answers_off_topic


if __name__ == "__main__":
    success = test_off_topic_handling()
    exit(0 if success else 1)
