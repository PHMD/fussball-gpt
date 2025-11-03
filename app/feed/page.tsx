/**
 * Newsfeed Page
 *
 * Displays personalized Bundesliga news in Netflix-style category sections.
 * Uses server-side data fetching with client-side interactivity.
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
  persona: string;
  category: string;
  count: number;
  timestamp: string;
}

// Feed categories - no tabs, just horizontal sections
const categories = [
  {
    id: 'latest' as const,
    label: { en: 'Latest', de: 'Aktuelles' },
  },
  {
    id: 'transfers' as const,
    label: { en: 'Transfers', de: 'Transfers' },
  },
  {
    id: 'analysis' as const,
    label: { en: 'Analysis', de: 'Analysen' },
  },
  {
    id: 'odds' as const,
    label: { en: 'Betting', de: 'Wetten' },
  },
];

export default function FeedPage() {
  const { profile, updateProfile } = useUserPreferences();
  const [showSettings, setShowSettings] = useState(false);
  const [feedData, setFeedData] = useState<Record<string, NewsArticle[]>>({});
  const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({});
  const [initialLoad, setInitialLoad] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const isGerman = profile.language === Language.GERMAN;

  /**
   * Fetch feed data for all categories
   */
  const fetchFeed = async (forceRefresh = false) => {
    if (forceRefresh) {
      setRefreshing(true);
    }

    // Set all categories to loading
    const newLoadingStates: Record<string, boolean> = {};
    categories.forEach((cat) => {
      newLoadingStates[cat.id] = true;
    });
    setLoadingStates(newLoadingStates);

    try {
      // Fetch categories sequentially to avoid rate limiting
      const newFeedData: Record<string, NewsArticle[]> = {};

      for (const category of categories) {
        try {
          const res = await fetch(
            `/api/feed?persona=${profile.persona}&category=${category.id}&maxResults=20`,
            {
              cache: 'no-store',
            }
          );

          if (res.ok) {
            const data: FeedResponse = await res.json();
            newFeedData[category.id] = data.articles;
          }
        } catch (error) {
          console.error(`Error fetching ${category.id}:`, error);
          newFeedData[category.id] = [];
        }

        // Update loading state for this category
        setLoadingStates(prev => ({ ...prev, [category.id]: false }));
        setFeedData(prev => ({ ...prev, [category.id]: newFeedData[category.id] }));
      }
    } catch (error) {
      console.error('Error fetching feed:', error);
    } finally {
      setInitialLoad(false);
      setRefreshing(false);
    }
  };

  // Load feed on mount or persona change
  useEffect(() => {
    fetchFeed();
  }, [profile.persona]);

  /**
   * Handle refresh button click
   */
  const handleRefresh = () => {
    fetchFeed(true);
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

      {/* Feed Content - Horizontal Sections (No Tabs) */}
      <div className="max-w-7xl mx-auto py-6 space-y-8">
        {initialLoad ? (
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
              const isLoading = loadingStates[category.id];

              // Show loading skeleton for this section
              if (isLoading) {
                return (
                  <div key={category.id} className="space-y-4">
                    <div className="flex items-center justify-between px-4">
                      <div className="h-8 w-32 bg-muted animate-pulse rounded" />
                      <div className="h-4 w-24 bg-muted animate-pulse rounded" />
                    </div>
                    <div className="flex gap-4 overflow-hidden px-4">
                      {[1, 2, 3].map((i) => (
                        <div key={i} className="w-80 flex-shrink-0 space-y-3">
                          <div className="aspect-video w-full bg-muted animate-pulse rounded-lg" />
                          <div className="h-4 w-3/4 bg-muted animate-pulse rounded" />
                          <div className="h-4 w-1/2 bg-muted animate-pulse rounded" />
                        </div>
                      ))}
                    </div>
                  </div>
                );
              }

              // Skip empty sections
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
