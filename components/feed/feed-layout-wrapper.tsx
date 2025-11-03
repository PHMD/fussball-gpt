/**
 * FeedLayout Wrapper
 *
 * Client component wrapper that provides FeedLayout with user preferences.
 * Used in root layout to provide consistent navigation across all pages.
 */

'use client';

import { useState } from 'react';
import { FeedLayout } from './feed-layout';
import { useUserPreferences } from '@/hooks/use-user-preferences';
import { SettingsPanel } from '@/components/settings/settings-panel';

export function FeedLayoutWrapper({ children }: { children: React.ReactNode }) {
  const { profile, updateProfile } = useUserPreferences();
  const [showSettings, setShowSettings] = useState(false);

  return (
    <>
      {showSettings && (
        <SettingsPanel
          profile={profile}
          onUpdate={updateProfile}
          onClose={() => setShowSettings(false)}
        />
      )}
      <FeedLayout
        language={profile.language}
        onSettingsClick={() => setShowSettings(true)}
      >
        {children}
      </FeedLayout>
    </>
  );
}
