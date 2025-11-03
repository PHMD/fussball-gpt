/**
 * Article Category Section Component
 *
 * Netflix-style horizontal scrolling section with article cards.
 * Each section represents a category (Latest, Transfers, Analysis, etc.).
 */

'use client';

import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useRef, useState, useEffect } from 'react';
import { CitationSourceCard } from '@/components/ui/citation-source-card';
import { Button } from '@/components/ui/button';
import type { NewsArticle } from '@/lib/models';
import type { Citation } from '@/lib/utils/parse-citations';

interface ArticleCategorySectionProps {
  title: string;
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

export function ArticleCategorySection({
  title,
  articles,
  language = 'en',
}: ArticleCategorySectionProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  // Check scroll position to show/hide navigation buttons
  const checkScrollButtons = () => {
    const container = scrollContainerRef.current;
    if (!container) return;

    setCanScrollLeft(container.scrollLeft > 0);
    setCanScrollRight(
      container.scrollLeft < container.scrollWidth - container.clientWidth - 10
    );
  };

  useEffect(() => {
    checkScrollButtons();
    const container = scrollContainerRef.current;
    if (container) {
      container.addEventListener('scroll', checkScrollButtons);
      return () => container.removeEventListener('scroll', checkScrollButtons);
    }
  }, [articles]);

  const scroll = (direction: 'left' | 'right') => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const scrollAmount = 400; // Scroll ~2 cards
    const newScrollLeft =
      direction === 'left'
        ? container.scrollLeft - scrollAmount
        : container.scrollLeft + scrollAmount;

    container.scrollTo({
      left: newScrollLeft,
      behavior: 'smooth',
    });
  };

  if (articles.length === 0) {
    return null;
  }

  return (
    <div className="mb-8">
      {/* Section Header */}
      <div className="flex items-center justify-between mb-4 px-4">
        <h2 className="text-2xl font-bold">{title}</h2>
        <span className="text-sm text-muted-foreground">
          {articles.length} {language === 'de' ? 'Artikel' : 'articles'}
        </span>
      </div>

      {/* Scrollable Container with Navigation */}
      <div className="relative group">
        {/* Left Navigation Button */}
        {canScrollLeft && (
          <Button
            variant="ghost"
            size="icon"
            className="absolute left-0 top-1/2 -translate-y-1/2 z-10 h-12 w-12 rounded-full bg-background/80 backdrop-blur-sm shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={() => scroll('left')}
            aria-label={language === 'de' ? 'Nach links scrollen' : 'Scroll left'}
          >
            <ChevronLeft className="h-6 w-6" />
          </Button>
        )}

        {/* Article Cards */}
        <div
          ref={scrollContainerRef}
          className="flex gap-4 overflow-x-auto pb-4 px-4 scrollbar-hide scroll-smooth"
          style={{
            scrollbarWidth: 'none',
            msOverflowStyle: 'none',
          }}
        >
          {articles.map((article, index) => (
            <CitationSourceCard
              key={`${article.url}-${index}`}
              citation={articleToCitation(article, index)}
              language={language}
            />
          ))}
        </div>

        {/* Right Navigation Button */}
        {canScrollRight && (
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-0 top-1/2 -translate-y-1/2 z-10 h-12 w-12 rounded-full bg-background/80 backdrop-blur-sm shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={() => scroll('right')}
            aria-label={language === 'de' ? 'Nach rechts scrollen' : 'Scroll right'}
          >
            <ChevronRight className="h-6 w-6" />
          </Button>
        )}
      </div>
    </div>
  );
}
