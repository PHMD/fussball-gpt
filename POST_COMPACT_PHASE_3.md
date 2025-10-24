# Post-Compact Prompt: Phase 3 - Frontend Development

**Location:** `/Users/patrickmeehan/knowledge-base/projects/ksi_prototype/`
**GitHub:** https://github.com/PHMD/fussball-gpt
**Branch:** `master` (beta-ready backend) → Create `frontend-phase-3`

---

## Current State Summary

### ✅ What's Complete (Backend - 9.1/10 Quality)

**Core Features:**
- ✅ **Player Statistics:** Current season (2024/25) from API-Football Pro tier
- ✅ **User Onboarding:** Bilingual (DE/EN) + 3 detail levels (Quick/Balanced/Detailed)
- ✅ **Team Form Guide:** Last 5 matches (W-D-L format) from TheSportsDB
- ✅ **Head-to-Head Records:** Last 10 matches between teams (seasonal)
- ✅ **Injury Data:** 18+ Bundesliga teams with detailed diagnoses
- ✅ **Betting Odds:** Real-time odds from The Odds API (18 fixtures)

**Technical Implementation:**
- ✅ **Caching System:** 6h/24h TTL saves 95% of API costs
- ✅ **User Preferences:** JSON storage (`.fussballgpt_config.json`)
- ✅ **Pydantic Models:** Type-safe data validation
- ✅ **Error Handling:** Graceful degradation on API failures

**Persona Quality Scores:**
- Casual Fan: 9/10
- Expert Analyst: 9-9.5/10
- Betting Enthusiast: 9.5-10/10 🎯
- Fantasy Player: 9/10

**API Integration:**
- TheSportsDB (FREE) - Standings, form, H2H
- API-Football (Pro $19/mo) - Stats, injuries
- The Odds API (FREE 500 req/mo) - Betting odds
- Kicker RSS (FREE) - News

---

## 🚀 Phase 3: Frontend Development (Starting Now)

### Goal

Build a production-ready web interface for Fußball GPT that:
1. Provides chat-style natural language queries
2. Displays rich match data (odds, form, injuries, H2H)
3. Supports user preferences (language, detail level)
4. Works seamlessly on mobile and desktop
5. Integrates with existing Python backend

---

## Tech Stack (User Preferences)

**Framework:** Next.js 14+ (React, TypeScript)
- Why: Best DX, handles routing/SSR/API routes in one codebase
- Server Components + Client Components for optimal performance
- Built-in API routes to bridge to Python backend

**Styling:** Tailwind CSS
- Why: No context switching to CSS files, utility-first
- shadcn/ui components are built on Tailwind

**Components:** shadcn/ui
- Why: Copy/paste components (not npm package)
- Full customization, no black box
- Beautiful defaults, accessibility built-in

**Deployment:** Vercel
- Why: Zero-config deployment, git push to deploy
- Automatic preview deployments for branches
- Edge functions for optimal performance

---

## Immediate Next Steps

### Step 1: Component Planning with shadcn Agent

**You have access to a shadcn research agent!**

Use it to identify the best shadcn components for:

1. **Chat Interface:**
   - User input for natural language queries
   - Streaming LLM responses
   - Message history
   - Typing indicators

2. **Match Cards:**
   - Display team matchups
   - Show betting odds (Home/Draw/Away)
   - Team form indicators (W-D-L)
   - Injury/suspension lists
   - H2H records

3. **User Preferences:**
   - Language toggle (German/English)
   - Detail level selector (Quick/Balanced/Detailed)
   - Persistent preferences

4. **Layout:**
   - Responsive navigation
   - Mobile-first design
   - Desktop sidebar for match list

**How to use the shadcn agent:**
```
Ask: "What shadcn components are available for building a chat interface with streaming responses?"

Ask: "What's the best way to build a card component showing sports betting odds using shadcn?"

Ask: "How do I implement a language toggle with shadcn components?"
```

The agent will:
- Show you available components
- Provide implementation details
- Suggest best practices for your use case

