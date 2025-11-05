#!/usr/bin/env python3
"""
Multi-Turn Conversation Test
Tests context retention and conversational flow with follow-up questions
"""
import os
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
7. Halte Antworten prägnant und journalistisch
8. Merke dir den Kontext vorheriger Fragen in der Konversation"""

# 5 conversation scenarios with follow-ups
CONVERSATION_SCENARIOS = [
    {
        "name": "Basic Info Gathering",
        "description": "Standings → Team details → Player stats",
        "turns": [
            "Wer führt die Bundesliga-Tabelle an?",
            "Wie viele Punkte haben sie?",
            "Wer ist ihr bester Torjäger?",
        ]
    },
    {
        "name": "Complex Tactical Discussion",
        "description": "Match analysis → Formation → Player roles",
        "turns": [
            "Gab es interessante Spiele diese Woche?",
            "Welche Taktik hat das Gewinnerteam verwendet?",
            "Welche Spieler waren besonders wichtig?",
        ]
    },
    {
        "name": "Prediction Request",
        "description": "Upcoming match → Head-to-head → Likely outcome",
        "turns": [
            "Welches ist das wichtigste kommende Bundesliga-Spiel?",
            "Wie ist die Bilanz zwischen diesen Teams?",
            "Wer wird deiner Meinung nach gewinnen?",
        ]
    },
    {
        "name": "News Follow-up",
        "description": "Transfer news → Player background → Impact analysis",
        "turns": [
            "Gibt es interessante Transfer-Nachrichten?",
            "Wer ist dieser Spieler?",
            "Wie wird er dem Team helfen?",
        ]
    },
    {
        "name": "Edge Case Handling",
        "description": "Unclear question → Clarification → Refined answer",
        "turns": [
            "Was gibt's Neues?",
            "Ich meine speziell über Bayern München",
            "Und wie sieht es mit Verletzungen aus?",
        ]
    }
]


def query_ksi_with_history(messages: list) -> tuple[str, float]:
    """Query KSI with conversation history"""
    start = time.time()

    # Build full message history with system prompt
    full_messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{data_context}"}
    ] + messages

    response = mistral_client.chat.complete(
        model="mistral-large-latest",
        messages=full_messages,
        max_tokens=1000,
        temperature=0.7
    )

    elapsed = time.time() - start
    return response.choices[0].message.content, elapsed


def evaluate_turn(question: str, response: str, response_time: float, turn_number: int) -> dict:
    """AI evaluates a single turn in the conversation"""

    eval_prompt = f"""Du bist ein kritischer Bewerter von Sportjournalismus.

TURN {turn_number} DER KONVERSATION:
FRAGE: {question}
ANTWORT: {response}
ANTWORTZEIT: {response_time:.2f}s

Bewerte die Antwort auf einer Skala von 1-10 für:
1. **Relevanz** (Beantwortet sie die Frage?)
2. **Kontext** (Bezieht sie sich auf vorherige Turns, wenn relevant?)
3. **Ton** (Professioneller Journalismus-Ton?)
4. **Genauigkeit** (Basiert auf bereitgestellten Daten?)
5. **Nützlichkeit** (Hilfreich für einen Fußballfan?)

Antworte GENAU in diesem Format:
RELEVANZ: X/10
KONTEXT: X/10
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


def evaluate_conversation_coherence(conversation_history: list, turn_results: list) -> dict:
    """Evaluate overall conversation coherence and context retention"""

    # Build conversation transcript
    transcript = ""
    for i, turn in enumerate(turn_results, 1):
        transcript += f"\nTURN {i}:\n"
        transcript += f"Frage: {turn['question']}\n"
        transcript += f"Antwort: {turn['response'][:200]}...\n"

    eval_prompt = f"""Du bist ein Experte für konversationelle KI-Systeme.

KOMPLETTE KONVERSATION:
{transcript}

Bewerte die GESAMTE Konversation auf einer Skala von 1-10 für:
1. **Kohärenz** (Bleiben die Antworten im Kontext der Konversation?)
2. **Kontext-Retention** (Bezieht sich das System auf vorherige Antworten?)
3. **Natürlicher Fluss** (Fühlt sich die Konversation natürlich an?)
4. **Pronomen-Handling** (Versteht das System "sie", "er", "dieser Team" korrekt?)
5. **Progressive Information** (Baut jede Antwort auf vorherigen auf?)

Antworte GENAU in diesem Format:
KOHÄRENZ: X/10
KONTEXT_RETENTION: X/10
NATÜRLICHER_FLUSS: X/10
PRONOMEN_HANDLING: X/10
PROGRESSIVE_INFO: X/10
GESAMT: X/10
KOMMENTAR: [2-3 Sätze über Kontext-Probleme oder Stärken]"""

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


