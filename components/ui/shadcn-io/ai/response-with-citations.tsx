'use client';

import { parseCitations } from '@/lib/utils/parse-citations';
import { Response, type ResponseProps } from './response';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cn } from '@/lib/utils';
import { CitationSourceCard } from '@/components/ui/citation-source-card';

export interface ResponseWithCitationsProps extends ResponseProps {
  language?: 'en' | 'de';
}

/**
 * Response component with automatic citation parsing and markdown rendering
 *
 * Parses LLM responses for citation markers (e.g., "via API-Football"),
 * renders markdown content as it streams, and displays sources section.
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
    sources: language === 'de' ? 'Quellen' : 'Sources',
  };

  // Custom link component for smooth scroll to citations
  const components = {
    a: ({ node, href, children, ...linkProps }: any) => {
      // Check if it's a citation anchor link
      if (href?.startsWith('#citation-')) {
        return (
          <a
            href={href}
            className="text-primary hover:underline cursor-pointer"
            onClick={(e) => {
              e.preventDefault();
              const target = document.getElementById(href.slice(1));
              target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }}
            {...linkProps}
          >
            {children}
          </a>
        );
      }
      // External links
      return (
        <a
          href={href}
          className="text-primary hover:underline"
          target="_blank"
          rel="noopener noreferrer"
          {...linkProps}
        >
          {children}
        </a>
      );
    },
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* AI Response with Markdown */}
      <div className="prose prose-sm max-w-none dark:prose-invert">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={components}
        >
          {fullContent}
        </ReactMarkdown>
      </div>

      {/* Sources Section */}
      {parsed.citations.length > 0 && (
        <div className="border-t pt-4 mt-6">
          <h3 className="text-sm font-semibold mb-3">{labels.sources}</h3>
          <div className="space-y-2">
            {parsed.citations.map((citation) => (
              <CitationSourceCard
                key={citation.citationNumber}
                citation={citation}
                language={language}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

ResponseWithCitations.displayName = 'ResponseWithCitations';
