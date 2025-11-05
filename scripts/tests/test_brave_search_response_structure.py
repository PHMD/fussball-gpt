"""
Explore Brave Search API response structure.

Tests both Web Search and News Search to see what metadata we can extract
for enhancing our dataset without full article access.
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

BRAVE_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")

print("=" * 70)
print("BRAVE SEARCH API RESPONSE STRUCTURE EXPLORATION")
print("=" * 70)

# Test query about Bundesliga
test_query = "Harry Kane Bayern München Bundesliga"

print(f"\nTest Query: {test_query}\n")


def test_web_search():
    """Test Web Search API (what we currently use)."""
    print("\n" + "=" * 70)
    print("1. WEB SEARCH API (Current Implementation)")
    print("=" * 70)

    try:
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": BRAVE_API_KEY,
            },
            params={
                "q": f"site:kicker.de {test_query}",
                "count": 3,
                "freshness": "pw",  # Past week
            },
            timeout=5
        )

        response.raise_for_status()
        data = response.json()

        print("\n✅ Response received")
        print(f"Status: {response.status_code}")

        # Show full structure of first result
        if data.get("web", {}).get("results"):
            result = data["web"]["results"][0]
            print("\nFull structure of first result:")
            print(json.dumps(result, indent=2))

            # Extract key fields
            print("\n" + "-" * 70)
            print("KEY FIELDS AVAILABLE:")
            print("-" * 70)
            for key in result.keys():
                value = result[key]
                if isinstance(value, str) and len(value) > 100:
                    print(f"  • {key}: {value[:100]}... ({len(value)} chars)")
                else:
                    print(f"  • {key}: {value}")

        return data

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_news_search():
    """Test News Search API (specialized for news articles)."""
    print("\n" + "=" * 70)
    print("2. NEWS SEARCH API (Specialized for News)")
    print("=" * 70)

    try:
        response = requests.get(
            "https://api.search.brave.com/res/v1/news/search",
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": BRAVE_API_KEY,
            },
            params={
                "q": test_query,
                "count": 3,
                "freshness": "pw",  # Past week
            },
            timeout=5
        )

        response.raise_for_status()
        data = response.json()

        print("\n✅ Response received")
        print(f"Status: {response.status_code}")

        # Show full structure of first result
        if data.get("results"):
            result = data["results"][0]
            print("\nFull structure of first result:")
            print(json.dumps(result, indent=2))

            # Extract key fields
            print("\n" + "-" * 70)
            print("KEY FIELDS AVAILABLE:")
            print("-" * 70)
            for key in result.keys():
                value = result[key]
                if isinstance(value, str) and len(value) > 100:
                    print(f"  • {key}: {value[:100]}... ({len(value)} chars)")
                else:
                    print(f"  • {key}: {value}")

        return data

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def compare_apis(web_data, news_data):
    """Compare what fields each API provides."""
    print("\n" + "=" * 70)
    print("3. API COMPARISON")
    print("=" * 70)

    if web_data and news_data:
        web_fields = set(web_data.get("web", {}).get("results", [{}])[0].keys()) if web_data.get("web", {}).get("results") else set()
        news_fields = set(news_data.get("results", [{}])[0].keys()) if news_data.get("results") else set()

        print("\nFields in Web Search only:")
        for field in sorted(web_fields - news_fields):
            print(f"  • {field}")

        print("\nFields in News Search only:")
        for field in sorted(news_fields - web_fields):
            print(f"  • {field}")

        print("\nFields in both:")
        for field in sorted(web_fields & news_fields):
            print(f"  • {field}")


def analyze_metadata_potential(web_data, news_data):
    """Analyze what metadata we can extract for article summaries."""
    print("\n" + "=" * 70)
    print("4. METADATA EXTRACTION POTENTIAL")
    print("=" * 70)

    print("\nCan we extract these for article summaries?")

    fields_to_check = [
        ("title", "Article headline"),
        ("description", "Article summary/snippet"),
        ("url", "Link to full article"),
        ("age", "Publication date"),
        ("author", "Article author"),
        ("thumbnail", "Featured image"),
        ("breaking", "Breaking news flag"),
        ("source", "Publication source"),
        ("meta_url", "Metadata about source"),
    ]

    # Check Web Search
    print("\n📰 Web Search API:")
    web_result = web_data.get("web", {}).get("results", [{}])[0] if web_data else {}
    for field, description in fields_to_check:
        has_field = field in web_result
        value_preview = ""
        if has_field and web_result[field]:
            val = str(web_result[field])
            value_preview = f" = {val[:50]}..." if len(val) > 50 else f" = {val}"
        print(f"  {'✅' if has_field else '❌'} {field:15} ({description}){value_preview}")

    # Check News Search
    print("\n📰 News Search API:")
    news_result = news_data.get("results", [{}])[0] if news_data else {}
    for field, description in fields_to_check:
        has_field = field in news_result
        value_preview = ""
        if has_field and news_result[field]:
            val = str(news_result[field])
            value_preview = f" = {val[:50]}..." if len(val) > 50 else f" = {val}"
        print(f"  {'✅' if has_field else '❌'} {field:15} ({description}){value_preview}")


def test_keyword_extraction():
    """Test if we can extract keywords/entities from descriptions."""
    print("\n" + "=" * 70)
    print("5. KEYWORD/ENTITY EXTRACTION POTENTIAL")
    print("=" * 70)

    print("\nBundesliga entities we could detect:")

    bundesliga_teams = [
        'Bayern', 'München', 'Dortmund', 'Leipzig', 'Leverkusen',
        'Frankfurt', 'Freiburg', 'Union Berlin', 'Köln', 'Hoffenheim',
        'Wolfsburg', 'Gladbach', 'Stuttgart', 'Bremen', 'Augsburg'
    ]

    bundesliga_keywords = [
        'Bundesliga', 'DFB', 'Pokal', 'goal', 'assist', 'injury',
        'transfer', 'tactics', 'match', 'fixture', 'standings'
    ]

    print("\nTeams (18 clubs):")
    print(f"  {', '.join(bundesliga_teams[:8])}...")

    print("\nKeywords (match type, stats, etc.):")
    print(f"  {', '.join(bundesliga_keywords)}")

    print("\nWith title + description, we could:")
    print("  ✅ Identify which team(s) the article is about")
    print("  ✅ Classify article type (match report, injury, transfer, etc.)")
    print("  ✅ Extract player names mentioned")
    print("  ✅ Detect match context (upcoming, recent, standings)")
    print("  ❌ Get exact stats (need full article)")
    print("  ❌ Get quotes (need full article)")


# Run all tests
web_data = test_web_search()
news_data = test_news_search()

if web_data or news_data:
    compare_apis(web_data, news_data)
    analyze_metadata_potential(web_data, news_data)
    test_keyword_extraction()

print("\n" + "=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)
print("""
Based on API responses, we can:

1. USE METADATA FOR ARTICLE CARDS:
   - Title, description, URL, publication date
   - No need for full article text
   - Create rich article previews

2. KEYWORD MATCHING FOR CLASSIFICATION:
   - Detect teams mentioned (Bayern, Dortmund, etc.)
   - Classify article type (match, injury, transfer)
   - Filter by relevance to user query

3. ENHANCE CONTEXT WITHOUT FULL TEXT:
   - "3 recent articles about Harry Kane"
   - "2 match reports about Bayern"
   - "1 injury update about Leverkusen"

4. CONSIDER NEWS SEARCH API:
   - May have better metadata for news articles
   - Potentially better freshness filtering
   - Worth testing vs Web Search
""")

print("\n" + "=" * 70)
