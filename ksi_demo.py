#!/usr/bin/env python3
"""
KSI (Kicker Sports Intelligence) - Demo
Powered by Mistral Large (7.33/10 quality, 3.64s avg response)

A German sports journalism assistant for Bundesliga and international football.
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv
from mistralai import Mistral

# Load environment variables
load_dotenv()

# Initialize Mistral client
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# ANSI colors for better CLI experience
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Current Bundesliga data (example - would be live in production)
BUNDESLIGA_DATA = """
=== AKTUELLE BUNDESLIGA DATEN (Saison 2024/25) ===

TABELLE (Stand: 22.10.2025):
1. Bayer Leverkusen - 25 Punkte (9 Spiele)
2. Bayern München - 23 Punkte (9 Spiele)
3. RB Leipzig - 20 Punkte (9 Spiele)
4. VfB Stuttgart - 18 Punkte (9 Spiele)
5. Borussia Dortmund - 16 Punkte (9 Spiele)

LETZTER SPIELTAG (Spieltag 9):
- Bayer Leverkusen 2:1 VfB Stuttgart
- Bayern München 3:0 Borussia Dortmund
- RB Leipzig 1:1 Eintracht Frankfurt
- SC Freiburg 2:2 FC Augsburg
- VfL Wolfsburg 0:1 Werder Bremen

NÄCHSTER SPIELTAG (Spieltag 10, dieses Wochenende):
Freitag, 20:30 - Borussia Dortmund vs. FC St. Pauli
Samstag, 15:30 - Bayern München vs. Union Berlin
Samstag, 15:30 - VfB Stuttgart vs. Holstein Kiel
Samstag, 18:30 - Bayer Leverkusen vs. Eintracht Frankfurt
Sonntag, 15:30 - RB Leipzig vs. SC Freiburg
Sonntag, 17:30 - VfL Wolfsburg vs. FC Augsburg

TORJÄGER:
1. Harry Kane (Bayern) - 11 Tore
2. Victor Boniface (Leverkusen) - 8 Tore
3. Serhou Guirassy (Dortmund) - 7 Tore

AKTUELLE TRANSFERS:
- Bayer Leverkusen verpflichtet Martin Terrier (Rennes) für 20 Mio. €
- Bayern München im Gespräch mit Jamal Musiala über Vertragsverlängerung
- Borussia Dortmund sucht Verstärkung für die Defensive

CHAMPIONS LEAGUE:
- Bayern München: Gruppenerster, 10 Punkte
- Borussia Dortmund: Gruppendritter, 6 Punkte
- RB Leipzig: Gruppenzweiter, 8 Punkte
- Bayer Leverkusen: Gruppenzweiter, 7 Punkte
"""

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
7. Halte Antworten prägnant und journalistisch (keine Meta-Erklärungen)"""

# Example queries that work well (from benchmark testing)
EXAMPLE_QUERIES = [
    "Welche Bundesliga-Spiele stehen dieses Wochenende an?",
    "Wer führt die Bundesliga-Tabelle an?",
    "Was ist das Ergebnis des letzten Bayern München Spiels?",
    "Welches Team hat die beste Offensive in der Bundesliga?",
    "Wie ist die Form von Bayer Leverkusen in den letzten Spielen?",
    "Gibt es aktuelle Nachrichten über Bundesliga-Transfers?",
    "Was sind die wichtigsten Sportnachrichten heute?",
    "Erkläre mir die aktuelle Champions League Situation deutscher Teams.",
    "Wer sind die Top-Torjäger der Bundesliga?",
    "Wie sieht die Spitzengruppe der Tabelle aus?"
]

def print_header():
    """Print KSI demo header"""
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  KSI - Kicker Sports Intelligence Demo{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.GREEN}  Powered by: Mistral Large{Colors.RESET}")
    print(f"{Colors.YELLOW}  Quality: 7.33/10 | Speed: ~3.6s avg{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_examples():
    """Print example queries"""
    print(f"{Colors.CYAN}Beispiel-Fragen (tippe die Nummer ein):{Colors.RESET}\n")
    for i, query in enumerate(EXAMPLE_QUERIES, 1):
        print(f"{Colors.MAGENTA}[{i}]{Colors.RESET} {query}")
    print(f"\n{Colors.YELLOW}Oder stelle eine eigene Frage auf Deutsch.{Colors.RESET}")
    print(f"{Colors.YELLOW}Tippe 'beispiele' um diese Liste erneut zu sehen.{Colors.RESET}")
    print(f"{Colors.YELLOW}Tippe 'quit' zum Beenden.{Colors.RESET}\n")

def query_ksi(user_question: str) -> tuple[str, float]:
    """
    Query KSI with Mistral Large

    Returns:
        tuple: (response_text, response_time_seconds)
    """
    # Construct messages
    messages = [
        {
            "role": "system",
            "content": f"{SYSTEM_PROMPT}\n\n{BUNDESLIGA_DATA}"
        },
        {
            "role": "user",
            "content": user_question
        }
    ]

    # Query Mistral Large
    start_time = time.time()

    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )

        elapsed = time.time() - start_time
        response_text = response.choices[0].message.content

        return response_text, elapsed

    except Exception as e:
        elapsed = time.time() - start_time
        return f"Fehler bei der Anfrage: {str(e)}", elapsed

def main():
    """Main demo loop"""
    print_header()
    print_examples()

    while True:
        # Get user input
        user_input = input(f"{Colors.BOLD}{Colors.GREEN}KSI>{Colors.RESET} ").strip()

        if not user_input:
            continue

        # Handle commands
        if user_input.lower() in ['quit', 'exit', 'q']:
            print(f"\n{Colors.CYAN}Auf Wiedersehen!{Colors.RESET}\n")
            break

        if user_input.lower() in ['beispiele', 'examples', 'help']:
            print()
            print_examples()
            continue

        # Handle numbered examples
        if user_input.isdigit():
            query_num = int(user_input)
            if 1 <= query_num <= len(EXAMPLE_QUERIES):
                user_question = EXAMPLE_QUERIES[query_num - 1]
                print(f"{Colors.CYAN}Frage:{Colors.RESET} {user_question}\n")
            else:
                print(f"{Colors.RED}Ungültige Nummer. Wähle 1-{len(EXAMPLE_QUERIES)}.{Colors.RESET}\n")
                continue
        else:
            user_question = user_input

        # Query KSI
        print(f"{Colors.YELLOW}Analysiere...{Colors.RESET}")
        response, elapsed = query_ksi(user_question)

        # Display response
        print(f"\n{Colors.BLUE}{'─'*80}{Colors.RESET}")
        print(f"{Colors.BOLD}Antwort:{Colors.RESET} ({elapsed:.2f}s)\n")
        print(response)
        print(f"{Colors.BLUE}{'─'*80}{Colors.RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}Auf Wiedersehen!{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Fehler: {str(e)}{Colors.RESET}\n")
