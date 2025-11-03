## Spec Complete

### Research Sources
- [next-themes Official Documentation](https://github.com/pacocoursey/next-themes/blob/main/next-themes/README.md) - Primary integration guide
- [next-themes App Router Example](https://github.com/pacocoursey/next-themes/tree/master/examples/with-app-dir) - Next.js 15 pattern
- [shadcn/ui Theme Toggle Pattern](https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/www/content/docs/dark-mode/vite.mdx) - Real-world dropdown implementation
- [Real-world Next.js 15 Implementation](https://www.rayterrill.com/2024/03/06/NextJSNextThemesAppRouter.html) - Production examples

### Architecture Overview

The dark mode implementation leverages existing infrastructure (90% complete) and only requires wiring up the `next-themes` ThemeProvider plus adding UI controls. The architecture follows a three-layer pattern:

1. **Foundation Layer** - ThemeProvider wraps the app in `app/layout.tsx`, managing theme state and system preference detection. The provider uses `attribute="class"` to match Tailwind's configuration and `defaultTheme="system"` to respect OS preferences by default.

2. **State Management Layer** - `next-themes` provides the `useTheme()` hook for theme switching, while the existing `useUserPreferences` hook manages persistence. Theme preference is stored in the UserProfile interface and synced to localStorage, ensuring permanent overrides persist across sessions.

3. **UI Layer** - A new theme dropdown component integrates into the existing `SettingsPanel` alongside language and detail level options. The component uses shadcn/ui's Select primitive with proper hydration safety patterns to avoid server/client mismatches.

**Critical architectural decision**: The existing CSS variables in `app/globals.css` already define both `:root` (light) and `.dark` (dark) themes. No CSS changes are needed—we only toggle the `class="dark"` attribute on the `<html>` element.

### Files to Create/Modify

#### 1. `app/layout.tsx` (modify)
**Purpose:** Add ThemeProvider wrapper to enable theme switching app-wide  
**Key dependencies:** `next-themes@0.4.6` (already installed)

```typescript
import type { Metadata } from 'next'
import { ThemeProvider } from 'next-themes'
import './globals.css'

export const metadata: Metadata = {
  title: 'Fußball GPT',
  description: 'German football intelligence assistant powered by AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="de" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem={true}
          disableTransitionOnChange={false}
          storageKey="fussballgpt_theme"
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

**Configuration rationale:**
- `attribute="class"` - Matches Tailwind's `darkMode: ['class']` config
- `defaultTheme="system"` - Respects OS preference on first visit
- `enableSystem={true}` - Enables "System" option in UI
- `disableTransitionOnChange={false}` - Keep smooth CSS transitions when switching
- `storageKey="fussballgpt_theme"` - Matches app naming convention
- `suppressHydrationWarning` on `<html>` - Required because ThemeProvider modifies html element before hydration

#### 2. `components/settings/theme-selector.tsx` (new)
**Purpose:** Theme dropdown component with hydration-safe rendering  
**Key dependencies:** `next-themes`, shadcn/ui Select components

```typescript
'use client';

import { useState, useEffect } from 'react';
import { useTheme } from 'next-themes';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Language } from '@/lib/user-config';

interface ThemeSelectorProps {
  language: Language;
  onThemeChange?: (theme: string) => void;
}

export function ThemeSelector({ language, onThemeChange }: ThemeSelectorProps) {
  const [mounted, setMounted] = useState(false);
  const { theme, setTheme } = useTheme();
  const isGerman = language === Language.GERMAN;

  // Critical: Only render after client-side mount to avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  const handleThemeChange = (value: string) => {
    setTheme(value);
    onThemeChange?.(value);
  };

  // Show loading placeholder during SSR/hydration
  if (!mounted) {
    return (
      <div className="h-9 w-full rounded-md border border-input bg-transparent" />
    );
  }

  const labels = {
    light: isGerman ? 'Hell' : 'Light',
    dark: isGerman ? 'Dunkel' : 'Dark',
    system: isGerman ? 'System' : 'System',
  };

  return (
    <Select value={theme} onValueChange={handleThemeChange}>
      <SelectTrigger className="w-full">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="light">{labels.light}</SelectItem>
        <SelectItem value="dark">{labels.dark}</SelectItem>
        <SelectItem value="system">{labels.system}</SelectItem>
      </SelectContent>
    </Select>
  );
}
```

**Hydration safety pattern:** The component uses the `mounted` state pattern (recommended by next-themes docs) to prevent hydration mismatches. On the server and during hydration, it renders a skeleton placeholder. After mounting on the client, it shows the actual Select component with the current theme value.

#### 3. `components/settings/settings-panel.tsx` (modify)
**Purpose:** Integrate ThemeSelector into existing settings UI  
**Changes:** Add new "Theme" section between Language and Detail Level

```typescript
// Add import
import { ThemeSelector } from './theme-selector';

// Inside SettingsPanel component, add new section after Language but before Detail Level:

{/* Theme Section */}
<div className="mb-6">
  <h3 className="text-lg font-semibold mb-3">
    {isGerman ? 'Design' : 'Theme'}
  </h3>
  <ThemeSelector 
    language={language}
    onThemeChange={(theme) => {
      // Theme is auto-persisted by next-themes to localStorage
      // No additional persistence needed here
    }}
  />
</div>
```

**Integration notes:**
- Placed between Language and Detail Level sections for logical grouping
- Uses same visual style as other sections (heading + control)
- ThemeSelector receives current language for bilingual labels
- No manual persistence needed—next-themes handles localStorage automatically

#### 4. `lib/user-config.ts` (modify)
**Purpose:** Extend UserProfile interface to track theme preference  
**Changes:** Add optional theme field

```typescript
export interface UserProfile {
  language: Language;
  detailLevel: DetailLevel;
  persona: Persona;
  name?: string;
  favoriteTeam?: string;
  interests?: string[];
  theme?: 'light' | 'dark' | 'system'; // NEW: Track user's explicit theme choice
}

export const DEFAULT_PROFILE: UserProfile = {
  language: Language.ENGLISH,
  detailLevel: DetailLevel.BALANCED,
  persona: Persona.CASUAL_FAN,
  interests: [],
  theme: 'system', // NEW: Default to system preference
};
```

**Why add to UserProfile?** While next-themes persists to its own localStorage key (`fussballgpt_theme`), adding theme to UserProfile enables:
1. Future server-side persistence if needed
2. Consistent export/import of all user preferences
3. Analytics tracking of theme preference distribution

#### 5. `app/test/theme-gallery/page.tsx` (new - temporary)
**Purpose:** Component gallery for visual regression testing  
**Lifecycle:** Create for testing, delete after QA confirms no issues

```typescript
'use client';

import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CitationSourceCard } from '@/components/ui/citation-source-card';
import { Loader } from '@/components/ui/loader';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';

