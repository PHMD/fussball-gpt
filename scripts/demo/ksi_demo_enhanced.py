#!/usr/bin/env python3
"""
KSI (Kicker Sports Intelligence) - Enhanced Demo with Model Switching
Powered by Mistral Large (7.33/10 quality, 3.64s avg response)

A German sports journalism assistant with slash commands for testing.
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from mistralai import Mistral
from openai import OpenAI
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Initialize API clients
mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY")) if os.getenv("MISTRAL_API_KEY") else None
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) if os.getenv("ANTHROPIC_API_KEY") else None

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

# Available models with benchmark data
AVAILABLE_MODELS = {
    # Mistral models
    "mistral-large": {
        "name": "Mistral Large",
        "provider": "mistral",
        "model_id": "mistral-large-latest",
        "quality": 7.33,
        "speed": 3.64,
        "available": mistral_client is not None
    },
    "mistral-small": {
        "name": "Mistral Small",
        "provider": "mistral",
        "model_id": "mistral-small-latest",
        "quality": 6.79,
        "speed": 2.67,
        "available": mistral_client is not None
    },
    # OpenAI models
    "gpt-5": {
        "name": "GPT-5",
        "provider": "openai",
        "model_id": "gpt-5",
        "quality": 7.25,
        "speed": 13.17,
        "available": openai_client is not None
    },
    "gpt-5-mini": {
        "name": "GPT-5 Mini",
        "provider": "openai",
        "model_id": "gpt-5-mini",
        "quality": 7.44,
        "speed": 11.17,
        "available": openai_client is not None
    },
    "gpt-5-chat": {
        "name": "GPT-5 Chat",
        "provider": "openai",
        "model_id": "gpt-5-chat-latest",
        "quality": 7.18,
        "speed": 4.02,
        "available": openai_client is not None
    },
    "gpt-5-nano": {
        "name": "GPT-5 Nano",
        "provider": "openai",
        "model_id": "gpt-5-nano",
        "quality": 6.39,
        "speed": 14.10,
        "available": openai_client is not None,
        "warning": "⚠️  Known to fail on complex queries"
    },
    # Anthropic models
    "claude-sonnet": {
        "name": "Claude Sonnet 4.5",
        "provider": "anthropic",
        "model_id": "claude-sonnet-4.5-20250514",
        "quality": 7.22,
        "speed": 7.33,
        "available": anthropic_client is not None
    },
    "claude-haiku": {
        "name": "Claude Haiku 3.5",
        "provider": "anthropic",
        "model_id": "claude-3-5-haiku-20241022",
        "quality": 6.87,
        "speed": 3.42,
        "available": anthropic_client is not None
    }
}

# Session state
class SessionState:
    def __init__(self):
        self.current_model = "mistral-large"
        self.bilingual_mode = "--bilingual" in sys.argv or "-b" in sys.argv
        self.output_language = "de"  # de = German (default), en = English
        self.query_count = 0
        self.total_response_time = 0.0
        self.responses = []

session = SessionState()

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

SYSTEM_PROMPT_DE = """Du bist KSI (Kicker Sports Intelligence), ein deutscher Sportjournalismus-Assistent und Experte für Fußball.

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

SYSTEM_PROMPT_EN = """You are KSI (Kicker Sports Intelligence), a sports journalism assistant and football expert.

Your expertise includes:
- German Bundesliga and 2. Bundesliga
- European competitions (Champions League, Europa League)
- International sports news

When answering questions:
1. Base your answers on the provided current data
2. Be precise with dates, results, and player names
3. If information is not in the data, state that clearly
4. Provide context and analysis, not just raw facts
5. Use a professional but friendly tone (sports journalism standard)
6. Always respond in English
7. Keep answers concise and journalistic (no meta-explanations)"""

def get_system_prompt():
    """Get system prompt in current language"""
    return SYSTEM_PROMPT_DE if session.output_language == "de" else SYSTEM_PROMPT_EN

