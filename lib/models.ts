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
 * Escape XML special characters
 */
function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Convert aggregated data to LLM context string (XML format)
 * Uses XML structure with source attributes for better citation
 */
export function toContextString(data: AggregatedData): string {
  // Handle timestamps as either Date objects or strings (from JSON serialization)
  const aggregationDate = data.aggregation_timestamp instanceof Date
    ? data.aggregation_timestamp
    : new Date(data.aggregation_timestamp);

  const lines: string[] = [
    `<timestamp>${aggregationDate.toISOString()}</timestamp>`
  ];

  if (data.news_articles.length > 0) {
    lines.push('<news_articles>');
    data.news_articles.forEach((article, index) => {
      const timestampDate = article.timestamp instanceof Date
        ? article.timestamp
        : new Date(article.timestamp);
      const date = timestampDate.toISOString().split('T')[0];

      // Number articles for easy citation: [1], [2], etc.
      // Include all metadata inline for LLM to extract
      lines.push(`  <article id="${index + 1}">`);
      lines.push(`    <title>${escapeXml(article.title)}</title>`);
      lines.push(`    <url>${article.url || ''}</url>`);
      lines.push(`    <image>${article.image_url || ''}</image>`);
      lines.push(`    <age>${article.age || date}</age>`);
      lines.push(`    <content>${escapeXml(article.content.substring(0, 300))}...</content>`);
      lines.push('  </article>');
    });
    lines.push('</news_articles>');
  }

  if (data.sports_events.length > 0) {
    lines.push('<events source="TheSportsDB">');
    for (const event of data.sports_events) {
      const timestampDate = event.timestamp instanceof Date
        ? event.timestamp
        : new Date(event.timestamp);
      const date = timestampDate.toISOString().split('T')[0];

      lines.push(`  <event type="${event.event_type}" date="${date}"${event.score ? ` score="${event.score}"` : ''}>`);
      lines.push(`    <title>${escapeXml(event.title)}</title>`);
      lines.push(`    <details>${escapeXml(event.content)}</details>`);
      lines.push('  </event>');
    }
    lines.push('</events>');
  }

  if (data.player_stats.length > 0) {
    lines.push('<player_stats source="API-Football" season="2024/25">');

    // Top scorers
    const topScorers = [...data.player_stats]
      .sort((a, b) => b.goals - a.goals)
      .slice(0, 10);

    lines.push('  <top_scorers>');
    topScorers.forEach((player, i) => {
      lines.push(`    <player rank="${i + 1}" name="${escapeXml(player.player_name)}" team="${escapeXml(player.team)}">`);
      lines.push(`      <goals>${player.goals}</goals><assists>${player.assists}</assists><minutes>${player.minutes_played}</minutes>`);
      lines.push('    </player>');
    });
    lines.push('  </top_scorers>');

    // Top assists
    const topAssists = [...data.player_stats]
      .sort((a, b) => b.assists - a.assists)
      .slice(0, 10);

    lines.push('  <top_assists>');
    topAssists.forEach((player, i) => {
      lines.push(`    <player rank="${i + 1}" name="${escapeXml(player.player_name)}" team="${escapeXml(player.team)}">`);
      lines.push(`      <assists>${player.assists}</assists><goals>${player.goals}</goals><appearances>${player.appearances}</appearances>`);
      lines.push('    </player>');
    });
    lines.push('  </top_assists>');

    lines.push('</player_stats>');
  }

  return lines.join('\n');
}