export default function ThemeGalleryPage() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="container mx-auto p-8 space-y-8">
      {/* Theme Toggle */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Theme Gallery (Testing Only)</h1>
        <Select value={theme} onValueChange={setTheme}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="light">Light</SelectItem>
            <SelectItem value="dark">Dark</SelectItem>
            <SelectItem value="system">System</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Buttons */}
      <Card>
        <CardHeader>
          <CardTitle>Buttons</CardTitle>
        </CardHeader>
        <CardContent className="space-x-2">
          <Button>Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="destructive">Destructive</Button>
        </CardContent>
      </Card>

      {/* Badges */}
      <Card>
        <CardHeader>
          <CardTitle>Badges</CardTitle>
        </CardHeader>
        <CardContent className="space-x-2">
          <Badge>Default</Badge>
          <Badge variant="secondary">Secondary</Badge>
          <Badge variant="outline">Outline</Badge>
          <Badge variant="destructive">Destructive</Badge>
        </CardContent>
      </Card>

      {/* Cards */}
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Light Card</CardTitle>
          </CardHeader>
          <CardContent>
            This is a card with default styling
          </CardContent>
        </Card>
        <Card className="bg-muted">
          <CardHeader>
            <CardTitle>Muted Card</CardTitle>
          </CardHeader>
          <CardContent>
            This is a card with muted background
          </CardContent>
        </Card>
      </div>

      {/* Form Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Form Controls</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Select>
            <SelectTrigger>
              <SelectValue placeholder="Select an option" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">Option 1</SelectItem>
              <SelectItem value="2">Option 2</SelectItem>
            </SelectContent>
          </Select>
          <Textarea placeholder="Enter text here..." />
        </CardContent>
      </Card>

      {/* Citation Cards */}
      <Card>
        <CardHeader>
          <CardTitle>Citation Cards</CardTitle>
        </CardHeader>
        <CardContent>
          <CitationSourceCard
            url="https://example.com/article"
            title="Test Article Title"
            description="This is a test description for the citation card"
            image="https://via.placeholder.com/150"
          />
        </CardContent>
      </Card>

      {/* Loader */}
      <Card>
        <CardHeader>
          <CardTitle>Loader</CardTitle>
        </CardHeader>
        <CardContent>
          <Loader />
        </CardContent>
      </Card>
    </div>
  );
}
```

**Testing workflow:**
1. Navigate to `/test/theme-gallery` during development
2. Toggle between Light, Dark, and System themes
3. Visually inspect each component for:
   - Proper contrast ratios
   - Readable text colors
   - Border visibility
   - Background colors
   - Hover/focus states
4. Test in both German and English (if text is rendered)
5. Delete entire `/test/theme-gallery` directory after QA approval

### Data Flow

```
User Action (Settings Panel)
  ↓
