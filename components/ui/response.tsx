'use client';

import { cn } from '@/lib/utils';
import type { HTMLAttributes } from 'react';
import { memo } from 'react';
import ReactMarkdown, { type Options } from 'react-markdown';
import rehypeKatex from 'rehype-katex';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import 'katex/dist/katex.min.css';

/**
 * Parses markdown text and removes incomplete tokens to prevent
 * partial rendering during streaming
 */
function parseIncompleteMarkdown(text: string): string {
  // For now, return text as-is
  // In a full implementation, this would auto-complete incomplete formatting markers
  return text;
}

export type ResponseProps = HTMLAttributes<HTMLDivElement> & {
  options?: Options;
  children: Options['children'];
  parseIncompleteMarkdown?: boolean;
};

const components: Options['components'] = {
  h1: ({ className, ...props }) => (
    <h1 className={cn('mt-6 text-2xl font-bold', className)} {...props} />
  ),
  h2: ({ className, ...props }) => (
    <h2 className={cn('mt-5 text-xl font-bold', className)} {...props} />
  ),
  h3: ({ className, ...props }) => (
    <h3 className={cn('mt-4 text-lg font-bold', className)} {...props} />
  ),
  p: ({ className, ...props }) => (
    <p className={cn('mt-2 leading-7', className)} {...props} />
  ),
  ul: ({ className, ...props }) => (
    <ul className={cn('mt-2 list-disc pl-6', className)} {...props} />
  ),
  ol: ({ className, ...props }) => (
    <ol className={cn('mt-2 list-decimal pl-6', className)} {...props} />
  ),
  li: ({ className, ...props }) => (
    <li className={cn('mt-1', className)} {...props} />
  ),
  blockquote: ({ className, ...props }) => (
    <blockquote
      className={cn('mt-2 border-l-4 border-muted pl-4 italic', className)}
      {...props}
    />
  ),
  code: ({ className, inline, ...props }) =>
    inline ? (
      <code
        className={cn(
          'rounded bg-muted px-1 py-0.5 font-mono text-sm',
          className
        )}
        {...props}
      />
    ) : (
      <code
        className={cn('block rounded bg-muted p-4 font-mono text-sm', className)}
        {...props}
      />
    ),
  pre: ({ className, ...props }) => (
    <pre
      className={cn('mt-2 overflow-x-auto rounded bg-muted p-4', className)}
      {...props}
    />
  ),
  a: ({ className, ...props }) => (
    <a
      className={cn('text-primary underline hover:text-primary/80', className)}
      rel="noreferrer"
      target="_blank"
      {...props}
    />
  ),
  table: ({ className, ...props }) => (
    <div className="mt-2 overflow-x-auto">
      <table className={cn('w-full border-collapse', className)} {...props} />
    </div>
  ),
  th: ({ className, ...props }) => (
    <th
      className={cn('border border-border bg-muted px-4 py-2 text-left font-bold', className)}
      {...props}
    />
  ),
  td: ({ className, ...props }) => (
    <td className={cn('border border-border px-4 py-2', className)} {...props} />
  ),
};

export const Response = memo(
  ({
    className,
    options,
    children,
    parseIncompleteMarkdown: shouldParseIncompleteMarkdown = true,
    ...props
  }: ResponseProps) => {
    const parsedChildren =
      typeof children === 'string' && shouldParseIncompleteMarkdown
        ? parseIncompleteMarkdown(children)
        : children;

    return (
      <div
        className={cn(
          'size-full text-sm [&>*:first-child]:mt-0 [&>*:last-child]:mb-0',
          className
        )}
        {...props}
      >
        <ReactMarkdown
          components={components}
          rehypePlugins={[rehypeKatex]}
          remarkPlugins={[remarkGfm, remarkMath]}
          {...options}
        >
          {parsedChildren}
        </ReactMarkdown>
      </div>
    );
  }
);

Response.displayName = 'Response';
