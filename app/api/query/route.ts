/**
 * LLM Query API Route
 *
 * Fetches Bundesliga data and streams AI responses using Vercel AI SDK.
 * Now with dynamic prompts based on user preferences!
 */

import { anthropic, type AnthropicProviderOptions } from '@ai-sdk/anthropic';
import {
  streamText,
  convertToModelMessages,
  createUIMessageStream,
  createUIMessageStreamResponse,
  type UIMessage,
} from 'ai';
import type { QueryCategory } from '@/lib/query-classifier';
import { NextRequest } from 'next/server';
import { Ratelimit } from '@upstash/ratelimit';
import { kv } from '@vercel/kv';
import { fetchKickerRss } from '@/lib/api-clients/kicker-rss';
import { fetchKickerArticlesBrave } from '@/lib/api-clients/brave-search';
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
import { classifyQuery, shouldFetchSource, estimateTokenSavings } from '@/lib/query-classifier';

// Allow streaming responses up to 60 seconds
export const maxDuration = 60;

// Map query category to effort level for Opus 4.5
const CATEGORY_EFFORT: Record<QueryCategory, 'low' | 'medium' | 'high'> = {
  news: 'low',       // Simple retrieval
  meta: 'low',       // Explaining capabilities
  general: 'medium', // Balanced
  standings: 'medium', // Data presentation
  player: 'high',    // Complex stats analysis
  match: 'high',     // Multi-factor analysis
};

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

  const body = await req.json();
  const { messages, userProfile }: { messages: UIMessage[]; userProfile?: UserProfile } = body;

  // Validate request structure
  if (!messages || !Array.isArray(messages)) {
    return new Response(
      JSON.stringify({ error: 'Invalid messages format' }),
      {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }

  // Use provided user profile or fallback to default
  const profile: UserProfile = userProfile || DEFAULT_PROFILE;

  // Extract user query for classification
  const lastMessage = messages[messages.length - 1];
  const textPart = lastMessage?.parts?.find(part => part.type === 'text');
  const userQuery = textPart?.type === 'text' ? textPart.text : 'Bundesliga';

  // Classify query to determine required data sources
  const classification = classifyQuery(userQuery);
  const tokenSavings = estimateTokenSavings(classification);

  console.log('🧠 Query Classification:', {
    query: userQuery.substring(0, 100),
    category: classification.category,
    confidence: classification.confidence.toFixed(2),
    requiredSources: classification.requiredSources,
    matchedKeywords: classification.matchedKeywords,
    tokenSavings: `${tokenSavings.savingsPercent}% (${tokenSavings.optimizedTokens.toLocaleString()} tokens vs ${tokenSavings.baselineTokens.toLocaleString()})`,
  });

  // Conditionally fetch data sources based on classification
  const [
    playerStats,
    injuries,
    standings,
    recentResults,
    teamForm,
    bettingOdds,
  ] = await Promise.all([
    shouldFetchSource('player_stats', classification) ? fetchPlayerStats() : Promise.resolve([]),
    shouldFetchSource('injuries', classification) ? fetchInjuries() : Promise.resolve([]),
    shouldFetchSource('standings', classification) ? fetchBundesligaStandings() : Promise.resolve([]),
    shouldFetchSource('results', classification) ? fetchRecentResults() : Promise.resolve([]),
    shouldFetchSource('team_form', classification) ? fetchTeamForm() : Promise.resolve([]),
    shouldFetchSource('betting_odds', classification) ? fetchBettingOdds() : Promise.resolve({}),
  ]);

  // News source strategy: Brave Search primary (query-specific, 8.5x more content)
  // Falls back to RSS if Brave unavailable/fails, then empty array if both fail
  let newsArticles = [];

  // Only fetch news if required by classification
  if (shouldFetchSource('news', classification) && process.env.BRAVE_SEARCH_API_KEY) {
    try {
      console.log('🔍 Fetching from Brave Search (primary source)...');
      newsArticles = await fetchKickerArticlesBrave(userQuery, 10);
      console.log(`✓ Brave Search: ${newsArticles.length} articles`);
    } catch (error) {
      console.error('⚠️ Brave Search failed:', error);
      console.log('→ Falling back to RSS...');
      try {
        newsArticles = await fetchKickerRss();
        console.log(`✓ RSS fallback: ${newsArticles.length} articles`);
      } catch (rssError) {
        console.error('⚠️ RSS also failed:', rssError);
        console.log('→ No news available, AI will handle gracefully');
      }
    }
  } else if (shouldFetchSource('news', classification)) {
    // No Brave API key - use RSS fallback
    console.log('📰 Using RSS (no Brave API key configured)');
    try {
      newsArticles = await fetchKickerRss();
      console.log(`✓ RSS: ${newsArticles.length} articles`);
    } catch (rssError) {
      console.error('⚠️ RSS failed:', rssError);
      console.log('→ No news available, AI will handle gracefully');
    }
  } else {
    console.log('⏭️  Skipping news fetch (not required for this query type)');
  }

  // Debug: Log first article to verify data
  if (newsArticles.length > 0) {
    const firstArticle = newsArticles[0];
    console.log('📰 Sample article data:', {
      title: firstArticle.title?.substring(0, 50),
      url: firstArticle.url,
      image_url: firstArticle.image_url,
      age: firstArticle.age,
    });
  }

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
          return `${match.homeTeam} vs ${match.awayTeam} - ${oddsStr} (${match.bookmaker}) [${match.commenceTime}]`;
        })
        .join('\n')}`
    : '';

  // Combine all context sections
  const fullContext = dataContext + standingsContext + teamFormContext + injuriesContext + oddsContext;

  // Build dynamic system prompt based on user preferences
  const systemPrompt = buildSystemPrompt(profile, fullContext);

  // Stream response from Claude Opus 4.5 with dynamic effort
  const result = streamText({
    model: anthropic('claude-opus-4-5-20251101'),
    system: systemPrompt,
    messages: convertToModelMessages(messages),
    providerOptions: {
      anthropic: {
        effort: CATEGORY_EFFORT[classification.category],
        cacheControl: { type: 'ephemeral' },
      } satisfies AnthropicProviderOptions,
    },
    onError({ error }) {
      console.error('AI SDK Error:', error);
    },
  });

  console.log('🚀 Using Opus 4.5 with effort:', CATEGORY_EFFORT[classification.category]);

  // Create UI message stream that sends articles BEFORE LLM response
  const stream = createUIMessageStream({
    execute: ({ writer }) => {
      // Stream articles immediately as data part (before LLM starts)
      // Uses 'data-articles' type which appears in message.parts
      if (newsArticles.length > 0) {
        console.log('📤 Streaming articles to client:', newsArticles.length);
        writer.write({
          type: 'data-articles',
          id: 'articles',
          data: {
            articles: newsArticles.map((article) => ({
              title: article.title,
              url: article.url,
              image_url: article.image_url,
              favicon_url: article.favicon_url,
              age: article.age,
              summary: article.summary,
            })),
          },
        });
      }

      // Merge the LLM stream
      writer.merge(result.toUIMessageStream());
    },
    onError: (error) => {
      if (error instanceof Error) {
        return `Error: ${error.message}`;
      }
      return 'An error occurred while processing your request.';
    },
  });

  return createUIMessageStreamResponse({ stream });
}
