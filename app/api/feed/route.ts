/**
 * Newsfeed API Endpoint
 *
 * Server-side fetching of personalized Bundesliga news based on user persona.
 * Leverages existing Brave Search client with query-driven personalization.
 */

import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { fetchKickerArticlesBrave } from '@/lib/api-clients/brave-search';
import { Persona } from '@/lib/user-config';
import { NewsArticle } from '@/lib/models';

const FeedRequestSchema = z.object({
  persona: z.nativeEnum(Persona).optional(),
  category: z.enum(['latest', 'transfers', 'analysis', 'odds']).optional(),
  maxResults: z.number().min(1).max(50).optional(),
});

/**
 * Map persona to Brave Search queries with fallback chain
 */
function getPersonaQueries(persona: Persona): string[] {
  const base = ''; // Don't add site prefix here - brave-search.ts already adds "site:kicker.de Bundesliga"

  const queryMap: Record<Persona, string[]> = {
    [Persona.CASUAL_FAN]: [
      'highlights goals',
      base, // Fallback to broad
    ],
    [Persona.EXPERT_ANALYST]: [
      'taktik analyse',
      'tactical analysis',
      base, // Fallback to broad
    ],
    [Persona.BETTING_ENTHUSIAST]: [
      'prognose quoten',
      'form predictions',
      base, // Fallback to broad
    ],
    [Persona.FANTASY_PLAYER]: [
      'spieler statistik',
      'aufstellung player stats',
      base, // Fallback to broad
    ],
  };

  return queryMap[persona];
}

/**
 * Map category to specific search terms
 */
function getCategoryQuery(category: string): string {
  const categoryMap: Record<string, string> = {
    latest: '', // Broad search
    transfers: 'transfer news',
    analysis: 'tactical analysis',
    odds: 'betting odds predictions',
  };

  return categoryMap[category] || '';
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;

    // Parse and validate request parameters
    const params = FeedRequestSchema.parse({
      persona: searchParams.get('persona') || Persona.CASUAL_FAN,
      category: searchParams.get('category') || 'latest',
      maxResults: parseInt(searchParams.get('maxResults') || '20'),
    });

    const { persona = Persona.CASUAL_FAN, category = 'latest', maxResults = 20 } = params;

    // Determine search query based on category or persona
    let searchQuery: string;
    let queries: string[];

    if (category && category !== 'latest') {
      // Category-specific search
      searchQuery = getCategoryQuery(category);
      queries = [searchQuery];
    } else {
      // Persona-based search with fallback chain
      queries = getPersonaQueries(persona);
    }

    // Try queries in order until we get results
    let articles: NewsArticle[] = [];
    for (const query of queries) {
      articles = await fetchKickerArticlesBrave(query, maxResults);

      if (articles.length > 0) {
        console.log(`[Feed API] Found ${articles.length} articles for query: "${query}"`);
        break;
      }
    }

    // Return articles with metadata
    return NextResponse.json({
      articles,
      persona,
      category,
      count: articles.length,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('[Feed API] Error:', error);

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request parameters', details: error.errors },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: 'Failed to fetch feed articles' },
      { status: 500 }
    );
  }
}
