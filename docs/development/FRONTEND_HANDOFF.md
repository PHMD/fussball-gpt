# Frontend Development Handoff

**Worktree Location:** `/Users/patrickmeehan/knowledge-base/projects/ksi_prototype_frontend`
**Branch:** `frontend`
**Start Date:** 2025-10-28

---

## Project Overview

You're building the Next.js frontend for **Fußball GPT** - a German football (Bundesliga) intelligence assistant powered by AI. The backend is complete and beta-ready (9.1/10 quality). Your job is to create a modern, AI-native web interface.

---

## What Already Exists (Backend)

### ✅ Complete Backend (Python)
- **Data aggregation** from 5 sources (TheSportsDB, API-Football, The Odds API, Kicker RSS, Brave Search)
- **LLM integration** (Anthropic Claude Sonnet 4.5)
- **4 personas** (Casual Fan, Expert Analyst, Betting Enthusiast, Fantasy Player)
- **Smart caching** (6-24 hour TTL for API data)
- **Proactive engagement** (context-aware follow-ups)
- **Off-topic handling** (3-tier scope management)
- **Source attribution** (citations for all facts)

### ✅ API Specification
Complete API contract defined in `API_SPEC.md` with:
- 8 RESTful endpoints
- Full TypeScript types
- Streaming support for AI chat
- Error handling patterns
- Caching strategies

---

## Your Mission

Build a Next.js 14+ (App Router) frontend with:

1. **AI Chat Interface** - Streaming responses, markdown support, source citations
2. **Stats Dashboard** - Standings, top scorers, fixtures with odds
3. **News Feed** - Kicker articles with team/topic filtering
4. **Personalized Feeds** - Persona-based content curation
5. **Responsive Design** - Mobile-first, desktop-optimized

---

## Tech Stack (Decided)

- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui (AI-optimized components)
- **Deployment:** Vercel
- **Backend Integration:** Next.js API routes → Python scripts

---

## Phase 1: Setup & Research (START HERE)

### Step 1: Initialize Next.js
```bash
cd /Users/patrickmeehan/knowledge-base/projects/ksi_prototype_frontend

# Initialize Next.js with TypeScript + Tailwind
npx create-next-app@latest . --typescript --tailwind --app

# Install shadcn/ui
npx shadcn@latest init
```

**Configuration choices:**
- ✅ TypeScript: Yes
- ✅ ESLint: Yes
- ✅ Tailwind CSS: Yes
- ✅ `src/` directory: Yes (keeps it clean)
- ✅ App Router: Yes (required)
- ✅ Import alias: `@/*` (standard)

### Step 2: Research shadcn/ui AI Components

**⚠️ Important Discovery (Context7 Validation - Oct 2025):**
shadcn/ui does NOT provide dedicated chat/message components. You'll need to build custom chat UI using shadcn primitives.

**Available shadcn/ui components (validated via Context7):**
- ✅ Card - Use for message containers
- ✅ Input - Use for chat input field
- ✅ Button - Use for send button
- ✅ Avatar - Use for user/AI avatars
- ✅ Badge - Use for role labels, team names
- ✅ Table - Use for standings, player stats
- ✅ Tabs - Use for switching between Q&A and Feed modes
- ✅ Skeleton - Use for loading states
- ✅ Separator - Use for message dividers

**NOT available in shadcn/ui:**
- ❌ Chat interface components
- ❌ Message bubble components
- ❌ Streaming text display components
- ❌ Conversation history components

**Custom components you'll need to build:**
1. **MessageList** - Display conversation history
2. **MessageBubble** - Individual message with role styling (user vs AI)
3. **StreamingText** - Display streaming LLM responses character-by-character
4. **TypingIndicator** - Show when AI is responding
5. **SourceCitation** - Inline source links with citations

**Reference patterns:**
- Vercel AI SDK `useChat()` hook (provides message state management)
- Tailwind Chat UI examples
- Radix UI composition patterns (shadcn/ui foundation)

**Document findings:**
Create `COMPONENT_PLAN.md` with:
- Custom chat component designs (using shadcn primitives)
- Component hierarchy diagram
- Data flow patterns
- State management strategy

