#!/usr/bin/env python3
"""
KSI (Kicker Sports Intelligence) - Bilingual Demo
Powered by Mistral Large (7.33/10 quality, 3.64s avg response)

A German sports journalism assistant with English translations for testing.
"""

import os
import sys
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
    DIM = '\033[2m'

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

# Example queries with English translations
EXAMPLE_QUERIES = [
    {
        "de": "Welche Bundesliga-Spiele stehen dieses Wochenende an?",
        "en": "Which Bundesliga games are happening this weekend?"
    },
    {
        "de": "Wer führt die Bundesliga-Tabelle an?",
        "en": "Who is leading the Bundesliga table?"
    },
    {
        "de": "Was ist das Ergebnis des letzten Bayern München Spiels?",
        "en": "What is the result of Bayern Munich's last game?"
    },
    {
        "de": "Welches Team hat die beste Offensive in der Bundesliga?",
        "en": "Which team has the best offense in the Bundesliga?"
    },
    {
        "de": "Wie ist die Form von Bayer Leverkusen in den letzten Spielen?",
        "en": "How is Bayer Leverkusen's form in recent games?"
    },
    {
        "de": "Gibt es aktuelle Nachrichten über Bundesliga-Transfers?",
        "en": "Are there any current news about Bundesliga transfers?"
    },
    {
        "de": "Was sind die wichtigsten Sportnachrichten heute?",
        "en": "What are the most important sports news today?"
    },
    {
        "de": "Erkläre mir die aktuelle Champions League Situation deutscher Teams.",
        "en": "Explain to me the current Champions League situation of German teams."
    },
    {
        "de": "Wer sind die Top-Torjäger der Bundesliga?",
        "en": "Who are the top scorers in the Bundesliga?"
    },
    {
        "de": "Wie sieht die Spitzengruppe der Tabelle aus?",
        "en": "What does the top of the table look like?"
    }
]

def print_header(bilingual_mode: bool):
    """Print KSI demo header"""
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  KSI - Kicker Sports Intelligence Demo{Colors.RESET}")
    if bilingual_mode:
        print(f"{Colors.YELLOW}  [BILINGUAL MODE: German + English translations]{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.GREEN}  Powered by: Mistral Large{Colors.RESET}")
    print(f"{Colors.YELLOW}  Quality: 7.33/10 | Speed: ~3.6s avg{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_examples(bilingual_mode: bool):
    """Print example queries"""
    print(f"{Colors.CYAN}Example Questions (type the number):{Colors.RESET}\n")
    for i, query in enumerate(EXAMPLE_QUERIES, 1):
        if bilingual_mode:
            print(f"{Colors.MAGENTA}[{i}]{Colors.RESET} {query['en']}")
            print(f"    {Colors.DIM}(DE: {query['de']}){Colors.RESET}")
        else:
            print(f"{Colors.MAGENTA}[{i}]{Colors.RESET} {query['de']}")

    print(f"\n{Colors.YELLOW}Or type your own question in German.{Colors.RESET}")
    print(f"{Colors.YELLOW}Type 'examples' to see this list again.{Colors.RESET}")
    print(f"{Colors.YELLOW}Type 'quit' to exit.{Colors.RESET}\n")

def translate_to_english(german_text: str) -> str:
    """
    Translate German response to English using Mistral

    Args:
        german_text: German text to translate

    Returns:
        English translation
    """
    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator. Translate the following German sports journalism text to English. Maintain the professional journalism tone and formatting."
                },
                {
                    "role": "user",
                    "content": german_text
                }
            ],
            max_tokens=2000,
            temperature=0.3  # Lower temperature for more accurate translation
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"[Translation error: {str(e)}]"

def query_ksi(user_question: str, bilingual_mode: bool = False) -> tuple[str, str, float]:
    """
    Query KSI with Mistral Large

    Args:
        user_question: German question to ask
        bilingual_mode: If True, also translate response to English

    Returns:
        tuple: (german_response, english_translation, response_time_seconds)
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
        german_response = response.choices[0].message.content

        # Optionally translate to English
        english_translation = ""
        if bilingual_mode:
            english_translation = translate_to_english(german_response)

        return german_response, english_translation, elapsed

    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Fehler bei der Anfrage: {str(e)}"
        return error_msg, "", elapsed

def main():
    """Main demo loop"""
    # Check for bilingual mode flag
    bilingual_mode = "--bilingual" in sys.argv or "-b" in sys.argv

    print_header(bilingual_mode)
    print_examples(bilingual_mode)

    while True:
        # Get user input
        user_input = input(f"{Colors.BOLD}{Colors.GREEN}KSI>{Colors.RESET} ").strip()

        if not user_input:
            continue

        # Handle commands
        if user_input.lower() in ['quit', 'exit', 'q']:
            print(f"\n{Colors.CYAN}Auf Wiedersehen! (Goodbye!){Colors.RESET}\n")
            break

        if user_input.lower() in ['beispiele', 'examples', 'help']:
            print()
            print_examples(bilingual_mode)
            continue

        # Handle numbered examples
        if user_input.isdigit():
            query_num = int(user_input)
            if 1 <= query_num <= len(EXAMPLE_QUERIES):
                query = EXAMPLE_QUERIES[query_num - 1]
                user_question = query['de']

                if bilingual_mode:
                    print(f"{Colors.CYAN}Question:{Colors.RESET} {query['en']}")
                    print(f"{Colors.DIM}(German: {query['de']}){Colors.RESET}\n")
                else:
                    print(f"{Colors.CYAN}Frage:{Colors.RESET} {user_question}\n")
            else:
                print(f"{Colors.RED}Invalid number. Choose 1-{len(EXAMPLE_QUERIES)}.{Colors.RESET}\n")
                continue
        else:
            user_question = user_input

        # Query KSI
        print(f"{Colors.YELLOW}Analyzing...{Colors.RESET}")
        german_response, english_translation, elapsed = query_ksi(user_question, bilingual_mode)

        # Display German response
        print(f"\n{Colors.BLUE}{'─'*80}{Colors.RESET}")
        print(f"{Colors.BOLD}German Response:{Colors.RESET} ({elapsed:.2f}s)\n")
        print(german_response)

        # Display English translation if in bilingual mode
        if bilingual_mode and english_translation:
            print(f"\n{Colors.BLUE}{'─'*80}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.CYAN}English Translation:{Colors.RESET}\n")
            print(english_translation)

        print(f"{Colors.BLUE}{'─'*80}{Colors.RESET}\n")

if __name__ == "__main__":
    # Display usage help if requested
    if "--help" in sys.argv or "-h" in sys.argv:
        print(f"""
{Colors.BOLD}KSI Bilingual Demo{Colors.RESET}

Usage:
  python ksi_demo_bilingual.py                 # German-only mode
  python ksi_demo_bilingual.py --bilingual     # German + English translations
  python ksi_demo_bilingual.py -b              # Short form

Flags:
  --bilingual, -b    Enable English translations of responses
  --help, -h         Show this help message

For testing without German knowledge, use --bilingual flag.
        """)
        sys.exit(0)

    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}Auf Wiedersehen! (Goodbye!){Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Fehler (Error): {str(e)}{Colors.RESET}\n")