---

### Step 2: Review AI-Specific Components

**Critical for this project:** We need components that handle AI streaming responses.

**Research before implementing:**

1. **Vercel AI SDK:**
   - `useChat` hook for streaming responses
   - Built-in handling for LLM streams
   - Works with Anthropic Claude API

2. **shadcn AI Components:**
   - Check if there are chat-specific shadcn components
   - Review streaming message display patterns
   - Look for loading states and error handling

3. **Comparison:**
   - shadcn chat components vs custom implementation
   - Vercel AI SDK integration patterns
   - Best practices for German/English streaming

**Questions to answer:**
- Does shadcn have pre-built chat components?
- How to integrate Vercel AI SDK with shadcn UI?
- What's the best pattern for streaming in both languages?

---

### Step 3: Architecture Planning

**Key Decisions to Make:**

#### 3.1: Next.js App Structure

**Option A: App Router (Recommended)**
```
app/
├── page.tsx                 # Main chat interface
├── api/
│   ├── chat/route.ts       # Streaming endpoint to Python backend
│   └── preferences/route.ts # User preference management
├── components/
│   ├── chat/
│   │   ├── ChatInput.tsx
│   │   ├── ChatMessage.tsx
│   │   └── ChatHistory.tsx
│   ├── match/
│   │   ├── MatchCard.tsx
│   │   ├── OddsDisplay.tsx
│   │   ├── FormGuide.tsx
│   │   ├── InjuryList.tsx
│   │   └── H2HRecord.tsx
│   └── ui/
│       └── [shadcn components]
└── lib/
    ├── api.ts              # Python backend client
    └── utils.ts
```

**Option B: Pages Router (Legacy)**
- Not recommended for new Next.js projects
- Less optimal for streaming responses

**Decide:** App Router (modern) vs Pages Router (legacy)

#### 3.2: Backend Integration Strategy

**Challenge:** Python backend (Claude Agent SDK) + Next.js frontend

**Option A: Python Backend as Separate Service**
```
User → Next.js Frontend → API Routes → Python Backend (FastAPI)
```
- Pros: Clean separation, Python stays independent
- Cons: Need to run two servers, more complex deployment

**Option B: Next.js API Routes Call Python Scripts**
```
User → Next.js API Routes → Python subprocess → Response
```
- Pros: Single deployment, Next.js handles everything
- Cons: Subprocess overhead, harder to scale

**Option C: Next.js API Routes Replicate Python Logic**
```
User → Next.js API Routes (TypeScript) → External APIs
```
- Pros: Single language, optimal performance
- Cons: Duplicate logic, lose existing Python code

**Recommendation to discuss:**
- **Option A for beta:** Python backend as FastAPI service
- **Future:** Migrate to Option C (TypeScript only) after validation

**Decide:** Which integration strategy for Phase 3?

#### 3.3: State Management

**Options:**

**A. React Context (Simple)**
- For user preferences (language, detail level)
- Lightweight, no external dependencies
- Good for small state surface

**B. Zustand (Recommended)**
- For global state (preferences, chat history)
- TypeScript-first, minimal boilerplate
- Works well with Next.js

**C. Redux Toolkit**
- Overkill for this project
- Too much boilerplate

**Decide:** Context only vs Zustand for global state?

---

### Step 4: Testing Strategy

**Frontend Testing Layers:**

**1. Component Tests (Jest + React Testing Library)**
```typescript
// MatchCard.test.tsx
test('displays betting odds correctly', () => {
  render(<MatchCard odds={{ home: 1.50, draw: 4.20, away: 7.00 }} />)
  expect(screen.getByText('1.50')).toBeInTheDocument()
})
```

**2. E2E Tests (Playwright)**
```typescript
// chat.spec.ts
test('user can ask question and get streaming response', async ({ page }) => {
  await page.goto('/')
  await page.fill('[data-testid="chat-input"]', 'Who is leading the Bundesliga?')
  await page.click('[data-testid="submit"]')
  await expect(page.locator('[data-testid="response"]')).toContainText('Bayern')
})
```

