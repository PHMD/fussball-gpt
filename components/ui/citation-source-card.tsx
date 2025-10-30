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

  return (
    <Card id={`citation-${citationNumber}`} className="scroll-mt-4">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1">
            <CardTitle className="text-base flex items-center gap-2">
              <span className="font-mono text-sm text-muted-foreground">
                [{citationNumber}]
              </span>
              {source}
            </CardTitle>
            {description && (
              <CardDescription className="mt-1">{description}</CardDescription>
            )}
          </div>
          <Badge variant="secondary" className="shrink-0">
            Brave Search
          </Badge>
        </div>
      </CardHeader>
      {url && (
        <CardContent className="pt-0">
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
          >
            <ExternalLink className="h-3 w-3" />
            <span className="truncate max-w-md">{url}</span>
          </a>
        </CardContent>
      )}
    </Card>
  );
}

CitationSourceCard.displayName = 'CitationSourceCard';