### Step 3: Review API Specification
Read `API_SPEC.md` in the parent directory (backend):
```bash
cat /Users/patrickmeehan/knowledge-base/projects/ksi_prototype/API_SPEC.md
```

**Key endpoints to understand:**
1. `POST /api/query` - **STREAMING** AI chat (most complex)
2. `GET /api/standings` - Bundesliga table
3. `GET /api/players/top-scorers` - Top 20 scorers
4. `GET /api/fixtures` - Upcoming matches with odds
5. `GET /api/news` - Kicker articles
6. `POST /api/feed` - Personalized content feeds

---

## Phase 2: Build Static UI (Mock Data)

### Strategy: Start with Mock Data
**Why:** You can build the entire UI without waiting for backend connection. The API contract is stable.

**Approach:**
1. Create `lib/mock-data.ts` with realistic sample data
2. Build UI components consuming mock data
3. Implement all interactions and loading states
4. Test responsive design
5. **Later:** Swap mock data for real API calls (minimal changes)

### Mock Data Structure
```typescript
// lib/mock-data.ts
export const mockStandings: TeamStanding[] = [
  {
    position: 1,
    team: "Bayern München",
    played: 34,
    won: 25,
    drawn: 7,
    lost: 2,
    goals_for: 99,
    goals_against: 32,
    goal_difference: 67,
    points: 82,
    form: { last_5: "WWWWW", points_last_5: 15 }
  },
  // ... more teams
];

export const mockScorers: PlayerStats[] = [
  {
    name: "Harry Kane",
    team: "Bayern München",
    goals: 12,
    assists: 3,
    minutes_played: 673,
    appearances: 10,
    goals_per_90: 1.61
  },
  // ... more players
];

// Simulate streaming response
export async function* mockStreamingResponse(query: string) {
  const response = "Harry Kane is the top scorer with 12 goals...";
  for (const char of response) {
    yield char;
    await new Promise(resolve => setTimeout(resolve, 20));
  }
}
```

### Component Structure (Suggested)
```
src/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home page (chat interface)
│   ├── standings/page.tsx      # Bundesliga table
│   ├── players/page.tsx        # Top scorers
│   ├── fixtures/page.tsx       # Upcoming matches
│   ├── news/page.tsx           # News articles
│   └── api/                    # API routes (Phase 3)
│       ├── health/route.ts
│       ├── standings/route.ts
│       ├── query/route.ts      # Streaming endpoint
│       └── ...
├── components/
│   ├── ui/                     # shadcn/ui components
│   ├── chat/
│   │   ├── ChatInterface.tsx   # Main chat UI
│   │   ├── MessageBubble.tsx   # Individual messages
│   │   ├── StreamingText.tsx   # Streaming display
│   │   └── SourceCitation.tsx  # Source attribution
│   ├── stats/
│   │   ├── StandingsTable.tsx
│   │   ├── ScorersTable.tsx
│   │   └── MatchCard.tsx
│   ├── feed/
│   │   ├── FeedView.tsx
│   │   └── FeedItem.tsx
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
├── lib/
│   ├── mock-data.ts            # Mock data for Phase 2
│   ├── api-client.ts           # API call utilities (Phase 3)
│   └── types.ts                # TypeScript types from API_SPEC
└── hooks/
    ├── useChat.ts              # Chat state management
    ├── useStreaming.ts         # Streaming response handler
    └── useStandings.ts         # Data fetching hooks
```

### Key Features to Build

**1. Chat Interface (Priority 1)**
- Input field for user queries
- Message history (user + assistant bubbles)
- Streaming text display (character-by-character)
- Source citations (inline links)
- Context-aware follow-up suggestions
- Loading states (skeleton, typing indicator)

**2. Stats Dashboard (Priority 2)**
- Bundesliga standings table (sortable)
- Top scorers table with stats
- Team form visualization (W-D-L icons)
- Responsive design (mobile collapse)

**3. Match Cards (Priority 2)**
- Fixture list with date/time
- Team logos (if available)
- Betting odds display
- "View Details" modal/drawer

