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
 * Fix broken Brave Search URLs where base64 path segments got split by whitespace.
 * LLMs often wrap long URLs, breaking the base64-encoded parts.
 *
 * Example input:  "https://imgs.search.brave.com/.../aHR0cHM6Ly9 tZWRp YWRi"
 * Example output: "https://imgs.search.brave.com/.../aHR0cHM6Ly9tZWRpYWRi"
 */
function fixBrokenBraveUrls(text: string): string {
  // Pattern: Brave URL followed by space-separated base64-looking fragments
  // Base64 chars: A-Z, a-z, 0-9, +, /, = (and _ for URL-safe variant)
  // Continue consuming fragments until we hit something that's clearly not base64
  // (like "ago", a number followed by time unit, or another URL)

  const braveUrlStart = /https:\/\/imgs\.search\.brave\.com\/[^\s]+/g;
  let result = text;
  let matchResult;

  // Find all Brave URLs and their positions
  const braveUrls: { url: string; start: number; end: number }[] = [];
  while ((matchResult = braveUrlStart.exec(text)) !== null) {
    braveUrls.push({
      url: matchResult[0],
      start: matchResult.index,
      end: matchResult.index + matchResult[0].length,
    });
  }

  // Process in reverse order to preserve positions
  for (let i = braveUrls.length - 1; i >= 0; i--) {
    const braveUrl = braveUrls[i];
    const afterUrl = text.slice(braveUrl.end);

    // Check if there are base64-looking fragments after the URL
    const fragments = afterUrl.split(/\s+/);
    let consumedLength = 0;
    let fragmentsToJoin: string[] = [];

    for (const fragment of fragments) {
      if (!fragment) {
        consumedLength += 1; // Account for the space
        continue;
      }

      // Stop if this looks like an age pattern
      if (/^\d+$/.test(fragment) || /^(hours?|days?|weeks?|months?|ago)$/i.test(fragment)) {
        break;
      }

      // Stop if this is another URL
      if (fragment.startsWith('http://') || fragment.startsWith('https://')) {
        break;
      }

      // Check if this looks like a base64 fragment (mostly alphanumeric)
      const isBase64Like = /^[A-Za-z0-9_/+=%-]+$/.test(fragment) && fragment.length > 2;

      if (isBase64Like) {
        fragmentsToJoin.push(fragment);
        consumedLength += fragment.length + 1; // +1 for the space before
      } else {
        break;
      }
    }

    // If we found fragments to join, rebuild the URL
    if (fragmentsToJoin.length > 0) {
      const fixedUrl = braveUrl.url + fragmentsToJoin.join('');
      const oldText = text.slice(braveUrl.start, braveUrl.end + consumedLength);
      result = result.replace(oldText, fixedUrl);
    }
  }

  return result;
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
  // Note: Kicker articles now use individual article titles as source names,
  // not the generic "Kicker RSS" label
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
  const citationMap = new Map<string, Citation>(); // Track unique citations by URL+source
  let citationCounter = 0;

  // Regex to match citation patterns:
  // - (via API-Football) - API sources
  // - (via [id] Title URL IMAGE AGE) - numbered news citations
  // - (via Title URL AGE) - legacy format
  const citationRegex = /\(via ([^)]+)\)/g;

  let lastIndex = 0;
  let match;

  while ((match = citationRegex.exec(text)) !== null) {
    const citationStart = match.index;
    const citationEnd = citationRegex.lastIndex;

    // Normalize whitespace: LLMs often break long URLs across lines
    // 1. Collapse all whitespace to single spaces
    // 2. Fix broken Brave URLs where base64 fragments got separated
    let rawSource = match[1].replace(/\s+/g, ' ').trim();
    rawSource = fixBrokenBraveUrls(rawSource);

    // Extract URL, image URL, favicon URL, and age
    // Formats supported:
    // - "[id] Title URL IMAGE AGE" (numbered format)
    // - "Title URL ImageURL FaviconURL Age" (legacy full format)
    // - "Title URL AGE" (simple format)
    let sourceName = rawSource;
    let sourceUrl: string | undefined;
    let imageUrl: string | undefined;
    let faviconUrl: string | undefined;
    let age: string | undefined;

    // Extract age pattern first (always at end): "X hours/days/weeks/months ago"
    const ageMatch = rawSource.match(/\s+(\d+\s+(?:hours?|days?|weeks?|months?)\s+ago)\s*$/i);
    const ageValue = ageMatch ? ageMatch[1] : undefined;
    // Remove age from rawSource for cleaner URL parsing
    const sourceWithoutAge = ageValue ? rawSource.slice(0, rawSource.lastIndexOf(ageValue)).trim() : rawSource;

    // Now extract URLs - find all https:// occurrences
    const urlMatches = sourceWithoutAge.match(/https?:\/\/\S+/g) || [];

    // Try numbered format first: "[id] Title URL IMAGE"
    const numberedMatch = sourceWithoutAge.match(/^\[(\d+)\]\s+(.*?)\s+(https?:\/\/\S+)(?:\s+(https?:\/\/\S+))?$/);
    if (numberedMatch) {
      // [1] = article ID (we don't use it directly, just for reference)
      sourceName = numberedMatch[2].trim();
      sourceUrl = numberedMatch[3];
      imageUrl = numberedMatch[4]; // May be undefined
      age = ageValue;
    }

    // If no numbered match, try legacy formats
    if (!sourceUrl) {
      // Try to match full format: "Source Name URL ImageURL FaviconURL Age"
      const fullMatch = rawSource.match(/(.*?)\s+(https?:\/\/\S+)\s+(https?:\/\/\S+)\s+(https?:\/\/\S+)\s+(.+)$/);
      if (fullMatch) {
        sourceName = fullMatch[1].trim();
        sourceUrl = fullMatch[2];
        imageUrl = fullMatch[3];
        faviconUrl = fullMatch[4];
        age = fullMatch[5].trim();
      } else {
        // Try format with 3 URLs: "Source Name URL ImageURL FaviconURL"
        const threeUrlMatch = rawSource.match(/(.*?)\s+(https?:\/\/\S+)\s+(https?:\/\/\S+)\s+(https?:\/\/\S+)$/);
        if (threeUrlMatch) {
          sourceName = threeUrlMatch[1].trim();
          sourceUrl = threeUrlMatch[2];
          imageUrl = threeUrlMatch[3];
          faviconUrl = threeUrlMatch[4];
        } else {
          // Try format with 2 URLs: "Source Name URL ImageURL"
          const twoUrlMatch = rawSource.match(/(.*?)\s+(https?:\/\/\S+)\s+(https?:\/\/\S+)$/);
          if (twoUrlMatch) {
            sourceName = twoUrlMatch[1].trim();
            sourceUrl = twoUrlMatch[2];
            imageUrl = twoUrlMatch[3];
          } else {
            // Try simple format: "Source Name URL Age" (1 URL + trailing age text)
            const simpleWithAgeMatch = rawSource.match(/(.*?)\s+(https?:\/\/\S+)\s+(\d+\s+(?:hours?|days?|weeks?|months?)\s+ago)$/i);
            if (simpleWithAgeMatch) {
              sourceName = simpleWithAgeMatch[1].trim();
              sourceUrl = simpleWithAgeMatch[2];
              age = simpleWithAgeMatch[3].trim();
            } else {
              // Fallback to single URL: "Source Name URL"
              const singleUrlMatch = rawSource.match(/(.*?)\s+(https?:\/\/\S+)$/);
              if (singleUrlMatch) {
                sourceName = singleUrlMatch[1].trim();
                sourceUrl = singleUrlMatch[2];
              }
            }
          }
        }
      }
    }

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
      // Use URL from citation if provided, otherwise fall back to metadata
      const metadata = SOURCE_METADATA[sourceName] || {};
      const finalUrl = sourceUrl || metadata.url;

      // CRITICAL: Deduplicate by URL only, NOT by source name
      // This ensures each article gets its own citation even if they share the same source
      const citationKey = finalUrl || `${sourceName}:${citationCounter + 1}`;

      // Check if we've seen this citation before (by URL)
      let citation = citationMap.get(citationKey);
      if (!citation) {
        // New citation - assign next number
        citationCounter++;
        citation = {
          text: citedText,
          source: sourceName,
          url: finalUrl,
          imageUrl: imageUrl, // Include image URL if present
          faviconUrl: faviconUrl, // Include favicon URL if present
          age: age, // Include age if present
          description: metadata.description || 'Article from Brave Search',
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