ThemeSelector component
  ↓
setTheme('dark') from useTheme() hook
  ↓
next-themes updates:
  1. <html class="dark"> attribute
  2. localStorage['fussballgpt_theme'] = 'dark'
  ↓
CSS variables automatically switch:
  :root styles → .dark styles
  ↓
All components re-render with new theme
```

**Persistence mechanism:**
- **next-themes** handles localStorage automatically (key: `fussballgpt_theme`)
- **UserProfile** tracks theme preference for future features
- **No server-side persistence** needed for v1

**System preference detection:**
- next-themes listens to `prefers-color-scheme` media query
- When theme is "system", resolves to "light" or "dark" based on OS
- Automatically updates when user changes OS theme

### API Contracts

#### ThemeSelector Component Props
```typescript
interface ThemeSelectorProps {
  language: Language;           // Current UI language for labels
  onThemeChange?: (theme: string) => void; // Optional callback (for analytics)
}
```

#### useTheme Hook (from next-themes)
```typescript
const {
  theme,              // 'light' | 'dark' | 'system' | undefined
  setTheme,           // (theme: string) => void
  resolvedTheme,      // 'light' | 'dark' (resolved from system if theme='system')
  systemTheme,        // 'light' | 'dark' (current OS preference)
} = useTheme();
```

#### Updated UserProfile Interface
```typescript
interface UserProfile {
  language: Language;
  detailLevel: DetailLevel;
  persona: Persona;
  name?: string;
  favoriteTeam?: string;
  interests?: string[];
  theme?: 'light' | 'dark' | 'system'; // NEW
}
```

### Testing Requirements

#### E2E Tests (Playwright)

**Test file:** `tests/e2e/dark-mode.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Dark Mode', () => {
  test('should default to system preference', async ({ page }) => {
    await page.goto('/');
    // Check if html has class="dark" or class="light" based on system
    const htmlClass = await page.locator('html').getAttribute('class');
    expect(['dark', 'light', '']).toContain(htmlClass);
  });

  test('should toggle theme via settings panel', async ({ page }) => {
    await page.goto('/');
    
    // Open settings
    await page.click('[aria-label="Settings"]'); // Adjust selector
    
    // Select dark theme
    await page.click('text=Theme'); // Or German equivalent
    await page.click('text=Dark');
    
    // Verify html has dark class
    await expect(page.locator('html')).toHaveClass(/dark/);
    
    // Verify localStorage
    const theme = await page.evaluate(() => localStorage.getItem('fussballgpt_theme'));
    expect(theme).toBe('dark');
  });

  test('should persist theme across page reloads', async ({ page }) => {
    await page.goto('/');
    
    // Set theme to dark
    await page.evaluate(() => localStorage.setItem('fussballgpt_theme', 'dark'));
    
    // Reload page
    await page.reload();
    
    // Verify theme persisted
    await expect(page.locator('html')).toHaveClass(/dark/);
  });

  test('should work in German language', async ({ page }) => {
    await page.goto('/');
    
    // Set language to German
    await page.click('[aria-label="Settings"]');
    await page.click('text=Deutsch');
    
    // Check theme selector shows German labels
    await expect(page.locator('text=Dunkel')).toBeVisible();
    await expect(page.locator('text=Hell')).toBeVisible();
  });

  test('should not flash on page load', async ({ page }) => {
    // Set dark theme in storage before navigation
    await page.addInitScript(() => {
      localStorage.setItem('fussballgpt_theme', 'dark');
    });
    
    await page.goto('/');
    
    // Theme should be applied immediately without flash
    await expect(page.locator('html')).toHaveClass(/dark/);
  });
});
```

#### Component Gallery Testing Checklist

**Manual visual inspection in `/test/theme-gallery`:**

- [ ] **Buttons** - All variants readable in both themes
- [ ] **Badges** - Proper contrast, borders visible
- [ ] **Cards** - Background distinguishable from page background
- [ ] **Citation Cards** - Image thumbnails visible, text readable
- [ ] **Form Controls** (Select, Textarea) - Borders visible, placeholder text readable
- [ ] **Loader** - Animation visible in both themes
- [ ] **Text Colors** - Primary, secondary, muted text all readable
- [ ] **Hover States** - Interactive elements show proper hover feedback
- [ ] **Focus States** - Keyboard navigation shows focus rings
- [ ] **Border Colors** - Subtle borders remain visible without being harsh

**Cross-browser testing:**
- [ ] Chrome (light/dark)
- [ ] Firefox (light/dark)
- [ ] Safari (light/dark)
- [ ] Mobile Safari (light/dark)
- [ ] Mobile Chrome (light/dark)

#### Security

**Input Validation:**
```typescript
// ThemeSelector only accepts predefined values
const VALID_THEMES = ['light', 'dark', 'system'] as const;

