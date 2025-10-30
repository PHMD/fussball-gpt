'use client';

import { parseCitations } from '@/lib/utils/parse-citations';
import { Response, type ResponseProps } from './response';
import {
  InlineCitation,
  InlineCitationText,
  InlineCitationCard,
  InlineCitationCardTrigger,
  InlineCitationCardBody,
  InlineCitationSource,
} from './inline-citation';

/**
 * Response component with automatic citation parsing
 *
 * Parses LLM responses for citation markers (e.g., "via API-Football")
 * and renders them with InlineCitation hover cards.
 */
export function ResponseWithCitations({
  children,
  ...props
}: ResponseProps) {
  // Only parse if children is a string
  if (typeof children !== 'string') {
    return <Response {...props}>{children}</Response>;
  }

  const parsed = parseCitations(children);

  // If no citations found, render normal Response
  if (parsed.segments.every((seg) => seg.type === 'text')) {
    return <Response {...props}>{children}</Response>;
  }

  // Render with citations
  return (
    <div className="space-y-2">
      {parsed.segments.map((segment, index) => {
        if (segment.type === 'text') {
          return (
            <Response key={index} {...props}>
              {segment.content}
            </Response>
          );
        }

        // Citation segment - render InlineCitation directly without Response wrapper
        const citation = segment.citation!;
        return (
          <div key={index} className="inline">
            <InlineCitation>
              <InlineCitationText>{segment.content}</InlineCitationText>
              <InlineCitationCard>
                <InlineCitationCardTrigger sources={[citation.url || '']} />
                <InlineCitationCardBody>
                  <InlineCitationSource
                    title={citation.source}
                    url={citation.url || ''}
                    description={citation.description}
                  />
                </InlineCitationCardBody>
              </InlineCitationCard>
            </InlineCitation>
          </div>
        );
      })}
    </div>
  );
}

ResponseWithCitations.displayName = 'ResponseWithCitations';
