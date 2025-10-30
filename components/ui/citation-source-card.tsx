/**
 * Citation Source Card Component
 *
 * Displays a citation source with shadcn/ui Card component.
 * Includes source badge, title, description, and clickable URL.
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { Badge } from './badge';
import { ExternalLink } from 'lucide-react';
import type { Citation } from '@/lib/utils/parse-citations';

export interface CitationSourceCardProps {
  citation: Citation;
  language?: 'en' | 'de';
}

export function CitationSourceCard({ citation, language = 'en' }: CitationSourceCardProps) {
  const { citationNumber, source, url, description } = citation;

  // Determine source type for badge
  const getBadgeText = () => {
    if (source === 'API-Football') return 'API';
    if (source === 'TheSportsDB') return 'API';
    if (source === 'The Odds API') return 'API';
    // For Kicker articles (those with kicker.de URLs), show "Kicker"
    if (url && url.includes('kicker.de')) return 'Kicker';
    // Default to article source
    return 'News';
  };

  return (
    <Card id={`citation-${citationNumber}`} className="scroll-mt-4 min-w-[300px] max-w-[300px] shrink-0">
      <CardHeader className="py-2 px-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-sm flex items-center gap-2">
              <span className="font-mono text-xs text-muted-foreground">
                [{citationNumber}]
              </span>
              <span className="truncate">{source}</span>
            </CardTitle>
            {description && (
              <CardDescription className="mt-0.5 text-xs line-clamp-1">{description}</CardDescription>
            )}
          </div>
          <Badge variant="secondary" className="shrink-0 text-xs px-1.5 py-0">
            {getBadgeText()}
          </Badge>
        </div>
      </CardHeader>
      {url && (
        <CardContent className="pt-0 pb-2 px-3">
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
          >
            <ExternalLink className="h-3 w-3 shrink-0" />
            <span className="truncate">{url}</span>
          </a>
        </CardContent>
      )}
    </Card>
  );
}

CitationSourceCard.displayName = 'CitationSourceCard';
