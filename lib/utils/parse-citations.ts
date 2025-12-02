/**
 * Citation parser utility (simplified)
 *
 * Parses LLM responses for citation markers:
 * - Article references: (via [1]), (via [2]), etc.
 * - API sources: (via API-Football), (via TheSportsDB), etc.
 *
 * Articles are pre-streamed to client, so we just need to match [N] to the array.
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
  text: string; // The cited text segment
  source: string; // Source name (e.g., "API-Football" or article title)
  url?: string; // Optional source URL
  imageUrl?: string; // Optional thumbnail image URL
  faviconUrl?: string; // Optional favicon URL
  age?: string; // Optional age like "1 day ago"
  description?: string; // Optional source description
  citationNumber?: number; // Sequential number for citation (1, 2, 3, etc.)
}

export interface ParsedResponse {
  segments: Array<{
    type: 'text' | 'citation';
    content: string;
    citation?: Citation;
  }>;
  citations: Citation[]; // Unique list of all citations in order
}

/**
 * Convert number to superscript Unicode characters
 * Example: 1 → ¹, 2 → ², 10 → ¹⁰
 */
function toSuperscript(num: number): string {
  const superscriptMap: Record<string, string> = {
    '0': '⁰',
    '1': '¹',
    '2': '²',
    '3': '³',
    '4': '⁴',
    '5': '⁵',
    '6': '⁶',
    '7': '⁷',
    '8': '⁸',
    '9': '⁹',
  };

  return String(num)
    .split('')
    .map((digit) => superscriptMap[digit] || digit)
    .join('');
}

/**
 * Source metadata mapping for API sources
 */
const SOURCE_METADATA: Record<string, { url?: string; description?: string }> = {
  'API-Football': {
    url: 'https://api-football.com',
    description: 'Professional football API for player statistics and match data',
  },
  'TheSportsDB': {
    url: 'https://thesportsdb.com',
    description: 'Free sports database for standings, results, and team form',
  },
  'The Odds API': {
    url: 'https://the-odds-api.com',
    description: 'Real-time betting odds from multiple bookmakers',
  },
};

/**
 * Parse LLM response text and extract citation markers
 *
 * Detects patterns like:
 * - "(via [1])" - article reference (looks up from articles array)
 * - "(via [2])" - article reference
 * - "(via API-Football)" - API source
 *
 * @param text - The LLM response text
 * @param articles - Pre-streamed articles array for [N] lookups
 */
export function parseCitations(text: string, articles: Article[] = []): ParsedResponse {
  const segments: ParsedResponse['segments'] = [];
  const citationMap = new Map<string, Citation>(); // Track unique citations
  let citationCounter = 0;

  // Match citation patterns:
  // - (via [N]) - article reference by number
  // - (via API-Football), (via TheSportsDB), (via The Odds API) - API sources
  const citationRegex = /\(via (\[(\d+)\]|[^)]+)\)/g;

  let lastIndex = 0;
  let match;

  while ((match = citationRegex.exec(text)) !== null) {
    const citationStart = match.index;
    const citationEnd = citationRegex.lastIndex;
    const fullMatch = match[1]; // Content inside (via ...)
    const articleNumber = match[2]; // Capture group for [N] number

    let sourceName: string;
    let sourceUrl: string | undefined;
    let imageUrl: string | undefined;
    let faviconUrl: string | undefined;
    let age: string | undefined;
    let description: string | undefined;

    if (articleNumber) {
      // Article reference: (via [N])
      const articleIndex = parseInt(articleNumber, 10) - 1; // Convert to 0-based index
      const article = articles[articleIndex];

      if (article) {
        sourceName = article.title;
        sourceUrl = article.url;
        imageUrl = article.image_url;
        faviconUrl = article.favicon_url;
        age = article.age;
        description = article.summary;
      } else {
        // Article not found, use placeholder
        sourceName = `Article ${articleNumber}`;
      }
    } else {
      // API source: (via API-Football), etc.
      sourceName = fullMatch.trim();
      const metadata = SOURCE_METADATA[sourceName];
      if (metadata) {
        sourceUrl = metadata.url;
        description = metadata.description;
      }
    }

    // Find the sentence or clause before the citation
    let textStart = lastIndex;
    const textEnd = citationStart;

    // Find sentence start by looking for boundaries
    const textBefore = text.substring(textStart, textEnd);
    const sentenceBoundary = Math.max(
      textBefore.lastIndexOf('. '),
      textBefore.lastIndexOf('! '),
      textBefore.lastIndexOf('? '),
      textBefore.lastIndexOf('\n')
    );

    if (sentenceBoundary > -1) {
      textStart = textStart + sentenceBoundary + 1;
    }

    // Add text before citation (if any)
    if (textStart > lastIndex) {
      const beforeText = text.substring(lastIndex, textStart).trim();
      if (beforeText) {
        segments.push({
          type: 'text',
          content: beforeText,
        });
      }
    }

    // Add cited text segment
    const citedText = text.substring(textStart, textEnd).trim();
    if (citedText) {
      // Deduplicate by URL or source name
      const citationKey = sourceUrl || sourceName;

      let citation = citationMap.get(citationKey);
      if (!citation) {
        citationCounter++;
        citation = {
          text: citedText,
          source: sourceName,
          url: sourceUrl,
          imageUrl,
          faviconUrl,
          age,
          description,
          citationNumber: citationCounter,
        };
        citationMap.set(citationKey, citation);
      }

      // Generate markdown with clickable superscript citation number
      const superscript = toSuperscript(citation.citationNumber!);
      const contentWithCitation = `${citedText}[${superscript}](#citation-${citation.citationNumber})`;

      segments.push({
        type: 'citation',
        content: contentWithCitation,
        citation,
      });
    }

    lastIndex = citationEnd;
  }

  // Add remaining text after last citation
  if (lastIndex < text.length) {
    const remainingText = text.substring(lastIndex).trim();
    if (remainingText) {
      segments.push({
        type: 'text',
        content: remainingText,
      });
    }
  }

  // If no citations found, return entire text as one segment
  if (segments.length === 0) {
    segments.push({
      type: 'text',
      content: text,
    });
  }

  // Convert citation map to array sorted by citation number
  const citations = Array.from(citationMap.values()).sort(
    (a, b) => (a.citationNumber || 0) - (b.citationNumber || 0)
  );

  return { segments, citations };
}

/**
 * Group consecutive text segments (optimization)
 */
export function optimizeSegments(parsed: ParsedResponse): ParsedResponse {
  const optimized: ParsedResponse['segments'] = [];

  for (const segment of parsed.segments) {
    const lastSegment = optimized[optimized.length - 1];

    // Merge consecutive text segments
    if (
      segment.type === 'text' &&
      lastSegment &&
      lastSegment.type === 'text'
    ) {
      lastSegment.content += ' ' + segment.content;
    } else {
      optimized.push(segment);
    }
  }

  return { segments: optimized, citations: parsed.citations };
}
