"""
Test language and detail level combinations.

Tests 4 scenarios:
1. Casual Fan (German, Quick mode)
2. Casual Fan (English, Quick mode)
3. Expert Analyst (German, Detailed mode)
4. Expert Analyst (English, Detailed mode)
"""

import os
import sys
from anthropic import Anthropic
from dotenv import load_dotenv
from data_aggregator import DataAggregator

load_dotenv()

# Initialize
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
aggregator = DataAggregator()

# Fetch current data
print("Fetching latest Bundesliga data...")
data = aggregator.aggregate_all()
context = data.to_context_string()

# Test query (same for all tests)
TEST_QUERY_DE = "Wer führt die Bundesliga-Tabelle an?"
TEST_QUERY_EN = "Who is leading the Bundesliga table?"

# System prompts for different combinations
PROMPTS = {
    "de_quick": """Du bist Fußball GPT, ein KI-Assistent für deutschen Fußball.

WICHTIG: Dieser Nutzer bevorzugt KURZE Antworten.
- Maximal 2-3 Sätze
- Nur die wichtigsten Highlights
- Keine taktischen Details
- Einfache Sprache
- Direkte Antworten ohne Kontext

Antworte auf Deutsch im professionellen Stil.
""",

    "en_quick": """You are Fußball GPT, an AI assistant for German football.

IMPORTANT: This user prefers SHORT answers.
- Maximum 2-3 sentences
- Only the most important highlights
- No tactical details
- Simple language
- Direct answers without context

Respond in English with professional style.
""",

    "de_detailed": """Du bist Fußball GPT, ein KI-Assistent für deutschen Fußball.

WICHTIG: Dieser Nutzer bevorzugt DETAILLIERTE Antworten.
- Umfassende Analysen
- Taktische Tiefe (Formationen, Systeme, Strategien)
- Statistische Belege
- Fachterminologie erwünscht
- Vergleiche und historischer Kontext
- 3-5 Absätze oder mehr bei Bedarf

Antworte auf Deutsch im professionellen Journalismus-Stil.
""",

    "en_detailed": """You are Fußball GPT, an AI assistant for German football.

IMPORTANT: This user prefers DETAILED answers.
- Comprehensive analysis
- Tactical depth (formations, systems, strategies)
- Statistical evidence
- Technical terminology welcome
- Comparisons and historical context
- 3-5 paragraphs or more as needed

Respond in English with professional journalism style.
"""
}

def test_scenario(name, prompt, query):
    """Test a specific language/detail combination."""
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"{'='*70}")
    print(f"Query: {query}\n")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=f"{prompt}\n\nHier sind die aktuellen Daten:\n\n{context}",
            messages=[{"role": "user", "content": query}]
        )

        answer = response.content[0].text
        word_count = len(answer.split())
        sentence_count = answer.count('.') + answer.count('!') + answer.count('?')

        print(f"Response ({word_count} words, ~{sentence_count} sentences):")
        print(f"{answer}\n")

        return {
            "name": name,
            "query": query,
            "response": answer,
            "word_count": word_count,
            "sentence_count": sentence_count
        }

    except Exception as e:
        print(f"❌ Error: {e}\n")
        return None

# Run all 4 tests
results = []

print("\n🧪 Testing Language + Detail Level Combinations")
print("="*70)

# Test 1: Casual Fan (German, Quick)
result1 = test_scenario(
    "Casual Fan (German, Quick)",
    PROMPTS["de_quick"],
    TEST_QUERY_DE
)
if result1:
    results.append(result1)

# Test 2: Casual Fan (English, Quick)
result2 = test_scenario(
    "Casual Fan (English, Quick)",
    PROMPTS["en_quick"],
    TEST_QUERY_EN
)
if result2:
    results.append(result2)

# Test 3: Expert Analyst (German, Detailed)
result3 = test_scenario(
    "Expert Analyst (German, Detailed)",
    PROMPTS["de_detailed"],
    TEST_QUERY_DE
)
if result3:
    results.append(result3)

# Test 4: Expert Analyst (English, Detailed)
result4 = test_scenario(
    "Expert Analyst (English, Detailed)",
    PROMPTS["en_detailed"],
    TEST_QUERY_EN
)
if result4:
    results.append(result4)

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

for r in results:
    print(f"\n{r['name']}:")
    print(f"  Words: {r['word_count']}")
    print(f"  Sentences: ~{r['sentence_count']}")
    print(f"  Preview: {r['response'][:80]}...")

print("\n✅ Test complete!")
print("\nExpected results:")
print("  Quick mode: 20-50 words, 2-3 sentences")
print("  Detailed mode: 150-300 words, 8-15 sentences")