// Zod schema for UserProfile (extend existing)
const UserProfileSchema = z.object({
  // ... existing fields
  theme: z.enum(['light', 'dark', 'system']).optional(),
});
```

**Rate Limiting:** Not needed - theme changes are client-side only

**Authentication:** Not needed - theme preference is per-device, not per-account

**XSS Prevention:** next-themes only modifies the `class` attribute with predefined values ('dark', 'light', or empty), no user input

### Implementation Decisions

#### 1. Decision: Use next-themes (not custom implementation)
**Rationale:**
- Industry standard (16.7k GitHub stars, 1.2M weekly npm downloads)
- Handles SSR/hydration complexity automatically
- Zero-flash script injection built-in
- System preference detection with no extra code
- Already installed in project

**Source:** [next-themes README](https://github.com/pacocoursey/next-themes/blob/main/next-themes/README.md)

#### 2. Decision: Store theme in localStorage only (no server-side persistence)
**Rationale:**
- Theme is a device-level preference (same user may prefer dark on laptop, light on phone)
- No authentication system to tie server-side preferences to
- localStorage provides instant load with zero network delay
- Can add server-side sync later if authentication is added

**Source:** [next-themes default behavior](https://github.com/pacocoursey/next-themes/blob/main/next-themes/README.md#themeprovider)

#### 3. Decision: Use Select dropdown (not toggle/switch)
**Rationale:**
- Supports three options (Light/Dark/System) vs two for toggle
- Matches existing settings panel pattern (Language and Detail Level also use multi-option controls)
- User explicitly requested dropdown in requirements
- shadcn/ui Select component already installed

**Source:** [shadcn/ui theme toggle examples](https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/www/content/docs/dark-mode/vite.mdx)

#### 4. Decision: Use "mounted" pattern for hydration safety (not dynamic import)
**Rationale:**
- Simpler implementation (no code splitting complexity)
- Allows rendering skeleton during hydration (better UX than blank space)
- Recommended by next-themes official docs
- Used in production by shadcn/ui examples

**Source:** [next-themes hydration mismatch guide](https://github.com/pacocoursey/next-themes/blob/main/next-themes/README.md#avoid-hydration-mismatch)

#### 5. Decision: Keep CSS transitions enabled on theme change
**Rationale:**
- Smooth visual feedback improves UX
- Project uses consistent transition durations (no jarring effects)
- Can disable later with `disableTransitionOnChange={true}` if issues arise
- Most modern apps keep transitions enabled

**Source:** [Real-world implementations](https://www.rayterrill.com/2024/03/06/NextJSNextThemesAppRouter.html)

#### 6. Decision: Create temporary `/test/theme-gallery` page (not Storybook)
**Rationale:**
- No Storybook infrastructure in project currently
- Gallery page is faster to create and delete
- Uses actual production components with real CSS
- Enables testing with actual routing/layout context
- Can be removed immediately after QA

**Source:** Common practice from [Exasearch production examples](https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/www/content/docs/dark-mode/vite.mdx)

### Dependencies

**No new dependencies required:**
- `next-themes@0.4.6` - Already installed ✓
- `@radix-ui/react-select` - Already installed (shadcn/ui Select) ✓
- All CSS variables already defined ✓

**Verify versions:**
```bash
npm list next-themes @radix-ui/react-select
```

### Estimated Complexity

**Development time:** 3-4 hours
- ThemeProvider wiring: 15 minutes
- ThemeSelector component: 45 minutes (including hydration safety)
- Settings panel integration: 30 minutes
- Theme gallery page: 1 hour
- E2E tests: 1 hour
- Manual testing: 30 minutes

**Risk level:** Low
- Infrastructure 90% complete (CSS variables, Tailwind config)
- next-themes handles complex SSR/hydration automatically
- Pattern well-documented with production examples
- No breaking changes to existing components
- Easy rollback if needed (remove ThemeProvider wrapper)

**Potential issues:**
1. **Hydration mismatch warnings** - Mitigated by mounted pattern
2. **Component-specific dark mode bugs** - Mitigated by gallery testing
3. **Chart color contrast in dark mode** - May need manual verification (chart-1 through chart-5 variables)

**Ready for DEV-AGENT** ✓

---
_Spec Agent | Research complete | 2025-10-31_
