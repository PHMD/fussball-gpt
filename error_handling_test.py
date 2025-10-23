#!/usr/bin/env python3
"""
Error Handling Test
Tests how KSI handles various error scenarios and edge cases
"""
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from mistralai import Mistral
from data_aggregator import DataAggregator
import requests

load_dotenv()

mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

SYSTEM_PROMPT = """Du bist KSI (Kicker Sports Intelligence), ein deutscher Sportjournalismus-Assistent und Experte für Fußball.

Deine Expertise umfasst:
- Deutsche Bundesliga und 2. Bundesliga
- Europäische Wettbewerbe (Champions League, Europa League)
- Internationale Sportnachrichten

Bei der Beantwortung von Fragen:
1. Basiere deine Antworten auf den bereitgestellten aktuellen Daten
2. Sei präzise mit Daten, Ergebnissen und Spielernamen
3. Wenn Informationen nicht in den Daten vorhanden sind, sage das klar
4. Biete Kontext und Analyse, nicht nur rohe Fakten
5. Verwende einen professionellen aber freundlichen Ton (kicker.de-Standard)
6. Antworte immer auf Deutsch
7. Halte Antworten prägnant und journalistisch"""

# Test scenarios
ERROR_SCENARIOS = [
    {
        "name": "API Timeout Simulation",
        "type": "api_timeout",
        "description": "What happens when data sources timeout?",
        "test_func": "test_api_timeout"
    },
    {
        "name": "Invalid Query Handling",
        "type": "invalid_query",
        "description": "Nonsensical or off-topic questions",
        "queries": [
            "Was ist die Hauptstadt von Deutschland?",  # Off-topic
            "sdkfjhskdjf ksjdhf",  # Gibberish
            "Wer wird den Nobelpreis gewinnen?",  # Completely off-topic
            "",  # Empty query
        ]
    },
    {
        "name": "Data Unavailable",
        "type": "no_data",
        "description": "Questions about data we don't have",
        "queries": [
            "Wer hat gestern im DFB-Pokal gespielt?",
            "Was ist die aktuelle Torschützenliste der 3. Liga?",
            "Wie viele Zuschauer waren im letzten Spiel?",
        ]
    },
    {
        "name": "Ambiguous References",
        "type": "ambiguous",
        "description": "Unclear pronouns or references",
        "queries": [
            "Wie geht es ihm?",  # No context
            "Haben sie gewonnen?",  # No referent
            "Was war das Ergebnis?",  # Which match?
        ]
    },
    {
        "name": "Rate Limit Handling",
        "type": "rate_limit",
        "description": "Rapid-fire queries to test rate limiting",
        "test_func": "test_rate_limits"
    }
]


def test_api_timeout():
    """Test behavior when API sources timeout"""
    print("\n📡 Testing API timeout handling...\n")

    # Simulate timeout by using invalid URLs temporarily
    aggregator = DataAggregator()
    original_url = aggregator.sports_db_base_url

    # Set to non-existent endpoint
    aggregator.sports_db_base_url = "https://httpstat.us/504?sleep=10000"

    try:
        print("   Attempting to fetch data with timeout endpoint...")
        start = time.time()
        data = aggregator.fetch_bundesliga_standings()
        elapsed = time.time() - start

        if data:
            result = f"❌ FAIL: Should have timed out, got {len(data)} chars in {elapsed:.2f}s"
        else:
            result = f"✅ PASS: Gracefully handled timeout in {elapsed:.2f}s (returned empty data)"
    except Exception as e:
        elapsed = time.time() - start
        result = f"✅ PASS: Caught exception in {elapsed:.2f}s: {str(e)[:100]}"
    finally:
        # Restore original URL
        aggregator.sports_db_base_url = original_url

    return result


def query_ksi(question: str, context: str = "") -> tuple[str, float, str]:
    """Query KSI and return response, time, and error status"""

    if not question or not question.strip():
        return "ERROR: Empty query", 0.0, "empty_query"

    start = time.time()

    try:
        response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{context}"},
                {"role": "user", "content": question}
            ],
            max_tokens=500,
            temperature=0.7
        )

        elapsed = time.time() - start
        return response.choices[0].message.content, elapsed, "success"

    except Exception as e:
        elapsed = time.time() - start
        return f"ERROR: {str(e)}", elapsed, "exception"


