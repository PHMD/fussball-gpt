/**
 * Welcome dialog for first-time users
 *
 * Guides users through language, detail level, and persona selection
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

interface WelcomeDialogProps {
  onComplete: (profile: Partial<UserProfile>) => void;
  onDismiss?: () => void;
  currentLanguage?: Language;
}

export function WelcomeDialog({
  onComplete,
  onDismiss,
  currentLanguage = Language.GERMAN,
}: WelcomeDialogProps) {
  const [step, setStep] = useState(1);
  const [selectedLanguage, setSelectedLanguage] = useState(currentLanguage);
  const [selectedDetail, setSelectedDetail] = useState(DetailLevel.BALANCED);
  const [selectedPersona, setSelectedPersona] = useState(Persona.CASUAL_FAN);

  const handleComplete = () => {
    onComplete({
      language: selectedLanguage,
      detailLevel: selectedDetail,
      persona: selectedPersona,
    });
  };

  const isGerman = selectedLanguage === Language.GERMAN;

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-card border rounded-lg shadow-lg max-w-2xl w-full p-6">
        {/* Header */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold mb-2">
            {isGerman ? 'Willkommen bei Fußball GPT!' : 'Welcome to Fußball GPT!'}
          </h2>
          <p className="text-muted-foreground">
            {isGerman
              ? 'Personalisiere deine Erfahrung in 3 einfachen Schritten'
              : 'Customize your experience in 3 simple steps'}
          </p>
        </div>

        {/* Step Indicator */}
        <div className="flex gap-2 mb-6">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={`flex-1 h-2 rounded-full transition-colors ${
                s <= step ? 'bg-primary' : 'bg-muted'
              }`}
            />
          ))}
        </div>

        {/* Step 1: Language Selection */}
        {step === 1 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">
              {isGerman ? 'Wähle deine Sprache' : 'Choose your language'}
            </h3>
            <div className="grid grid-cols-2 gap-4">
              {Object.values(Language).map((lang) => (
                <button
                  key={lang}
                  onClick={() => setSelectedLanguage(lang)}
                  className={`p-6 rounded-lg border-2 transition-all hover:border-primary ${
                    selectedLanguage === lang
                      ? 'border-primary bg-primary/10'
                      : 'border-border'
                  }`}
                >
                  <div className="text-4xl mb-2">{LABELS.language[lang].flag}</div>
                  <div className="font-semibold text-lg">
                    {LABELS.language[lang][lang === Language.GERMAN ? 'de' : 'en']}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Detail Level */}
        {step === 2 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">
              {isGerman
                ? 'Wie ausführlich sollen die Antworten sein?'
                : 'How detailed should responses be?'}
            </h3>
            <div className="space-y-3">
              {Object.values(DetailLevel).map((level) => (
                <button
                  key={level}
                  onClick={() => setSelectedDetail(level)}
                  className={`w-full p-4 rounded-lg border-2 text-left transition-all hover:border-primary ${
                    selectedDetail === level
                      ? 'border-primary bg-primary/10'
                      : 'border-border'
                  }`}
                >
                  <div className="font-semibold mb-1">
                    {LABELS.detailLevel[level][isGerman ? 'de' : 'en']}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {LABELS.detailLevel[level].description[isGerman ? 'de' : 'en']}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Persona (Optional) */}
        {step === 3 && (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold">
                {isGerman ? 'Was beschreibt dich am besten?' : 'What describes you best?'}
              </h3>
              <p className="text-sm text-muted-foreground mt-1">
                {isGerman ? '(Optional - hilft uns, Inhalte anzupassen)' : '(Optional - helps us tailor content)'}
              </p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {Object.values(Persona).map((persona) => (
                <button
                  key={persona}
                  onClick={() => setSelectedPersona(persona)}
                  className={`p-4 rounded-lg border-2 text-left transition-all hover:border-primary ${
                    selectedPersona === persona
                      ? 'border-primary bg-primary/10'
                      : 'border-border'
                  }`}
                >
                  <div className="font-semibold text-sm mb-1">
                    {LABELS.persona[persona][isGerman ? 'de' : 'en']}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {LABELS.persona[persona].description[isGerman ? 'de' : 'en']}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between mt-8 pt-4 border-t">
          <div>
            {step > 1 && (
              <button
                onClick={() => setStep(step - 1)}
                className="px-4 py-2 rounded-lg border hover:bg-muted transition-colors"
              >
                {isGerman ? 'Zurück' : 'Back'}
              </button>
            )}
          </div>
          <div className="flex gap-2">
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="px-4 py-2 rounded-lg text-muted-foreground hover:text-foreground transition-colors"
              >
                {isGerman ? 'Überspringen' : 'Skip'}
              </button>
            )}
            {step < 3 ? (
              <button
                onClick={() => setStep(step + 1)}
                className="px-6 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                {isGerman ? 'Weiter' : 'Next'}
              </button>
            ) : (
              <button
                onClick={handleComplete}
                className="px-6 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-semibold"
              >
                {isGerman ? 'Fertig' : 'Complete'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