**4. News Feed (Priority 3)**
- Article cards with thumbnails
- Team/topic filtering
- "Read more" links to Kicker
- Date/time display

**5. Personalized Feeds (Priority 3)**
- Topic selection
- Persona toggle (4 personas)
- Relevance scoring visualization
- Engagement fallback indicator

---

## Phase 3: Backend Connection

**⚠️ Critical Decision Point:** How to connect Python backend to Next.js?

### Option A: Next.js API Routes → Python Scripts (RECOMMENDED START)

**How it works:**
```typescript
// app/api/standings/route.ts
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function GET() {
  try {
    // Execute Python script
    const { stdout } = await execAsync(
      'python3 /path/to/backend/get_standings.py'
    );
    const data = JSON.parse(stdout);
    return Response.json(data);
  } catch (error) {
    return Response.json({ error: 'Backend error' }, { status: 500 });
  }
}
```

**Pros:**
- Simple to start with
- Python backend stays unchanged
- Easy local development

**Cons:**
- Cold start latency (spawning Python process)
- Process overhead for each request
- Harder to handle streaming

### Option B: FastAPI Wrapper (BETTER FOR PRODUCTION)

**How it works:**
1. Create `backend/api_server.py`:
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from data_aggregator import DataAggregator
from cli import LLMClient

app = FastAPI()

@app.get("/api/standings")
async def get_standings():
    aggregator = DataAggregator()
    data = aggregator.fetch_bundesliga_standings()
    return {"data": data}

@app.post("/api/query")
async def query(request: QueryRequest):
    llm = LLMClient(provider="anthropic")
    # Return streaming response
    async def generate():
        for chunk in llm.stream_query(request.query):
            yield f"data: {chunk}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

2. Run FastAPI server: `uvicorn api_server:app --port 8000`
3. Next.js API routes proxy to FastAPI:
```typescript
// app/api/standings/route.ts
export async function GET() {
  const res = await fetch('http://localhost:8000/api/standings');
  const data = await res.json();
  return Response.json(data);
}
```

**Pros:**
- Better performance (persistent Python process)
- Native streaming support
- Easier to scale
- Can deploy independently

**Cons:**
- More setup complexity
- Need to run 2 servers in dev
- Need 2 deployments in prod

### Option C: Vercel AI SDK ⭐ (NEW - Discovered via Context7 Oct 2025)

**Discovery:** Vercel AI SDK has native Anthropic Claude support. This is the simplest approach IF you're willing to rewrite the Python data pipeline in TypeScript.

**Installation:**
```bash
npm install ai @ai-sdk/anthropic
```

**How it works:**
```typescript
// app/api/query/route.ts
import { anthropic } from '@ai-sdk/anthropic';
import { streamText } from 'ai';

export const maxDuration = 60; // Allow longer responses

export async function POST(req: Request) {
  const { messages } = await req.json();

  // Fetch Bundesliga data (needs TypeScript rewrite of data_aggregator.py)
  const sportsData = await fetchSportsData();

  // Build system prompt with data context
  const systemMessage = {
    role: 'system',
    content: `You are Fußball GPT, a German football intelligence assistant.

Current Bundesliga Data:
- Standings: ${JSON.stringify(sportsData.standings)}
- Top Scorers: ${JSON.stringify(sportsData.topScorers)}
- Fixtures: ${JSON.stringify(sportsData.fixtures)}
- Injuries: ${JSON.stringify(sportsData.injuries)}
- News: ${JSON.stringify(sportsData.news)}

Provide accurate, context-aware responses using this data. Include source citations.`
  };

  const result = streamText({
    model: anthropic('claude-3-5-sonnet-20241022'),
    messages: [systemMessage, ...messages],
  });

  return result.toDataStreamResponse();
}

// TypeScript data fetching (replaces Python backend)
async function fetchSportsData() {
  // Call sports APIs directly from Next.js
  const [standings, scorers, fixtures, injuries, news] = await Promise.all([
    fetchStandings(), // Call TheSportsDB API
    fetchScorers(),   // Call API-Football
    fetchFixtures(),  // Call TheSportsDB + The Odds API
    fetchInjuries(),  // Call API-Football
    fetchNews(),      // Call Kicker RSS + Brave Search
  ]);

  return { standings, scorers, fixtures, injuries, news };
}
```

