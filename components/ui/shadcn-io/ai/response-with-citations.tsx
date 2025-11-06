'use client';

import { parseCitations } from '@/lib/utils/parse-citations';
import { Response, type ResponseProps } from './response';
import { cn } from '@/lib/utils';
import { CitationSourceCard } from '@/components/ui/citation-source-card';

export interface ResponseWithCitationsProps extends ResponseProps {
  language?: 'en' | 'de';
}

/**
 * Response component with automatic citation parsing and markdown rendering
 *
 * Parses LLM responses for citation markers (e.g., "via API-Football"),
 * renders markdown content using the unified Response component, and displays sources section.
 */
export function ResponseWithCitations({
  children,
  language = 'en',
  className,
  ...props
}: ResponseWithCitationsProps) {
  // Only parse if children is a string
  if (typeof children !== 'string') {
    return <Response {...props}>{children}</Response>;
  }

  const parsed = parseCitations(children);

  // If no citations found, render normal Response (with markdown)
  if (parsed.citations.length === 0) {
    return <Response {...props}>{children}</Response>;
  }

  // Build full content with citation superscripts
  const fullContent = parsed.segments
    .map((segment) => segment.content)
    .join(' ');

  // Bilingual labels
  const labels = {
    sources: language === 'de' ? 'Quellen von Kicker' : 'Sources from Kicker',
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* AI Response with Markdown - using unified Response component */}
      <Response {...props}>{fullContent}</Response>

      {/* Sources Section - Only show article sources, not background APIs */}
      {(() => {
        // Filter out background API sources (API-Football, TheSportsDB, The Odds API)
        const backgroundAPIs = ['API-Football', 'TheSportsDB', 'The Odds API'];
        const articleCitations = parsed.citations.filter(
          (citation) => !backgroundAPIs.includes(citation.source)
        );

        return articleCitations.length > 0 ? (
          <div className="border-t pt-6 mt-8">
            <h3 className="text-base font-semibold mb-4">{labels.sources}</h3>
            <div className="flex gap-3 overflow-x-auto pb-2">
              {articleCitations.map((citation) => (
                <CitationSourceCard
                  key={citation.citationNumber}
                  citation={citation}
                  language={language}
                />
              ))}
            </div>
          </div>
        ) : null;
      })()}
    </div>
  );
}

ResponseWithCitations.displayName = 'ResponseWithCitations';