def run_conversation_scenario(scenario: dict) -> dict:
    """Run a single conversation scenario"""

    print(f"\n{'='*80}")
    print(f"SCENARIO: {scenario['name']}")
    print(f"Description: {scenario['description']}")
    print(f"{'='*80}\n")

    # Initialize conversation history
    messages = []
    turn_results = []

    for turn_num, question in enumerate(scenario['turns'], 1):
        print(f"\n[Turn {turn_num}/{len(scenario['turns'])}]")
        print(f"📝 Frage: {question}")

        # Add user message to history
        messages.append({"role": "user", "content": question})

        # Get KSI response
        response, response_time = query_ksi_with_history(messages)

        # Add assistant message to history
        messages.append({"role": "assistant", "content": response})

        print(f"⏱️  Antwortzeit: {response_time:.2f}s")
        print(f"📊 Antwort ({len(response)} chars):")
        print("-" * 80)
        print(response[:300] + "..." if len(response) > 300 else response)
        print("-" * 80)

        # Evaluate turn
        print("🤖 Evaluating turn...")
        evaluation = evaluate_turn(question, response, response_time, turn_num)

        scores = evaluation['scores']
        print(f"\n✅ Bewertung Turn {turn_num}:")
        for key, value in scores.items():
            if key != 'GESAMT':
                print(f"   {key}: {value}/10")
        if 'GESAMT' in scores:
            print(f"   {'='*20}")
            print(f"   GESAMT: {scores['GESAMT']}/10")

        if evaluation['comment']:
            print(f"\n💭 Kommentar: {evaluation['comment']}")

        turn_results.append({
            'turn': turn_num,
            'question': question,
            'response': response,
            'response_time': response_time,
            'evaluation': evaluation
        })

        time.sleep(1)  # Rate limiting between turns

    # Evaluate overall conversation coherence
    print(f"\n🔍 Evaluating conversation coherence...")
    coherence_eval = evaluate_conversation_coherence(messages, turn_results)

    print(f"\n✅ Conversation Coherence:")
    for key, value in coherence_eval['scores'].items():
        if key != 'GESAMT':
            print(f"   {key}: {value}/10")
    if 'GESAMT' in coherence_eval['scores']:
        print(f"   {'='*20}")
        print(f"   GESAMT: {coherence_eval['scores']['GESAMT']}/10")

    if coherence_eval['comment']:
        print(f"\n💭 Kommentar: {coherence_eval['comment']}")

    return {
        'scenario': scenario,
        'turns': turn_results,
        'coherence': coherence_eval
    }


def run_multi_turn_test():
    """Run complete multi-turn conversation test"""

    print("=" * 80)
    print("MULTI-TURN CONVERSATION TEST")
    print("Testing context retention and conversational flow")
    print("=" * 80)
    print(f"Testing with LIVE DATA from Kicker RSS + TheSportsDB")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    all_results = []

    for i, scenario in enumerate(CONVERSATION_SCENARIOS, 1):
        print(f"\n\n{'#'*80}")
        print(f"# SCENARIO {i}/{len(CONVERSATION_SCENARIOS)}")
        print(f"{'#'*80}")

        result = run_conversation_scenario(scenario)
        all_results.append(result)

        time.sleep(3)  # Pause between scenarios

    # Generate summary report
    print("\n\n" + "=" * 80)
    print("ZUSAMMENFASSUNG / SUMMARY")
    print("=" * 80)

    # Average response times
    all_times = []
    for result in all_results:
        for turn in result['turns']:
            all_times.append(turn['response_time'])
    avg_time = sum(all_times) / len(all_times) if all_times else 0
    print(f"\n⏱️  Durchschnittliche Antwortzeit: {avg_time:.2f}s")

    # Average turn scores
    all_turn_scores = {}
    for result in all_results:
        for turn in result['turns']:
            for key, value in turn['evaluation']['scores'].items():
                if key not in all_turn_scores:
                    all_turn_scores[key] = []
                all_turn_scores[key].append(value)

    print(f"\n📊 Durchschnittliche Turn-Bewertungen:")
    for key, values in all_turn_scores.items():
        avg = sum(values) / len(values)
        print(f"   {key}: {avg:.1f}/10")

    # Average coherence scores
    all_coherence_scores = {}
    for result in all_results:
        for key, value in result['coherence']['scores'].items():
            if key not in all_coherence_scores:
                all_coherence_scores[key] = []
            all_coherence_scores[key].append(value)

    print(f"\n🔗 Durchschnittliche Konversations-Kohärenz:")
    for key, values in all_coherence_scores.items():
        avg = sum(values) / len(values)
        print(f"   {key}: {avg:.1f}/10")

    # Context retention issues
    print(f"\n⚠️  Context Retention Issues:")
    issues_found = False
    for i, result in enumerate(all_results, 1):
        coherence_score = result['coherence']['scores'].get('GESAMT', 0)
        if coherence_score < 7:
            print(f"   Scenario {i} ({result['scenario']['name']}): {coherence_score}/10")
            print(f"      Problem: {result['coherence']['comment'][:100]}...")
            issues_found = True

    if not issues_found:
        print(f"   ✅ Keine schwerwiegenden Probleme gefunden")

    # Overall assessment
    avg_turn_overall = sum(all_turn_scores.get('GESAMT', [7])) / len(all_turn_scores.get('GESAMT', [1]))
    avg_coherence_overall = sum(all_coherence_scores.get('GESAMT', [7])) / len(all_coherence_scores.get('GESAMT', [1]))
    overall_score = (avg_turn_overall + avg_coherence_overall) / 2

    print(f"\n🎯 Gesamtbewertung:")
    print(f"   Turn Quality: {avg_turn_overall:.1f}/10")
    print(f"   Conversation Coherence: {avg_coherence_overall:.1f}/10")
    print(f"   Overall: {overall_score:.1f}/10")

    if overall_score >= 8:
        status = "✅ AUSGEZEICHNET - Context handling bereit für Beta"
    elif overall_score >= 7:
        status = "✅ GUT - Kleinere Context-Probleme"
    elif overall_score >= 6:
        status = "⚠️  AKZEPTABEL - Context retention verbesserungsbedürftig"
    else:
        status = "❌ PROBLEME - Context handling muss überarbeitet werden"

    print(f"   Status: {status}")

    print("\n" + "=" * 80)
    print(f"Test abgeschlossen: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    return all_results


if __name__ == "__main__":
    try:
        results = run_multi_turn_test()
    except KeyboardInterrupt:
        print("\n\nTest abgebrochen.")
    except Exception as e:
        print(f"\n\nFehler: {e}")
        import traceback
        traceback.print_exc()