**Frontend consumption (simpler than Option A/B):**
```typescript
// app/page.tsx (Chat interface)
'use client';
import { useChat } from 'ai/react';

export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: '/api/query',
  });

  return (
    <div>
      <div>
        {messages.map(m => (
          <div key={m.id}>
            <strong>{m.role}:</strong> {m.content}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Ask about Bundesliga..."
        />
      </form>
    </div>
  );
}
```

**Pros:**
- **Official Vercel solution** - First-class platform support
- **Simplest deployment** - No Python runtime, no child_process
- **Type-safe end-to-end** - TypeScript from frontend to LLM
- **Automatic streaming** - SSE formatting handled automatically
- **Built-in error handling** - Retry logic, connection management
- **React hooks included** - `useChat()` hook for instant chat UI
- **Optimized for Vercel** - Best performance on Vercel platform

**Cons:**
- **Major backend rewrite** - Must port `data_aggregator.py` (1,100+ lines) to TypeScript
- **Loss of Python ecosystem** - Can't use Pydantic models, requests library, existing caching
- **Duplicate API calls** - Frontend → Next.js API → Sports APIs (adds network hop)
- **Cache complexity** - Must rebuild 6-24 hour caching in TypeScript/Redis
- **Learning curve** - Team needs Node.js data pipeline expertise
- **Estimated effort** - 2-3 weeks to rewrite and test data aggregation

**When to choose Option C:**
- You're starting fresh (no existing Python backend)
- Team has strong TypeScript/Node.js expertise
- Willing to invest 2-3 weeks in backend rewrite
- Want the absolute simplest deployment (single Next.js app)
- Prefer official Vercel solutions over custom integration

**When NOT to choose Option C:**
- Python backend already works (6+ months of development)
- Complex caching strategy is critical (6-24 hour TTLs with file-based cache)
- Team lacks TypeScript data pipeline experience
- Need to preserve Pydantic models and Python API clients
- Want to launch quickly (Option A/B faster to integrate)

**Tradeoff summary:**
- **Option A (child_process):** Fast integration, keeps Python, more complex streaming
- **Option B (FastAPI):** Production-ready, Python stays, two deployments
- **Option C (AI SDK):** Simplest deployment, requires full backend rewrite

### Recommendation: Hybrid Approach

**Given your existing Python backend (6+ months of work), start with Option A or B:**

**Phase 3A: Start with Option A (child_process)**
- Get basic endpoints working quickly
- Test data flow end-to-end
- Validate Python backend integration
- Identify performance bottlenecks

**Phase 3B: Migrate to Option B (FastAPI) if needed**
- If latency is >500ms
- If streaming is problematic
- Before production launch

---

## Streaming Implementation (Critical)

The AI chat endpoint (`POST /api/query`) requires streaming. Here's the complete pattern:

### Backend: Python Streaming Generator
```python
# Create streaming_chat.py
from cli import LLMClient
from data_aggregator import DataAggregator
import json
import sys

def stream_query(query: str):
    """Stream LLM response character by character."""
    llm = LLMClient(provider="anthropic")
    aggregator = DataAggregator()
    data = aggregator.aggregate_all()

    # Stream response (Claude Sonnet 4.5 supports streaming)
    response = llm.query_stream(query, data)  # Need to implement this

    for chunk in response:
        # Output to stdout for Next.js to capture
        print(chunk, end='', flush=True)

if __name__ == "__main__":
    query = sys.argv[1]
    stream_query(query)
```

### Frontend: Next.js API Route
```typescript
// app/api/query/route.ts
import { spawn } from 'child_process';

export async function POST(request: Request) {
  const { query } = await request.json();

  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    start(controller) {
      // Spawn Python process
      const python = spawn('python3', [
        '/path/to/streaming_chat.py',
        query
      ]);

      // Stream stdout
      python.stdout.on('data', (data) => {
        controller.enqueue(encoder.encode(`data: ${data}\n\n`));
      });

      python.on('close', () => {
        controller.close();
      });

      python.on('error', (err) => {
        controller.error(err);
      });
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-store',
      'Connection': 'keep-alive',
    },
  });
}
```

