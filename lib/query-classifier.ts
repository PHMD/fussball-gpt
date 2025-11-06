/**
 * Query Classification System
 *
 * Classifies user queries to determine which data sources are needed.
 * Week 1 implementation: Simple keyword matching
 *
 * Token savings: 60-70% by only fetching relevant data
 */

export type QueryCategory =
  | 'news'        // Latest news, articles, transfers
  | 'player'      // Player stats, performance, injuries
  | 'match'       // Match schedules, results, predictions
  | 'standings'   // League tables, form, rankings
  | 'meta'        // Questions about the system itself
  | 'general';    // Catch-all requiring multiple sources

export interface ClassificationResult {
  category: QueryCategory;
  confidence: number;
  requiredSources: DataSource[];
  matchedKeywords?: string[];
}

export type DataSource =
  | 'news'
  | 'player_stats'
  | 'injuries'
  | 'standings'
  | 'results'
  | 'team_form'
  | 'betting_odds';

/**
 * Keyword patterns for each category
 */
const CATEGORY_PATTERNS: Record<QueryCategory, string[]> = {
  news: [
    'news', 'nachrichten', 'artikel', 'latest', 'neueste',
    'transfer', 'rumor', 'gerücht', 'breaking',
    'headlines', 'schlagzeilen', 'update'
  ],
  player: [
    'player', 'spieler', 'stats', 'statistik', 'scorer', 'torschütze',
    'assists', 'vorlagen', 'performance', 'leistung',
    'injury', 'verletzung', 'form', 'fitness',
    'rating', 'bewertung', 'age', 'alter',
    'goals', 'tore', 'top scorer', 'bester', 'who scored'
  ],
  match: [
    'match', 'spiel', 'game', 'fixture', 'schedule', 'spielplan',
    'next', 'nächste', 'when', 'wann', 'vs', 'gegen',
    'prediction', 'prognose', 'preview', 'vorschau',
    'result', 'ergebnis', 'score', 'final'
  ],
  standings: [
    'table', 'tabelle', 'standings', 'ranking', 'platzierung',
    'position', 'place', 'platz', 'league', 'liga',
    'top', 'bottom', 'unten', 'form', 'streak'
  ],
  meta: [
    'what is', 'was ist', 'how does', 'wie funktioniert',
    'can you', 'kannst du', 'help', 'hilfe',
    'explain', 'erklär', 'about you', 'über dich'
  ],
  general: [] // Catch-all - no specific patterns
};

/**
 * Data sources required for each category
 */
const CATEGORY_DATA_SOURCES: Record<QueryCategory, DataSource[]> = {
  news: ['news'],
  player: ['player_stats', 'injuries'],
  match: ['results', 'standings', 'team_form', 'betting_odds'],
  standings: ['standings', 'team_form'],
  meta: [], // No external data needed
  general: ['news', 'player_stats', 'standings', 'results', 'team_form'], // Exclude injuries and odds
};

/**
 * Classify a user query to determine required data sources
 */
export function classifyQuery(query: string): ClassificationResult {
  const normalizedQuery = query.toLowerCase();

  // Check each category for keyword matches
  const categoryScores: Record<QueryCategory, { score: number; keywords: string[] }> = {
    news: { score: 0, keywords: [] },
    player: { score: 0, keywords: [] },
    match: { score: 0, keywords: [] },
    standings: { score: 0, keywords: [] },
    meta: { score: 0, keywords: [] },
    general: { score: 0, keywords: [] },
  };

  // Score each category based on keyword matches
  for (const [category, patterns] of Object.entries(CATEGORY_PATTERNS)) {
    for (const pattern of patterns) {
      if (normalizedQuery.includes(pattern)) {
        categoryScores[category as QueryCategory].score += 1;
        categoryScores[category as QueryCategory].keywords.push(pattern);
      }
    }
  }

  // Find the category with the highest score
  let bestCategory: QueryCategory = 'general';
  let bestScore = 0;
  let bestKeywords: string[] = [];

  for (const [category, { score, keywords }] of Object.entries(categoryScores)) {
    if (score > bestScore) {
      bestCategory = category as QueryCategory;
      bestScore = score;
      bestKeywords = keywords;
    }
  }

  // Calculate confidence (0-1)
  const confidence = Math.min(bestScore / 3, 1); // Max confidence at 3+ keyword matches

  // Get required data sources
  const requiredSources = CATEGORY_DATA_SOURCES[bestCategory];

  return {
    category: bestCategory,
    confidence,
    requiredSources,
    matchedKeywords: bestKeywords.length > 0 ? bestKeywords : undefined,
  };
}

/**
 * Estimate token savings from classification
 */
export function estimateTokenSavings(classification: ClassificationResult): {
  baselineTokens: number;
  optimizedTokens: number;
  savingsPercent: number;
} {
  // Approximate token counts per data source
  const SOURCE_TOKEN_COSTS: Record<DataSource, number> = {
    news: 3000,           // Articles with full text
    player_stats: 800,    // 20 players × 40 tokens
    injuries: 8000,       // 647 records (WAY TOO MUCH)
    standings: 600,       // 18 teams × 33 tokens
    results: 500,         // 5 recent matches
    team_form: 400,       // 5 teams × 80 tokens
    betting_odds: 1200,   // 18 fixtures × 67 tokens
  };

  // All sources combined
  const allSources: DataSource[] = [
    'news',
    'player_stats',
    'injuries',
    'standings',
    'results',
    'team_form',
    'betting_odds',
  ];

  const baselineTokens = allSources.reduce((sum, source) => sum + SOURCE_TOKEN_COSTS[source], 0);
  const optimizedTokens = classification.requiredSources.reduce(
    (sum, source) => sum + SOURCE_TOKEN_COSTS[source],
    0
  );

  const savingsPercent = Math.round(((baselineTokens - optimizedTokens) / baselineTokens) * 100);

  return {
    baselineTokens,
    optimizedTokens,
    savingsPercent,
  };
}

/**
 * Check if a data source should be fetched for a query
 */
export function shouldFetchSource(
  source: DataSource,
  classification: ClassificationResult
): boolean {
  return classification.requiredSources.includes(source);
}
