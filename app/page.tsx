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
import { ArrowUpIcon, SquareIcon } from 'lucide-react';
import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from '@/components/ui/shadcn-io/ai/conversation';
import { Message, MessageContent } from '@/components/ui/shadcn-io/ai/message';
import { Loader } from '@/components/ui/loader';
import { Suggestions, Suggestion } from '@/components/ui/suggestion';
import { useUserPreferences } from '@/hooks/use-user-preferences';
import { WelcomeDialog } from '@/components/onboarding/welcome-dialog';
import { Language } from '@/lib/user-config';
import { AssistantMessage, SourcesCarousel } from '@/components/ui/assistant-message';

export default function ChatPage() {
  const [input, setInput] = useState('');

  // User preferences hook
  const { profile, hasOnboarded, markOnboardingComplete } = useUserPreferences();

  const { messages, sendMessage, status, stop } = useChat({
    transport: new DefaultChatTransport({
      // Relative URL - frontend and backend on same server
      api: '/api/query',
    }),
    // Send user profile with every request
    body: { userProfile: profile },
  });

  // Articles are now extracted per-message inside the render loop
  // This allows each message to have its own article carousel

  const handleSubmit = () => {
    if (input.trim() && status === 'ready') {
      sendMessage({ text: input });
      setInput('');
    }
  };

  // Handle onboarding completion
  const handleOnboardingComplete = () => {
    markOnboardingComplete();
  };

  const isGerman = profile.language === Language.GERMAN;

  const hasMessages = messages.length > 0;

  return (
    <div className="flex flex-col h-screen relative">
      {/* Onboarding Dialog */}
      {!hasOnboarded && (
        <WelcomeDialog
          onComplete={handleOnboardingComplete}
          onDismiss={markOnboardingComplete}
          currentLanguage={profile.language}
        />
      )}

      {/* Empty State - Centered Welcome + Input */}
      {!hasMessages && (
        <div className="flex-1 flex flex-col items-center justify-center px-4">
          <div className="text-center text-muted-foreground mb-8">
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

          {/* Centered Input for Empty State */}
          <div className="w-full max-w-2xl">
            <PromptInput
              className="bg-muted shadow-lg"
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
                  className="h-8 w-8 rounded-full"
                  disabled={!input.trim() || status !== 'ready'}
                  onClick={handleSubmit}
                >
                  {status === 'submitted' || status === 'streaming' ? (
                    <SquareIcon className="size-5 fill-current" />
                  ) : (
                    <ArrowUpIcon className="size-5" />
                  )}
                </Button>
              </PromptInputActions>
            </PromptInput>
          </div>
        </div>
      )}

      {/* Chat Messages - Only shown when there are messages */}
      {hasMessages && (
        <Conversation className="flex-1 relative" style={{ minHeight: 0 }}>
          <ConversationContent className="max-w-2xl mx-auto pb-48 px-4">

        {messages.map((message, messageIndex) => {
          // Extract articles from this message's parts for citation lookups
          const messageArticles = (() => {
            if (message.role !== 'assistant') return [];
            const articlesPart = message.parts.find(
              (part): part is { type: 'data-articles'; data: { articles: Array<{
                title: string;
                url?: string;
                image_url?: string;
                favicon_url?: string;
                age?: string;
                summary?: string;
              }> } } => part.type === 'data-articles'
            );
            return articlesPart?.data?.articles || [];
          })();

          const messageText = message.parts
            .map((part) => (part.type === 'text' ? part.text : ''))
            .join('');

          return (
            <div key={message.id}>
              <Message from={message.role === 'user' ? 'user' : 'assistant'}>
                <MessageContent>
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
                    <AssistantMessage
                      text={messageText}
                      articles={messageArticles}
                      language={profile.language}
                    />
                  )}
                </MessageContent>
              </Message>
              {/* Sources carousel OUTSIDE MessageContent for overflow effect */}
              {message.role === 'assistant' && (
                <SourcesCarousel
                  text={messageText}
                  articles={messageArticles}
                  language={profile.language}
                />
              )}
            </div>
          );
        })}

        {(status === 'submitted' || status === 'streaming') && (
          <Message from="assistant">
            <MessageContent>
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
            </MessageContent>
          </Message>
        )}
        </ConversationContent>

          {/* Fade effect overlay - positioned above content */}
          <div className="absolute bottom-0 left-0 right-0 h-48 bg-gradient-to-t from-background via-background to-transparent pointer-events-none z-[5]" />

          <ConversationScrollButton />
        </Conversation>
      )}

      {/* Floating Input - Only shown when there are messages */}
      {hasMessages && (
        <div className="fixed bottom-0 left-0 right-0 z-10 px-4 py-4 bg-background">
          <div className="max-w-2xl mx-auto">
            <PromptInput
              className="bg-muted shadow-lg"
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
                  className="h-8 w-8 rounded-full"
                  disabled={!input.trim() || status !== 'ready'}
                  onClick={handleSubmit}
                >
                  {status === 'submitted' || status === 'streaming' ? (
                    <SquareIcon className="size-5 fill-current" />
                  ) : (
                    <ArrowUpIcon className="size-5" />
                  )}
                </Button>
              </PromptInputActions>
            </PromptInput>
          </div>
        </div>
      )}
    </div>
  );
}
