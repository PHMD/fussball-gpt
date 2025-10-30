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
    sources: language === 'de' ? 'Quellen von Kicker' : 'Sources from Kicker',
  };

  // Custom components for markdown rendering with proper spacing and hierarchy
  const components = {
    p: ({ children }: any) => <p className="mb-4 leading-relaxed">{children}</p>,
    h1: ({ children }: any) => <h1 className="text-2xl font-bold mt-6 mb-3">{children}</h1>,
    h2: ({ children }: any) => <h2 className="text-xl font-bold mt-6 mb-3">{children}</h2>,
    h3: ({ children }: any) => <h3 className="text-lg font-semibold mt-5 mb-2">{children}</h3>,
    h4: ({ children }: any) => <h4 className="text-base font-semibold mt-4 mb-2">{children}</h4>,
    ul: ({ children }: any) => <ul className="mb-4 space-y-2 list-disc list-inside">{children}</ul>,
    ol: ({ children }: any) => <ol className="mb-4 space-y-2 list-decimal list-inside">{children}</ol>,
    li: ({ children }: any) => <li className="leading-relaxed">{children}</li>,
    blockquote: ({ children }: any) => (
      <blockquote className="border-l-4 border-primary/30 pl-4 my-4 italic text-muted-foreground">
        {children}
      </blockquote>
    ),
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
        <div className="border-t pt-6 mt-8">
          <h3 className="text-base font-semibold mb-4">{labels.sources}</h3>
          <div className="flex gap-3 overflow-x-auto pb-2">
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
