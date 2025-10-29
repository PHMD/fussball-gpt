/**
 * LLM Query API Route
 *
 * Fetches Bundesliga data and streams AI responses using Vercel AI SDK.
 * Now with dynamic prompts based on user preferences!
 */

import { anthropic } from '@ai-sdk/anthropic';
import { streamText, convertToModelMessages } from 'ai';
import { fetchKickerRss } from '@/lib/api-clients/kicker-rss';
import { toContextString } from '@/lib/models';
import { buildSystemPrompt } from '@/lib/prompts';
import { DEFAULT_PROFILE, type UserProfile } from '@/lib/user-config';

// Allow streaming responses up to 60 seconds
export const maxDuration = 60;

export async function POST(req: Request) {
  const { messages, userProfile } = await req.json();

  // Use provided user profile or fallback to default
  const profile: UserProfile = userProfile || DEFAULT_PROFILE;

  // Fetch current Bundesliga data
  const newsArticles = await fetchKickerRss();

  // Build context string for LLM
  const dataContext = toContextString({
    news_articles: newsArticles,
    sports_events: [],
    player_stats: [],
    aggregation_timestamp: new Date(),
  });

  // Build dynamic system prompt based on user preferences
  const systemPrompt = buildSystemPrompt(profile, dataContext);

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