# Example queries with English translations
EXAMPLE_QUERIES = [
    {"de": "Welche Bundesliga-Spiele stehen dieses Wochenende an?", "en": "Which Bundesliga games are happening this weekend?"},
    {"de": "Wer führt die Bundesliga-Tabelle an?", "en": "Who is leading the Bundesliga table?"},
    {"de": "Was ist das Ergebnis des letzten Bayern München Spiels?", "en": "What is the result of Bayern Munich's last game?"},
    {"de": "Welches Team hat die beste Offensive in der Bundesliga?", "en": "Which team has the best offense in the Bundesliga?"},
    {"de": "Wie ist die Form von Bayer Leverkusen in den letzten Spielen?", "en": "How is Bayer Leverkusen's form in recent games?"},
    {"de": "Gibt es aktuelle Nachrichten über Bundesliga-Transfers?", "en": "Are there any current news about Bundesliga transfers?"},
    {"de": "Was sind die wichtigsten Sportnachrichten heute?", "en": "What are the most important sports news today?"},
    {"de": "Erkläre mir die aktuelle Champions League Situation deutscher Teams.", "en": "Explain to me the current Champions League situation of German teams."},
    {"de": "Wer sind die Top-Torjäger der Bundesliga?", "en": "Who are the top scorers in the Bundesliga?"},
    {"de": "Wie sieht die Spitzengruppe der Tabelle aus?", "en": "What does the top of the table look like?"}
]

