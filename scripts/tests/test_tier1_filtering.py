"""Test Tier 1 changes - Bundesliga filtering and relevance-first strategy."""
from data_aggregator import DataAggregator
from cli import LLMClient
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("TIER 1 IMPLEMENTATION TEST")
print("=" * 70)

# Test 1: Check what articles we're now fetching
print("\n[Test 1: RSS Article Filtering]")
print("-" * 70)
aggregator = DataAggregator()
data = aggregator.aggregate_all()

print(f"\nFetched {len(data.news_articles)} articles")
print("\nArticle sources:")
for article in data.news_articles:
    print(f"  • {article.title}")
    print(f"    Category: {article.category}")
    # Check if it's Bundesliga-related
    is_bundesliga = 'bundesliga' in article.title.lower() or 'bundesliga' in str(article.category).lower()
    print(f"    Bundesliga-related: {'✅' if is_bundesliga else '❌'}")
    print()

# Test 2: Check LLM response with relevance-first strategy
print("\n[Test 2: Relevance-First Article Recommendations]")
print("-" * 70)

llm = LLMClient(provider="openai")

# Query that should show relevant articles
query1 = "What's happening with Bayern?"
print(f"\nQuery: {query1}")
print("Expected: Should show Bayern-related article if exists, or zero if none relevant\n")
response1 = llm.query(query1, data, conversation_history=None)
print(response1)

# Validation
print("\n[Validation]")
has_kicker = "📰" in response1 or "kicker" in response1.lower()
has_wrong_sport = "nfl" in response1.lower() or "vikings" in response1.lower() or "quarterback" in response1.lower()

print(f"  {'✅' if has_kicker else '⚠️'} Has Kicker section: {has_kicker}")
print(f"  {'✅' if not has_wrong_sport else '❌'} No wrong sport articles: {not has_wrong_sport}")

if has_wrong_sport:
    print("\n  ⚠️ WARNING: Still recommending non-Bundesliga content!")
else:
    print("\n  ✅ SUCCESS: Only Bundesliga-relevant content recommended")

print("\n" + "=" * 70)
