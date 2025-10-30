/**
 * The Odds API client for betting odds
 *
 * Fetches pre-match betting odds for Bundesliga fixtures.
 * Requires ODDS_API_KEY environment variable.
 */

import { z } from 'zod';
import { fetchWithCache, cacheKeys, CACHE_DURATIONS } from '../cache';

const ODDS_API_BASE_URL = 'https://api.the-odds-api.com/v4';

/**
 * Check if The Odds API is configured
 */
function isConfigured(): boolean {
  return Boolean(process.env.ODDS_API_KEY);
}

/**
 * The Odds API response schema
 */
const OddsApiResponseSchema = z.array(
  z.object({
    id: z.string(),
    home_team: z.string(),
    away_team: z.string(),
    commence_time: z.string(),
    bookmakers: z.array(
      z.object({
        title: z.string().optional(),
        markets: z.array(
          z.object({
            key: z.string(),
            outcomes: z.array(
              z.object({
                name: z.string(),
                price: z.number(),
              })
            ),
          })
        ),
      })
    ),
  })
);

/**
 * Betting odds for a single match
 */
export interface MatchOdds {
  matchId: string;
  homeTeam: string;
  awayTeam: string;
  commenceTime: string;
  odds: {
    home?: number;
    draw?: number;
    away?: number;
  };
  bookmaker: string;
}

/**
 * Fetch betting odds from The Odds API (internal, no cache)
 */
async function fetchBettingOddsInternal(): Promise<Record<string, MatchOdds>> {
  if (!isConfigured()) {
    console.warn('The Odds API not configured (ODDS_API_KEY missing)');
    return {};
  }

  try {
    const params = new URLSearchParams({
      apiKey: process.env.ODDS_API_KEY!,
      regions: 'eu',  // European bookmakers
      markets: 'h2h', // Head-to-head (match winner)
      oddsFormat: 'decimal',  // European decimal format
    });
    const url = `${ODDS_API_BASE_URL}/sports/soccer_germany_bundesliga/odds/?${params}`;

    const response = await fetch(url, {
      next: { revalidate: CACHE_DURATIONS.BETTING_ODDS },
    });

    if (!response.ok) {
      if (response.status === 401) {
        console.error('⚠️  The Odds API: Invalid API key');
      } else if (response.status === 429) {
        console.error('⚠️  The Odds API: Rate limit exceeded (500 req/month on free tier)');
      } else {
        console.error(`HTTP ${response.status} fetching betting odds`);
      }
      return {};
    }

    const data = await response.json();

    // Validate response structure
    const validated = OddsApiResponseSchema.parse(data);

    const oddsData: Record<string, MatchOdds> = {};

    // Process odds data
    for (const event of validated) {
      const matchId = event.id;
      const homeTeam = event.home_team;
      const awayTeam = event.away_team;
      const commenceTime = event.commence_time;

      // Get odds from first bookmaker (could average multiple in future)
      const bookmakers = event.bookmakers;
      if (bookmakers.length === 0) {
        continue;
      }

      const firstBookmaker = bookmakers[0];
      const markets = firstBookmaker.markets;

      // Find h2h market
      const h2hMarket = markets.find((m) => m.key === 'h2h');
      if (!h2hMarket) {
        continue;
      }

      const outcomes = h2hMarket.outcomes;

      // Extract odds for home, draw, away
      const odds: { home?: number; draw?: number; away?: number } = {};
      for (const outcome of outcomes) {
        const name = outcome.name;
        const price = outcome.price;

        if (name === homeTeam) {
          odds.home = price;
        } else if (name === awayTeam) {
          odds.away = price;
        } else if (name.toLowerCase() === 'draw') {
          odds.draw = price;
        }
      }

      if (Object.keys(odds).length > 0) {
        oddsData[matchId] = {
          matchId,
          homeTeam,
          awayTeam,
          commenceTime,
          odds,
          bookmaker: firstBookmaker.title || 'Unknown',
        };
      }
    }

    console.log(`Fetched odds for ${Object.keys(oddsData).length} Bundesliga fixtures`);

    // Check remaining quota
    const remaining = response.headers.get('x-requests-remaining');
    if (remaining) {
      console.log(`Odds API requests remaining: ${remaining}`);
    }

    return oddsData;
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error('The Odds API response validation error:', error.errors);
    } else {
      console.error('Error fetching betting odds:', error);
    }
    return {};
  }
}

/**
 * Fetch betting odds (with caching)
 *
 * Uses 24-hour cache to avoid rate limits (free tier: 500 req/month).
 */
export async function fetchBettingOdds(): Promise<Record<string, MatchOdds>> {
  return fetchWithCache(
    cacheKeys.bettingOdds(),
    fetchBettingOddsInternal,
    CACHE_DURATIONS.BETTING_ODDS
  );
}
