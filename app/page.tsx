'use client';

import { useChat } from '@ai-sdk/react';
import { DefaultChatTransport } from 'ai';
import { useState } from 'react';
import {
  PromptInput,
  PromptInputTextarea,
  PromptInputActions,
} from '@/components/ui/prompt-input';
import { Button } from '@/components/ui/button';
import { SendIcon, Loader2Icon, SquareIcon } from 'lucide-react';
import { Response } from '@/components/ui/response';
import { Loader } from '@/components/ui/loader';
import { Suggestions, Suggestion } from '@/components/ui/suggestion';
import { useUserPreferences } from '@/hooks/use-user-preferences';
import { WelcomeDialog } from '@/components/onboarding/welcome-dialog';
import { SettingsPanel } from '@/components/settings/settings-panel';
import { Language } from '@/lib/user-config';

export default function ChatPage() {
  const [input, setInput] = useState('');
  const [showSettings, setShowSettings] = useState(false);

  // User preferences hook
  const { profile, updateProfile, hasOnboarded, markOnboardingComplete } = useUserPreferences();

  const { messages, sendMessage, status, stop } = useChat({
    transport: new DefaultChatTransport({
      // Relative URL - frontend and backend on same server
      api: '/api/query',
    }),
    // Send user profile with every request
    body: { userProfile: profile },
  });

  const handleSubmit = () => {
    if (input.trim() && status === 'ready') {
      sendMessage({ text: input });
      setInput('');
    }
  };

  // Handle onboarding completion
  const handleOnboardingComplete = (updates: Partial<typeof profile>) => {
    updateProfile(updates);
    markOnboardingComplete();
  };

  const isGerman = profile.language === Language.GERMAN;

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Onboarding Dialog */}
      {!hasOnboarded && (
        <WelcomeDialog
          onComplete={handleOnboardingComplete}
          onDismiss={markOnboardingComplete}
          currentLanguage={profile.language}
        />
      )}

      {/* Settings Panel */}
      {showSettings && (
        <SettingsPanel
          profile={profile}
          onUpdate={updateProfile}
          onClose={() => setShowSettings(false)}
        />
      )}

      {/* Header */}
      <header className="border-b p-4 bg-card">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">⚽ Fußball GPT</h1>
            <p className="text-sm text-muted-foreground">
              {isGerman ? 'Bundesliga-Intelligenz mit KI' : 'Bundesliga intelligence powered by AI'}
            </p>
          </div>
          <button
            onClick={() => setShowSettings(true)}
            className="p-2 hover:bg-muted rounded-lg transition-colors"
            aria-label={isGerman ? 'Einstellungen' : 'Settings'}
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
              <circle cx="12" cy="12" r="3" />
              <path d="M12 1v6m0 6v6m-9-9h6m6 0h6" />
            </svg>
          </button>
        </div>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.length === 0 && (
          <div className="text-center text-muted-foreground mt-16">
            <p className="text-lg mb-2">
              {isGerman ? 'Willkommen bei Fußball GPT!' : 'Welcome to Fußball GPT!'}
            </p>
            <p className="text-sm mb-6">
              {isGerman
                ? 'Frag mich alles über die Bundesliga...'
                : 'Ask me anything about Bundesliga...'}
            </p>
            <div className="max-w-3xl mx-auto">
              <p className="text-xs text-muted-foreground mb-3">
                {isGerman ? 'Beispielfragen:' : 'Try asking:'}
              </p>
              <Suggestions className="justify-center">
                {isGerman ? (
                  <>
                    <Suggestion
                      suggestion="Was sind die neuesten Bundesliga-Nachrichten?"
                      onClick={(text) => sendMessage({ text })}
                    />
                    <Suggestion
                      suggestion="Zeige mir die aktuelle Tabelle"
                      onClick={(text) => sendMessage({ text })}
                    />
                    <Suggestion
                      suggestion="Wer ist aktueller Torschützenkönig?"
                      onClick={(text) => sendMessage({ text })}
                    />
                    <Suggestion
                      suggestion="Welche Spiele sind heute?"
                      onClick={(text) => sendMessage({ text })}
                    />
                  </>
                ) : (
                  <>
                    <Suggestion
                      suggestion="What's the latest Bundesliga news?"
                      onClick={(text) => sendMessage({ text })}
                    />
                    <Suggestion
                      suggestion="Show me the current standings"
                      onClick={(text) => sendMessage({ text })}
                    />
                    <Suggestion
                      suggestion="Who is the top scorer?"
                      onClick={(text) => sendMessage({ text })}
                    />
                    <Suggestion
                      suggestion="What matches are today?"
                      onClick={(text) => sendMessage({ text })}
                    />
                  </>
                )}
              </Suggestions>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[85%] rounded-lg ${
                message.role === 'user'
                  ? 'bg-primary text-primary-foreground px-4 py-2'
                  : 'bg-card border px-4 py-3'
              }`}
            >
              <div className="text-xs font-semibold mb-2 opacity-70">
                {message.role === 'user' ? (isGerman ? 'Du' : 'You') : 'Fußball GPT'}
              </div>
              {message.role === 'user' ? (
                <div className="text-sm">
                  {message.parts.map((part, index) => {
                    if (part.type === 'text') {
                      return <span key={index}>{part.text}</span>;
                    }
                    return null;
                  })}
                </div>
              ) : (
                <Response>
                  {message.parts
                    .map((part) => (part.type === 'text' ? part.text : ''))
                    .join('')}
                </Response>
              )}
            </div>
          </div>
        ))}

        {(status === 'submitted' || status === 'streaming') && (
          <div className="flex justify-start">
            <div className="bg-card border rounded-lg px-4 py-3">
              <div className="flex items-center gap-3">
                <Loader size={16} />
                <span className="text-sm text-muted-foreground">
                  {status === 'submitted'
                    ? (isGerman ? 'Denke nach...' : 'Thinking...')
                    : (isGerman ? 'Streame Antwort...' : 'Streaming response...')}
                </span>
                <button
                  type="button"
                  onClick={() => stop()}
                  className="text-xs text-destructive hover:text-destructive/80 underline ml-2"
                >
                  {isGerman ? 'Stopp' : 'Stop'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t p-4 bg-card">
        <div className="max-w-4xl mx-auto">
          <PromptInput
            value={input}
            onValueChange={setInput}
            onSubmit={handleSubmit}
            isLoading={status === 'submitted' || status === 'streaming'}
          >
            <PromptInputTextarea
              placeholder={
                isGerman
                  ? 'Frage nach Tabelle, Spielern, Spielen...'
                  : 'Ask about Bundesliga standings, players, fixtures...'
              }
              disabled={status !== 'ready'}
            />
            <PromptInputActions className="justify-end">
              <Button
                type="submit"
                size="icon"
                disabled={!input.trim() || status !== 'ready'}
                onClick={handleSubmit}
              >
                {status === 'submitted' ? (
                  <Loader2Icon className="size-4 animate-spin" />
                ) : status === 'streaming' ? (
                  <SquareIcon className="size-4" />
                ) : (
                  <SendIcon className="size-4" />
                )}
              </Button>
            </PromptInputActions>
          </PromptInput>
          <p className="text-xs text-muted-foreground mt-3 text-center">
            {isGerman
              ? 'Angetrieben von Vercel AI SDK + Claude 4 Sonnet'
              : 'Powered by Vercel AI SDK + Claude 4 Sonnet'}
          </p>
        </div>
      </div>
    </div>
  );
}
