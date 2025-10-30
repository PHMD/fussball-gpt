/**
 * TheSportsDB client for standings, results, and team form
 *
 * Fetches Bundesliga standings, match results, and team form data from TheSportsDB.
 * Uses FREE TIER (no API key required).
 */

import { z } from 'zod';
import { SportsEvent, SportsEventSchema } from '../models';
import { fetchWithCache, cacheKeys, CACHE_DURATIONS } from '../cache';

const SPORTS_DB_BASE_URL = 'https://www.thesportsdb.com/api/v1/json/3';
const BUNDESLIGA_LEAGUE_ID = '4331';
const CURRENT_SEASON = '2024-2025';

/**
 * TheSportsDB standings table schema
 */
const StandingsTableSchema = z.object({
  table: z.array(
    z.object({
      intRank: z.string().optional(),
      strTeam: z.string().optional(),
      idTeam: z.string().optional(),
      intPlayed: z.string().optional(),
      intPoints: z.string().optional(),
      intGoalsFor: z.string().optional(),
      intGoalsAgainst: z.string().optional(),
    })
  ).optional(),
});

/**
 * Standing entry for a team
 */
export interface StandingEntry {
  position: number;
  team: string;
  teamId: string;
  played: number;
  points: number;
  goalsFor: number;
  goalsAgainst: number;
  goalDifference: number;
}

/**
 * Fetch Bundesliga standings (internal, no cache)
 */
async function fetchBundesligaStandingsInternal(): Promise<StandingEntry[]> {
  try {
    const params = new URLSearchParams({
      l: BUNDESLIGA_LEAGUE_ID,
      s: CURRENT_SEASON,
    });
    const url = `${SPORTS_DB_BASE_URL}/lookuptable.php?${params}`;

    const response = await fetch(url, {
      next: { revalidate: CACHE_DURATIONS.TEAM_FORM },
    });

    if (!response.ok) {
      console.error(`HTTP ${response.status} fetching standings`);
      return [];
    }

    const data = await response.json();
    const validated = StandingsTableSchema.parse(data);

    if (!validated.table) {
      return [];
    }

    const standings: StandingEntry[] = validated.table.slice(0, 18).map((team) => {
      const goalsFor = parseInt(team.intGoalsFor || '0');
      const goalsAgainst = parseInt(team.intGoalsAgainst || '0');

      return {
        position: parseInt(team.intRank || '0'),
        team: team.strTeam || 'Unknown',
        teamId: team.idTeam || '',
        played: parseInt(team.intPlayed || '0'),
        points: parseInt(team.intPoints || '0'),
        goalsFor,
        goalsAgainst,
        goalDifference: goalsFor - goalsAgainst,
      };
    });

    console.log(`Fetched ${standings.length} team standings from TheSportsDB`);
    return standings;
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error('TheSportsDB standings validation error:', error.errors);
    } else {
      console.error('Error fetching standings:', error);
    }
    return [];
  }
}

/**
 * Fetch Bundesliga standings (with caching)
 */
export async function fetchBundesligaStandings(): Promise<StandingEntry[]> {
  return fetchWithCache(
    cacheKeys.standings(CURRENT_SEASON),
    fetchBundesligaStandingsInternal,
    CACHE_DURATIONS.TEAM_FORM
  );
}

/**
 * TheSportsDB events schema
 */
const EventsSchema = z.object({
  events: z.array(
    z.object({
      strHomeTeam: z.string().optional(),
      strAwayTeam: z.string().optional(),
      intHomeScore: z.string().nullable().optional(),
      intAwayScore: z.string().nullable().optional(),
      dateEvent: z.string().optional(),
      strLeague: z.string().optional(),
    })
  ).optional(),
});

/**
 * Fetch recent Bundesliga results (internal, no cache)
 */
async function fetchRecentResultsInternal(): Promise<SportsEvent[]> {
  try {
    const params = new URLSearchParams({
      id: BUNDESLIGA_LEAGUE_ID,
    });
    const url = `${SPORTS_DB_BASE_URL}/eventspastleague.php?${params}`;

    const response = await fetch(url, {
      next: { revalidate: CACHE_DURATIONS.TEAM_FORM },
    });

    if (!response.ok) {
      console.error(`HTTP ${response.status} fetching recent results`);
      return [];
    }

    const data = await response.json();
    const validated = EventsSchema.parse(data);

    if (!validated.events) {
      return [];
    }

    const events: SportsEvent[] = [];

    for (const eventData of validated.events.slice(0, 5)) {
      const homeTeam = eventData.strHomeTeam || 'Unknown';
      const awayTeam = eventData.strAwayTeam || 'Unknown';
      const homeScore = eventData.intHomeScore || '';
      const awayScore = eventData.intAwayScore || '';
      const dateStr = eventData.dateEvent || '';

      // Parse date
      let timestamp = new Date();
      if (dateStr) {
        try {
          timestamp = new Date(dateStr);
        } catch {
          // Keep default timestamp
        }
      }

      events.push({
        source: 'sports_api',
        event_type: 'result',
        title: `${homeTeam} ${homeScore}:${awayScore} ${awayTeam}`,
        content: 'Bundesliga - Ergebnis',
        timestamp,
        home_team: homeTeam,
        away_team: awayTeam,
        score: `${homeScore}:${awayScore}`,
        league: 'Bundesliga',
      });
    }

    console.log(`Fetched ${events.length} recent results from TheSportsDB`);
    return events;
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error('TheSportsDB events validation error:', error.errors);
    } else {
      console.error('Error fetching recent results:', error);
    }
    return [];
  }
}

/**
 * Fetch recent Bundesliga results (with caching)
 */
