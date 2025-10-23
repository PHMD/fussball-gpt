#!/usr/bin/env python3
"""
Multi-Persona Testing
Tests KSI with different user personas: casual fan, expert analyst, betting enthusiast, fantasy player
"""
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from mistralai import Mistral
from data_aggregator import DataAggregator

load_dotenv()

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
7. Halte Antworten prägnant und journalistisch
8. Passe deine Antwort-Tiefe an die Frage an"""

# Define personas with their characteristics and test queries
PERSONAS = [
    {
        "name": "Casual Fan",
        "description": "Gelegenheitsfan, der nur die Highlights sehen will",
        "personality": "Möchte schnelle, einfache Antworten ohne zu viel Detail. Interessiert sich für große Namen und wichtige Ergebnisse.",
        "queries": [
            "Wer hat am Wochenende gewonnen?",
            "Wie steht Bayern?",
            "Gibt es Transfer-News?",
            "Was ist passiert bei der Champions League?",
        ],
        "evaluation_criteria": {
            "Einfachheit": "Sind Antworten klar und leicht verständlich?",
            "Kürze": "Sind Antworten prägnant (nicht zu lang)?",
            "Highlights": "Fokussiert auf wichtigste Informationen?",
            "Zugänglichkeit": "Keine übermäßigen Fachbegriffe?",
        }
    },
    {
        "name": "Expert Analyst",
        "description": "Taktik-Experte, will tiefe Analysen",
        "personality": "Möchte detaillierte taktische Einblicke, Formationen, Spielsysteme, und strategische Analyse.",
        "queries": [
            "Welche taktischen Veränderungen hat Leverkusen in der letzten Zeit vorgenommen?",
            "Wie hat Stuttgart defensiv gegen Fenerbahce gespielt?",
            "Welche Formation verwendet Bayern derzeit und warum?",
            "Wo sind die taktischen Schwächen von Dortmund?",
        ],
        "evaluation_criteria": {
            "Taktische_Tiefe": "Werden Formationen, Systeme, Strategien erklärt?",
            "Analyse_Qualität": "Geht über bloße Fakten hinaus?",
            "Fachsprache": "Verwendet angemessene taktische Begriffe?",
            "Nuancen": "Erfasst subtile taktische Details?",
        }
    },
    {
        "name": "Betting Enthusiast",
        "description": "Wettet auf Spiele, braucht Vorhersagen",
        "personality": "Möchte Form-Analysen, Head-to-Head-Statistiken, Verletzungen, und datenbasierte Einschätzungen.",
        "queries": [
            "Welches Team ist aktuell in bester Form?",
            "Wie ist die Heimbilanz von Bayern diese Saison?",
            "Welche Teams sind anfällig für Überraschungen?",
            "Gibt es Verletzungen bei wichtigen Spielern?",
        ],
        "evaluation_criteria": {
            "Daten_Fokus": "Basiert auf Statistiken und Fakten?",
            "Form_Analyse": "Berücksichtigt aktuelle Form?",
            "Trends": "Identifiziert Muster und Trends?",
            "Objektivität": "Vermeidet emotionale Einschätzungen?",
        }
    },
    {
        "name": "Fantasy Player",
        "description": "Spielt Fantasy Football, braucht Spieler-Stats",
        "personality": "Möchte individuelle Spielerleistungen, Tore, Vorlagen, Einsatzzeiten, Formkurven.",
        "queries": [
            "Welche Spieler haben am meisten Tore geschossen?",
            "Wer sind die besten Vorlagengeber?",
            "Welche Spieler sind in guter Form?",
            "Gibt es überraschende Leistungsträger?",
        ],
        "evaluation_criteria": {
            "Spieler_Fokus": "Konzentriert auf individuelle Leistungen?",
            "Statistiken": "Bietet konkrete Zahlen (Tore, Vorlagen)?",
            "Form_Bewertung": "Bewertet aktuelle Spielerform?",
            "Empfehlungen": "Gibt hilfreiche Hinweise für Fantasy?",
        }
    }
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


def evaluate_for_persona(persona: dict, question: str, response: str, response_time: float) -> dict:
    """AI evaluates response for specific persona needs"""

    criteria_text = "\n".join([f"- **{key}**: {value}" for key, value in persona["evaluation_criteria"].items()])

    eval_prompt = f"""Du bist ein Experte für Nutzer-Erfahrung und bewertest KI-Antworten.

PERSONA: {persona['name']}
Beschreibung: {persona['description']}
Erwartungen: {persona['personality']}

FRAGE: {question}
ANTWORT: {response}
ANTWORTZEIT: {response_time:.2f}s

Bewerte, wie gut diese Antwort für diese SPEZIFISCHE PERSONA ist (1-10):

{criteria_text}

