"""Test Brave Search API integration."""
import os
from dotenv import load_dotenv
from data_aggregator import DataAggregator

load_dotenv()

print("=" * 70)
print("BRAVE SEARCH API INTEGRATION TEST")
print("=" * 70)

aggregator = DataAggregator()

# Check if Brave Search is configured
if not aggregator.has_brave_search:
    print("\n⚠️  Brave Search API key not configured")
    print("\nTo enable Brave Search fallback:")
    print("1. Get free API key at: https://brave.com/search/api/")
    print("2. Add to .env file: BRAVE_SEARCH_API_KEY=your_key_here")
    print("3. Free tier: 2,000 requests/month, 1 req/sec")
    print("\nBenefits:")
    print("✅ Access to entire kicker.de archive (not just recent RSS)")
    print("✅ Query-specific article discovery")
    print("✅ Fallback when RSS has <5 Bundesliga articles")
    print("\n" + "=" * 70)
    exit(0)

print("\n✅ Brave Search API configured")
print(f"   Endpoint: {aggregator.brave_search_base_url}")

# Test queries
test_queries = [
    "Harry Kane Bayern München",
    "RB Leipzig Bundesliga",
    "Borussia Dortmund tactics",
]

print("\n" + "=" * 70)
print("TESTING BRAVE SEARCH QUERIES")
print("=" * 70)

for query in test_queries:
    print(f"\n🔍 Query: {query}")
    print("-" * 70)

    try:
        articles = aggregator.fetch_kicker_articles_brave(query, max_results=5)

        if articles:
            print(f"✅ Found {len(articles)} articles:\n")
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article.title}")
                print(f"   URL: {article.url}")
                print(f"   Snippet: {article.content[:100]}...")
                print()
        else:
            print("❌ No articles found (API might be rate-limited or query too specific)")

    except Exception as e:
        print(f"❌ Error: {e}")

print("=" * 70)
print("INTEGRATION WITH CLI")
print("=" * 70)
print("""
When you run the CLI:
1. RSS feeds fetch ~7 Bundesliga articles (baseline)
2. If <5 articles available, Brave Search automatically augments
3. User query is used to find relevant kicker.de articles
4. LLM sees combined pool of RSS + Brave Search results

Example flow:
  User: "Tell me about Leverkusen's recent performance"

  System checks: 7 RSS articles available (>=5, no Brave Search needed)
  → LLM uses 7 RSS articles

  ---

  User: "What's the latest on transfer rumors?"

  System checks: 7 RSS articles, but none about transfers
  System triggers: Brave Search for "transfer rumors"
  → Finds 5 transfer-related articles from kicker.de archive
  → LLM sees 7 RSS + 5 Brave = 12 total articles
""")

print("\n" + "=" * 70)
