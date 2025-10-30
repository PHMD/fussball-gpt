/**
 * Brave Search API client for Kicker.de archive access
 *
 * Provides site-specific search when RSS feeds have insufficient coverage (<10 articles).
 * Includes entity extraction, article classification, and session caching.
 */

import { NewsArticle } from '../models';
import { extractEntities, classifyArticleType, combineSnippets } from '../utils/entity-extraction';

const BRAVE_SEARCH_BASE_URL = 'https://api.search.brave.com/res/v1/news/search';
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

interface BraveNewsResult {
  title: string;
  description: string;
  url: string;
  thumbnail?: {
    src: string;
  };
  age?: string;
  page_age?: string;
  meta_url?: {
    scheme: string;
    netloc: string;
    hostname: string;
    favicon?: string;
    path?: string;
  };
  extra_snippets?: string[];
}

interface BraveSearchResponse {
  results?: BraveNewsResult[];
}

interface CacheEntry {
  articles: NewsArticle[];
  cachedAt: Date;
}

// Session-level cache (in-memory)
const sessionCache = new Map<number, CacheEntry>();

/**
 * Simple hash function for query caching
 */
function hashQuery(query: string): number {
  const str = query.toLowerCase().trim();
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return hash;
}

/**
 * Check if cached results are still valid
 */
function getCachedResults(queryKey: number): NewsArticle[] | null {
  const cached = sessionCache.get(queryKey);

  if (!cached) {
    return null;
  }

  const age = Date.now() - cached.cachedAt.getTime();

  if (age < CACHE_TTL_MS) {
    console.log(`[Using cached Brave Search results (${Math.floor(age / 1000)}s old)]`);
    return cached.articles;
  }

  // Expired - remove from cache
  sessionCache.delete(queryKey);
  return null;
}

/**
 * Search Kicker.de using Brave Search API
 *
 * @param query - Search query (will be prepended with "site:kicker.de Bundesliga")
 * @param maxResults - Maximum number of results to return (default: 5)
 * @returns Array of NewsArticle objects from Brave Search results
 */
export async function fetchKickerArticlesBrave(
  query: string,
  maxResults: number = 5
): Promise<NewsArticle[]> {
  const apiKey = process.env.BRAVE_SEARCH_API_KEY;

  if (!apiKey) {
    console.warn('BRAVE_SEARCH_API_KEY not configured');
    return [];
  }

  // Check session cache
  const queryKey = hashQuery(query);
  const cached = getCachedResults(queryKey);

  if (cached) {
    return cached;
  }

  const articles: NewsArticle[] = [];

  try {
    // Search kicker.de specifically for Bundesliga content using News Search
    const searchQuery = `site:kicker.de Bundesliga ${query}`;
    const url = `${BRAVE_SEARCH_BASE_URL}?q=${encodeURIComponent(searchQuery)}&count=${maxResults}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'X-Subscription-Token': apiKey,
      },
      signal: AbortSignal.timeout(2000), // 2s timeout
    });

    if (!response.ok) {
      throw new Error(`Brave Search API error: ${response.status}`);
    }

    const data: BraveSearchResponse = await response.json();

    // Extract news results
    const results = data.results || [];

    for (const result of results.slice(0, maxResults)) {
      // Extract metadata
      const title = result.title || 'No title';
      const description = result.description || '';
      const thumbnailUrl = result.thumbnail?.src;
      const faviconUrl = result.meta_url?.favicon;
      const age = result.age;
      const extraSnippets = result.extra_snippets || [];

      // Combine description + extra_snippets for richer context
      const fullContent = combineSnippets(description, extraSnippets);

      // Extract entities and classify (using description + extra snippets)
      const entities = extractEntities(title, description, extraSnippets);
      const articleType = classifyArticleType(entities);

      // Create enhanced NewsArticle with all metadata
      articles.push({
        source: 'kicker_rss', // Keep same source type for consistency
        title,
        content: fullContent,
        url: result.url,
        image_url: thumbnailUrl,
        favicon_url: faviconUrl,
        age: age,
        timestamp: new Date(), // Use current time since page_age parsing is complex
        category: `${articleType} (via Brave Search)`,
      });
    }

    if (articles.length > 0) {
      console.log(`Brave Search found ${articles.length} additional Bundesliga articles`);
    }

    // Cache results for session
    sessionCache.set(queryKey, {
      articles,
      cachedAt: new Date(),
    });

  } catch (error) {
    if (error instanceof Error) {
      if (error.name === 'AbortError' || error.message.includes('timeout')) {
        console.warn('Brave Search timeout (2s limit exceeded)');
      } else {
        console.error('Brave Search failed:', error.message);
      }
    }
  }

  return articles;
}

/**
 * Clear the session cache (useful for testing or manual refresh)
 */
export function clearBraveSearchCache(): void {
  sessionCache.clear();
  console.log('Brave Search cache cleared');
}