def print_header():
    """Print KSI demo header"""
    model_info = AVAILABLE_MODELS[session.current_model]
    lang_flag = "🇩🇪 German" if session.output_language == "de" else "🇬🇧 English"

    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  KSI - Kicker Sports Intelligence Demo{Colors.RESET}")
    if session.bilingual_mode:
        print(f"{Colors.YELLOW}  [BILINGUAL MODE: German + English translations]{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.GREEN}  Model: {model_info['name']} | Language: {lang_flag}{Colors.RESET}")
    print(f"{Colors.YELLOW}  Benchmark: {model_info['quality']}/10 quality | {model_info['speed']}s avg speed{Colors.RESET}")
    if model_info.get('warning'):
        print(f"{Colors.RED}  {model_info['warning']}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_examples():
    """Print example queries"""
    print(f"{Colors.CYAN}Example Questions (type the number):{Colors.RESET}\n")
    for i, query in enumerate(EXAMPLE_QUERIES, 1):
        if session.bilingual_mode:
            print(f"{Colors.MAGENTA}[{i}]{Colors.RESET} {query['en']}")
            print(f"    {Colors.DIM}(DE: {query['de']}){Colors.RESET}")
        else:
            print(f"{Colors.MAGENTA}[{i}]{Colors.RESET} {query['de']}")

    print(f"\n{Colors.CYAN}Commands:{Colors.RESET}")
    print(f"  {Colors.MAGENTA}/model <name>{Colors.RESET}     - Switch model (e.g., /model gpt-5-mini)")
    print(f"  {Colors.MAGENTA}/models{Colors.RESET}           - List available models")
    print(f"  {Colors.MAGENTA}/language <de|en>{Colors.RESET} - Switch output language (de=German, en=English)")
    print(f"  {Colors.MAGENTA}/stats{Colors.RESET}            - Show session statistics")
    print(f"  {Colors.MAGENTA}/translate{Colors.RESET}        - Toggle translation on/off")
    print(f"  {Colors.MAGENTA}/benchmark{Colors.RESET}        - Show benchmark comparison")
    print(f"  {Colors.MAGENTA}/clear{Colors.RESET}            - Clear screen")
    print(f"  {Colors.MAGENTA}/help{Colors.RESET}             - Show this help")
    print(f"  {Colors.MAGENTA}/quit{Colors.RESET}             - Exit demo\n")

def query_llm(user_question: str, model_key: str) -> tuple[str, float]:
    """
    Query the specified LLM model

    Args:
        user_question: Question to ask
        model_key: Key from AVAILABLE_MODELS

    Returns:
        tuple: (response_text, response_time_seconds)
    """
    model_config = AVAILABLE_MODELS[model_key]
    provider = model_config['provider']
    model_id = model_config['model_id']

    start_time = time.time()

    system_prompt = get_system_prompt()

    try:
        if provider == "mistral":
            response = mistral_client.chat.complete(
                model=model_id,
                messages=[
                    {"role": "system", "content": f"{system_prompt}\n\n{BUNDESLIGA_DATA}"},
                    {"role": "user", "content": user_question}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            response_text = response.choices[0].message.content

        elif provider == "openai":
            response = openai_client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": f"{system_prompt}\n\n{BUNDESLIGA_DATA}"},
                    {"role": "user", "content": user_question}
                ],
                max_completion_tokens=2000,
                temperature=0.7
            )
            response_text = response.choices[0].message.content

        elif provider == "anthropic":
            response = anthropic_client.messages.create(
                model=model_id,
                max_tokens=2000,
                temperature=0.7,
                system=f"{system_prompt}\n\n{BUNDESLIGA_DATA}",
                messages=[
                    {"role": "user", "content": user_question}
                ]
            )
            response_text = response.content[0].text

        else:
            return f"Unknown provider: {provider}", 0.0

        elapsed = time.time() - start_time
        return response_text, elapsed

    except Exception as e:
        elapsed = time.time() - start_time
        return f"Error: {str(e)}", elapsed

def translate_to_english(german_text: str) -> str:
    """Translate German response to English using current model"""
    model_config = AVAILABLE_MODELS[session.current_model]
    provider = model_config['provider']

    try:
        if provider == "mistral":
            response = mistral_client.chat.complete(
                model=model_config['model_id'],
                messages=[
                    {"role": "system", "content": "You are a professional translator. Translate the following German sports journalism text to English. Maintain the professional journalism tone and formatting."},
                    {"role": "user", "content": german_text}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            return response.choices[0].message.content

        elif provider == "openai":
            response = openai_client.chat.completions.create(
                model=model_config['model_id'],
                messages=[
                    {"role": "system", "content": "You are a professional translator. Translate the following German sports journalism text to English. Maintain the professional journalism tone and formatting."},
                    {"role": "user", "content": german_text}
                ],
                max_completion_tokens=2000,
                temperature=0.3
            )
            return response.choices[0].message.content

        elif provider == "anthropic":
            response = anthropic_client.messages.create(
                model=model_config['model_id'],
                max_tokens=2000,
                temperature=0.3,
                system="You are a professional translator. Translate the following German sports journalism text to English. Maintain the professional journalism tone and formatting.",
                messages=[
                    {"role": "user", "content": german_text}
                ]
            )
            return response.content[0].text

    except Exception as e:
        return f"[Translation error: {str(e)}]"

def handle_command(command: str) -> bool:
    """Handle slash commands. Returns True if should continue, False if should exit."""

    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else None

    # /model <name>
    if cmd == "/model":
        if not arg:
            print(f"{Colors.RED}Usage: /model <model-name>{Colors.RESET}")
            print(f"Use /models to see available models\n")
            return True

        model_key = arg.lower()
        if model_key not in AVAILABLE_MODELS:
            print(f"{Colors.RED}Unknown model: {arg}{Colors.RESET}")
            print(f"Use /models to see available models\n")
            return True

        if not AVAILABLE_MODELS[model_key]['available']:
            print(f"{Colors.RED}Model {arg} not available (missing API key){Colors.RESET}\n")
            return True

        session.current_model = model_key
        print(f"{Colors.GREEN}Switched to {AVAILABLE_MODELS[model_key]['name']}{Colors.RESET}\n")
        print_header()
        return True

    # /models
    elif cmd == "/models":
        print(f"\n{Colors.CYAN}Available Models:{Colors.RESET}\n")
        for key, model in sorted(AVAILABLE_MODELS.items(), key=lambda x: x[1]['quality'], reverse=True):
            status = "✅" if model['available'] else "❌"
            current = "⭐ " if key == session.current_model else "   "
            warning = f" {model.get('warning', '')}" if model.get('warning') else ""
            print(f"{current}{status} {Colors.BOLD}{key.ljust(20)}{Colors.RESET} {model['name'].ljust(25)} "
                  f"{Colors.YELLOW}{model['quality']}/10{Colors.RESET} @ {Colors.CYAN}{model['speed']}s{Colors.RESET}{warning}")
        print()
        return True

    # /language <de|en>
    elif cmd == "/language":
        if not arg:
            print(f"{Colors.RED}Usage: /language <de|en>{Colors.RESET}")
            print(f"  de = German output (default)")
            print(f"  en = English output\n")
            return True

        lang = arg.lower()
        if lang not in ['de', 'en']:
            print(f"{Colors.RED}Invalid language: {arg}. Use 'de' or 'en'{Colors.RESET}\n")
            return True

        session.output_language = lang
        lang_name = "German" if lang == "de" else "English"
        print(f"{Colors.GREEN}Output language switched to {lang_name}{Colors.RESET}\n")
        print_header()
        return True

    # /stats
    elif cmd == "/stats":
        avg_speed = session.total_response_time / session.query_count if session.query_count > 0 else 0
        lang_name = "German" if session.output_language == "de" else "English"
        print(f"\n{Colors.CYAN}Session Statistics:{Colors.RESET}\n")
        print(f"  Queries: {session.query_count}")
        print(f"  Average Response Time: {avg_speed:.2f}s")
        print(f"  Total Time: {session.total_response_time:.2f}s")
        print(f"  Current Model: {AVAILABLE_MODELS[session.current_model]['name']}")
        print(f"  Output Language: {lang_name}")
        print(f"  Bilingual Mode: {'On' if session.bilingual_mode else 'Off'}\n")
        return True

    # /translate
    elif cmd == "/translate":
        session.bilingual_mode = not session.bilingual_mode
        status = "enabled" if session.bilingual_mode else "disabled"
        print(f"{Colors.GREEN}Translation {status}{Colors.RESET}\n")
        return True

    # /benchmark
    elif cmd == "/benchmark":
        print(f"\n{Colors.CYAN}Benchmark Results (8-Model Comparison):{Colors.RESET}\n")
        print(f"{'Model'.ljust(25)} {'Quality'.ljust(12)} {'Speed'.ljust(10)} Status")
        print("─" * 70)
        for key, model in sorted(AVAILABLE_MODELS.items(), key=lambda x: x[1]['quality'], reverse=True):
            quality_bar = "█" * int(model['quality']) + "░" * (10 - int(model['quality']))
            status = "✅" if model['available'] else "❌ Missing API key"
            print(f"{model['name'].ljust(25)} {quality_bar} {model['quality']}/10  {str(model['speed']) + 's'.ljust(8)} {status}")
        print("\nRecommendation: Mistral Large (best balance of quality & speed)")
        print("See FINAL_LLM_BENCHMARK_REPORT.md for full details\n")
        return True

    # /clear
    elif cmd == "/clear":
        os.system('clear' if os.name != 'nt' else 'cls')
        print_header()
        return True

    # /help
    elif cmd == "/help":
        print_examples()
        return True

    # /quit
    elif cmd == "/quit":
        return False

    else:
        print(f"{Colors.RED}Unknown command: {cmd}{Colors.RESET}")
        print(f"Type /help to see available commands\n")
        return True

def main():
    """Main demo loop"""
    print_header()
    print_examples()

    # Check if any API keys are available
    if not any(AVAILABLE_MODELS[m]['available'] for m in AVAILABLE_MODELS):
        print(f"{Colors.RED}ERROR: No API keys found!{Colors.RESET}")
        print(f"Please set at least one of: MISTRAL_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY\n")
        return

    # Set default model to first available
    if not AVAILABLE_MODELS[session.current_model]['available']:
        for key, model in AVAILABLE_MODELS.items():
            if model['available']:
                session.current_model = key
                print(f"{Colors.YELLOW}Default model unavailable, using {model['name']}{Colors.RESET}\n")
                break

    while True:
        # Get user input
        user_input = input(f"{Colors.BOLD}{Colors.GREEN}KSI>{Colors.RESET} ").strip()

        if not user_input:
            continue

        # Handle slash commands
        if user_input.startswith('/'):
            if not handle_command(user_input):
                print(f"\n{Colors.CYAN}Auf Wiedersehen! (Goodbye!){Colors.RESET}\n")
                break
            continue

        # Handle quit keywords
        if user_input.lower() in ['quit', 'exit', 'q']:
            print(f"\n{Colors.CYAN}Auf Wiedersehen! (Goodbye!){Colors.RESET}\n")
            break

        # Handle examples keyword
        if user_input.lower() in ['beispiele', 'examples', 'help']:
            print()
            print_examples()
            continue

        # Handle numbered examples
        if user_input.isdigit():
            query_num = int(user_input)
            if 1 <= query_num <= len(EXAMPLE_QUERIES):
                query = EXAMPLE_QUERIES[query_num - 1]
                user_question = query['de']

                if session.bilingual_mode:
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
        model_name = AVAILABLE_MODELS[session.current_model]['name']
        print(f"{Colors.YELLOW}Querying {model_name}...{Colors.RESET}")

        response, elapsed = query_llm(user_question, session.current_model)

        # Update stats
        session.query_count += 1
        session.total_response_time += elapsed

        # Display response with appropriate language label
        response_lang = "German" if session.output_language == "de" else "English"
        print(f"\n{Colors.BLUE}{'─'*80}{Colors.RESET}")
        print(f"{Colors.BOLD}{response_lang} Response:{Colors.RESET} ({elapsed:.2f}s)\n")
        print(response)

        # Display translation if in bilingual mode (only translate German to English)
        if session.bilingual_mode and session.output_language == "de" and not response.startswith("Error"):
            print(f"\n{Colors.YELLOW}Translating to English...{Colors.RESET}")
            english_translation = translate_to_english(response)
            print(f"\n{Colors.BLUE}{'─'*80}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.CYAN}English Translation:{Colors.RESET}\n")
            print(english_translation)

        print(f"{Colors.BLUE}{'─'*80}{Colors.RESET}\n")

if __name__ == "__main__":
    # Display usage help if requested
    if "--help" in sys.argv or "-h" in sys.argv:
        print(f"""
{Colors.BOLD}KSI Enhanced Demo with Model Switching{Colors.RESET}

Usage:
  python ksi_demo_enhanced.py                 # German-only mode
  python ksi_demo_enhanced.py --bilingual     # German + English translations
  python ksi_demo_enhanced.py -b              # Short form

Flags:
  --bilingual, -b    Enable English translations of responses
  --help, -h         Show this help message

Commands (during session):
  /model <name>      Switch LLM model (e.g., /model gpt-5-mini)
  /models            List all available models with benchmarks
  /language <de|en>  Switch output language (de=German, en=English)
  /stats             Show session statistics
  /translate         Toggle translation on/off
  /benchmark         Show benchmark comparison
  /clear             Clear screen
  /help              Show help
  /quit              Exit

Examples:
  /language en       # Switch to English responses
  /language de       # Switch back to German responses (default)
  /translate         # Toggle translation mode

For testing without German knowledge, use --bilingual flag or /language en.
        """)
        sys.exit(0)

    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}Auf Wiedersehen! (Goodbye!){Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.RESET}\n")
