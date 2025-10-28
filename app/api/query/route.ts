/**
 * LLM Query API Route
 *
 * Fetches Bundesliga data and streams AI responses using Vercel AI SDK.
 */

import { anthropic } from '@ai-sdk/anthropic';
import { streamText, convertToModelMessages } from 'ai';
import { fetchKickerRss } from '@/lib/api-clients/kicker-rss';
import { toContextString } from '@/lib/models';

// Allow streaming responses up to 60 seconds
export const maxDuration = 60;

export async function POST(req: Request) {
  const { messages } = await req.json();

  // Fetch current Bundesliga data
  const newsArticles = await fetchKickerRss();

  // Build context string for LLM
  const dataContext = toContextString({
    news_articles: newsArticles,
    sports_events: [],
    player_stats: [],
    aggregation_timestamp: new Date(),
  });

  // Build system prompt with data context
  const systemPrompt = `You are Fußball GPT, a German football intelligence assistant specializing in Bundesliga.

Current Bundesliga Data:
${dataContext}

Provide accurate, context-aware responses about Bundesliga using this data. Respond in German by default unless the user asks in English.`;

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
