/**
 * Image proxy utility
 *
 * Uses local API route to proxy external images server-side,
 * bypassing CORS restrictions and 403 blocking from Brave Search.
 */

/**
 * Proxy an image URL through our local API route.
 * Server-side fetch bypasses CORS and referrer restrictions.
 *
 * @param imageUrl - The original image URL to proxy
 * @returns Proxied URL that can be loaded without CORS issues
 */
export function proxyImageUrl(imageUrl: string | undefined): string | undefined {
  if (!imageUrl) return undefined;

  // Skip if already proxied or is a data URL
  if (imageUrl.startsWith('/api/image-proxy') || imageUrl.startsWith('data:')) {
    return imageUrl;
  }

  // Use local API route for server-side proxying
  return `/api/image-proxy?url=${encodeURIComponent(imageUrl)}`;
}

/**
 * Proxy image URL for thumbnails.
 * Uses our server-side proxy to fetch images.
 */
export function proxyThumbnail(imageUrl: string | undefined): string | undefined {
  return proxyImageUrl(imageUrl);
}
