/**
 * Settings panel for updating user preferences
 *
 * Allows users to change language, detail level, and persona after onboarding
 */

'use client';

import { useState } from 'react';
import {
  Language,
  DetailLevel,
  Persona,
  LABELS,
  type UserProfile,
} from '@/lib/user-config';

interface SettingsPanelProps {
  profile: UserProfile;
  onUpdate: (profile: Partial<UserProfile>) => void;
  onClose: () => void;
}

export function SettingsPanel({ profile, onUpdate, onClose }: SettingsPanelProps) {
  const [language, setLanguage] = useState(profile.language);
  const [detailLevel, setDetailLevel] = useState(profile.detailLevel);
  const [persona, setPersona] = useState(profile.persona);

  const handleSave = () => {
    onUpdate({ language, detailLevel, persona });
    onClose();
  };

  const isGerman = language === Language.GERMAN;

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-card border rounded-lg shadow-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">
            {isGerman ? 'Einstellungen' : 'Settings'}
          </h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
            aria-label="Close"
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Language Section */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">
            {isGerman ? 'Sprache' : 'Language'}
          </h3>
          <div className="grid grid-cols-2 gap-4">
            {Object.values(Language).map((lang) => (
              <button
                key={lang}
                onClick={() => setLanguage(lang)}
                className={`p-4 rounded-lg border-2 transition-all hover:border-primary ${
                  language === lang
                    ? 'border-primary bg-primary/10'
                    : 'border-border'
                }`}
              >
                <div className="text-3xl mb-1">{LABELS.language[lang].flag}</div>
                <div className="font-semibold">
                  {LABELS.language[lang][lang === Language.GERMAN ? 'de' : 'en']}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Detail Level Section */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">
            {isGerman ? 'Detailgrad' : 'Detail Level'}
          </h3>
          <div className="space-y-2">
            {Object.values(DetailLevel).map((level) => (
              <button
                key={level}
                onClick={() => setDetailLevel(level)}
                className={`w-full p-3 rounded-lg border-2 text-left transition-all hover:border-primary ${
                  detailLevel === level
                    ? 'border-primary bg-primary/10'
                    : 'border-border'
                }`}
              >
                <div className="font-semibold text-sm mb-0.5">
                  {LABELS.detailLevel[level][isGerman ? 'de' : 'en']}
                </div>
                <div className="text-xs text-muted-foreground">
                  {LABELS.detailLevel[level].description[isGerman ? 'de' : 'en']}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Persona Section */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">
            {isGerman ? 'Profil' : 'Profile'}
          </h3>
          <div className="grid grid-cols-2 gap-2">
            {Object.values(Persona).map((p) => (
              <button
                key={p}
                onClick={() => setPersona(p)}
                className={`p-3 rounded-lg border-2 text-left transition-all hover:border-primary ${
                  persona === p
                    ? 'border-primary bg-primary/10'
                    : 'border-border'
                }`}
              >
                <div className="font-semibold text-xs mb-0.5">
                  {LABELS.persona[p][isGerman ? 'de' : 'en']}
                </div>
                <div className="text-[10px] text-muted-foreground leading-tight">
                  {LABELS.persona[p].description[isGerman ? 'de' : 'en']}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-2 pt-4 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg border hover:bg-muted transition-colors"
          >
            {isGerman ? 'Abbrechen' : 'Cancel'}
          </button>
          <button
            onClick={handleSave}
            className="px-6 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-semibold"
          >
            {isGerman ? 'Speichern' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}
