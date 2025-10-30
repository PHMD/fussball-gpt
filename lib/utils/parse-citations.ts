/**
 * Citation parser utility
 *
 * Parses LLM responses for citation markers (e.g., "via API-Football")
 * and converts them into structured citation data for InlineCitation components.
 */

export interface Citation {
  text: string; // The cited text segment
  source: string; // Source name (e.g., "API-Football")
  url?: string; // Optional source URL
  description?: string; // Optional source description
}

export interface ParsedResponse {
  segments: Array<{
    type: 'text' | 'citation';
    content: string;
    citation?: Citation;
  }>;
}

/**
 * Source metadata mapping
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
  'Kicker RSS': {
    url: 'https://www.kicker.de',
    description: 'Leading German football news source',
  },
};

/**
 * Parse LLM response text and extract citation markers
 *
 * Detects patterns like:
 * - "Kane has 12 goals (via API-Football)"
 * - "Bayern leads (via TheSportsDB)"
 *
 * Returns structured segments for rendering with InlineCitation components.
 */
export function parseCitations(text: string): ParsedResponse {
  const segments: ParsedResponse['segments'] = [];

  // Regex to match citation patterns: (via Source Name)
  const citationRegex = /\(via ([^)]+)\)/g;

  let lastIndex = 0;
  let match;

  while ((match = citationRegex.exec(text)) !== null) {
    const citationStart = match.index;
    const citationEnd = citationRegex.lastIndex;
    const sourceName = match[1];

    // Find the sentence or clause before the citation
    // Look backwards for sentence boundaries (., !, ?, or start of text)
    let textStart = lastIndex;
    let textEnd = citationStart;

    // Find sentence start
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
      const metadata = SOURCE_METADATA[sourceName] || {};

      segments.push({
        type: 'citation',
        content: citedText,
        citation: {
          text: citedText,
          source: sourceName,
          url: metadata.url,
          description: metadata.description,
        },
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

  return { segments };
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

  return { segments: optimized };
}
