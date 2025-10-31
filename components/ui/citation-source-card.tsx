/**
 * Citation Source Card Component
 *
 * Compact citation card matching ChatGPT-style design.
 * Shows thumbnail image, domain/source, and wrapping title.
 * Entire card is clickable to open article in new tab.
 */

import { Card, CardContent, CardTitle } from './card';
import { ExternalLink } from 'lucide-react';
import type { Citation } from '@/lib/utils/parse-citations';

export interface CitationSourceCardProps {
  citation: Citation;
  language?: 'en' | 'de';
}

export function CitationSourceCard({ citation, language = 'en' }: CitationSourceCardProps) {
  const { citationNumber, source, url, imageUrl, faviconUrl, age, summary } = citation;

  // Extract domain from URL for display
  const getDomain = () => {
    if (!url) return null;
    try {
      const urlObj = new URL(url);
      return urlObj.hostname.replace('www.', '');
    } catch {
      return null;
    }
  };

  const domain = getDomain();

  return (
    <Card
      id={`citation-${citationNumber}`}
      className="scroll-mt-4 min-w-[220px] max-w-[220px] shrink-0 overflow-hidden bg-muted hover:bg-accent transition-colors cursor-pointer"
      onClick={() => url && window.open(url, '_blank', 'noopener,noreferrer')}
    >
      {imageUrl && (
        <div className="relative w-full h-36 bg-muted">
          <img
            src={imageUrl}
            alt={source}
            className="w-full h-full object-cover"
            onError={(e) => {
              // Hide image if it fails to load
              e.currentTarget.parentElement!.style.display = 'none';
            }}
          />
        </div>
      )}
      <CardContent className="p-2.5 space-y-1.5 flex flex-col min-h-[140px]">
        {/* Domain/Source at top with favicon */}
        {domain && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            {faviconUrl ? (
              <img
                src={faviconUrl}
                alt=""
                className="h-3 w-3 shrink-0"
                onError={(e) => {
                  // Fallback to ExternalLink icon if favicon fails
                  e.currentTarget.style.display = 'none';
                  e.currentTarget.insertAdjacentHTML('afterend', '<svg class="h-3 w-3 shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" x2="21" y1="14" y2="3"/></svg>');
                }}
              />
            ) : (
              <ExternalLink className="h-3 w-3 shrink-0" />
            )}
            <span className="font-medium">{domain}</span>
          </div>
        )}

        {/* Title - truncate after 2 lines when summary present, 3 lines otherwise */}
        <CardTitle className={`text-sm leading-snug flex-1 ${summary ? 'line-clamp-2' : 'line-clamp-3'}`}>
          {source}
        </CardTitle>

        {/* Summary - truncate after 3 lines */}
        {summary && (
          <p className="text-xs text-muted-foreground line-clamp-3 leading-relaxed">
            {summary}
          </p>
        )}

        {/* Age fixed at bottom */}
        {age && (
          <p className="text-xs text-muted-foreground">{age}</p>
        )}
      </CardContent>
    </Card>
  );
}

CitationSourceCard.displayName = 'CitationSourceCard';