### Frontend: React Component
```typescript
// components/chat/ChatInterface.tsx
'use client';
import { useState } from 'react';

export function ChatInterface() {
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  async function sendQuery(query: string) {
    setLoading(true);
    setResponse('');

    const res = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    const reader = res.body?.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader!.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          setResponse((prev) => prev + data);
        }
      }
    }

    setLoading(false);
  }

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto p-4">
        {response && <div className="prose">{response}</div>}
        {loading && <div>Thinking...</div>}
      </div>
      <div className="p-4 border-t">
        <input
          type="text"
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              sendQuery(e.currentTarget.value);
              e.currentTarget.value = '';
            }
          }}
          placeholder="Ask about Bundesliga..."
          className="w-full p-2 border rounded"
        />
      </div>
    </div>
  );
}
```

---

## Testing Strategy

### Unit Tests (Jest + React Testing Library)
```typescript
// __tests__/components/ChatInterface.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInterface } from '@/components/chat/ChatInterface';

describe('ChatInterface', () => {
  it('should display streamed response', async () => {
    render(<ChatInterface />);
    const input = screen.getByPlaceholderText('Ask about Bundesliga...');
    fireEvent.change(input, { target: { value: 'Who is top scorer?' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    // Wait for streaming response
    const response = await screen.findByText(/Harry Kane/);
    expect(response).toBeInTheDocument();
  });
});
```

### E2E Tests (Playwright)
```typescript
// e2e/chat.spec.ts
import { test, expect } from '@playwright/test';

test('should stream AI response', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.fill('input[placeholder="Ask about Bundesliga..."]', 'Who is top scorer?');
  await page.press('input[placeholder="Ask about Bundesliga..."]', 'Enter');

  // Wait for streaming to complete
  await expect(page.locator('text=Harry Kane')).toBeVisible();
  await expect(page.locator('text=via API-Football')).toBeVisible();
});
```

---

## Deployment (Vercel)

### Configuration
```json
// vercel.json
{
  "buildCommand": "npm run build",
  "installCommand": "npm install && pip install -r requirements.txt",
  "functions": {
    "app/api/**/*.ts": {
      "memory": 1024,
      "maxDuration": 30
    }
  }
}
```

### Environment Variables
```bash
# .env.local (development)
ANTHROPIC_API_KEY=your_key_here
RAPIDAPI_KEY=your_key_here
ODDS_API_KEY=your_key_here
BRAVE_SEARCH_API_KEY=your_key_here
PYTHON_BACKEND_PATH=/absolute/path/to/backend

# Production (Vercel dashboard)
# Same variables, but point to production paths
```

---

## Performance Optimization

### 1. Route Segment Config
```typescript
// app/standings/page.tsx
export const revalidate = 21600; // Revalidate every 6 hours
export const dynamic = 'force-static'; // Static generation

export default async function StandingsPage() {
  const standings = await fetch('/api/standings', { next: { revalidate: 21600 } });
  return <StandingsTable data={standings} />;
}
```

### 2. React Server Components
Use Server Components by default, Client Components only when needed:
```typescript
// Server Component (default)
async function StandingsTable() {
  const data = await fetchStandings();
  return <table>...</table>;
}

// Client Component (interactive)
'use client';
function ChatInterface() {
  const [messages, setMessages] = useState([]);
  return <div>...</div>;
}
```

### 3. Streaming with Suspense
```typescript
// app/page.tsx
import { Suspense } from 'react';

export default function HomePage() {
  return (
    <Suspense fallback={<LoadingSkeleton />}>
      <StandingsTable />
    </Suspense>
  );
}
```

---

## Known Challenges & Solutions

### Challenge 1: Python Cold Starts on Vercel
**Problem:** Spawning Python process adds 200-500ms latency
**Solutions:**
- Use FastAPI wrapper (persistent process)
- Pre-warm functions with cron job
- Cache aggressively
- Consider edge runtime for static endpoints

