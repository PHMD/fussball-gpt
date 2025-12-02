/**
 * Citation parser utility
 *
 * Parses LLM responses for [N] citation markers and transforms them into
 * clickable links to article URLs. Also tracks which citations were used.
 */

export interface Article {
  title: string;
  url?: string;
  image_url?: string;
  favicon_url?: string;
  age?: string;
  summary?: string;
}

export interface Citation {
  text: string;
  citationNumber: number;
  source: string;
  url?: string;
  imageUrl?: string;
  faviconUrl?: string;
  age?: string;
  summary?: string;
}

export interface ParseResult {
  /** Transformed text with [N] replaced by markdown links */
  content: string;
  /** Set of article indices (0-based) that were cited */
  citedIndices: Set<number>;
  /** List of citations with metadata */
  citations: Citation[];
  /** Map from original article index (0-based) to new display index (1-based) */
  indexMap: Map<number, number>;
}

/**
 * Parse LLM response text and transform [N] patterns into clickable links
 * with sequential renumbering.
 *
 * Input: "Bayern won 3-0 [4] against Dortmund [1] and drew [5]."
 * Output: "Bayern won 3-0 [1](url4) against Dortmund [2](url1) and drew [3](url5)."
 *
 * Citations are renumbered sequentially (1, 2, 3...) in order of first appearance.
 * The indexMap allows mapping back to original articles.
 *
 * @param text - The LLM response text
 * @param articles - Pre-streamed articles array for lookups
 */
export function parseCitations(text: string, articles: Article[] = []): ParseResult {
  const citedIndices = new Set<number>();
  const citations: Citation[] = [];
  const indexMap = new Map<number, number>(); // original 0-based index -> new 1-based display number

  const citationRegex = /\[(\d+)\](?!\()/g;

  // First pass: collect cited indices in order of first appearance
  const orderedIndices: number[] = [];
  let match;
  while ((match = citationRegex.exec(text)) !== null) {
    const num = parseInt(match[1], 10);
    const articleIndex = num - 1;
    if (articleIndex >= 0 && articleIndex < articles.length && !citedIndices.has(articleIndex)) {
      citedIndices.add(articleIndex);
      orderedIndices.push(articleIndex);
    }
  }

  // Build index map: original index -> new sequential number (1-based)
  orderedIndices.forEach((originalIndex, i) => {
    indexMap.set(originalIndex, i + 1);
  });

  // Second pass: replace citations with new sequential numbers
  const content = text.replace(citationRegex, (matchStr, numStr) => {
    const num = parseInt(numStr, 10);
    const articleIndex = num - 1;

    if (articleIndex >= 0 && articleIndex < articles.length) {
      const article = articles[articleIndex];
      const newDisplayNum = indexMap.get(articleIndex);

      if (newDisplayNum !== undefined) {
        // Track citation metadata with new number
        if (!citations.find(c => c.citationNumber === newDisplayNum)) {
          citations.push({
            text: '',
            citationNumber: newDisplayNum,
            source: article.title,
            url: article.url,
            imageUrl: article.image_url,
            faviconUrl: article.favicon_url,
            age: article.age,
            summary: article.summary,
          });
        }

        // Transform to markdown link with NEW display number
        if (article.url) {
          return `[${newDisplayNum}](${article.url})`;
        }
        return `[${newDisplayNum}]`;
      }
    }

    return matchStr;
  });

  // Sort citations by new number
  citations.sort((a, b) => a.citationNumber - b.citationNumber);

  return { content, citedIndices, citations, indexMap };
}

/**
 * Legacy interface for backwards compatibility
 */
export interface ParsedResponse {
  segments: Array<{
    type: 'text' | 'citation';
    content: string;
    citation?: Citation;
  }>;
  citations: Citation[];
}