**3. API Mocking (MSW - Mock Service Worker)**
```typescript
// mocks/handlers.ts
export const handlers = [
  rest.post('/api/chat', (req, res, ctx) => {
    return res(ctx.json({ message: 'Mocked response' }))
  })
]
```

**4. Visual Regression (Optional - Chromatic/Percy)**
- Catch UI regressions automatically
- Compare screenshots before/after changes

**Questions to answer:**
- When to write tests? (TDD vs after implementation)
- Coverage targets? (80%+ for critical paths)
- CI/CD integration? (GitHub Actions)

---

### Step 5: Git Workflow for Frontend

**Branch Strategy:**

```bash
# Create frontend branch
git checkout -b frontend-phase-3

# Feature sub-branches
git checkout -b frontend/chat-interface
git checkout -b frontend/match-cards
git checkout -b frontend/user-preferences

# Merge back to frontend-phase-3
# Then merge frontend-phase-3 → master when complete
```

**Commit Convention:**
```
feat(frontend): add chat interface component
fix(api): handle streaming errors gracefully
docs(frontend): add component documentation
test(e2e): add chat flow test

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**PR Strategy:**
- Small, focused PRs (1 feature at a time)
- Always include tests
- Document components with JSDoc

---

## Phase 3 Implementation Plan (Recommended Order)

### Week 1: Foundation

**Day 1-2: Component Research & Planning**
1. Use shadcn agent to identify all required components
2. Review AI-specific components (Vercel AI SDK, streaming patterns)
3. Make architecture decisions (App Router, backend integration, state management)
4. Create ADR (Architecture Decision Record) document

**Day 3-4: Project Setup**
1. Create Next.js project with TypeScript + Tailwind
2. Install shadcn/ui CLI and core components
3. Set up ESLint, Prettier, Husky (pre-commit hooks)
4. Configure testing infrastructure (Jest, Playwright, MSW)

**Day 5: Basic Layout**
1. Implement responsive layout with shadcn components
2. Navigation header with language toggle
3. Main content area for chat interface
4. Sidebar for match cards (desktop)

### Week 2: Core Features

**Day 6-8: Chat Interface**
1. Implement ChatInput component (shadcn Input + Button)
2. Implement ChatMessage component (streaming support)
3. Implement ChatHistory component (message list)
4. Integrate Vercel AI SDK for streaming responses

**Day 9-10: Backend Integration**
1. Create Next.js API route: `/api/chat`
2. Connect to Python backend (FastAPI wrapper)
3. Handle streaming from Python to Next.js to client
4. Error handling and loading states

### Week 3: Match Data UI

**Day 11-13: Match Cards**
1. MatchCard component (shadcn Card)
2. OddsDisplay (betting odds visualization)
3. FormGuide (W-D-L indicators)
4. InjuryList (player status)
5. H2HRecord (historical matchup)

**Day 14-15: User Preferences**
1. Language toggle component
2. Detail level selector
3. Persistent preferences (localStorage + backend sync)
4. Preference UI in settings panel

### Week 4: Polish & Testing

**Day 16-18: Testing**
1. Write component tests (80%+ coverage)
2. Write E2E tests (critical user flows)
3. Set up CI/CD (GitHub Actions)
4. Visual regression testing setup

**Day 19-20: Deployment**
1. Deploy to Vercel (preview)
2. Configure environment variables
3. Test with real Python backend
4. Performance optimization (Lighthouse 90+)

---

## Key Questions to Answer in Planning Session

### 1. Component Selection (Use shadcn agent!)

**Questions for shadcn agent:**
- "What components are available for chat interfaces?"
- "Best practice for displaying sports betting odds?"
- "How to implement a language toggle with shadcn?"
- "What's the best card component for match data?"

**Deliverable:** Component list with shadcn recommendations

### 2. AI Streaming Implementation

**Research:**
- Vercel AI SDK docs: https://sdk.vercel.ai/docs
- shadcn chat components (if available)
- Anthropic streaming API integration

**Deliverable:** Streaming architecture diagram

### 3. Backend Integration

**Options to evaluate:**
- FastAPI wrapper for existing Python backend
- Direct subprocess calls from Next.js
- Full TypeScript rewrite (future consideration)

**Deliverable:** Integration strategy decision + ADR

### 4. Testing Approach

**Decisions:**
- TDD vs test-after-implementation?
- Coverage targets (recommend 80%+)
- E2E test scenarios (minimum 5 critical paths)
- Visual regression testing (yes/no?)

**Deliverable:** Testing strategy document

---

## Success Criteria for Phase 3

**Minimum Viable Frontend (Beta Launch):**
- ✅ Chat interface with streaming responses
- ✅ Match cards showing odds, form, injuries
- ✅ Language toggle (German/English)
- ✅ Detail level selector (Quick/Balanced/Detailed)
- ✅ Responsive design (mobile + desktop)
- ✅ 80%+ test coverage
- ✅ Deployed to Vercel
- ✅ Performance: Lighthouse 90+ score

**Nice-to-Have (Post-Beta):**
- Match search/filter
- Historical chat persistence
- User accounts
- Favorite teams
- Push notifications for matches

---

## Resources

**Documentation:**
- `CLAUDE.md` - Complete project overview
- `ODDS_API_SETUP.md` - Betting odds API setup
- Backend code in `data_aggregator.py`, `models.py`, `user_config.py`

**shadcn Resources:**
- shadcn/ui docs: https://ui.shadcn.com/
- shadcn CLI: `npx shadcn-ui@latest init`
- Component examples: https://ui.shadcn.com/examples

**Next.js Resources:**
- Next.js 14 docs: https://nextjs.org/docs
- App Router guide: https://nextjs.org/docs/app
- Vercel AI SDK: https://sdk.vercel.ai/docs

**Testing Resources:**
- React Testing Library: https://testing-library.com/react
- Playwright: https://playwright.dev/
- MSW: https://mswjs.io/

---

## Start Here (First Commands)

```bash
# 1. Create frontend branch
git checkout -b frontend-phase-3