Antworte GENAU in diesem Format:
{chr(10).join([f"{key.upper()}: X/10" for key in persona["evaluation_criteria"].keys()])}
GESAMT: X/10
KOMMENTAR: [2-3 Sätze: Was passt gut für diese Persona? Was fehlt?]"""

    eval_response = mistral_client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {"role": "user", "content": eval_prompt}
        ],
        max_tokens=600,
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


def test_persona(persona: dict) -> dict:
    """Test KSI with a specific persona"""

    print(f"\n{'='*80}")
    print(f"PERSONA: {persona['name']}")
    print(f"{'='*80}")
    print(f"Beschreibung: {persona['description']}")
    print(f"Erwartungen: {persona['personality']}")
    print(f"{'='*80}\n")

    results = []

    for i, query in enumerate(persona['queries'], 1):
        print(f"\n[Frage {i}/{len(persona['queries'])}]")
        print(f"📝 {query}")

        # Get KSI response
        response, response_time = query_ksi(query)
        print(f"⏱️  Antwortzeit: {response_time:.2f}s")
        print(f"📊 Antwort ({len(response)} chars):")
        print("-" * 80)
        print(response[:300] + "..." if len(response) > 300 else response)
        print("-" * 80)

        # Evaluate for persona
        print("🤖 Evaluating for persona...")
        evaluation = evaluate_for_persona(persona, query, response, response_time)

        scores = evaluation['scores']
        print(f"\n✅ Bewertung für {persona['name']}:")
        for key, value in scores.items():
            if key != 'GESAMT':
                print(f"   {key}: {value}/10")
        if 'GESAMT' in scores:
            print(f"   {'='*20}")
            print(f"   GESAMT: {scores['GESAMT']}/10")

        if evaluation['comment']:
            print(f"\n💭 {evaluation['comment']}")

        results.append({
            'query': query,
            'response': response,
            'response_time': response_time,
            'evaluation': evaluation
        })

        print()
        time.sleep(2)  # Rate limiting

    return {
        'persona': persona,
        'results': results
    }


def run_multi_persona_test():
    """Run complete multi-persona test"""

    print("=" * 80)
    print("MULTI-PERSONA TEST")
    print("Testing KSI with different user types")
    print("=" * 80)
    print(f"Testing with LIVE DATA from Kicker RSS + TheSportsDB")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    all_results = []

    for i, persona in enumerate(PERSONAS, 1):
        print(f"\n\n{'#'*80}")
        print(f"# PERSONA {i}/{len(PERSONAS)}")
        print(f"{'#'*80}")

        result = test_persona(persona)
        all_results.append(result)

        time.sleep(3)  # Pause between personas

    # Generate summary report
    print("\n\n" + "=" * 80)
    print("ZUSAMMENFASSUNG / SUMMARY")
    print("=" * 80)

    # Average scores per persona
    print("\n📊 Durchschnittliche Bewertungen pro Persona:\n")

    persona_averages = []
    for result in all_results:
        persona_name = result['persona']['name']
        all_scores = []

        for query_result in result['results']:
            gesamt = query_result['evaluation']['scores'].get('GESAMT', 0)
            all_scores.append(gesamt)

        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        persona_averages.append((persona_name, avg_score))

        print(f"   {persona_name:20} | {avg_score:.1f}/10")

    # Overall average
    overall_avg = sum(score for _, score in persona_averages) / len(persona_averages)
    print(f"\n   {'='*30}")
    print(f"   {'GESAMT':20} | {overall_avg:.1f}/10")

    # Identify strengths and weaknesses
    print(f"\n💪 Stärken (>8.0/10):")
    strong_personas = [name for name, score in persona_averages if score > 8.0]
    if strong_personas:
        for name in strong_personas:
            print(f"   ✅ {name}")
    else:
        print(f"   Keine Persona erreicht >8.0")

    print(f"\n⚠️  Verbesserungsbedarf (<7.0/10):")
    weak_personas = [name for name, score in persona_averages if score < 7.0]
    if weak_personas:
        for name in weak_personas:
            print(f"   📝 {name}")
    else:
        print(f"   ✅ Alle Personas >7.0")

    # Overall assessment
    print(f"\n🎯 Gesamtbewertung: {overall_avg:.1f}/10")

    if overall_avg >= 8:
        status = "✅ AUSGEZEICHNET - KSI passt sich gut an verschiedene Nutzertypen an"
    elif overall_avg >= 7:
        status = "✅ GUT - Funktioniert für die meisten Personas, kleinere Anpassungen empfohlen"
    elif overall_avg >= 6:
        status = "⚠️  AKZEPTABEL - Einige Personas werden nicht optimal bedient"
    else:
        status = "❌ PROBLEME - Persona-spezifische Anpassungen erforderlich"

    print(f"   Status: {status}")

    print("\n" + "=" * 80)
    print(f"Test abgeschlossen: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    return all_results


if __name__ == "__main__":
    try:
        results = run_multi_persona_test()
    except KeyboardInterrupt:
        print("\n\nTest abgebrochen.")
    except Exception as e:
        print(f"\n\nFehler: {e}")
        import traceback
        traceback.print_exc()
