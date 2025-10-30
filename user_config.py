"""User configuration and preference management."""
import json
from pathlib import Path
from enum import Enum
from pydantic import BaseModel


class DetailLevel(str, Enum):
    """Response detail level preferences."""
    QUICK = "quick"
    BALANCED = "balanced"
    DETAILED = "detailed"


class Language(str, Enum):
    """Supported languages."""
    GERMAN = "de"
    ENGLISH = "en"


class Persona(str, Enum):
    """User persona types with different content preferences."""
    CASUAL_FAN = "casual_fan"  # Quick highlights, simple presentation
    EXPERT_ANALYST = "expert_analyst"  # Tactical depth, analysis prioritized
    BETTING_ENTHUSIAST = "betting_enthusiast"  # Stats, odds, form data
    FANTASY_PLAYER = "fantasy_player"  # Player stats, performance data


class UserProfile(BaseModel):
    """User preferences and profile."""
    detail_level: DetailLevel = DetailLevel.BALANCED
    language: Language = Language.GERMAN
    name: str = "User"
    persona: Persona = Persona.CASUAL_FAN

    # Personalization
    favorite_team: str = ""
    interests: list[str] = []  # ["tactics", "transfers", "stats", etc.]

    class Config:
        use_enum_values = True


class UserConfigManager:
    """Manages user configuration persistence."""

    def __init__(self, config_path: str = ".fussballgpt_config.json"):
        self.config_path = Path(config_path)
        self.profile = self.load_profile()

    def load_profile(self) -> UserProfile:
        """Load user profile from config file."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                    return UserProfile(**data)
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
                return UserProfile()
        return UserProfile()

    def save_profile(self):
        """Save user profile to config file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.profile.dict(), f, indent=2)

    def update_detail_level(self, level: DetailLevel):
        """Update and save detail level preference."""
        self.profile.detail_level = level
        self.save_profile()

    def update_language(self, language: Language):
        """Update and save language preference."""
        self.profile.language = language
        self.save_profile()

    def update_persona(self, persona: Persona):
        """Update and save persona preference."""
        self.profile.persona = persona
        self.save_profile()

    def get_system_prompt_modifier(self) -> str:
        """Get system prompt modifier based on preferences."""

        # Detail level modifiers by language
        if self.profile.language == Language.GERMAN:
            detail_modifiers = {
                DetailLevel.QUICK: """
WICHTIG: Dieser Nutzer bevorzugt KURZE Antworten.
- Maximal 2-3 Sätze
- Nur die wichtigsten Highlights
- Keine taktischen Details
- Einfache Sprache
- Direkte Antworten ohne Kontext
Beispiel: "Bayern führt die Tabelle mit 82 Punkten an, 13 Punkte vor Leverkusen."
""",
                DetailLevel.BALANCED: """
WICHTIG: Dieser Nutzer bevorzugt AUSGEWOGENE Antworten.
- 2-3 Absätze
- Wichtige Fakten + etwas Kontext
- Gelegentliche taktische Einblicke
- Professioneller Ton
- Journalistischer Stil (aktuelles Verhalten)
""",
                DetailLevel.DETAILED: """
WICHTIG: Dieser Nutzer bevorzugt DETAILLIERTE Antworten.
- Umfassende Analysen
- Taktische Tiefe (Formationen, Systeme, Strategien)
- Statistische Belege
- Fachterminologie erwünscht
- Vergleiche und historischer Kontext
- 3-5 Absätze oder mehr bei Bedarf
"""
            }
        else:  # English
            detail_modifiers = {
                DetailLevel.QUICK: """
IMPORTANT: This user prefers SHORT answers.
- Maximum 2-3 sentences
- Only the most important highlights
- No tactical details
- Simple language
- Direct answers without context
Example: "Bayern leads the table with 82 points, 13 ahead of Leverkusen."
""",
                DetailLevel.BALANCED: """
IMPORTANT: This user prefers BALANCED answers.
- 2-3 paragraphs
- Key facts + some context
- Occasional tactical insights
- Professional tone
- Journalism style (current behavior)
""",
                DetailLevel.DETAILED: """
IMPORTANT: This user prefers DETAILED answers.
- Comprehensive analysis
- Tactical depth (formations, systems, strategies)
- Statistical evidence
- Technical terminology welcome
- Comparisons and historical context
- 3-5 paragraphs or more as needed
"""
            }

        return detail_modifiers.get(self.profile.detail_level, detail_modifiers[DetailLevel.BALANCED])

    def get_base_system_prompt(self) -> str:
        """Get base system prompt in user's preferred language."""

        if self.profile.language == Language.GERMAN:
            return """Du bist Fußball GPT, ein KI-Assistent für deutschen Fußball.

Dein Fachwissen umfasst:
- Deutsche Bundesliga und 2. Bundesliga
- Europäische Wettbewerbe (Champions League, Europa League)
- Spielanalysen und Spielerstatistiken
- Anstehende Spiele und Spielpläne

Du hast Zugriff auf aktuelle Sportdaten. Bei Antworten:
1. Basiere Antworten auf den bereitgestellten Daten
2. Sei spezifisch mit Daten, Ergebnissen und Spielernamen
3. Wenn Informationen nicht verfügbar sind, sage das klar
4. Biete Kontext und Analyse, nicht nur rohe Fakten
5. Verwende einen professionellen aber freundlichen Ton

Antworte immer auf Deutsch."""

        else:  # English
            return """You are Fußball GPT, an AI assistant for German football.

Your expertise includes:
- German Bundesliga and 2. Bundesliga
- European competitions (Champions League, Europa League)
- Match analysis and player statistics
- Upcoming fixtures and schedules

You have access to real-time sports data. When answering:
1. Base answers on the provided data
2. Be specific with dates, scores, and player names
3. If information isn't available, clearly state that
4. Provide context and analysis, not just raw facts
5. Use a professional but friendly tone

Always respond in English."""