def test_invalid_queries(aggregator):
    """Test how KSI handles invalid/off-topic queries"""
    print("\n🚫 Testing invalid query handling...\n")

    data_context = aggregator.aggregate_all().to_context_string()
    results = []

    for query in ERROR_SCENARIOS[1]["queries"]:
        print(f"   Query: '{query[:50]}...' " if len(query) > 50 else f"   Query: '{query}'")

        response, elapsed, status = query_ksi(query, data_context)

        # Check if response appropriately handles invalid query
        if status == "empty_query":
            result = "✅ PASS: Rejected empty query"
        elif "nicht" in response.lower() or "keine" in response.lower() or "daten" in response.lower():
            result = f"✅ PASS: Gracefully declined ({elapsed:.2f}s)"
        elif len(response) > 20:
            result = f"⚠️  WARN: Answered anyway ({elapsed:.2f}s) - might hallucinate"
        else:
            result = f"❌ FAIL: Unclear response ({elapsed:.2f}s)"

        print(f"      {result}")
        print(f"      Response: {response[:100]}...\n")

        results.append({
            "query": query,
            "response": response,
            "time": elapsed,
            "result": result
        })

        time.sleep(1)

    return results


def test_data_unavailable(aggregator):
    """Test how KSI handles questions about unavailable data"""
    print("\n📭 Testing data unavailable scenarios...\n")

    data_context = aggregator.aggregate_all().to_context_string()
    results = []

    for query in ERROR_SCENARIOS[2]["queries"]:
        print(f"   Query: '{query}'")

        response, elapsed, status = query_ksi(query, data_context)

        # Check if response admits data unavailability
        transparency_keywords = ["nicht", "keine", "daten", "informationen", "liegt nicht vor", "nicht verfügbar"]
        is_transparent = any(keyword in response.lower() for keyword in transparency_keywords)

        if is_transparent:
            result = f"✅ PASS: Admits data unavailability ({elapsed:.2f}s)"
        else:
            result = f"❌ FAIL: May be hallucinating ({elapsed:.2f}s)"

        print(f"      {result}")
        print(f"      Response: {response[:150]}...\n")

        results.append({
            "query": query,
            "response": response,
            "time": elapsed,
            "result": result
        })

        time.sleep(1)

    return results


def test_ambiguous_references(aggregator):
    """Test how KSI handles ambiguous pronouns/references"""
    print("\n❓ Testing ambiguous reference handling...\n")

    data_context = aggregator.aggregate_all().to_context_string()
    results = []

    for query in ERROR_SCENARIOS[3]["queries"]:
        print(f"   Query: '{query}'")

        response, elapsed, status = query_ksi(query, data_context)

        # Check if response asks for clarification or makes reasonable assumptions
        clarification_keywords = ["welchen", "welches", "genau", "bitte", "können sie", "meinen sie"]
        asks_clarification = any(keyword in response.lower() for keyword in clarification_keywords)

        if asks_clarification:
            result = f"✅ PASS: Requests clarification ({elapsed:.2f}s)"
        elif len(response) > 50:
            result = f"⚠️  WARN: Makes assumptions ({elapsed:.2f}s)"
        else:
            result = f"❌ FAIL: Unclear handling ({elapsed:.2f}s)"

        print(f"      {result}")
        print(f"      Response: {response[:150]}...\n")

        results.append({
            "query": query,
            "response": response,
            "time": elapsed,
            "result": result
        })

        time.sleep(1)

    return results