### Challenge 2: Streaming with Claude API
**Problem:** Anthropic's Python SDK returns full response by default
**Solution:** Use streaming mode (already in backend):
```python
response = client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    messages=[{"role": "user", "content": query}],
)

for chunk in response:
    if chunk.type == "content_block_delta":
        print(chunk.delta.text, end='', flush=True)
```

### Challenge 3: CORS in Development
**Problem:** Next.js dev server (3000) calling Python backend (8000)
**Solution:** Configure Next.js proxy:
```typescript
// next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/python-api/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ];
  },
};
```

### Challenge 4: TypeScript Types from Python
**Problem:** Keeping TS types in sync with Python Pydantic models
**Solution:** Use `pydantic-to-typescript` CLI:
```bash
pip install pydantic-to-typescript
pydantic2ts --module backend.models --output src/lib/types.ts
```

---

## Communication with Backend Team

### While Building in Parallel

**File to watch:** `API_SPEC.md`
- Any changes to API contract will be documented here
- Check for updates before integrating real API

**Expected stability:**
- ✅ Endpoint paths: Stable
- ✅ Request/response types: Stable
- ⚠️ Streaming format: May evolve during integration
- ⚠️ Error codes: May expand

### When Ready to Integrate

**Create:** `INTEGRATION_NOTES.md` documenting:
1. Blockers you encountered
2. API changes needed
3. Performance observations
4. Questions for backend team

---

## Success Criteria

### Phase 2 Complete (Static UI)
- [ ] All pages render with mock data
- [ ] Chat interface displays streaming text
- [ ] Tables are sortable and responsive
- [ ] Mobile design looks good
- [ ] All loading states work
- [ ] Component library documented

### Phase 3 Complete (Backend Integration)
- [ ] All API endpoints connected
- [ ] Real data displays correctly
- [ ] Streaming chat works end-to-end
- [ ] Error handling graceful
- [ ] Caching respects TTL
- [ ] Performance <2s initial load

### Production Ready
- [ ] E2E tests passing
- [ ] Deployed on Vercel
- [ ] Environment variables configured
- [ ] Error monitoring setup (Sentry?)
- [ ] Analytics integrated (optional)

---

## Helpful Resources

### Documentation
- Next.js App Router: https://nextjs.org/docs/app
- shadcn/ui: https://ui.shadcn.com
- Tailwind CSS: https://tailwindcss.com/docs
- Vercel Deployment: https://vercel.com/docs

### Example Projects
- Next.js AI Chatbot: https://github.com/vercel/ai-chatbot
- shadcn Chat UI: Research with `/shadcn-research chat`

### Tools
- shadcn CLI: `npx shadcn@latest add <component>`
- TypeScript playground: https://www.typescriptlang.org/play
- Tailwind Playground: https://play.tailwindcss.com

---

## Questions? Blockers?

**Document them in:** `FRONTEND_PROGRESS.md`

**Include:**
- What you tried
- What error you got
- What the API_SPEC says
- Your proposed solution

The backend team (me) will review and respond in master branch.

---

## Quick Start Commands

```bash
# Navigate to frontend worktree
cd /Users/patrickmeehan/knowledge-base/projects/ksi_prototype_frontend

# Initialize Next.js
npx create-next-app@latest . --typescript --tailwind --app

# Install shadcn/ui
npx shadcn@latest init

# Start development server
npm run dev

# Research shadcn components
# (Use /shadcn-research in Claude Code)

# Create mock data
mkdir -p src/lib
touch src/lib/mock-data.ts

# Build a component
mkdir -p src/components/chat
touch src/components/chat/ChatInterface.tsx

# Run tests (when ready)
npm test

# Build for production
npm run build
```

---

**Current Status:** Ready for Phase 1 (Setup & Research)
**Next Step:** Initialize Next.js and research shadcn/ui AI components
**Estimated Time:** Phase 2 (Static UI) = 2-3 days, Phase 3 (Integration) = 1-2 days

Good luck! 🚀
