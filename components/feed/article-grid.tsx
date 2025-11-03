/**
 * Article Grid Component
 *
 * Responsive grid layout for article cards.
 * Adapts columns based on screen size: 1 → 2 → 3 columns.
 */

'use client';

import { CitationSourceCard } from '@/components/ui/citation-source-card';
import type { NewsArticle } from '@/lib/models';
import type { Citation } from '@/lib/utils/parse-citations';

interface ArticleGridProps {
  articles: NewsArticle[];
  language?: 'en' | 'de';
}

/**
 * Convert NewsArticle to Citation format for CitationSourceCard
 */
function articleToCitation(article: NewsArticle, index: number): Citation {
  return {
    text: '', // Not used for standalone cards
    citationNumber: index + 1,
    source: article.title,
    url: article.url || '',
    imageUrl: article.image_url,
    faviconUrl: article.favicon_url,
    age: article.age,
  };
}

export function ArticleGrid({ articles, language = 'en' }: ArticleGridProps) {
  if (articles.length === 0) {
    return (
      <div className="text-center py-16 text-muted-foreground">
        <p>
          {language === 'de'
            ? 'Keine Artikel gefunden'
            : 'No articles found'}
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
      {articles.map((article, index) => (
        <div key={`${article.url}-${index}`} className="flex justify-center">
          <CitationSourceCard
            citation={articleToCitation(article, index)}
            language={language}
          />
        </div>
      ))}
    </div>
  );
}
