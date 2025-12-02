/**
 * Server-side Image Proxy API
 *
 * Fetches external images server-side to bypass CORS and 403 restrictions.
 * Extracts original URLs from Brave Search proxy URLs (base64 encoded).
 */

import { NextRequest, NextResponse } from 'next/server';

// Cache images for 1 hour
const CACHE_MAX_AGE = 3600;

/**
 * Extract original image URL from Brave Search proxy URL.
 * Brave encodes the original URL as base64 in the path.
 * Example: imgs.search.brave.com/.../aHR0cHM6Ly9tZWRp... -> https://mediadb.kicker.de/...
 */
function extractOriginalUrl(imageUrl: string): string {
  // Check if this is a Brave Search proxy URL
  if (imageUrl.includes('imgs.search.brave.com')) {
    try {
      const url = new URL(imageUrl);
      const pathParts = url.pathname.split('/');
      // The last part of the path is the base64-encoded original URL
      const base64Part = pathParts[pathParts.length - 1];
      if (base64Part) {
        // Brave uses URL-safe base64 (with slashes in path segments)
        // Combine all path segments after the resize parameters
        const base64Segments = pathParts.slice(4).join(''); // Skip /hash/rs:fit:w:h:1:0/g:ce/
        const decoded = Buffer.from(base64Segments, 'base64').toString('utf-8');
        if (decoded.startsWith('http')) {
          console.log(`Decoded Brave URL: ${decoded}`);
          return decoded;
        }
      }
    } catch (e) {
      console.log('Failed to decode Brave URL, using original:', e);
    }
  }
  return imageUrl;
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  let imageUrl = searchParams.get('url');

  if (!imageUrl) {
    return new NextResponse('Missing url parameter', { status: 400 });
  }

  try {
    // Extract original URL if this is a Brave proxy URL
    imageUrl = extractOriginalUrl(imageUrl);

    // Validate URL
    const url = new URL(imageUrl);

    // Only allow http/https protocols
    if (!['http:', 'https:'].includes(url.protocol)) {
      return new NextResponse('Invalid protocol', { status: 400 });
    }

    // Fetch the image server-side with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

    const response = await fetch(imageUrl, {
      signal: controller.signal,
      headers: {
        // Mimic browser request to avoid bot blocking
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': url.origin,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      console.error(`Image proxy failed: ${response.status} for ${imageUrl}`);
      return new NextResponse('Failed to fetch image', { status: response.status });
    }

    // Get content type from response
    const contentType = response.headers.get('content-type') || 'image/jpeg';

    // Get image data as array buffer
    const imageBuffer = await response.arrayBuffer();

    // Return proxied image with caching headers
    return new NextResponse(imageBuffer, {
      headers: {
        'Content-Type': contentType,
        'Cache-Control': `public, max-age=${CACHE_MAX_AGE}, s-maxage=${CACHE_MAX_AGE}`,
        'Access-Control-Allow-Origin': '*',
      },
    });
  } catch (error) {
    console.error('Image proxy error:', error);
    return new NextResponse('Image proxy error', { status: 500 });
  }
}
