/**
 * Query Classification System - Week 1: Keyword-based Classifier
 *
 * Classifies user queries into categories for smart data routing.
 * Target: 75%+ accuracy with regex pattern matching.
 *
 * Categories:
 * - news: Latest news, transfers, rumors
 * - player: Player stats, injuries, performance
 * - match: Fixtures, schedules, odds, results
 * - standings: League table, positions, rankings
 * - meta: Questions about the app itself
 * - general: Broad questions requiring all data
 */

export type QueryCategory =
  | 'news'
  | 'player'
  | 'match'
  | 'standings'
  | 'meta'
  | 'general';

export interface ClassificationResult {
  category: QueryCategory;
  confidence: number;
  method: 'keyword' | 'embedding' | 'llm';
  matchedPatterns?: string[];
}

interface CategoryPatterns {
  category: QueryCategory;
  patterns: RegExp[];
  keywords: string[];
}

/**
 * Keyword patterns for each category
 * Ordered by specificity to avoid false positives
 */
const CATEGORY_PATTERNS: CategoryPatterns[] = [
  // Meta queries (check first - most specific)
  {
    category: 'meta',
    keywords: ['how does this work', 'what can you do', 'help', 'about', 'features'],
    patterns: [
      /how (does|do) (this|you|it) (work|function)/i,
      /what (can|do) you (do|offer|provide)/i,
      /tell me about (this app|yourself|your features)/i,
      /what (is|are) (your|this) (capabilities|features)/i,
    ],
  },

  // Player queries
  {
    category: 'player',
    keywords: [
      'player', 'injured', 'injury', 'fitness', 'stats', 'scorer', 'goals',
      'assists', 'performance', 'form', 'rating', 'suspended', 'ban',
      'neuer', 'müller', 'kane', 'musiala', 'sané', 'kimmich', 'davies',
      'top scorer', 'best player', 'star player',
    ],
    patterns: [
      /is \w+ (injured|fit|available|suspended|banned)/i,
      /\w+ (injury|fitness|stats|performance|form|rating)/i,
      /(who is|who'?s) (the )?(top|best|leading) (scorer|player|striker)/i,
      /how (is|has) \w+ (playing|performing|doing)/i,
      /(player|squad|lineup) (stats|statistics|analysis)/i,
      /tell me about \w+ (player|stats|performance)/i,
    ],
  },

  // Match queries
  {
    category: 'match',
    keywords: [
      'match', 'game', 'fixture', 'play', 'playing', 'when', 'schedule',
      'odds', 'betting', 'prediction', 'vs', 'against', 'kick off',
      'result', 'score', 'won', 'lost', 'draw', 'played',
      'bayern', 'dortmund', 'leipzig', 'leverkusen', 'frankfurt',
    ],
    patterns: [
      /when (does|do|is|are) \w+ (play|playing|vs|against)/i,
      /(match|game|fixture) (schedule|time|details|info)/i,
      /(what are|show me) (the )?(odds|betting lines) (for|on)/i,
      /(who|what) (won|lost|played|scored)/i,
      /\w+ vs \w+/i,
      /(upcoming|next|recent|last) (match|game|fixture)/i,
      /kick off time/i,
      /(match|game) (result|score|prediction)/i,
    ],
  },

  // Standings queries
  {
    category: 'standings',
    keywords: [
      'standings', 'table', 'position', 'rank', 'first place', 'top of',
      'bottom', 'league table', 'points', 'who is leading', 'leader',
      'relegated', 'relegation', 'champions league', 'europa league',
    ],
    patterns: [
      /(show|display|get|tell) (me )?(the )?((league|bundesliga) )?(table|standings|position)/i,
      /(who is|who'?s) (in )?(first|top|leading|last)/i,
      /(what|where) (is|are) \w+ (position|rank|place)/i,
      /(current|latest) (standings|table|position)/i,
      /(top|bottom) (of|in) (the )?(league|table)/i,
      /(relegation|champions league|europa league) (zone|spots)/i,
    ],
  },

  // News queries
  {
    category: 'news',
    keywords: [
      'news', 'latest', 'recent', 'update', 'transfer', 'rumor', 'signing',
      'headline', 'breaking', 'announcement', 'report', 'story', 'article',
      'what happened', 'whats new', 'what\'s new',
    ],
    patterns: [
      /(latest|recent|new|breaking) (news|updates|headlines|stories)/i,
      /(transfer|signing|rumor|rumour) (news|update|report)/i,
      /what (happened|is happening|'?s new|'?s going on)/i,
      /(tell|show) me (about )?(the )?(latest|recent|new)/i,
      /bundesliga (news|update|headlines)/i,
      /(any|what) (news|updates) (about|on|for)/i,
    ],
  },

  // General queries (fallback - least specific)
  // Broad questions that need multiple data sources
  {
    category: 'general',
    keywords: [
      'who will win', 'prediction', 'forecast', 'best team', 'favorite',
      'analysis', 'overview', 'summary', 'tell me about bundesliga',
      'whats happening', 'what\'s happening',
    ],
    patterns: [
      /who (will|might|could|is going to) win (the )?bundesliga/i,
      /(give|show|provide) (me )?(an )?(overview|summary|analysis)/i,
      /(what is|tell me about) (the )?bundesliga/i,
      /(overall|general) (analysis|situation|status)/i,
      /(best|strongest|weakest) team/i,
    ],
  },
];

/**
 * Classifies a query using keyword pattern matching
 *
 * @param query - User's natural language query
 * @returns Classification result with category and confidence
 */
export function classifyQuery(query: string): ClassificationResult {
  const normalizedQuery = query.toLowerCase().trim();
  const matchedPatterns: string[] = [];

  // Try to match against each category's patterns
  for (const categoryDef of CATEGORY_PATTERNS) {
    // Check regex patterns first (higher confidence)
    for (const pattern of categoryDef.patterns) {
      if (pattern.test(normalizedQuery)) {
        matchedPatterns.push(pattern.source);
        return {
          category: categoryDef.category,
          confidence: 0.85, // High confidence for regex match
          method: 'keyword',
          matchedPatterns,
        };
      }
    }

    // Check keywords (lower confidence)
    for (const keyword of categoryDef.keywords) {
      if (normalizedQuery.includes(keyword.toLowerCase())) {
        matchedPatterns.push(keyword);
        return {
          category: categoryDef.category,
          confidence: 0.70, // Medium confidence for keyword match
          method: 'keyword',
          matchedPatterns,
        };
      }
    }
  }

  // No match found - default to general
  return {
    category: 'general',
    confidence: 0.50, // Low confidence - needs all data
    method: 'keyword',
    matchedPatterns: ['fallback'],
  };
}

/**
 * Get required data sources for a query category
 * Maps categories to minimal data needed for accurate responses
 */
export function getRequiredDataSources(category: QueryCategory): string[] {
  switch (category) {
    case 'news':
      return ['news_articles'];

    case 'player':
      return ['player_stats', 'injuries'];

    case 'match':
      return ['sports_events', 'betting_odds', 'team_form'];

    case 'standings':
      return ['standings', 'team_form'];

    case 'meta':
      return []; // No external data needed

    case 'general':
    default:
      return ['news_articles', 'sports_events', 'player_stats', 'standings', 'team_form', 'betting_odds', 'injuries'];
  }
}

/**
 * Estimates token savings from using classified data routing
 * Based on research: Full context = ~50K tokens, specific context = ~5K tokens
 */
export function estimateTokenSavings(category: QueryCategory): {
  baselineTokens: number;
  optimizedTokens: number;
  savingsPercent: number;
} {
  const FULL_CONTEXT_TOKENS = 50_000;

  const tokensByCategory: Record<QueryCategory, number> = {
    news: 5_000,      // Just news articles
    player: 3_000,    // Player stats + injuries
    match: 7_000,     // Fixtures + odds + form
    standings: 2_000, // Table + form
    meta: 100,        // No external data
    general: 50_000,  // Everything
  };

  const optimizedTokens = tokensByCategory[category];
  const savingsPercent = Math.round(((FULL_CONTEXT_TOKENS - optimizedTokens) / FULL_CONTEXT_TOKENS) * 100);

  return {
    baselineTokens: FULL_CONTEXT_TOKENS,
    optimizedTokens,
    savingsPercent,
  };
}
