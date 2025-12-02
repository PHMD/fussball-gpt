'use client';

import { parseCitations, type Article } from '@/lib/utils/parse-citations';
import { Response, type ResponseProps } from './response';
import { cn } from '@/lib/utils';

export interface ResponseWithCitationsProps extends ResponseProps {
  language?: 'en' | 'de';
  articles?: Article[]; // Pre-streamed articles for [N] citation lookups
}

/**
 * Response component with automatic citation parsing and markdown rendering
 *
 * Parses LLM responses for citation markers:
 * - (via [1]), (via [2]) - article references (looks up from articles prop)
 * - (via API-Football) - API source references
 *
 * Articles are shown in carousel above, so we just render inline citation superscripts.
 */
export function ResponseWithCitations({
  children,
  language = 'en',
  articles = [],
  className,
  ...props
}: ResponseWithCitationsProps) {
  // Only parse if children is a string
  if (typeof children !== 'string') {
    return <Response {...props}>{children}</Response>;
  }

  // Parse citations with articles array for [N] lookups
  const parsed = parseCitations(children, articles);

  // Build full content with citation superscripts
  const fullContent = parsed.segments
    .map((segment) => segment.content)
    .join(' ');

  // Render response with markdown
  // Articles are already shown in carousel above, no need for sources section
  return (
    <div className={cn(className)}>
      <Response {...props}>{fullContent}</Response>
    </div>
  );
}

ResponseWithCitations.displayName = 'ResponseWithCitations';
