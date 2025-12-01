/**
 * API-Football client for player stats and injuries
 *
 * Fetches Bundesliga player statistics and injury data from API-Football (api-sports.io).
 * Requires APIFOOTBALL_API_KEY environment variable.
 */

import { z } from 'zod';
import { PlayerStats, PlayerStatsSchema } from '../models';
import { fetchWithCache, cacheKeys, CACHE_DURATIONS } from '../cache';

const API_FOOTBALL_BASE_URL = 'https://v3.football.api-sports.io';
const BUNDESLIGA_LEAGUE_ID = 78;
// Free tier only supports 2021-2023. Current season requires paid plan (~$15/mo)
const CURRENT_SEASON = '2023'; // 2023/24 - last free tier season

/**
 * Check if API-Football is configured
 */
function isConfigured(): boolean {
  return Boolean(process.env.APIFOOTBALL_API_KEY);
}

/**
 * API-Football response schema for player top scorers
 */
const ApiFootballPlayerResponseSchema = z.object({
  response: z.array(
    z.object({
      player: z.object({
        name: z.string(),
      }),
      statistics: z.array(
        z.object({
          team: z.object({
            name: z.string(),
          }),
          games: z.object({
            position: z.string().optional(),
            appearences: z.number().optional(), // Note: API typo "appearences"
            minutes: z.number().optional(),
          }).optional(),
          goals: z.object({
            total: z.number().nullable().optional(),
            assists: z.number().nullable().optional(),
            saves: z.number().nullable().optional(),
          }).optional(),
          shots: z.object({
            total: z.number().nullable().optional(),
            on: z.number().nullable().optional(),
          }).optional(),
          cards: z.object({
            yellow: z.number().nullable().optional(),
            red: z.number().nullable().optional(),
          }).optional(),
          passes: z.object({
            total: z.number().nullable().optional(),
            accuracy: z.number().nullable().optional(),
          }).optional(),
          dribbles: z.object({
            success: z.number().nullable().optional(),
          }).optional(),
        })
      ),
    })
  ),
});

/**
 * Fetch top player statistics from API-Football (internal, no cache)
 */
async function fetchPlayerStatsInternal(
  leagueId: number = BUNDESLIGA_LEAGUE_ID,
  season: string = CURRENT_SEASON
): Promise<PlayerStats[]> {
  if (!isConfigured()) {
    console.warn('API-Football not configured (APIFOOTBALL_API_KEY missing)');
    return [];
  }

  try {
    // Build URL with query parameters
    const params = new URLSearchParams({
      league: leagueId.toString(),
      season: season,
    });
    const url = `${API_FOOTBALL_BASE_URL}/players/topscorers?${params}`;

    const response = await fetch(url, {
      headers: {
        'x-apisports-key': process.env.APIFOOTBALL_API_KEY!,
      },
      method: 'GET',
      next: { revalidate: CACHE_DURATIONS.PLAYER_STATS },
    });

    if (!response.ok) {
      if (response.status === 403) {
        console.error('⚠️  API-Football: Invalid API key or quota exceeded (100 req/day limit)');
      } else {
        console.error(`HTTP ${response.status} fetching player stats`);
      }
      return [];
    }

    const data = await response.json();

    // Validate response structure
    const validated = ApiFootballPlayerResponseSchema.parse(data);

    const players: PlayerStats[] = [];

    // Get top 20 players
    for (const playerData of validated.response.slice(0, 20)) {
      const playerInfo = playerData.player;
      const stats = playerData.statistics[0] || {};

      const player: PlayerStats = {
        source: 'sports_api',
        player_name: playerInfo.name || 'Unknown',
        team: stats.team?.name || 'Unknown',
        position: stats.games?.position || 'Unknown',

        // Appearance stats (with null coalescing)
        appearances: stats.games?.appearences ?? 0,
        minutes_played: stats.games?.minutes ?? 0,

        // Performance stats
        goals: stats.goals?.total ?? 0,
        assists: stats.goals?.assists ?? 0,
        shots_total: stats.shots?.total ?? 0,
        shots_on_target: stats.shots?.on ?? 0,

        // Disciplinary
        yellow_cards: stats.cards?.yellow ?? 0,
        red_cards: stats.cards?.red ?? 0,

        // Additional (optional)
        passes_total: stats.passes?.total ?? undefined,
        passes_accurate: stats.passes?.accuracy ?? undefined,
        dribbles_successful: stats.dribbles?.success ?? undefined,

        // Goalkeeper (if applicable)
        saves: stats.goals?.saves ?? undefined,

        // Metadata
        season: `${season}-${parseInt(season) + 1}`,
        league: 'Bundesliga',
      };

      players.push(player);
    }

    console.log(`Fetched ${players.length} player stats from API-Football`);
    return players;
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error('API-Football response validation error:', error.errors);
    } else {
      console.error('Error fetching player stats:', error);
    }
    return [];
  }
}

