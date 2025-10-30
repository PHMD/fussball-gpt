/**
 * Entity extraction and article classification utilities
 *
 * Extracts teams, players, and topics from article text.
 * Classifies articles by type (Match Report, Injury Update, etc.).
 */

// Bundesliga teams
const BUNDESLIGA_TEAMS = [
  'bayern', 'münchen', 'dortmund', 'bvb', 'leipzig', 'rb leipzig',
  'leverkusen', 'bayer leverkusen', 'frankfurt', 'eintracht',
  'freiburg', 'union berlin', 'köln', 'fc köln', 'hoffenheim',
  'wolfsburg', 'vfl wolfsburg', 'gladbach', 'borussia', 'stuttgart',
  'bremen', 'werder', 'augsburg', 'bochum', 'mainz', 'heidenheim'
] as const;

// Topic keywords (German + English for bilingual support)
const TOPIC_KEYWORDS = {
  match: ['spiel', 'match', 'sieg', 'niederlage', 'unentschieden', 'tor', 'goal'],
  injury: ['verletzung', 'injury', 'ausfall', 'gesperrt', 'suspended'],
  transfer: ['transfer', 'wechsel', 'verpflichtet', 'signing'],
  tactics: ['taktik', 'tactics', 'formation', 'strategie', 'strategy'],
  stats: ['statistik', 'stats', 'zahlen', 'rekord', 'record']
} as const;

export interface ExtractedEntities {
  teams: string[];
  topics: string[];
}

/**
 * Extract entities (teams, topics) from article text
 *
 * @param title - Article title
 * @param description - Article description
 * @param snippets - Additional text snippets
 * @returns Object containing found teams and topics
 */
export function extractEntities(
  title: string,
  description: string,
  snippets: string[]
): ExtractedEntities {
  const text = `${title} ${description} ${snippets.join(' ')}`.toLowerCase();

  // Find teams
  const foundTeams = BUNDESLIGA_TEAMS.filter(team => text.includes(team));

  // Find topics
  const foundTopics: string[] = [];
  for (const [category, words] of Object.entries(TOPIC_KEYWORDS)) {
    if (words.some(word => text.includes(word))) {
      foundTopics.push(category);
    }
  }

  return {
    teams: Array.from(new Set(foundTeams)), // Remove duplicates
    topics: foundTopics
  };
}

/**
 * Classify article type based on extracted entities
 *
 * @param entities - Extracted teams and topics
 * @returns Article type classification
 */
export function classifyArticleType(entities: ExtractedEntities): string {
  const { topics } = entities;

  if (topics.includes('match')) {
    return 'Match Report';
  } else if (topics.includes('injury')) {
    return 'Injury Update';
  } else if (topics.includes('transfer')) {
    return 'Transfer News';
  } else if (topics.includes('tactics')) {
    return 'Tactical Analysis';
  } else if (topics.includes('stats')) {
    return 'Performance Stats';
  } else {
    return 'General News';
  }
}

/**
 * Combine description and extra snippets for richer content
 *
 * @param description - Main article description
 * @param extraSnippets - Additional text snippets from search result
 * @returns Combined text content
 */
export function combineSnippets(description: string, extraSnippets: string[]): string {
  const parts = [description];

  if (extraSnippets && extraSnippets.length > 0) {
    parts.push(...extraSnippets);
  }

  return parts.join('\n\n');
}
