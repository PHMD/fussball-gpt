'use client';

import { useChat } from '@ai-sdk/react';
import { DefaultChatTransport } from 'ai';
import { useState } from 'react';
import {
  PromptInput,
  PromptInputTextarea,
  PromptInputToolbar,
  PromptInputSubmit,
} from '@/components/ui/prompt-input';
import { Response } from '@/components/ui/response';
import { Loader } from '@/components/ui/loader';
import { Suggestions, Suggestion } from '@/components/ui/suggestion';

export default function ChatPage() {
  const [input, setInput] = useState('');

  const { messages, sendMessage, status, stop } = useChat({
    transport: new DefaultChatTransport({
      // Relative URL - frontend and backend on same server
      api: '/api/query',
    }),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && status === 'ready') {
      sendMessage({ text: input });
      setInput('');
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="border-b p-4 bg-card">
        <h1 className="text-2xl font-bold">⚽ Fußball GPT</h1>
        <p className="text-sm text-muted-foreground">
          Bundesliga intelligence powered by AI
        </p>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.length === 0 && (
          <div className="text-center text-muted-foreground mt-16">
            <p className="text-lg mb-2">Welcome to Fußball GPT!</p>
            <p className="text-sm mb-6">Ask me anything about Bundesliga...</p>
            <div className="max-w-3xl mx-auto">
              <p className="text-xs text-muted-foreground mb-3">Try asking (English & German):</p>
              <Suggestions className="justify-center">
                <Suggestion
                  suggestion="What's the latest Bundesliga news?"
                  onClick={(text) => {
                    sendMessage({ text });
                  }}
                />
                <Suggestion
                  suggestion="Was sind die neuesten Bundesliga-Nachrichten?"
                  onClick={(text) => {
                    sendMessage({ text });
                  }}
                />
                <Suggestion
                  suggestion="Show me the current standings"
                  onClick={(text) => {
                    sendMessage({ text });
                  }}
                />
                <Suggestion
                  suggestion="Zeige mir die aktuelle Tabelle"
                  onClick={(text) => {
                    sendMessage({ text });
                  }}
                />
                <Suggestion
                  suggestion="Top scorers this season"
                  onClick={(text) => {
                    sendMessage({ text });
                  }}
                />
                <Suggestion
                  suggestion="Welche Spiele sind heute?"
                  onClick={(text) => {
                    sendMessage({ text });
                  }}
                />
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
                {message.role === 'user' ? 'You' : 'Fußball GPT'}
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
                  {status === 'submitted' ? 'Thinking...' : 'Streaming response...'}
                </span>
                <button
                  type="button"
                  onClick={() => stop()}
                  className="text-xs text-destructive hover:text-destructive/80 underline ml-2"
                >
                  Stop
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t p-4 bg-card">
        <div className="max-w-4xl mx-auto">
          <PromptInput onSubmit={handleSubmit}>
            <PromptInputTextarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about Bundesliga standings, players, fixtures..."
              disabled={status !== 'ready'}
            />
            <PromptInputToolbar className="justify-end">
              <PromptInputSubmit status={status} disabled={!input.trim()} />
            </PromptInputToolbar>
          </PromptInput>
          <p className="text-xs text-muted-foreground mt-3 text-center">
            Powered by Vercel AI SDK + Claude 4 Sonnet
          </p>
        </div>
      </div>
    </div>
  );
}
