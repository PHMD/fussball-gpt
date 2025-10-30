/**
 * LLM Query API Route
 *
 * Fetches Bundesliga data and streams AI responses using Vercel AI SDK.
 * Now with dynamic prompts based on user preferences!
 */

import { anthropic } from '@ai-sdk/anthropic';
import { streamText, convertToModelMessages } from 'ai';
import { NextRequest } from 'next/server';
import { Ratelimit } from '@upstash/ratelimit';
import { kv } from '@vercel/kv';
import { fetchKickerRss } from '@/lib/api-clients/kicker-rss';
import { fetchPlayerStats, fetchInjuries } from '@/lib/api-clients/api-football';
import {
  fetchBundesligaStandings,
  fetchRecentResults,
  fetchTeamForm,
} from '@/lib/api-clients/thesportsdb';
import { fetchBettingOdds } from '@/lib/api-clients/the-odds-api';
import { toContextString } from '@/lib/models';
import { buildSystemPrompt } from '@/lib/prompts';
import { DEFAULT_PROFILE, type UserProfile } from '@/lib/user-config';

// Allow streaming responses up to 60 seconds
export const maxDuration = 60;

// Rate limiting: 5 requests per 30 seconds per IP
// Only enabled in production when KV env vars are available
const ratelimit = process.env.KV_REST_API_URL
  ? new Ratelimit({
      redis: kv,
      limiter: Ratelimit.fixedWindow(5, '30s'),
    })
  : null;

export async function POST(req: NextRequest) {
  // Rate limiting check (skip in local dev when KV isn't configured)
  if (ratelimit) {
    const ip = req.ip ?? 'anonymous';
    const { success } = await ratelimit.limit(ip);

    if (!success) {
      return new Response('Rate limited! Please try again in 30 seconds.', {
        status: 429,
        headers: {
          'Retry-After': '30',
        },
      });
    }
  }

  const { messages, userProfile } = await req.json();

  // Use provided user profile or fallback to default
  const profile: UserProfile = userProfile || DEFAULT_PROFILE;

  // Fetch all Bundesliga data sources in parallel
  const [
    newsArticles,
    playerStats,
    injuries,
    standings,
    recentResults,
    teamForm,
    bettingOdds,
  ] = await Promise.all([
    fetchKickerRss(),
    fetchPlayerStats(),
    fetchInjuries(),
    fetchBundesligaStandings(),
    fetchRecentResults(),
    fetchTeamForm(),
    fetchBettingOdds(),
  ]);

  // Build context string for LLM with all data sources
  const dataContext = toContextString({
    news_articles: newsArticles,
    sports_events: [...recentResults], // Combine recent match results
    player_stats: playerStats,
    aggregation_timestamp: new Date(),
  });

  // Add supplementary context sections
  const standingsContext = standings.length > 0
    ? `\n\n## BUNDESLIGA STANDINGS (${standings[0]?.team ? '2024/25 Season' : 'Current'})\n${standings
        .map((entry) => `${entry.position}. ${entry.team} - ${entry.points} pts (${entry.played} played, GD: ${entry.goalDifference})`)
        .join('\n')}`
    : '';

  const teamFormContext = Object.keys(teamForm).length > 0
    ? `\n\n## TEAM FORM (Last 5 Matches)\n${Object.entries(teamForm)
        .map(([team, form]) => `${team}: ${form.form} (${form.points} points from last 5)`)
        .join('\n')}`
    : '';

  const injuriesContext = injuries.length > 0
    ? `\n\n## INJURIES\n${injuries
        .map((inj) => `${inj.player_name} (${inj.team}) - ${inj.injury_type || 'Unknown'} as of ${inj.date}`)
        .join('\n')}`
    : '';

  const oddsContext = Object.keys(bettingOdds).length > 0
    ? `\n\n## BETTING ODDS (European Decimal Format)\n${Object.values(bettingOdds)
        .map((match) => {
          const oddsStr = match.odds.home && match.odds.draw && match.odds.away
            ? `${match.odds.home.toFixed(2)} / ${match.odds.draw.toFixed(2)} / ${match.odds.away.toFixed(2)}`
            : 'N/A';
          return `${match.homeTeam} vs ${match.awayTeam} - ${oddsStr} (${match.bookmaker})`;
        })
        .join('\n')}`
    : '';

  // Combine all context sections
  const fullContext = dataContext + standingsContext + teamFormContext + injuriesContext + oddsContext;

  // Build dynamic system prompt based on user preferences
  const systemPrompt = buildSystemPrompt(profile, fullContext);

  // Stream response from Claude
  const result = streamText({
    model: anthropic('claude-sonnet-4-20250514'),
    system: systemPrompt,
    messages: convertToModelMessages(messages),
    onError({ error }) {
      console.error('AI SDK Error:', error);
    },
  });

  return result.toUIMessageStreamResponse({
    onError: error => {
      if (error instanceof Error) {
        return `Error: ${error.message}`;
      }
      return 'An error occurred while processing your request.';
    },
  });
}
