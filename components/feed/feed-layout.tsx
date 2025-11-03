/**
 * Feed Layout Component
 *
 * Main layout with left sidebar navigation (Chat, Feed).
 * Responsive: collapsible drawer on mobile, persistent sidebar on desktop.
 */

'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { MessageSquare, Newspaper, Menu, X, Settings, User, PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface FeedLayoutProps {
  children: React.ReactNode;
  language?: 'en' | 'de';
  onSettingsClick: () => void;
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

export function FeedLayout({ children, language = 'en', onSettingsClick }: FeedLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const pathname = usePathname();
  const isGerman = language === 'de';

  // Load collapsed state from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('sidebar-collapsed');
    if (stored) {
      setSidebarCollapsed(stored === 'true');
    }
  }, []);

  // Save collapsed state to localStorage
  const toggleCollapsed = () => {
    const newState = !sidebarCollapsed;
    setSidebarCollapsed(newState);
    localStorage.setItem('sidebar-collapsed', String(newState));
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Floating Panel Button (Desktop Collapsed State) */}
      <div
        className={cn(
          'hidden lg:block fixed top-4 left-4 z-30',
          'transition-opacity duration-500 ease-in-out',
          sidebarCollapsed ? 'opacity-100' : 'opacity-0 pointer-events-none'
        )}
      >
        <div
          onClick={toggleCollapsed}
          className="p-3 cursor-pointer hover:bg-muted/50 rounded-lg transition-colors"
          role="button"
          tabIndex={0}
          aria-label={isGerman ? 'Seitenleiste öffnen' : 'Open sidebar'}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              toggleCollapsed();
            }
          }}
        >
          <PanelLeftOpen className="h-6 w-6" />
        </div>
      </div>

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed top-0 left-0 h-screen bg-muted border-r z-40',
          'flex flex-col w-64',
          'transition-transform duration-500 ease-in-out',
          // Mobile: drawer behavior
          sidebarOpen ? 'translate-x-0' : '-translate-x-full',
          // Desktop: slide in/out, stay fixed when collapsed for proper content centering
          sidebarCollapsed ? 'lg:-translate-x-full' : 'lg:translate-x-0'
        )}
      >
        {/* Sidebar Header */}
        <div className="p-4 border-b flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">⚽</span>
            <h2 className="font-bold text-lg">Fußball GPT</h2>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={toggleCollapsed}
              className="hidden lg:block p-2 hover:bg-background rounded-lg transition-colors"
              aria-label={isGerman ? 'Seitenleiste einklappen' : 'Collapse sidebar'}
            >
              <PanelLeftClose className="h-5 w-5" />
            </button>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 hover:bg-muted rounded-lg transition-colors"
              aria-label={isGerman ? 'Schließen' : 'Close'}
            >
              <X className="h-5 w-5" />
            </button>
          </div>
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

        {/* Profile Section */}
        <div className="p-4 border-t">
          <button
            onClick={onSettingsClick}
            className="flex items-center gap-3 w-full hover:bg-muted/50 rounded-lg p-2 -m-2 transition-colors"
          >
            {/* Avatar */}
            <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center shrink-0">
              <User className="h-5 w-5 text-muted-foreground" />
            </div>
            {/* User Info */}
            <div className="flex-1 min-w-0 text-left">
              <div className="text-sm font-medium">User Profile</div>
            </div>
            {/* Settings Icon */}
            <Settings className="h-4 w-4 shrink-0" />
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div
        className={cn(
          "flex-1 flex flex-col min-w-0 transition-all duration-500 ease-in-out",
          // Add left margin on desktop when sidebar is open
          !sidebarCollapsed ? "lg:ml-64" : "lg:ml-0"
        )}
      >
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
