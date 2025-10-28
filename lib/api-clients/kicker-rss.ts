/**
 * Kicker RSS feed client
 *
 * Fetches Bundesliga news from Kicker.de RSS feeds with content filtering.
 */

import Parser from 'rss-parser';
import { NewsArticle } from '../models';
import { fetchWithCache, cacheKeys, CACHE_DURATIONS } from '../cache';

const RSS_FEEDS = [
  'https://newsfeed.kicker.de/news/aktuell',   // General news (5 Bundesliga)
  'https://newsfeed.kicker.de/news/fussball',  // Soccer-specific (7 Bundesliga, some overlap)
] as const;

/**
 * Check if content is Bundesliga-related
 */
function isBundesligaContent(title: string, content: string): boolean {
  const text = `${title} ${content}`.toLowerCase();

  // Exclude non-soccer sports
  const excludedSports = ['nfl', 'quarterback', 'vikings', 'nba', 'baseball', 'hockey', 'tennis'];
  if (excludedSports.some(sport => text.includes(sport))) {
    return false;
  }

  // Bundesliga team names (major clubs)
  const bundesligaTeams = [
    'bayern', 'münchen', 'dortmund', 'bvb', 'leipzig', 'leverkusen',
    'frankfurt', 'freiburg', 'union berlin', 'köln', 'hoffenheim',
    'wolfsburg', 'gladbach', 'stuttgart', 'bremen', 'augsburg',
    'bochum', 'mainz', 'heidenheim', 'darmstadt'
  ];

  // Bundesliga keywords
  const bundesligaKeywords = ['bundesliga', '1. bundesliga', 'dfl'];

  // Check for matches
  const hasTeam = bundesligaTeams.some(team => text.includes(team));
  const hasKeyword = bundesligaKeywords.some(keyword => text.includes(keyword));

  return hasTeam || hasKeyword;
}

/**
 * Fetch Bundesliga news from Kicker RSS feeds (internal, no cache)
 */
async function fetchKickerRssInternal(): Promise<NewsArticle[]> {
  const parser = new Parser();
  const articles: NewsArticle[] = [];
  const seenUrls = new Set<string>();

  for (const feedUrl of RSS_FEEDS) {
    try {
      const feed = await parser.parseURL(feedUrl);

      // Fetch more articles since we're filtering (get 20, filter to ~5-10 Bundesliga)
      for (const entry of feed.items.slice(0, 20)) {
        const title = entry.title || 'No title';
        const content = entry.contentSnippet || entry.content || 'No content';
        const url = entry.link;

        // Skip duplicates (same article in multiple feeds)
        if (url && seenUrls.has(url)) {
          continue;
        }

        // Filter: Only include Bundesliga-related content
        if (!isBundesligaContent(title, content)) {
          continue;
        }

        // Mark as seen
        if (url) seenUrls.add(url);

        // Parse timestamp
        const timestamp = entry.pubDate ? new Date(entry.pubDate) : new Date();

        articles.push({
          source: 'kicker_rss',
          title,
          content,
          url,
          timestamp,
          category: feed.title,
        });
      }
    } catch (error) {
      console.error(`Error parsing RSS feed ${feedUrl}:`, error);
    }
  }

  return articles;
}

/**
 * Fetch Kicker RSS articles (with caching)
 *
 * Uses 6-hour cache to reduce RSS feed requests.
 */
export async function fetchKickerRss(): Promise<NewsArticle[]> {
  return fetchWithCache(
    cacheKeys.kickerRss(),
    fetchKickerRssInternal,
    CACHE_DURATIONS.TEAM_FORM // 6 hours
  );
}
