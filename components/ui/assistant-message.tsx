'use client';

import { useMemo } from 'react';
import { Response } from '@/components/ui/shadcn-io/ai/response';
import { CitationSourceCard } from '@/components/ui/citation-source-card';
import { parseCitations, type Article } from '@/lib/utils/parse-citations';
import type { Language } from '@/lib/user-config';

interface AssistantMessageProps {
  text: string;
  articles: Article[];
  language: Language;
}

// Hook to compute citations - shared between text and carousel
export function useCitedArticles(text: string, articles: Article[]) {
  const { content, indexMap } = useMemo(() => {
    return parseCitations(text, articles);
  }, [text, articles]);

  const citedArticles = useMemo(() => {
    const result: Array<{ article: Article; displayNumber: number; originalIndex: number }> = [];
    indexMap.forEach((displayNumber, originalIndex) => {
      if (originalIndex < articles.length) {
        result.push({
          article: articles[originalIndex],
          displayNumber,
          originalIndex,
        });
      }
    });
    return result.sort((a, b) => a.displayNumber - b.displayNumber);
  }, [articles, indexMap]);

  return { content, citedArticles };
}

/**
 * Assistant message TEXT only - renders inside MessageContent
 */
export function AssistantMessageText({ text, articles }: { text: string; articles: Article[] }) {
  const { content } = useCitedArticles(text, articles);
  return <Response>{content}</Response>;
}

/**
 * Sources carousel - renders OUTSIDE MessageContent for overflow effect
 */
export function SourcesCarousel({
  text,
  articles,
  language,
}: AssistantMessageProps) {
  const isGerman = language === 'de';
  const { citedArticles } = useCitedArticles(text, articles);

  if (citedArticles.length === 0) return null;

  return (
    <div className="mt-4 mb-6">
      <div className="max-w-2xl mx-auto px-4">
        <h3 className="text-sm font-semibold mb-3 text-muted-foreground">
          {isGerman ? 'Quellen' : 'Sources'}
        </h3>
      </div>
      {/* Full-width carousel with padding to align start with content */}
      <div className="overflow-x-auto scrollbar-thin">
        <div className="flex gap-3 px-4 md:px-[calc(50%-320px)] pb-2 snap-x snap-mandatory">
          {citedArticles.map(({ article, displayNumber, originalIndex }) => (
            <CitationSourceCard
              key={originalIndex}
              citation={{
                text: '',
                citationNumber: displayNumber,
                source: article.title,
                url: article.url,
                imageUrl: article.image_url,
                faviconUrl: article.favicon_url,
                age: article.age,
                summary: article.summary,
              }}
              language={language}
              className="snap-start"
            />
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * Combined component for backwards compatibility (if needed)
 */
export function AssistantMessage({ text, articles, language }: AssistantMessageProps) {
  return <AssistantMessageText text={text} articles={articles} />;
}
