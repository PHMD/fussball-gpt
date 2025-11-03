/**
 * Feed Layout Component
 *
 * Main layout with left sidebar navigation (Chat, Feed).
 * Responsive: collapsible drawer on mobile, persistent sidebar on desktop.
 */

'use client';

import { useState } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { MessageSquare, Newspaper, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface FeedLayoutProps {
  children: React.ReactNode;
  language?: 'en' | 'de';
}

const navigationItems = [
  {
    href: '/',
    icon: MessageSquare,
    label: { en: 'Chat', de: 'Chat' },
    id: 'chat',
  },
  {
    href: '/feed',
    icon: Newspaper,
    label: { en: 'Feed', de: 'Feed' },
    id: 'feed',
  },
];

export function FeedLayout({ children, language = 'en' }: FeedLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const pathname = usePathname();
  const isGerman = language === 'de';

  return (
    <div className="flex h-screen bg-background">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed lg:sticky top-0 left-0 h-screen bg-muted border-r z-50 transition-transform duration-200',
          'w-64 flex flex-col',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Sidebar Header */}
        <div className="p-4 border-b flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">⚽</span>
            <h2 className="font-bold text-lg">Fußball GPT</h2>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 hover:bg-muted rounded-lg transition-colors"
            aria-label={isGerman ? 'Schließen' : 'Close'}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.id}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-muted text-foreground'
                )}
              >
                <Icon className="h-5 w-5 shrink-0" />
                <span className="font-medium">
                  {item.label[isGerman ? 'de' : 'en']}
                </span>
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t">
          <p className="text-xs text-muted-foreground">
            {isGerman
              ? 'Bundesliga-Intelligenz mit KI'
              : 'Bundesliga intelligence powered by AI'}
          </p>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Header with Menu Button */}
        <header className="lg:hidden border-b p-4 bg-muted flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(true)}
            aria-label={isGerman ? 'Menü öffnen' : 'Open menu'}
          >
            <Menu className="h-5 w-5" />
          </Button>
          <h1 className="text-lg font-bold">
            {pathname === '/feed'
              ? isGerman
                ? 'News-Feed'
                : 'News Feed'
              : isGerman
              ? 'Chat'
              : 'Chat'}
          </h1>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