export async function fetchRecentResults(): Promise<SportsEvent[]> {
  return fetchWithCache(
    `bundesliga:recent_results:${CURRENT_SEASON}`,
    fetchRecentResultsInternal,
    CACHE_DURATIONS.TEAM_FORM
  );
}

/**
 * Team form data
 */
export interface TeamForm {
  form: string; // e.g., "W-W-D-W-L"
  points: number; // Points from last 5 matches
  matches: Array<{
    home: string;
    away: string;
    score: string;
  }>;
}

/**
 * TheSportsDB team events schema
 */
const TeamEventsSchema = z.object({
  results: z.array(
    z.object({
      strHomeTeam: z.string().optional(),
      strAwayTeam: z.string().optional(),
      intHomeScore: z.string().nullable().optional(),
      intAwayScore: z.string().nullable().optional(),
    })
  ).optional(),
});

/**
 * Fetch team form (last 5 matches) for Bundesliga teams (internal, no cache)
 */
async function fetchTeamFormInternal(): Promise<Record<string, TeamForm>> {
  const teamForms: Record<string, TeamForm> = {};

  try {
    // First, get standings to get team IDs
    const standings = await fetchBundesligaStandingsInternal();

    // Get top 10 teams (most relevant for users)
    for (const teamData of standings.slice(0, 10)) {
      const teamName = teamData.team;
      const teamId = teamData.teamId;

      if (!teamId || !teamName) {
        continue;
      }

      // Fetch last 5 events for this team
      try {
        const params = new URLSearchParams({ id: teamId });
        const url = `${SPORTS_DB_BASE_URL}/eventslast.php?${params}`;

        const response = await fetch(url, {
          next: { revalidate: CACHE_DURATIONS.TEAM_FORM },
        });

        if (!response.ok) {
          console.error(`HTTP ${response.status} fetching form for ${teamName}`);
          continue;
        }

        const data = await response.json();
        const validated = TeamEventsSchema.parse(data);

        if (!validated.results) {
          continue;
        }

        // Process last 5 matches
        const matches: Array<{ home: string; away: string; score: string }> = [];
        const formLetters: string[] = [];
        let points = 0;

        for (const match of validated.results.slice(0, 5)) {
          const homeTeam = match.strHomeTeam;
          const awayTeam = match.strAwayTeam;
          const homeScore = match.intHomeScore;
          const awayScore = match.intAwayScore;

          // Skip if scores are missing
          if (homeScore === null || awayScore === null || !homeTeam || !awayTeam) {
            continue;
          }

          const homeScoreNum = parseInt(homeScore);
          const awayScoreNum = parseInt(awayScore);

          // Determine result from team's perspective
          if (homeTeam === teamName) {
            if (homeScoreNum > awayScoreNum) {
              formLetters.push('W');
              points += 3;
            } else if (homeScoreNum === awayScoreNum) {
              formLetters.push('D');
              points += 1;
            } else {
              formLetters.push('L');
            }
          } else if (awayTeam === teamName) {
            if (awayScoreNum > homeScoreNum) {
              formLetters.push('W');
              points += 3;
            } else if (awayScoreNum === homeScoreNum) {
              formLetters.push('D');
              points += 1;
            } else {
              formLetters.push('L');
            }
          }

          matches.push({
            home: homeTeam,
            away: awayTeam,
            score: `${homeScoreNum}:${awayScoreNum}`,
          });
        }

        if (formLetters.length > 0) {
          teamForms[teamName] = {
            form: formLetters.join('-'),
            points,
            matches,
          };
        }
      } catch (error) {
        console.error('Error fetching form for team:', teamName, error);
        continue;
      }
    }

    console.log(`Fetched form data for ${Object.keys(teamForms).length} teams`);
  } catch (error) {
    console.error('Error fetching team forms:', error);
  }

  return teamForms;
}

/**
 * Fetch team form (with caching)
 */
export async function fetchTeamForm(): Promise<Record<string, TeamForm>> {
  return fetchWithCache(
    `bundesliga:team_forms:${CURRENT_SEASON}`,
    fetchTeamFormInternal,
    CACHE_DURATIONS.TEAM_FORM
  );
}

/**
 * Head-to-head record between two teams
 */
export interface HeadToHeadRecord {
  team1_name: string;
  team2_name: string;
  team1_wins: number;
  draws: number;
  team2_wins: number;
  total_matches: number;
  matches: Array<{
    home: string;
    away: string;
    score: string;
    date?: string;
  }>;
}

/**
 * Fetch head-to-head record between two teams
 */
export async function fetchHeadToHead(
  teamId1: string,
  teamId2: string,
  limit: number = 10
): Promise<HeadToHeadRecord | null> {
  try {
    // Fetch recent events for team1
    const params1 = new URLSearchParams({ id: teamId1 });
    const url1 = `${SPORTS_DB_BASE_URL}/eventslast.php?${params1}`;

    const response1 = await fetch(url1, {
      next: { revalidate: CACHE_DURATIONS.H2H_RECORDS },
    });

    if (!response1.ok) {
      console.error(`HTTP ${response1.status} fetching H2H for team ${teamId1}`);
      return null;
    }

    const data1 = await response1.json();
    const validated1 = TeamEventsSchema.parse(data1);

    if (!validated1.results) {
      return null;
    }

    // Filter for matches against team2 (simplified version - full implementation would fetch both teams)
    // For now, return null to indicate this needs team event data with IDs
    console.log('H2H fetching requires team event data - placeholder');
    return null;
  } catch (error) {
    console.error('Error fetching H2H for teams:', teamId1, 'vs', teamId2, error);
    return null;
  }
}
