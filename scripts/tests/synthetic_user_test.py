#!/usr/bin/env python3
"""
Synthetic User Testing - Quick Version
AI persona interacts with KSI and evaluates responses
"""
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from mistralai import Mistral
from data_aggregator import DataAggregator

load_dotenv()

# Initialize clients
mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
aggregator = DataAggregator()

# Fetch live data once
print("Fetching live sports data...")
live_data = aggregator.aggregate_all()
data_context = live_data.to_context_string()
print(f"✓ Loaded {len(live_data.news_articles)} articles, {len(live_data.sports_events)} events\n")

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

# Test queries (German football fan perspective)
TEST_QUERIES = [
    # Basic queries
    "Was sind die wichtigsten Sportnachrichten heute?",
    "Welche Bundesliga-Spiele stehen am Wochenende an?",
    "Wer führt die Bundesliga-Tabelle an?",

    # Complex queries
    "Gibt es interessante Transfer-Nachrichten?",
    "Wie läuft die Champions League für deutsche Teams?",

    # Edge cases
    "Was ist mit dem DFB-Pokal passiert?",  # Might not have data
    "Wer sind die Top-Torjäger?",
    "Welche Überraschungen gab es diese Woche?",
]

def query_ksi(question: str) -> tuple[str, float]:
    """Query KSI with live data"""
    start = time.time()

    response = mistral_client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{data_context}"},
            {"role": "user", "content": question}
        ],
        max_tokens=1000,
        temperature=0.7
    )

    elapsed = time.time() - start
    return response.choices[0].message.content, elapsed

def evaluate_response(question: str, response: str, response_time: float) -> dict:
    """AI evaluates the response quality"""

    eval_prompt = f"""Du bist ein kritischer Bewerter von Sportjournalismus.

FRAGE: {question}

ANTWORT: {response}

ANTWORTZEIT: {response_time:.2f}s

Bewerte die Antwort auf einer Skala von 1-10 für:
1. **Relevanz** (Beantwortet sie die Frage?)
2. **Vollständigkeit** (Ist die Antwort vollständig?)
3. **Ton** (Professioneller Journalismus-Ton?)
4. **Genauigkeit** (Basiert auf bereitgestellten Daten?)
5. **Nützlichkeit** (Hilfreich für einen Fußballfan?)

Antworte GENAU in diesem Format:
RELEVANZ: X/10
VOLLSTÄNDIGKEIT: X/10
TON: X/10
GENAUIGKEIT: X/10
NÜTZLICHKEIT: X/10
GESAMT: X/10
KOMMENTAR: [1-2 Sätze Begründung]"""

    eval_response = mistral_client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {"role": "user", "content": eval_prompt}
        ],
        max_tokens=500,
        temperature=0.3
    )

    eval_text = eval_response.choices[0].message.content

    # Parse scores
    scores = {}
    for line in eval_text.split('\n'):
        if ':' in line:
            key = line.split(':')[0].strip().upper()
            value = line.split(':')[1].strip()
            if '/' in value:
                score = value.split('/')[0].strip()
                try:
                    scores[key] = int(score)
                except:
                    pass

    # Extract comment
    comment = ""
    if "KOMMENTAR:" in eval_text:
        comment = eval_text.split("KOMMENTAR:")[1].strip()

    return {
        "scores": scores,
        "comment": comment,
        "full_eval": eval_text
    }

def run_synthetic_test():
    """Run complete synthetic user test"""

    print("=" * 80)
    print("SYNTHETIC USER TEST - German Football Fan Persona")
    print("=" * 80)
    print(f"Testing with LIVE DATA from Kicker RSS + TheSportsDB")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    results = []

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n[Query {i}/{len(TEST_QUERIES)}]")
        print(f"📝 Frage: {query}")

        # Get KSI response
        response, response_time = query_ksi(query)
        print(f"⏱️  Antwortzeit: {response_time:.2f}s")
        print(f"📊 Antwort ({len(response)} chars):")
        print("-" * 80)
        print(response[:300] + "..." if len(response) > 300 else response)
        print("-" * 80)

        # Evaluate response
        print("🤖 Evaluating...")
        evaluation = evaluate_response(query, response, response_time)

        scores = evaluation['scores']
        print(f"\n✅ Bewertung:")
        for key, value in scores.items():
            if key != 'GESAMT':
                print(f"   {key}: {value}/10")
        if 'GESAMT' in scores:
            print(f"   {'='*20}")
            print(f"   GESAMT: {scores['GESAMT']}/10")

        if evaluation['comment']:
            print(f"\n💭 Kommentar: {evaluation['comment']}")

        results.append({
            'query': query,
            'response': response,
            'response_time': response_time,
            'evaluation': evaluation
        })

        print("\n" + "=" * 80)
        time.sleep(2)  # Rate limiting

    # Generate summary report
    print("\n\n" + "=" * 80)
    print("ZUSAMMENFASSUNG / SUMMARY")
    print("=" * 80)

    avg_time = sum(r['response_time'] for r in results) / len(results)
    print(f"\n⏱️  Durchschnittliche Antwortzeit: {avg_time:.2f}s")

    # Calculate average scores
    all_scores = {}
    for result in results:
        for key, value in result['evaluation']['scores'].items():
            if key not in all_scores:
                all_scores[key] = []
            all_scores[key].append(value)

    print(f"\n📊 Durchschnittliche Bewertungen:")
    for key, values in all_scores.items():
        avg = sum(values) / len(values)
        print(f"   {key}: {avg:.1f}/10")

    # Identify issues
    print(f"\n⚠️  Niedrige Bewertungen (<7/10):")
    for i, result in enumerate(results, 1):
        gesamt = result['evaluation']['scores'].get('GESAMT', 0)
        if gesamt < 7:
            print(f"   Query {i}: {result['query'][:60]}... (Score: {gesamt}/10)")

    # Overall assessment
    avg_overall = sum(all_scores.get('GESAMT', [7])) / len(all_scores.get('GESAMT', [1]))
    print(f"\n🎯 Gesamtbewertung: {avg_overall:.1f}/10")

    if avg_overall >= 8:
        status = "✅ AUSGEZEICHNET - Bereit für Kicker Demo"
    elif avg_overall >= 7:
        status = "✅ GUT - Kleinere Verbesserungen empfohlen"
    elif avg_overall >= 6:
        status = "⚠️  AKZEPTABEL - Mehrere Verbesserungen nötig"
    else:
        status = "❌ PROBLEME - Überarbeitung erforderlich"

    print(f"   Status: {status}")

    print("\n" + "=" * 80)
    print(f"Test abgeschlossen: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    return results

if __name__ == "__main__":
    try:
        results = run_synthetic_test()
    except KeyboardInterrupt:
        print("\n\nTest abgebrochen.")
    except Exception as e:
        print(f"\n\nFehler: {e}")
        import traceback
        traceback.print_exc()
