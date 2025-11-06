/**
 * Caching layer using Vercel KV (Redis-compatible)
 *
 * Ports Python's file-based caching to Vercel KV with same TTL durations:
 * - Player stats, team form, injuries: 6 hours
 * - Betting odds, H2H records: 24 hours
 * - Brave Search results: 5 minutes (in-memory in Python, KV here)
 */

import { kv } from '@vercel/kv';

/**
 * Cache durations (in seconds)
 */
export const CACHE_DURATIONS = {
  PLAYER_STATS: 21600,      // 6 hours
  TEAM_FORM: 21600,         // 6 hours
  INJURIES: 21600,          // 6 hours
  BETTING_ODDS: 86400,      // 24 hours
  H2H_RECORDS: 86400,       // 24 hours
  BRAVE_SEARCH: 300,        // 5 minutes
} as const;

/**
 * Cache key namespaces
 */
const CACHE_KEYS = {
  playerStats: (season: string) => `bundesliga:player_stats:${season}`,
  teamForm: (teamId: string) => `bundesliga:team_form:${teamId}`,
  standings: (season: string) => `bundesliga:standings:${season}`,
  injuries: (season: string) => `bundesliga:injuries:${season}`,
  bettingOdds: () => `bundesliga:betting_odds`,
  h2hRecords: (team1: string, team2: string) => `bundesliga:h2h:${team1}_${team2}`,
  braveSearch: (query: string) => `bundesliga:brave:${query}`,
  kickerRss: () => `bundesliga:kicker_rss`,
} as const;

/**
 * Check if KV is available (has required env vars)
 */
function isKVAvailable(): boolean {
  const hasUrl = Boolean(process.env.KV_REST_API_URL);
  const hasToken = Boolean(process.env.KV_REST_API_TOKEN);
  const available = hasUrl && hasToken;

  console.log('🔍 KV Availability Check:', {
    available,
    hasUrl,
    hasToken,
    urlPreview: hasUrl ? process.env.KV_REST_API_URL?.substring(0, 30) + '...' : 'MISSING',
    tokenPreview: hasToken ? process.env.KV_REST_API_TOKEN?.substring(0, 10) + '...' : 'MISSING',
  });

  return available;
}

/**
 * Get cached data from Vercel KV
 */
export async function getCached<T>(key: string): Promise<T | null> {
  if (!isKVAvailable()) {
    console.log(`⚠️ Cache SKIP for ${key} - KV not available`);
    return null; // Skip cache if KV not configured
  }

  try {
    console.log(`🔎 Attempting to get from KV: ${key}`);
    const data = await kv.get<T>(key);

    if (data === null) {
      console.log(`❌ KV returned null for ${key} (key not found or expired)`);
    } else {
      console.log(`✅ KV returned data for ${key}:`, {
        type: typeof data,
        isArray: Array.isArray(data),
        length: Array.isArray(data) ? data.length : 'N/A',
        hasData: data !== null && data !== undefined,
      });
    }

    return data;
  } catch (error) {
    console.error(`❌ Cache get error for key ${key}:`, {
      error,
      errorMessage: error instanceof Error ? error.message : 'Unknown error',
      errorStack: error instanceof Error ? error.stack : undefined,
    });
    return null;
  }
}

/**
 * Set cached data in Vercel KV with TTL
 */
export async function setCached<T>(
  key: string,
  data: T,
  ttl: number
): Promise<void> {
  if (!isKVAvailable()) {
    console.log(`⚠️ Cache SET SKIP for ${key} - KV not available`);
    return; // Skip cache if KV not configured
  }

  try {
    console.log(`💾 Attempting to set in KV: ${key}`, {
      ttl: `${ttl}s (${Math.round(ttl / 3600)}h)`,
      dataType: typeof data,
      isArray: Array.isArray(data),
      dataLength: Array.isArray(data) ? data.length : 'N/A',
    });

    await kv.set(key, data, { ex: ttl });

    console.log(`✅ Successfully cached ${key} with TTL ${ttl}s`);
  } catch (error) {
    console.error(`❌ Cache set error for key ${key}:`, {
      error,
      errorMessage: error instanceof Error ? error.message : 'Unknown error',
      errorStack: error instanceof Error ? error.stack : undefined,
      ttl,
      dataType: typeof data,
    });
  }
}

/**
 * Delete cached data
 */
export async function deleteCached(key: string): Promise<void> {
  try {
    await kv.del(key);
  } catch (error) {
    console.error(`Cache delete error for key ${key}:`, error);
  }
}

/**
 * Fetch with cache wrapper
 *
 * Tries to get from cache first, falls back to fetcher function if cache miss.
 * Automatically caches the result with specified TTL.
 */
export async function fetchWithCache<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl: number
): Promise<T> {
  // Try cache first
  const cached = await getCached<T>(key);
  if (cached !== null) {
    console.log(`Cache HIT for ${key}`);
    return cached;
  }

  // Cache miss - fetch fresh data
  console.log(`Cache MISS for ${key} - fetching fresh data...`);
  const data = await fetcher();

  // Cache the result
  await setCached(key, data, ttl);

  return data;
}

/**
 * Exported cache key generators for use by API clients
 */
export const cacheKeys = CACHE_KEYS;
