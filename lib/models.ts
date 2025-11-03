/**
 * Data models for Fußball GPT - TypeScript/Zod port from Python/Pydantic
 *
 * All data sources are normalized to these schemas for consistent LLM processing.
 */

import { z } from 'zod';

/**
 * Enumeration of supported data sources
 */
export const DataSourceSchema = z.enum(['kicker_api', 'kicker_rss', 'sports_api']);
export type DataSource = z.infer<typeof DataSourceSchema>;

/**
 * Normalized news article from any source
 */
export const NewsArticleSchema = z.object({
  source: DataSourceSchema,
  title: z.string(),
  content: z.string(),
  url: z.string().optional(),
  image_url: z.string().optional(),
  favicon_url: z.string().optional(),
  age: z.string().optional(), // Human-readable age like "1 day ago"
  summary: z.string().optional(), // AI-generated summary for carousel display
  timestamp: z.date(),
  author: z.string().optional(),
  category: z.string().optional(),
});
export type NewsArticle = z.infer<typeof NewsArticleSchema>;

/**
 * Normalized sports event data (scores, schedules, stats)
 */
export const SportsEventSchema = z.object({
  source: DataSourceSchema,
  event_type: z.string().describe('Type of event: match, score, schedule, stat'),
  title: z.string(),
  content: z.string(), // Human-readable description
  timestamp: z.date(),

  // Optional structured data
  home_team: z.string().optional(),
  away_team: z.string().optional(),
  score: z.string().optional(),
  league: z.string().optional(),
});
export type SportsEvent = z.infer<typeof SportsEventSchema>;

/**
 * Player statistics from API-Football
 */
export const PlayerStatsSchema = z.object({
  source: DataSourceSchema.default('sports_api'),
  player_name: z.string(),
  team: z.string(),
  position: z.string(),

  // Appearance stats
  appearances: z.number().default(0),
  minutes_played: z.number().default(0),

  // Performance stats
  goals: z.number().default(0),
  assists: z.number().default(0),
  shots_total: z.number().default(0),
  shots_on_target: z.number().default(0),

  // Disciplinary
  yellow_cards: z.number().default(0),
  red_cards: z.number().default(0),

  // Additional (optional)
  passes_total: z.number().optional(),
  passes_accurate: z.number().optional(),
  dribbles_successful: z.number().optional(),

  // Goalkeeper (if applicable)
  saves: z.number().optional(),
  goals_conceded: z.number().optional(),
  clean_sheets: z.number().optional(),

  // Metadata
  season: z.string().default('2024-2025'),
  league: z.string().default('Bundesliga'),
});
export type PlayerStats = z.infer<typeof PlayerStatsSchema>;

/**
 * Container for all aggregated data to pass to LLM
 */
export const AggregatedDataSchema = z.object({
  news_articles: z.array(NewsArticleSchema).default([]),
  sports_events: z.array(SportsEventSchema).default([]),
  player_stats: z.array(PlayerStatsSchema).default([]),
  aggregation_timestamp: z.date().default(() => new Date()),
});
export type AggregatedData = z.infer<typeof AggregatedDataSchema>;

/**
 * Convert aggregated data to LLM context string
 * (Port of Python's AggregatedData.to_context_string() method)
 */
export function toContextString(data: AggregatedData): string {
  // Handle timestamps as either Date objects or strings (from JSON serialization)
  const aggregationDate = data.aggregation_timestamp instanceof Date
    ? data.aggregation_timestamp
    : new Date(data.aggregation_timestamp);

  const lines: string[] = [
    `Data aggregated at: ${aggregationDate.toISOString()}\n`
  ];

  if (data.news_articles.length > 0) {
    lines.push('=== NEWS ARTICLES (Kicker Content) ===');
    for (const article of data.news_articles) {
      // Handle timestamp as either Date object or string (from JSON serialization)
      const timestampDate = article.timestamp instanceof Date
        ? article.timestamp
        : new Date(article.timestamp);
      const timestamp = timestampDate.toISOString().split('T')[0];
      const time = timestampDate.toTimeString().substring(0, 5);
      lines.push(`[${timestamp} ${time}] ${article.title}`);
      lines.push(`Source: ${article.source}`);
      if (article.url) {
        lines.push(`URL: ${article.url}`);
      }
      if (article.image_url) {
        lines.push(`Image URL: ${article.image_url}`);
      }
      if (article.favicon_url) {
        lines.push(`Favicon URL: ${article.favicon_url}`);
      }
      if (article.age) {
        lines.push(`Age: ${article.age}`);
      }
      // Truncate content for context
      const truncatedContent = article.content.substring(0, 500);
      lines.push(`Content: ${truncatedContent}...`);
      lines.push('');
    }
  }

  if (data.sports_events.length > 0) {
    lines.push('=== SPORTS EVENTS ===');
    for (const event of data.sports_events) {
      // Handle timestamp as either Date object or string (from JSON serialization)
      const timestampDate = event.timestamp instanceof Date
        ? event.timestamp
        : new Date(event.timestamp);
      const timestamp = timestampDate.toISOString().split('T')[0];
      const time = timestampDate.toTimeString().substring(0, 5);
      lines.push(`[${timestamp} ${time}] ${event.title}`);
      lines.push(`Source: ${event.source}`);
      lines.push(`Content: ${event.content}`);
      if (event.score) {
        lines.push(`Score: ${event.score}`);
      }
      lines.push('');
    }
  }

  if (data.player_stats.length > 0) {
    lines.push('=== TOP PLAYER STATISTICS (Bundesliga 2024/25 - AKTUELLE SAISON) ===');

    // Group by category for better readability
    const topScorers = [...data.player_stats]
      .sort((a, b) => b.goals - a.goals)
      .slice(0, 10);

    const topAssists = [...data.player_stats]
      .sort((a, b) => b.assists - a.assists)
      .slice(0, 10);

    lines.push('\nTop Scorers:');
    topScorers.forEach((player, i) => {
      lines.push(
        `${i + 1}. ${player.player_name} (${player.team}) - ` +
        `${player.goals} Tore, ${player.assists} Vorlagen, ${player.minutes_played} Min`
      );
    });

    lines.push('\nTop Assists:');
    topAssists.forEach((player, i) => {
      lines.push(
        `${i + 1}. ${player.player_name} (${player.team}) - ` +
        `${player.assists} Vorlagen, ${player.goals} Tore, ${player.appearances} Spiele`
      );
    });

    lines.push('');
  }

  return lines.join('\n');
}
