/**
 * React hook for managing user preferences
 *
 * Provides centralized access to user profile with localStorage persistence
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  UserProfile,
  Language,
  DetailLevel,
  Persona,
  DEFAULT_PROFILE,
  loadUserProfile,
  saveUserProfile,
  hasCompletedOnboarding,
} from '@/lib/user-config';

export interface UseUserPreferencesResult {
  profile: UserProfile;
  updateLanguage: (language: Language) => void;
  updateDetailLevel: (level: DetailLevel) => void;
  updatePersona: (persona: Persona) => void;
  updateProfile: (profile: Partial<UserProfile>) => void;
  resetProfile: () => void;
  hasOnboarded: boolean;
  markOnboardingComplete: () => void;
}

/**
 * Hook for managing user preferences with localStorage persistence
 */
export function useUserPreferences(): UseUserPreferencesResult {
  const [profile, setProfile] = useState<UserProfile>(DEFAULT_PROFILE);
  const [hasOnboarded, setHasOnboarded] = useState(true);

  // Load preferences on mount
  useEffect(() => {
    const loaded = loadUserProfile();
    setProfile(loaded);
    setHasOnboarded(hasCompletedOnboarding());
  }, []);

  // Save preferences whenever they change
  const persistProfile = useCallback((newProfile: UserProfile) => {
    setProfile(newProfile);
    saveUserProfile(newProfile);
  }, []);

  const updateLanguage = useCallback(
    (language: Language) => {
      persistProfile({ ...profile, language });
    },
    [profile, persistProfile]
  );

  const updateDetailLevel = useCallback(
    (detailLevel: DetailLevel) => {
      persistProfile({ ...profile, detailLevel });
    },
    [profile, persistProfile]
  );

  const updatePersona = useCallback(
    (persona: Persona) => {
      persistProfile({ ...profile, persona });
    },
    [profile, persistProfile]
  );

  const updateProfile = useCallback(
    (updates: Partial<UserProfile>) => {
      persistProfile({ ...profile, ...updates });
    },
    [profile, persistProfile]
  );

  const resetProfile = useCallback(() => {
    persistProfile(DEFAULT_PROFILE);
  }, [persistProfile]);

  const markOnboardingComplete = useCallback(() => {
    setHasOnboarded(true);
    // Save current profile to mark onboarding as complete
    saveUserProfile(profile);
  }, [profile]);

  return {
    profile,
    updateLanguage,
    updateDetailLevel,
    updatePersona,
    updateProfile,
    resetProfile,
    hasOnboarded,
    markOnboardingComplete,
  };
}
