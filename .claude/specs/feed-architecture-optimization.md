# Feed Architecture Optimization - Technical Specification

## Executive Summary

This specification details a comprehensive refactor of the news feed system from inefficient keyword-based searches to an intelligent AI-powered pipeline with Vercel KV caching. The new architecture eliminates rate limiting issues, provides bilingual content, and delivers sub-2-second load times.

**Key Changes:**
- Single Brave Search API call (instead of 4 sequential calls)
- AI-powered categorization with multi-category support
- Upfront German→English translation during cache population
- Vercel KV caching with 15-minute TTL
- Background refresh strategy for zero perceived latency

---

## Research Sources

**Vercel KV & Caching:**
- [Vercel AI SDK - Caching Middleware](https://ai-sdk.dev/cookbook/next/caching-middleware)
- [Next.js Vercel KV Examples](https://github.com/vercel/next.js/tree/canary/examples/with-redis)
- [React Tweet KV Caching Pattern](https://github.com/vercel/react-tweet) - Clean cache key structure

**AI SDK for Categorization & Translation:**
- [Vercel AI SDK - generateText & streamText](https://ai-sdk.dev/docs/ai-sdk-core/generating-text)
- [Building AI Classifier with Vercel AI SDK](https://medium.com/@laiso/building-an-intelligent-hacker-news-classifier-with-vercel-ai-sdk-core-6221c98ba6bc)
- [Next.js AI Translation Example](https://dev.to/lico/nextjs-german-translator-example-with-openai-api-4k2f)

**Current Implementation:**
- Existing chat translation in `app/api/query/route.ts` uses Vercel AI SDK's `generateText`
- Brave Search client already exists at `lib/api-clients/brave-search.ts`

---

## Architecture Overview

### Current Flow (Problems)
```
User visits /feed
  → Frontend calls /api/feed?category=latest
  → API calls Brave Search for "highlights goals"
  → Returns articles
  → Frontend calls /api/feed?category=transfers
  → API calls Brave Search for "transfer news"
  → Returns articles
  → Frontend calls /api/feed?category=analysis
  → API calls Brave Search for "tactical analysis"
  → Returns articles
  → Frontend calls /api/feed?category=odds
  → API calls Brave Search for "betting odds"
  → Returns articles (or 429 error)

Total: 4 sequential Brave API calls, German titles, fake categories
```

### New Flow (Solution)
```
User visits /feed
  → Frontend calls /api/feed
  → API checks Vercel KV cache
  ├─ Cache HIT (< 15min old)
  │  └─ Return cached bilingual articles with AI categories
  └─ Cache MISS or stale (> 15min old)
     ├─ Return stale cache (if exists) immediately
     └─ Trigger background refresh:
        1. Single Brave Search call for "Bundesliga" (50 articles)
        2. AI categorizes each article → categories: ['Latest', 'Transfers']
        3. AI translates German titles → English
        4. Save bilingual articles to Vercel KV
        5. Next request gets fresh data

Total: 1 Brave API call, bilingual, AI-categorized
```

---

## Cache Architecture (Vercel KV)

### Cache Key Structure

**Single master key for all feed data:**
```typescript
const FEED_CACHE_KEY = 'feed:bundesliga:master';
```

**Why single key instead of per-category:**
- Articles belong to multiple categories (Latest + Transfers)
- Simpler invalidation (one key to update)
- Fewer cache reads (1 read instead of 4)

### Cache Schema

```typescript
interface CachedArticle {
  // Core fields (existing NewsArticle + enhancements)
  id: string;                    // Unique ID: hash of URL
  url: string;
  source: 'kicker_rss';         // Keep for consistency
  
  // Bilingual content (AI-translated)
  title_de: string;             // Original German title
  title_en: string;             // AI-translated English title
  content_de: string;           // Original German content/snippet
  content_en: string;           // AI-translated English content
  
  // AI-generated categorization
  categories: string[];         // e.g., ['Latest', 'Transfers', 'Analysis']
  
  // Metadata
  image_url?: string;
  favicon_url?: string;
  age?: string;                 // "2 hours ago"
  timestamp: string;            // ISO 8601 timestamp
  
  // Cache tracking
  cachedAt: string;             // When this article was cached
}

interface FeedCacheEntry {
  articles: CachedArticle[];
  lastUpdated: string;          // ISO 8601 timestamp
  ttl: number;                  // TTL in seconds (900 = 15 min)
  version: string;              // Schema version for migrations
}
```

### TTL Strategy

```typescript
// Environment variable (default 15 minutes)
const FEED_CACHE_TTL = parseInt(process.env.FEED_CACHE_TTL_SECONDS || '900');

// Cache with TTL
await kv.set(FEED_CACHE_KEY, cacheEntry, { ex: FEED_CACHE_TTL });
```

**TTL Tuning:**
- Start: 15 minutes (900 seconds)
- Monitor: Cache hit rate, user complaints about stale content
- Adjust: Decrease for breaking news scenarios, increase for stable periods

### Cache Invalidation

**Automatic (TTL-based):**
- Cache expires after 15 minutes
- Next request triggers background refresh

**Manual (if needed):**
```typescript
// Clear cache endpoint (admin only)
export async function DELETE() {
  await kv.del(FEED_CACHE_KEY);
  return NextResponse.json({ cleared: true });
}
```

---

## AI Processing Pipeline

### Overview

```
Brave Search (50 articles, German)
  ↓
AI Categorization (generateText with structured output)
  ↓
AI Translation (generateText batch processing)
  ↓
Cache Storage (Vercel KV)
```

### 1. AI Categorization

**Prompt Engineering:**

```typescript
const CATEGORIZATION_SYSTEM_PROMPT = `You are a Bundesliga football content categorizer.

Your task: Analyze German football article titles and assign relevant categories.

Available categories:
- Latest: Breaking news, recent match results, player updates
- Transfers: Player signings, transfer rumors, contract extensions
- Analysis: Tactical analysis, team performance reviews, statistics
- Betting: Odds, predictions, betting tips, fantasy football

Rules:
1. Assign 1-3 categories per article (most can belong to multiple)
2. If article is about recent match/goal → ALWAYS include "Latest"
3. If article mentions "Transfer", "Wechsel", "Vertrag" → include "Transfers"
4. If article has tactical/statistical focus → include "Analysis"
5. If article discusses odds/predictions → include "Betting"

Respond ONLY with JSON array of category names. No explanations.`;

const CATEGORIZATION_USER_PROMPT = (title: string, snippet: string) => `
Title: ${title}
Snippet: ${snippet}

Categories:`;

// Implementation
import { generateText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';

async function categorizeArticle(
  title: string,
  content: string
): Promise<string[]> {
  try {
    const { text } = await generateText({
      model: anthropic('claude-sonnet-4-20250514'),
      system: CATEGORIZATION_SYSTEM_PROMPT,
      prompt: CATEGORIZATION_USER_PROMPT(title, content.substring(0, 300)),
      temperature: 0.3, // Low temperature for consistent categorization
      maxSteps: 1,
    });

    // Parse JSON response
    const categories = JSON.parse(text.trim()) as string[];
    
    // Validation
    const validCategories = ['Latest', 'Transfers', 'Analysis', 'Betting'];
    return categories.filter(c => validCategories.includes(c));
    
  } catch (error) {
    console.error('Categorization failed:', error);
    // Fallback: assign to "Latest" if AI fails
    return ['Latest'];
  }
}
```

**Why Claude Sonnet 4 (not GPT):**
- Already using Anthropic in chat (consistency)
- Excellent multilingual capabilities for German content
- Fast response times for batch processing

**Batch Processing Strategy:**
```typescript
// Process articles in parallel (max 10 concurrent)
const CONCURRENCY_LIMIT = 10;

async function categorizeArticles(
  articles: NewsArticle[]
): Promise<Map<string, string[]>> {
  const results = new Map<string, string[]>();
  
  for (let i = 0; i < articles.length; i += CONCURRENCY_LIMIT) {
    const batch = articles.slice(i, i + CONCURRENCY_LIMIT);
    
    const batchResults = await Promise.all(
      batch.map(article =>
        categorizeArticle(article.title, article.content)
          .then(categories => ({ url: article.url, categories }))
      )
    );
    
    batchResults.forEach(({ url, categories }) => {
      results.set(url, categories);
    });
  }
  
  return results;
}
```

### 2. AI Translation

**Prompt Engineering:**

```typescript
const TRANSLATION_SYSTEM_PROMPT = `You are a German→English football translation expert.

Rules:
1. Translate German football articles to natural English
2. Keep proper nouns unchanged (player names, team names)
3. Preserve football terminology (e.g., "Bundesliga" stays "Bundesliga")
4. Be concise - match the tone of the original
5. Respond ONLY with the English translation. No explanations.`;

const TRANSLATION_USER_PROMPT = (germanText: string) => `
Translate to English:

${germanText}`;

// Implementation
async function translateToEnglish(germanText: string): Promise<string> {
  try {
    const { text } = await generateText({
      model: anthropic('claude-sonnet-4-20250514'),
      system: TRANSLATION_SYSTEM_PROMPT,
      prompt: TRANSLATION_USER_PROMPT(germanText),
      temperature: 0.2, // Very low for consistent translations
      maxSteps: 1,
    });

    return text.trim();
    
  } catch (error) {
    console.error('Translation failed:', error);
    // Fallback: return original German text
    return germanText;
  }
}
```

**Batch Translation Strategy:**

```typescript
async function translateArticles(
  articles: NewsArticle[]
): Promise<Map<string, { title_en: string; content_en: string }>> {
  const results = new Map();
  
  for (let i = 0; i < articles.length; i += CONCURRENCY_LIMIT) {
    const batch = articles.slice(i, i + CONCURRENCY_LIMIT);
    
    const batchResults = await Promise.all(
      batch.map(async (article) => {
        // Translate title and first 300 chars of content in parallel
        const [title_en, content_en] = await Promise.all([
          translateToEnglish(article.title),
          translateToEnglish(article.content.substring(0, 300)),
        ]);
        
        return {
          url: article.url,
          title_en,
          content_en,
        };
      })
    );
    
    batchResults.forEach(({ url, title_en, content_en }) => {
      results.set(url, { title_en, content_en });
    });
  }
  
  return results;
}
```

### 3. Combined Processing Pipeline

```typescript
async function processArticles(
  rawArticles: NewsArticle[]
): Promise<CachedArticle[]> {
  console.log(`Processing ${rawArticles.length} articles...`);
  
  // Step 1: Categorize in parallel
  const categoriesMap = await categorizeArticles(rawArticles);
  
  // Step 2: Translate in parallel
  const translationsMap = await translateArticles(rawArticles);
  
  // Step 3: Combine results
  const processedArticles: CachedArticle[] = rawArticles.map((article) => {
    const categories = categoriesMap.get(article.url) || ['Latest'];
    const { title_en, content_en } = translationsMap.get(article.url) || {
      title_en: article.title,
      content_en: article.content,
    };
    
    return {
      id: hashUrl(article.url),
      url: article.url,
      source: 'kicker_rss',
      title_de: article.title,
      title_en,
      content_de: article.content,
      content_en,
      categories,
      image_url: article.image_url,
      favicon_url: article.favicon_url,
      age: article.age,
      timestamp: article.timestamp.toISOString(),
      cachedAt: new Date().toISOString(),
    };
  });
  
  console.log(`Processed ${processedArticles.length} articles`);
  return processedArticles;
}

// Simple hash function for generating article IDs
function hashUrl(url: string): string {
  let hash = 0;
  for (let i = 0; i < url.length; i++) {
    const char = url.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return `article_${Math.abs(hash)}`;
}
```

---

## API Design

### File Structure

```
/lib/services/feed-cache.ts          # Cache management layer
/lib/services/ai-processor.ts        # AI categorization + translation
/app/api/feed/route.ts                # Main feed API (modified)
/app/api/feed/refresh/route.ts        # Background refresh trigger (new)
```

### 1. Feed Cache Service (`/lib/services/feed-cache.ts`)

```typescript
/**
 * Feed Cache Service
 * 
 * Manages Vercel KV cache for news feed articles.
 * Handles cache reads, writes, and background refresh logic.
 */

import { kv } from '@vercel/kv';
import type { CachedArticle, FeedCacheEntry } from '@/lib/models';

const FEED_CACHE_KEY = 'feed:bundesliga:master';
const FEED_CACHE_TTL = parseInt(process.env.FEED_CACHE_TTL_SECONDS || '900'); // 15 min
const CACHE_VERSION = '1.0.0';

export async function getFeedCache(): Promise<FeedCacheEntry | null> {
  try {
    const cached = await kv.get<FeedCacheEntry>(FEED_CACHE_KEY);
    
    if (!cached) {
      return null;
    }
    
    // Check version compatibility
    if (cached.version !== CACHE_VERSION) {
      console.warn('Cache version mismatch, invalidating...');
      await kv.del(FEED_CACHE_KEY);
      return null;
    }
    
    return cached;
  } catch (error) {
    console.error('Failed to read feed cache:', error);
    return null;
  }
}

export async function setFeedCache(
  articles: CachedArticle[]
): Promise<void> {
  try {
    const cacheEntry: FeedCacheEntry = {
      articles,
      lastUpdated: new Date().toISOString(),
      ttl: FEED_CACHE_TTL,
      version: CACHE_VERSION,
    };
    
    await kv.set(FEED_CACHE_KEY, cacheEntry, { ex: FEED_CACHE_TTL });
    console.log(`Cached ${articles.length} articles (TTL: ${FEED_CACHE_TTL}s)`);
  } catch (error) {
    console.error('Failed to write feed cache:', error);
    throw error;
  }
}

export async function clearFeedCache(): Promise<void> {
  await kv.del(FEED_CACHE_KEY);
  console.log('Feed cache cleared');
}

export function isCacheStale(cache: FeedCacheEntry): boolean {
  const cacheAge = Date.now() - new Date(cache.lastUpdated).getTime();
  return cacheAge > (FEED_CACHE_TTL * 1000);
}
```

### 2. AI Processor Service (`/lib/services/ai-processor.ts`)

```typescript
/**
 * AI Processor Service
 * 
 * Handles AI-powered categorization and translation of articles.
 * Uses Vercel AI SDK with Claude Sonnet 4.
 */

import { generateText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';
import type { NewsArticle, CachedArticle } from '@/lib/models';

const CONCURRENCY_LIMIT = 10;
const VALID_CATEGORIES = ['Latest', 'Transfers', 'Analysis', 'Betting'];

// Categorization prompts (see AI Processing Pipeline section above)
const CATEGORIZATION_SYSTEM_PROMPT = `You are a Bundesliga football content categorizer...`;

async function categorizeArticle(
  title: string,
  content: string
): Promise<string[]> {
  // Implementation from AI Processing Pipeline section
}

async function translateToEnglish(germanText: string): Promise<string> {
  // Implementation from AI Processing Pipeline section
}

export async function processArticles(
  rawArticles: NewsArticle[]
): Promise<CachedArticle[]> {
  // Implementation from AI Processing Pipeline section
}
```

### 3. Main Feed API (`/app/api/feed/route.ts`)

```typescript
/**
 * Feed API Endpoint
 * 
 * Serves cached, AI-processed feed articles.
 * Triggers background refresh if cache is stale.
 */

import { NextRequest, NextResponse } from 'next/server';
import { getFeedCache, isCacheStale } from '@/lib/services/feed-cache';
import { Language } from '@/lib/user-config';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const category = searchParams.get('category') || 'all';
    const language = (searchParams.get('language') || 'de') as Language;
    
    // 1. Check cache
    const cache = await getFeedCache();
    
    if (!cache) {
      // Cold start: No cache exists
      // Trigger background refresh and return empty state
      triggerBackgroundRefresh();
      
      return NextResponse.json({
        articles: [],
        message: 'Cache warming up, please refresh in a few seconds',
        cached: false,
      });
    }
    
    // 2. Filter articles by category
    let articles = cache.articles;
    
    if (category !== 'all') {
      const categoryLabel = mapCategoryParam(category);
      articles = articles.filter(a => a.categories.includes(categoryLabel));
    }
    
    // 3. Map to language-specific response
    const responseArticles = articles.map(article => ({
      source: article.source,
      title: language === Language.ENGLISH ? article.title_en : article.title_de,
      content: language === Language.ENGLISH ? article.content_en : article.content_de,
      url: article.url,
      image_url: article.image_url,
      favicon_url: article.favicon_url,
      age: article.age,
      timestamp: new Date(article.timestamp),
      category: article.categories.join(', '),
    }));
    
    // 4. Trigger background refresh if stale (don't wait)
    if (isCacheStale(cache)) {
      triggerBackgroundRefresh();
    }
    
    return NextResponse.json({
      articles: responseArticles,
      count: responseArticles.length,
      category,
      language,
      cached: true,
      lastUpdated: cache.lastUpdated,
    });
    
  } catch (error) {
    console.error('[Feed API] Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch feed articles' },
      { status: 500 }
    );
  }
}

function mapCategoryParam(param: string): string {
  const mapping: Record<string, string> = {
    'latest': 'Latest',
    'transfers': 'Transfers',
    'analysis': 'Analysis',
    'odds': 'Betting',
  };
  return mapping[param] || 'Latest';
}

function triggerBackgroundRefresh() {
  // Fire-and-forget fetch to refresh endpoint
  fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/api/feed/refresh`, {
    method: 'POST',
  }).catch(err => console.error('Background refresh trigger failed:', err));
}
```

### 4. Background Refresh API (`/app/api/feed/refresh/route.ts`)

```typescript
/**
 * Feed Refresh API
 * 
 * Background endpoint for refreshing feed cache.
 * Fetches from Brave Search, processes with AI, updates cache.
 */

import { NextRequest, NextResponse } from 'next/server';
import { fetchKickerArticlesBrave } from '@/lib/api-clients/brave-search';
import { processArticles } from '@/lib/services/ai-processor';
import { setFeedCache } from '@/lib/services/feed-cache';

// Prevent multiple concurrent refreshes
let isRefreshing = false;

export async function POST(request: NextRequest) {
  // Check if already refreshing
  if (isRefreshing) {
    return NextResponse.json({
      message: 'Refresh already in progress',
      status: 'skipped',
    });
  }
  
  isRefreshing = true;
  
  try {
    console.log('[Feed Refresh] Starting background refresh...');
    
    // Step 1: Fetch from Brave Search (single call)
    const rawArticles = await fetchKickerArticlesBrave('Bundesliga', 50);
    console.log(`[Feed Refresh] Fetched ${rawArticles.length} articles from Brave`);
    
    if (rawArticles.length === 0) {
      throw new Error('No articles returned from Brave Search');
    }
    
    // Step 2: Process with AI (categorize + translate)
    const processedArticles = await processArticles(rawArticles);
    console.log(`[Feed Refresh] Processed ${processedArticles.length} articles with AI`);
    
    // Step 3: Update cache
    await setFeedCache(processedArticles);
    console.log('[Feed Refresh] Cache updated successfully');
    
    return NextResponse.json({
      message: 'Feed refreshed successfully',
      status: 'success',
      articlesProcessed: processedArticles.length,
      timestamp: new Date().toISOString(),
    });
    
  } catch (error) {
    console.error('[Feed Refresh] Error:', error);
    
    return NextResponse.json(
      {
        message: 'Feed refresh failed',
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
    
  } finally {
    isRefreshing = false;
  }
}
```

---

## Frontend Modifications

### `/app/feed/page.tsx` Changes

```typescript
/**
 * Newsfeed Page
 * 
 * Modified to use single API call with cached, bilingual data.
 */

'use client';

import { useEffect, useState } from 'react';
import { ArticleCategorySection } from '@/components/feed/article-category-section';
import { Button } from '@/components/ui/button';
import { RefreshCw, Settings } from 'lucide-react';
import { useUserPreferences } from '@/hooks/use-user-preferences';
import { SettingsPanel } from '@/components/settings/settings-panel';
import { Loader } from '@/components/ui/loader';
import type { NewsArticle } from '@/lib/models';
import { Language } from '@/lib/user-config';

interface FeedResponse {
  articles: NewsArticle[];
  count: number;
  category: string;
  language: string;
  cached: boolean;
  lastUpdated?: string;
}

// Feed categories - rendered as horizontal sections
const categories = [
  { id: 'latest' as const, label: { en: 'Latest', de: 'Aktuelles' } },
  { id: 'transfers' as const, label: { en: 'Transfers', de: 'Transfers' } },
  { id: 'analysis' as const, label: { en: 'Analysis', de: 'Analysen' } },
  { id: 'odds' as const, label: { en: 'Betting', de: 'Wetten' } },
];

export default function FeedPage() {
  const { profile, updateProfile } = useUserPreferences();
  const [showSettings, setShowSettings] = useState(false);
  const [feedData, setFeedData] = useState<Record<string, NewsArticle[]>>({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const isGerman = profile.language === Language.GERMAN;

  /**
   * Fetch feed data - SINGLE API CALL for all categories
   */
  const fetchFeed = async (forceRefresh = false) => {
    if (forceRefresh) {
      setRefreshing(true);
    }
    
    setLoading(true);

    try {
      // Single call to get ALL articles
      const res = await fetch(
        `/api/feed?language=${profile.language}&category=all`,
        { cache: forceRefresh ? 'no-store' : 'default' }
      );

      if (res.ok) {
        const data: FeedResponse = await res.json();
        
        // Group articles by category
        const grouped: Record<string, NewsArticle[]> = {};
        
        categories.forEach((cat) => {
          grouped[cat.id] = data.articles.filter((article: NewsArticle) =>
            article.category?.includes(cat.label.en)
          );
        });
        
        setFeedData(grouped);
        setLastUpdated(data.lastUpdated || null);
      }
    } catch (error) {
      console.error('Error fetching feed:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Load feed on mount or language change
  useEffect(() => {
    fetchFeed();
  }, [profile.language]);

  /**
   * Handle refresh button click
   */
  const handleRefresh = async () => {
    // Force cache refresh
    await fetch('/api/feed/refresh', { method: 'POST' });
    
    // Wait 2 seconds for refresh to complete, then fetch
    setTimeout(() => fetchFeed(true), 2000);
  };

  return (
    <>
      {/* Settings Panel */}
      {showSettings && (
        <SettingsPanel
          profile={profile}
          onUpdate={updateProfile}
          onClose={() => setShowSettings(false)}
        />
      )}

      {/* Feed Header */}
      <div className="border-b bg-card sticky top-0 z-10">
        <div className="p-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">
              {isGerman ? 'News-Feed' : 'News Feed'}
            </h1>
            <p className="text-sm text-muted-foreground">
              {isGerman
                ? 'Personalisierte Bundesliga-Nachrichten'
                : 'Personalized Bundesliga news'}
            </p>
            {lastUpdated && (
              <p className="text-xs text-muted-foreground mt-1">
                {isGerman ? 'Aktualisiert: ' : 'Updated: '}
                {new Date(lastUpdated).toLocaleString(
                  isGerman ? 'de-DE' : 'en-US'
                )}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={handleRefresh}
              disabled={refreshing}
              aria-label={isGerman ? 'Aktualisieren' : 'Refresh'}
            >
              <RefreshCw className={`h-5 w-5 ${refreshing ? 'animate-spin' : ''}`} />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => setShowSettings(true)}
              aria-label={isGerman ? 'Einstellungen' : 'Settings'}
            >
              <Settings className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Feed Content - Horizontal Sections */}
      <div className="max-w-7xl mx-auto py-6 space-y-8">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <Loader size={32} />
            <p className="mt-4 text-sm text-muted-foreground">
              {isGerman ? 'Lade Artikel...' : 'Loading articles...'}
            </p>
          </div>
        ) : (
          <>
            {categories.map((category) => {
              const articles = feedData[category.id] || [];

              if (articles.length === 0) return null;

              return (
                <ArticleCategorySection
                  key={category.id}
                  title={isGerman ? category.label.de : category.label.en}
                  articles={articles}
                />
              );
            })}
          </>
        )}
      </div>
    </>
  );
}
```

**Key Changes:**
1. Single API call instead of 4 sequential calls
2. Language parameter passed to API
3. Articles pre-translated based on user language
4. Grouping happens client-side (articles already have categories)
5. Force refresh triggers background cache update

---

## Data Models

### Updated Types (`/lib/models.ts`)

```typescript
/**
 * Enhanced types for cached, bilingual articles
 */

import { z } from 'zod';

// Existing NewsArticle schema (unchanged for backwards compatibility)
export const NewsArticleSchema = z.object({
  source: z.enum(['kicker_api', 'kicker_rss', 'sports_api']),
  title: z.string(),
  content: z.string(),
  url: z.string().optional(),
  image_url: z.string().optional(),
  favicon_url: z.string().optional(),
  age: z.string().optional(),
  summary: z.string().optional(),
  timestamp: z.date(),
  author: z.string().optional(),
  category: z.string().optional(),
});
export type NewsArticle = z.infer<typeof NewsArticleSchema>;

// New cached article schema (bilingual + AI-categorized)
export const CachedArticleSchema = z.object({
  id: z.string(),
  url: z.string(),
  source: z.enum(['kicker_api', 'kicker_rss', 'sports_api']),
  
  // Bilingual content
  title_de: z.string(),
  title_en: z.string(),
  content_de: z.string(),
  content_en: z.string(),
  
  // AI-generated categories
  categories: z.array(z.enum(['Latest', 'Transfers', 'Analysis', 'Betting'])),
  
  // Metadata
  image_url: z.string().optional(),
  favicon_url: z.string().optional(),
  age: z.string().optional(),
  timestamp: z.string(), // ISO 8601
  cachedAt: z.string(),  // ISO 8601
});
export type CachedArticle = z.infer<typeof CachedArticleSchema>;

// Cache entry schema
export const FeedCacheEntrySchema = z.object({
  articles: z.array(CachedArticleSchema),
  lastUpdated: z.string(), // ISO 8601
  ttl: z.number(),
  version: z.string(),
});
export type FeedCacheEntry = z.infer<typeof FeedCacheEntrySchema>;
```

---

## Error Handling Strategy

### 1. Cache Read Failures

```typescript
async function getFeedCache(): Promise<FeedCacheEntry | null> {
  try {
    return await kv.get<FeedCacheEntry>(FEED_CACHE_KEY);
  } catch (error) {
    console.error('Cache read failed:', error);
    // Return null to trigger fresh fetch
    return null;
  }
}
```

### 2. Brave Search Failures

```typescript
try {
  const rawArticles = await fetchKickerArticlesBrave('Bundesliga', 50);
} catch (error) {
  console.error('Brave Search failed:', error);
  
  // Fallback 1: Try with fewer results
  try {
    rawArticles = await fetchKickerArticlesBrave('Bundesliga', 20);
  } catch (retryError) {
    // Fallback 2: Return error, keep stale cache
    throw new Error('All Brave Search attempts failed');
  }
}
```

### 3. AI Processing Failures

```typescript
async function categorizeArticle(title: string, content: string): Promise<string[]> {
  try {
    const { text } = await generateText({ /* ... */ });
    return JSON.parse(text.trim());
  } catch (error) {
    console.error('Categorization failed:', error);
    // Graceful degradation: Assign to "Latest" category
    return ['Latest'];
  }
}

async function translateToEnglish(germanText: string): Promise<string> {
  try {
    const { text } = await generateText({ /* ... */ });
    return text.trim();
  } catch (error) {
    console.error('Translation failed:', error);
    // Graceful degradation: Return original German text
    return germanText;
  }
}
```

### 4. Partial AI Failures

```typescript
async function processArticles(rawArticles: NewsArticle[]): Promise<CachedArticle[]> {
  const categoriesMap = await categorizeArticles(rawArticles);
  const translationsMap = await translateArticles(rawArticles);
  
  return rawArticles.map((article) => {
    // Fallback to defaults if AI failed for this article
    const categories = categoriesMap.get(article.url) || ['Latest'];
    const { title_en, content_en } = translationsMap.get(article.url) || {
      title_en: article.title,  // Keep German if translation failed
      content_en: article.content,
    };
    
    return { /* ... */ };
  });
}
```

### 5. Frontend Error Handling

```typescript
const fetchFeed = async (forceRefresh = false) => {
  try {
    const res = await fetch(`/api/feed?language=${profile.language}&category=all`);
    
    if (!res.ok) {
      throw new Error(`API returned ${res.status}`);
    }
    
    const data = await res.json();
    
    if (!data.articles || data.articles.length === 0) {
      // Show empty state
      setFeedData({});
      return;
    }
    
    // Group articles...
  } catch (error) {
    console.error('Feed fetch failed:', error);
    // Show error toast or message
    // Keep existing feed data if available (stale is better than nothing)
  }
};
```

---

## Testing Strategy

### 1. E2E Tests (Playwright)

**File:** `tests/feed-architecture.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feed Architecture', () => {
  
  test('should load feed with single API call', async ({ page }) => {
    // Monitor network requests
    const apiCalls: string[] = [];
    page.on('request', (request) => {
      if (request.url().includes('/api/feed')) {
        apiCalls.push(request.url());
      }
    });
    
    await page.goto('/feed');
    
    // Wait for content
    await expect(page.locator('h1')).toContainText('News Feed');
    
    // Verify ONLY ONE API call was made
    expect(apiCalls.length).toBe(1);
    expect(apiCalls[0]).toContain('category=all');
  });
  
  test('should display bilingual content correctly (German)', async ({ page }) => {
    // Set language to German
    await page.goto('/feed');
    await page.click('button[aria-label="Einstellungen"]');
    await page.selectOption('select[name="language"]', 'de');
    
    // Verify German titles are displayed
    const articleTitle = await page.locator('[data-testid="article-title"]').first().textContent();
    expect(articleTitle).toBeTruthy();
    // German articles typically have "ä", "ö", "ü" characters
    // or common German football terms
  });
  
  test('should display bilingual content correctly (English)', async ({ page }) => {
    await page.goto('/feed');
    await page.click('button[aria-label="Settings"]');
    await page.selectOption('select[name="language"]', 'en');
    
    // Verify English titles are displayed (no German special characters)
    const articleTitle = await page.locator('[data-testid="article-title"]').first().textContent();
    expect(articleTitle).toBeTruthy();
    expect(articleTitle).not.toMatch(/[äöüßÄÖÜ]/); // No German umlauts
  });
  
  test('should show articles in correct categories', async ({ page }) => {
    await page.goto('/feed');
    
    // Wait for categories to load
    await page.waitForSelector('[data-testid="category-section"]');
    
    // Verify all 4 categories are present
    const categories = await page.locator('[data-testid="category-section"]').count();
    expect(categories).toBeGreaterThan(0);
    
    // Verify category labels
    await expect(page.locator('h2:has-text("Latest")')).toBeVisible();
    await expect(page.locator('h2:has-text("Transfers")')).toBeVisible();
    await expect(page.locator('h2:has-text("Analysis")')).toBeVisible();
    await expect(page.locator('h2:has-text("Betting")')).toBeVisible();
  });
  
  test('should refresh feed on button click', async ({ page }) => {
    await page.goto('/feed');
    
    // Wait for initial load
    await page.waitForSelector('[data-testid="article-card"]');
    
    // Click refresh button
    await page.click('button[aria-label="Refresh"]');
    
    // Verify refresh indicator appears
    await expect(page.locator('.animate-spin')).toBeVisible();
    
    // Wait for refresh to complete
    await page.waitForSelector('.animate-spin', { state: 'hidden', timeout: 10000 });
    
    // Verify content is still present
    await expect(page.locator('[data-testid="article-card"]')).toBeVisible();
  });
  
  test('should load in under 2 seconds', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/feed');
    await page.waitForSelector('[data-testid="article-card"]');
    
    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(2000); // < 2 seconds
  });
  
});
```

### 2. Unit Tests

**Cache Service Tests:**
```typescript
describe('FeedCacheService', () => {
  test('should set and get cache', async () => {
    const articles: CachedArticle[] = [/* ... */];
    await setFeedCache(articles);
    const cached = await getFeedCache();
    expect(cached?.articles).toHaveLength(articles.length);
  });
  
  test('should detect stale cache', () => {
    const freshCache: FeedCacheEntry = {
      articles: [],
      lastUpdated: new Date().toISOString(),
      ttl: 900,
      version: '1.0.0',
    };
    expect(isCacheStale(freshCache)).toBe(false);
    
    const staleCache: FeedCacheEntry = {
      articles: [],
      lastUpdated: new Date(Date.now() - 1000000).toISOString(),
      ttl: 900,
      version: '1.0.0',
    };
    expect(isCacheStale(staleCache)).toBe(true);
  });
});
```

**AI Processor Tests:**
```typescript
describe('AIProcessor', () => {
  test('should categorize article correctly', async () => {
    const categories = await categorizeArticle(
      'Bayern Munich signs new striker',
      'Transfer news...'
    );
    expect(categories).toContain('Transfers');
    expect(categories).toContain('Latest');
  });
  
  test('should translate German to English', async () => {
    const english = await translateToEnglish('Bayern München gewinnt');
    expect(english).toContain('Bayern');
    expect(english.toLowerCase()).toContain('win');
  });
  
  test('should handle AI failures gracefully', async () => {
    // Mock AI failure
    jest.spyOn(console, 'error').mockImplementation();
    const categories = await categorizeArticle('', '');
    expect(categories).toEqual(['Latest']); // Fallback
  });
});
```

### 3. Manual Testing Checklist

- [ ] Feed loads < 2 seconds on cold start
- [ ] Feed loads instantly from cache on subsequent visits
- [ ] German language shows German titles
- [ ] English language shows English titles
- [ ] Articles appear in correct categories
- [ ] Multi-category articles appear in multiple sections
- [ ] Refresh button triggers cache update
- [ ] No rate limiting errors (429) from Brave Search
- [ ] Cache invalidates after 15 minutes
- [ ] Background refresh works when cache is stale
- [ ] Error states display correctly (empty feed, API failures)

---

## Migration Plan

### Phase 1: Preparation (No user impact)

1. **Add new dependencies:**
   ```bash
   # Already have these:
   # - @vercel/kv
   # - ai
   # - @ai-sdk/anthropic
   ```

2. **Create new files:**
   - `/lib/services/feed-cache.ts`
   - `/lib/services/ai-processor.ts`
   - `/app/api/feed/refresh/route.ts`

3. **Update environment variables:**
   ```env
   # .env.local
   FEED_CACHE_TTL_SECONDS=900  # 15 minutes
   ```

4. **Test in development:**
   - Verify Vercel KV connection works
   - Test AI categorization on sample articles
   - Test AI translation on sample articles
   - Validate cache read/write

### Phase 2: Deploy with Feature Flag (Canary testing)

1. **Add feature flag to user config:**
   ```typescript
   // lib/user-config.ts
   export interface UserProfile {
     // ... existing fields
     experimental_newFeed?: boolean; // Default: false
   }
   ```

2. **Conditional routing in frontend:**
   ```typescript
   // app/feed/page.tsx
   const endpoint = profile.experimental_newFeed
     ? '/api/feed?category=all'  // New endpoint
     : '/api/feed?category=latest'; // Old endpoint (fallback)
   ```

3. **Deploy to production:**
   - New API routes available but not used by default
   - Enable for internal testing first
   - Monitor Vercel KV metrics and AI SDK usage

### Phase 3: Gradual Rollout

1. **Enable for 10% of users:**
   ```typescript
   const useNewFeed = profile.experimental_newFeed || (Math.random() < 0.1);
   ```

2. **Monitor metrics:**
   - Cache hit rate
   - Feed load times
   - Brave Search API usage (should drop 75%)
   - AI SDK usage (new cost)
   - Error rates

3. **Scale to 50%, then 100%**

### Phase 4: Cleanup (After 100% rollout)

1. **Remove old category-based endpoints:**
   - Delete `/api/feed?category=latest` logic
   - Keep only `/api/feed?category=all` logic

2. **Remove feature flag:**
   - Delete `experimental_newFeed` from user config
   - Remove conditional routing

3. **Update documentation:**
   - Mark old API as deprecated

---

## Performance Benchmarks

### Expected Performance

| Metric | Current | Target | Actual (Post-Launch) |
|--------|---------|--------|---------------------|
| Feed load time (cold) | 8-12s | < 2s | TBD |
| Feed load time (cached) | 2-4s | < 500ms | TBD |
| Brave API calls per feed load | 4 | 1 (background) | TBD |
| Rate limit errors (429) | Frequent | 0 | TBD |
| Cache hit rate | N/A | > 90% | TBD |
| AI processing time | N/A | < 30s | TBD |

### Cost Analysis

**Current (per 1000 feed loads):**
- Brave Search: 4 calls × 1000 = 4000 API calls
- Rate limits cause failures → Poor UX

**New (per 1000 feed loads):**
- Brave Search: ~67 calls (1 per 15 min × 16.67 hours)
- AI SDK (Claude Sonnet 4): 
  - Categorization: 50 articles × 67 refreshes = 3,350 calls
  - Translation: 100 translations × 67 refreshes = 6,700 calls
  - Total tokens: ~2M input + 500K output
  - Cost: ~$6-8 per 1000 feed loads

**Trade-off:** Higher AI costs for better UX and no rate limiting

---

## Security Considerations

### 1. Rate Limiting (Vercel KV)

```typescript
import { Ratelimit } from '@upstash/ratelimit';
import { kv } from '@vercel/kv';

const feedRatelimit = new Ratelimit({
  redis: kv,
  limiter: Ratelimit.slidingWindow(20, '1 m'), // 20 requests per minute
});

export async function GET(request: NextRequest) {
  const ip = request.ip ?? 'anonymous';
  const { success } = await feedRatelimit.limit(`feed_${ip}`);
  
  if (!success) {
    return NextResponse.json(
      { error: 'Too many requests' },
      { status: 429 }
    );
  }
  
  // ... rest of handler
}
```

### 2. Input Validation

```typescript
// Validate category parameter
const categorySchema = z.enum(['all', 'latest', 'transfers', 'analysis', 'odds']);
const category = categorySchema.parse(searchParams.get('category'));

// Validate language parameter
const languageSchema = z.nativeEnum(Language);
const language = languageSchema.parse(searchParams.get('language'));
```

### 3. Cache Poisoning Prevention

```typescript
// Version check prevents loading incompatible cached data
if (cached.version !== CACHE_VERSION) {
  await kv.del(FEED_CACHE_KEY);
  return null;
}

// Hash URLs for consistent IDs
function hashUrl(url: string): string {
  // Prevent cache collision attacks by using cryptographic hash
  return `article_${crypto.subtle.digest('SHA-256', new TextEncoder().encode(url))}`;
}
```

### 4. AI Prompt Injection Prevention

```typescript
// Sanitize user-provided content before AI processing
function sanitizeForAI(text: string): string {
  return text
    .replace(/[<>]/g, '') // Remove potential HTML/XML
    .substring(0, 1000);   // Limit length
}

const { text } = await generateText({
  prompt: CATEGORIZATION_USER_PROMPT(
    sanitizeForAI(article.title),
    sanitizeForAI(article.content)
  ),
});
```

---

## Dependencies

### Already Installed (No new dependencies needed)

```json
{
  "@vercel/kv": "^3.0.0",          // Vercel KV for caching
  "ai": "^5.0.82",                  // Vercel AI SDK
  "@ai-sdk/anthropic": "^2.0.38",  // Claude Sonnet 4
  "zod": "^3.24.2"                  // Schema validation
}
```

### Environment Variables

```env
# Required (already have)
ANTHROPIC_API_KEY=your_key
BRAVE_SEARCH_API_KEY=your_key

# Required (Vercel KV - auto-configured on Vercel)
KV_URL=your_vercel_kv_url
KV_REST_API_URL=your_vercel_kv_rest_url
KV_REST_API_TOKEN=your_vercel_kv_token
KV_REST_API_READ_ONLY_TOKEN=your_vercel_kv_readonly_token

# Optional (new)
FEED_CACHE_TTL_SECONDS=900  # Default: 15 minutes
```

---

## Estimated Complexity

**Development Time:** 12-16 hours
- Feed cache service: 2 hours
- AI processor service: 4 hours
- API route modifications: 3 hours
- Frontend modifications: 2 hours
- Testing: 3-4 hours
- Deployment & monitoring: 2 hours

**Risk Level:** Medium

**Risks:**
1. **AI processing time:** 50 articles × 2 AI calls each = 100 AI calls
   - Mitigation: Batch processing with concurrency limit (10 concurrent)
   - Expected: ~20-30 seconds for full refresh (acceptable for background)

2. **AI costs:** Translation + categorization for 50 articles every 15 minutes
   - Mitigation: Monitor costs, adjust TTL if needed
   - Expected: $6-8 per 1000 feed loads

3. **Cache cold start:** First user sees empty feed
   - Mitigation: Pre-warm cache on deployment (deployment hook)
   - Fallback: Show "warming up" message, auto-refresh after 30s

4. **Translation quality:** AI might produce awkward English
   - Mitigation: Use Claude Sonnet 4 (excellent multilingual)
   - Fallback: Keep German text visible if translation seems wrong

---

## Ready for DEV-AGENT ✓

This specification provides complete architectural design, data schemas, API contracts, error handling, and testing requirements. All research sources are documented and current API patterns verified with Ref.

**Next Steps:**
1. Review spec with orchestrator
2. Launch DEV-AGENT for implementation
3. Test in development environment
4. Deploy with feature flag for canary testing

---

_SPEC-AGENT | Research complete | 2025-10-31_
