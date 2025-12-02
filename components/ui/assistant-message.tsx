'use client';

import { useMemo } from 'react';
import { ResponseWithCitations } from '@/components/ui/shadcn-io/ai/response-with-citations';
import { CitationSourceCard } from '@/components/ui/citation-source-card';
import { parseCitations } from '@/lib/utils/parse-citations';
import type { Language } from '@/lib/user-config';

interface Article {
  title: string;
  url?: string;
  image_url?: string;
  favicon_url?: string;
  age?: string;
  summary?: string;
}

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

  // Parse citations to find which articles were cited and get the index mapping
  const { indexMap } = useMemo(() => {
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
      {/* Article Sources - only show cited articles with sequential numbers */}
      {citedArticles.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold mb-3 text-muted-foreground">
            {isGerman ? 'Quellen' : 'Sources'}
          </h3>
          <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
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
              />
            ))}
          </div>
        </div>
      )}

      {/* Main AI Response */}
      <ResponseWithCitations language={language} articles={articles}>
        {text}
      </ResponseWithCitations>
    </>
  );
}
