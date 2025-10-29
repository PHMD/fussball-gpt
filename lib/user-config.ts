/**
 * User configuration and preference management
 *
 * Port from Python user_config.py with TypeScript/React patterns
 */

/**
 * Supported languages
 */
export enum Language {
  GERMAN = 'de',
  ENGLISH = 'en',
}

/**
 * Response detail level preferences
 */
export enum DetailLevel {
  QUICK = 'quick',
  BALANCED = 'balanced',
  DETAILED = 'detailed',
}

/**
 * User persona types with different content preferences
 */
export enum Persona {
  CASUAL_FAN = 'casual_fan',
  EXPERT_ANALYST = 'expert_analyst',
  BETTING_ENTHUSIAST = 'betting_enthusiast',
  FANTASY_PLAYER = 'fantasy_player',
}

/**
 * User preferences and profile
 */
export interface UserProfile {
  language: Language;
  detailLevel: DetailLevel;
  persona: Persona;
  name?: string;
  favoriteTeam?: string;
  interests?: string[];
}

/**
 * Default user profile (German, balanced, casual fan)
 */
export const DEFAULT_PROFILE: UserProfile = {
  language: Language.GERMAN,
  detailLevel: DetailLevel.BALANCED,
  persona: Persona.CASUAL_FAN,
  interests: [],
};

/**
 * LocalStorage key for user preferences
 */
export const PREFERENCES_KEY = 'fussballgpt_preferences';

/**
 * Load user profile from localStorage
 */
export function loadUserProfile(): UserProfile {
  if (typeof window === 'undefined') {
    return DEFAULT_PROFILE;
  }

  try {
    const stored = localStorage.getItem(PREFERENCES_KEY);
    if (!stored) {
      return DEFAULT_PROFILE;
    }

    const parsed = JSON.parse(stored);

    // Validate and merge with defaults
    return {
      ...DEFAULT_PROFILE,
      ...parsed,
      // Ensure enums are valid
      language: Object.values(Language).includes(parsed.language)
        ? parsed.language
        : DEFAULT_PROFILE.language,
      detailLevel: Object.values(DetailLevel).includes(parsed.detailLevel)
        ? parsed.detailLevel
        : DEFAULT_PROFILE.detailLevel,
      persona: Object.values(Persona).includes(parsed.persona)
        ? parsed.persona
        : DEFAULT_PROFILE.persona,
    };
  } catch (error) {
    console.error('Error loading user profile:', error);
    return DEFAULT_PROFILE;
  }
}

/**
 * Save user profile to localStorage
 */
export function saveUserProfile(profile: UserProfile): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    localStorage.setItem(PREFERENCES_KEY, JSON.stringify(profile));
  } catch (error) {
    console.error('Error saving user profile:', error);
  }
}

/**
 * Check if user has completed onboarding (has saved preferences)
 */
export function hasCompletedOnboarding(): boolean {
  if (typeof window === 'undefined') {
    return true; // Assume true on server-side
  }

  return localStorage.getItem(PREFERENCES_KEY) !== null;
}

/**
 * Clear user preferences (for testing or reset)
 */
export function clearUserProfile(): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    localStorage.removeItem(PREFERENCES_KEY);
  } catch (error) {
    console.error('Error clearing user profile:', error);
  }
}

/**
 * Get display labels for enums (multilingual)
 */
export const LABELS = {
  language: {
    [Language.GERMAN]: {
      de: 'Deutsch',
      en: 'German',
      flag: '🇩🇪',
    },
    [Language.ENGLISH]: {
      de: 'Englisch',
      en: 'English',
      flag: '🇬🇧',
    },
  },
  detailLevel: {
    [DetailLevel.QUICK]: {
      de: 'Schnell',
      en: 'Quick',
      description: {
        de: 'Kurze, prägnante Antworten (2-3 Sätze)',
        en: 'Short, concise answers (2-3 sentences)',
      },
    },
    [DetailLevel.BALANCED]: {
      de: 'Ausgewogen',
      en: 'Balanced',
      description: {
        de: 'Ausgewogene Antworten mit Kontext (2-3 Absätze)',
        en: 'Balanced answers with context (2-3 paragraphs)',
      },
    },
    [DetailLevel.DETAILED]: {
      de: 'Detailliert',
      en: 'Detailed',
      description: {
        de: 'Umfassende Analysen mit taktischer Tiefe (3-5+ Absätze)',
        en: 'Comprehensive analysis with tactical depth (3-5+ paragraphs)',
      },
    },
  },
  persona: {
    [Persona.CASUAL_FAN]: {
      de: 'Gelegenheitsfan',
      en: 'Casual Fan',
      description: {
        de: 'Schnelle Highlights, einfache Präsentation',
        en: 'Quick highlights, simple presentation',
      },
    },
    [Persona.EXPERT_ANALYST]: {
      de: 'Experte/Analytiker',
      en: 'Expert Analyst',
      description: {
        de: 'Taktische Tiefe, priorisierte Analysen',
        en: 'Tactical depth, prioritized analysis',
      },
    },
    [Persona.BETTING_ENTHUSIAST]: {
      de: 'Wettbegeisterter',
      en: 'Betting Enthusiast',
      description: {
        de: 'Statistiken, Quoten, Formdaten',
        en: 'Stats, odds, form data',
      },
    },
    [Persona.FANTASY_PLAYER]: {
      de: 'Fantasy-Spieler',
      en: 'Fantasy Player',
      description: {
        de: 'Spielerstatistiken, Leistungsdaten',
        en: 'Player stats, performance data',
      },
    },
  },
};
