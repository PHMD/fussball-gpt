/**
 * FeedLayout Wrapper
 *
 * Client component wrapper that provides FeedLayout with user preferences.
 * Used in root layout to provide consistent navigation across all pages.
 */

'use client';

import { FeedLayout } from './feed-layout';
import { useUserPreferences } from '@/hooks/use-user-preferences';

export function FeedLayoutWrapper({ children }: { children: React.ReactNode }) {
  const { profile } = useUserPreferences();

  return (
    <FeedLayout language={profile.language}>
      {children}
    </FeedLayout>
  );
}