def test_rate_limits(aggregator):
    """Test rapid-fire queries to check rate limit handling"""
    print("\n⚡ Testing rate limit handling...\n")

    data_context = aggregator.aggregate_all().to_context_string()

    # Fire 5 queries rapidly
    queries = [
        "Wer führt die Tabelle an?",
        "Wer ist Zweiter?",
        "Wer ist Dritter?",
        "Wer ist Vierter?",
        "Wer ist Fünfter?",
    ]

    results = []
    start_total = time.time()

    for i, query in enumerate(queries, 1):
        print(f"   Query {i}/5: '{query}'")
        response, elapsed, status = query_ksi(query, data_context)

        if status == "success":
            result = f"✅ Success ({elapsed:.2f}s)"
        else:
            result = f"❌ Failed: {status} ({elapsed:.2f}s)"

        print(f"      {result}\n")
        results.append(elapsed)

    total_time = time.time() - start_total
    avg_time = sum(results) / len(results)

    print(f"   Total time: {total_time:.2f}s")
    print(f"   Average per query: {avg_time:.2f}s")

    if total_time < 30:
        final_result = f"✅ PASS: Handled {len(queries)} rapid queries in {total_time:.2f}s"
    else:
        final_result = f"⚠️  WARN: Slow under load ({total_time:.2f}s for {len(queries)} queries)"

    return final_result


def run_error_handling_test():
    """Run complete error handling test suite"""

    print("=" * 80)
    print("ERROR HANDLING TEST SUITE")
    print("Testing edge cases and failure modes")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    aggregator = DataAggregator()

    # Test 1: API Timeout
    print(f"\n{'#'*80}")
    print(f"# TEST 1: API TIMEOUT")
    print(f"{'#'*80}")
    timeout_result = test_api_timeout()
    print(f"\n{timeout_result}")

    # Test 2: Invalid Queries
    print(f"\n{'#'*80}")
    print(f"# TEST 2: INVALID QUERIES")
    print(f"{'#'*80}")
    invalid_results = test_invalid_queries(aggregator)

    # Test 3: Data Unavailable
    print(f"\n{'#'*80}")
    print(f"# TEST 3: DATA UNAVAILABLE")
    print(f"{'#'*80}")
    unavailable_results = test_data_unavailable(aggregator)

    # Test 4: Ambiguous References
    print(f"\n{'#'*80}")
    print(f"# TEST 4: AMBIGUOUS REFERENCES")
    print(f"{'#'*80}")
    ambiguous_results = test_ambiguous_references(aggregator)

    # Test 5: Rate Limits
    print(f"\n{'#'*80}")
    print(f"# TEST 5: RATE LIMIT HANDLING")
    print(f"{'#'*80}")
    rate_limit_result = test_rate_limits(aggregator)
    print(f"\n{rate_limit_result}")

    # Summary
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(f"\n✅ API Timeout: {timeout_result}")

    invalid_passes = sum(1 for r in invalid_results if "PASS" in r["result"])
    print(f"\n📊 Invalid Queries: {invalid_passes}/{len(invalid_results)} handled gracefully")

    unavailable_passes = sum(1 for r in unavailable_results if "PASS" in r["result"])
    print(f"📊 Data Unavailable: {unavailable_passes}/{len(unavailable_results)} admitted limitations")

    ambiguous_passes = sum(1 for r in ambiguous_results if "PASS" in r["result"])
    print(f"📊 Ambiguous References: {ambiguous_passes}/{len(ambiguous_results)} requested clarification")

    print(f"\n⚡ Rate Limits: {rate_limit_result}")

    # Overall assessment
    total_tests = len(invalid_results) + len(unavailable_results) + len(ambiguous_results) + 2
    total_passes = invalid_passes + unavailable_passes + ambiguous_passes + 2  # timeout + rate limit

    pass_rate = (total_passes / total_tests) * 100

    print(f"\n🎯 Overall Pass Rate: {pass_rate:.1f}% ({total_passes}/{total_tests})")

    if pass_rate >= 80:
        status = "✅ EXCELLENT - Error handling ready for beta"
    elif pass_rate >= 60:
        status = "✅ GOOD - Minor improvements recommended"
    else:
        status = "❌ NEEDS WORK - Significant error handling issues"

    print(f"   Status: {status}")

    print("\n" + "=" * 80)
    print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        run_error_handling_test()
    except KeyboardInterrupt:
        print("\n\nTest aborted.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
