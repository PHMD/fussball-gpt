/**
 * Citation Source Card Component
 *
 * Compact citation card matching ChatGPT-style design.
 * Shows thumbnail image, domain/source, and wrapping title.
 * Entire card is clickable to open article in new tab.
 */

import { useState } from 'react';
import { Card, CardContent, CardTitle } from './card';
import { ExternalLink } from 'lucide-react';
import type { Citation } from '@/lib/utils/parse-citations';
import { proxyImageUrl } from '@/lib/utils/image-proxy';

export interface CitationSourceCardProps {
  citation: Citation;
  language?: 'en' | 'de';
}

export function CitationSourceCard({ citation, language = 'en' }: CitationSourceCardProps) {
  const [faviconFailed, setFaviconFailed] = useState(false);
  const { citationNumber, source, url, imageUrl, faviconUrl, age } = citation;

  // Use server-side proxy for all images to bypass CORS/403 restrictions
  const proxiedImageUrl = proxyImageUrl(imageUrl);
  const proxiedFaviconUrl = proxyImageUrl(faviconUrl);

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
      className="scroll-mt-4 min-w-[220px] max-w-[220px] shrink-0 overflow-hidden hover:bg-accent/50 transition-colors cursor-pointer"
      onClick={() => url && window.open(url, '_blank', 'noopener,noreferrer')}
    >
      {proxiedImageUrl && (
        <div className="relative w-full h-36 bg-muted">
          <img
            src={proxiedImageUrl}
            alt={source}
            className="w-full h-full object-cover"
            loading="lazy"
            onError={(e) => {
              // Hide image container if it fails to load
              e.currentTarget.parentElement!.style.display = 'none';
            }}
          />
        </div>
      )}
      <CardContent className="p-2.5 space-y-1.5 flex flex-col min-h-[140px]">
        {/* Domain/Source at top with favicon */}
        {domain && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            {proxiedFaviconUrl && !faviconFailed ? (
              <img
                src={proxiedFaviconUrl}
                alt=""
                className="h-3 w-3 shrink-0"
                loading="lazy"
                onError={() => setFaviconFailed(true)}
              />
            ) : (
              <ExternalLink className="h-3 w-3 shrink-0" />
            )}
            <span className="font-medium">{domain}</span>
          </div>
        )}

        {/* Title - truncate after 3 lines */}
        <CardTitle className="text-sm leading-snug line-clamp-3 flex-1">
          {source}
        </CardTitle>

        {/* Age fixed at bottom */}
        {age && (
          <p className="text-xs text-muted-foreground">{age}</p>
        )}
      </CardContent>
    </Card>
  );
}

CitationSourceCard.displayName = 'CitationSourceCard';