# 2. Use shadcn agent for component research
# Ask: "What shadcn components are best for a chat interface with streaming AI responses?"

# 3. Review AI-specific components
# Research Vercel AI SDK integration with shadcn/ui

# 4. Make architecture decisions
# Document in architecture-decisions.md

# 5. Create Next.js project (when ready)
npx create-next-app@latest fussball-gpt-web --typescript --tailwind --app
cd fussball-gpt-web
npx shadcn-ui@latest init
```

---

## User Context (Important!)

**User Background:**
- Product designer transitioning to AI-augmented solution architecture
- Strong product thinking and UX expertise
- Growing technical depth, not traditional software engineer
- Learning enterprise architecture patterns

**How to Help:**
1. Explain technical concepts when they come up (the "why" not just "what")
2. Flag decisions needing technical validation
3. Separate explanations (for user) from deliverables (for project)
4. Ask clarifying questions when proposals seem unclear
5. Provide context on industry standards

**Communication Style:**
- For user: Explain technical reasoning, trade-offs, implications
- For deliverables: Solution-focused, clean documentation
- Position as collaborative partner, not instruction-taker

---

## Next Session Goals

**Planning Session:**
1. Use shadcn agent to identify all required components
2. Research AI-specific streaming components
3. Make architecture decisions (document in ADR)
4. Define testing strategy
5. Create detailed implementation plan

**Output:**
- Component selection document
- Architecture decision record
- Testing strategy
- Week-by-week implementation plan

**Then:** Create Next.js project and start building! 🚀

---

**Current Branch:** `master` (backend complete, beta-ready)
**Next Branch:** `frontend-phase-3` (create in next session)
**Goal:** Production-ready web interface for Fußball GPT beta launch