/**
 * Fetch player statistics (with caching)
 *
 * Uses 6-hour cache to avoid rate limits (API-Football free tier: 100 req/day).
 */
export async function fetchPlayerStats(
  leagueId: number = BUNDESLIGA_LEAGUE_ID,
  season: string = CURRENT_SEASON
): Promise<PlayerStats[]> {
  return fetchWithCache(
    cacheKeys.playerStats(season),
    () => fetchPlayerStatsInternal(leagueId, season),
    CACHE_DURATIONS.PLAYER_STATS
  );
}

/**
 * API-Football response schema for injuries
 */
const ApiFootballInjuryResponseSchema = z.object({
  response: z.array(
    z.object({
      player: z.object({
        name: z.string(),
      }),
      team: z.object({
        name: z.string(),
      }),
      fixture: z.object({
        date: z.string().optional(),
      }).optional(),
      league: z.object({
        name: z.string().optional(),
      }).optional(),
    })
  ),
});

/**
 * Injury data type (simpler than PlayerStats, just for context)
 */
export interface InjuryData {
  player_name: string;
  team: string;
  injury_type: string;
  date: string;
  league: string;
}

/**
 * Fetch injury data from API-Football (internal, no cache)
 */
async function fetchInjuriesInternal(
  leagueId: number = BUNDESLIGA_LEAGUE_ID,
  season: string = CURRENT_SEASON
): Promise<InjuryData[]> {
  if (!isConfigured()) {
    console.warn('API-Football not configured (APIFOOTBALL_API_KEY missing)');
    return [];
  }

  try {
    // Build URL with query parameters
    const params = new URLSearchParams({
      league: leagueId.toString(),
      season: season,
    });
    const url = `${API_FOOTBALL_BASE_URL}/injuries?${params}`;

    const response = await fetch(url, {
      headers: {
        'x-apisports-key': process.env.APIFOOTBALL_API_KEY!,
      },
      method: 'GET',
      next: { revalidate: CACHE_DURATIONS.INJURIES },
    });

    if (!response.ok) {
      console.error(`HTTP ${response.status} fetching injuries`);
      return [];
    }

    const data = await response.json();

    // Validate response structure
    const validated = ApiFootballInjuryResponseSchema.parse(data);

    // CRITICAL: Limit to 30 most recent injuries to reduce token usage
    // Was returning 647 records (8000 tokens!) - now limited to ~30 records (~400 tokens)
    const injuries: InjuryData[] = validated.response
      .slice(0, 30) // Only take first 30 injuries
      .map((injuryData) => ({
        player_name: injuryData.player.name,
        team: injuryData.team.name,
        injury_type: 'Unknown', // API doesn't provide injury type in this endpoint
        date: injuryData.fixture?.date || new Date().toISOString(),
        league: injuryData.league?.name || 'Bundesliga',
      }));

    console.log(`Fetched ${injuries.length} injury records from API-Football (limited to 30 for token efficiency)`);
    return injuries;
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error('API-Football injuries response validation error:', error.errors);
    } else {
      console.error('Error fetching injuries:', error);
    }
    return [];
  }
}

/**
 * Fetch injury data (with caching)
 *
 * Uses 6-hour cache to avoid rate limits.
 */
export async function fetchInjuries(
  leagueId: number = BUNDESLIGA_LEAGUE_ID,
  season: string = CURRENT_SEASON
): Promise<InjuryData[]> {
  return fetchWithCache(
    cacheKeys.injuries(season),
    () => fetchInjuriesInternal(leagueId, season),
    CACHE_DURATIONS.INJURIES
  );
}
