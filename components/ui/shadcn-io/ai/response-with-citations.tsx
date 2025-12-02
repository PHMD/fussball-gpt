'use client';

import { parseCitations, type Article } from '@/lib/utils/parse-citations';
import { Response, type ResponseProps } from './response';
import { cn } from '@/lib/utils';
import { useMemo } from 'react';

export interface ResponseWithCitationsProps extends ResponseProps {
  language?: 'en' | 'de';
  articles?: Article[]; // Pre-streamed articles for [N] citation lookups
  onCitedIndicesChange?: (indices: Set<number>) => void; // Callback when cited indices change
}

/**
 * Response component with automatic citation parsing and markdown rendering
 *
 * Parses LLM responses for [N] citation markers and transforms them into
 * clickable links to the actual article URLs.
 *
 * Articles are filtered to only show cited ones in the carousel above.
 */
export function ResponseWithCitations({
  children,
  language = 'en',
  articles = [],
  onCitedIndicesChange,
  className,
  ...props
}: ResponseWithCitationsProps) {
  // Parse citations and get transformed content with cited indices
  const { content, citedIndices } = useMemo(() => {
    if (typeof children !== 'string') {
      return { content: children, citedIndices: new Set<number>() };
    }
    return parseCitations(children, articles);
  }, [children, articles]);

  // Notify parent of cited indices changes (for filtering articles)
  useMemo(() => {
    if (onCitedIndicesChange && citedIndices.size > 0) {
      onCitedIndicesChange(citedIndices);
    }
  }, [citedIndices, onCitedIndicesChange]);

  // Render response with markdown
  return (
    <div className={cn(className)}>
      <Response {...props}>{content}</Response>
    </div>
  );
}

ResponseWithCitations.displayName = 'ResponseWithCitations';
