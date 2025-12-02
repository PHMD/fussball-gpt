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

/**
 * Assistant message component that filters articles to only show cited ones
 *
 * Parses the response text to find [N] citation patterns, then filters
 * the articles carousel to only show articles that were actually cited.
 * Articles are renumbered sequentially (1, 2, 3...) based on order of first citation.
 */
export function AssistantMessage({ text, articles, language }: AssistantMessageProps) {
  const isGerman = language === 'de';

  // Parse citations ONCE - get transformed content and index mapping
  const { content, indexMap } = useMemo(() => {
    return parseCitations(text, articles);
  }, [text, articles]);

  // Build ordered list of cited articles with their NEW sequential display numbers
  const citedArticles = useMemo(() => {
    const result: Array<{ article: Article; displayNumber: number; originalIndex: number }> = [];

    // indexMap: original 0-based index -> new 1-based display number
    indexMap.forEach((displayNumber, originalIndex) => {
      if (originalIndex < articles.length) {
        result.push({
          article: articles[originalIndex],
          displayNumber,
          originalIndex,
        });
      }
    });

    // Sort by display number so they appear in citation order
    return result.sort((a, b) => a.displayNumber - b.displayNumber);
  }, [articles, indexMap]);

  return (
    <>
      {/* Main AI Response - pass pre-computed content (already has [N](url) links) */}
      <Response>{content}</Response>

      {/* Article Sources - at bottom, overflowing the content column */}
      {citedArticles.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-semibold mb-3 text-muted-foreground">
            {isGerman ? 'Quellen' : 'Sources'}
          </h3>
          {/* Negative margins to overflow content column, with scroll padding */}
          <div className="-mx-8 px-8">
            <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin snap-x snap-mandatory">
              {citedArticles.map(({ article, displayNumber, originalIndex }) => (
                <CitationSourceCard
                  key={originalIndex}
                  citation={{
                    text: '',
                    citationNumber: displayNumber, // NEW sequential number (1, 2, 3...)
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
      )}
    </>
  );
}
