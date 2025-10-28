# Fußball GPT API Specification

**Version:** 1.0
**Last Updated:** 2025-10-28
**Status:** Draft for Frontend Development

---

## Overview

This document defines the API contract between the Next.js frontend and Python backend for Fußball GPT. The API follows RESTful principles with streaming support for AI-powered chat.

**Architecture Pattern:**
```
Next.js Frontend (App Router)
    ↓ (API Routes in app/api/)
Python Backend (data_aggregator.py, cli.py)
    ↓
LLM (Anthropic Claude Sonnet 4.5)
    ↓
Streaming Response → Frontend
```

---

## Implementation Strategy

### Option A: Next.js API Routes → Python Scripts (RECOMMENDED)
```typescript
// app/api/query/route.ts
export async function POST(request: Request) {
  // Call Python script via child_process or HTTP
  // Stream response back to frontend
}
```

**Pros:**
- Keeps Python backend intact
- Easy to deploy on Vercel
- TypeScript type safety

**Cons:**
- Requires Python runtime on Vercel (supported)
- Extra layer of abstraction

### Option B: FastAPI Wrapper
Create `api_server.py` that wraps existing Python code and exposes REST endpoints.

**Pros:**
- Native Python HTTP server
- Can run independently

**Cons:**
- Extra codebase to maintain
- Need to deploy both Next.js and FastAPI

### Option C: Vercel AI SDK (NEW - Discovered via Context7 Oct 2025)

**Discovery:** Vercel AI SDK has native Anthropic Claude support via `@ai-sdk/anthropic` package.

**Installation:**
```bash
npm install ai @ai-sdk/anthropic
```

**Implementation:**
```typescript
// app/api/query/route.ts
import { anthropic } from '@ai-sdk/anthropic';
import { streamText } from 'ai';

export const maxDuration = 60; // 60 seconds for long responses

export async function POST(req: Request) {
  const { messages } = await req.json();

  // Fetch sports data (would need to rewrite data_aggregator.py logic in TypeScript)
  const sportsData = await fetchSportsData();

  // Add system prompt with sports data context
  const systemMessage = {
    role: 'system',
    content: `You are Fußball GPT, a German football intelligence assistant.

Current Bundesliga Data:
${JSON.stringify(sportsData, null, 2)}

Provide accurate, context-aware responses using this data.`
  };

  const result = streamText({
    model: anthropic('claude-3-5-sonnet-20241022'),
    messages: [systemMessage, ...messages],
  });

  return result.toDataStreamResponse();
}
```

**Pros:**
- **Official Vercel solution** - Maintained by Vercel team
- **Type-safe TypeScript** - Full TypeScript support end-to-end
- **Automatic streaming** - Handles SSE formatting automatically
- **Simpler deployment** - No child_process complexity on serverless
- **Built-in error handling** - Retry and error handling included
- **Optimized for Vercel** - Best performance on Vercel platform

**Cons:**
- **Backend rewrite required** - Must port `data_aggregator.py` to TypeScript
- **Loss of Python ecosystem** - Can't use requests, Pydantic, existing caching
- **Adds network hop** - Frontend → Next.js API → Sports APIs (extra latency)
- **API rate limits** - Must manage sports API calls from Next.js instead of Python cache layer

**When to choose Option C:**
- Building greenfield Next.js application
- Team has strong TypeScript expertise
- Willing to rewrite Python data pipeline
- Want simplest deployment story on Vercel
- Prefer official Vercel solutions

**When NOT to choose Option C:**
- Want to preserve existing Python backend (6+ months of work)
- Complex Python dependencies (Pydantic models, caching, API clients)
- Team lacks TypeScript/Node.js data pipeline experience
- Python caching strategy is critical (6-24 hour TTLs)

**Decision:** Start with Option A (Next.js API Routes calling Python), migrate to Option C if TypeScript data pipeline becomes priority. Option C requires ~2-3 weeks to rewrite data_aggregator.py.

---

## Base URL

**Development:** `http://localhost:3000/api`
**Production:** `https://fussball-gpt.vercel.app/api`

---

## Authentication

**Current:** None (public beta)
**Future:** API key or OAuth for personalized features

---

## Common Response Format

### Success Response
```json
{
  "data": { ... },
  "timestamp": "2025-10-28T12:00:00Z",
  "cached": true,
  "cache_age_seconds": 3600
}
```

### Error Response
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Human-readable error message",
    "details": { ... }
  },
  "timestamp": "2025-10-28T12:00:00Z"
}
```

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /api/health`
**Description:** Check API and backend health status

**Request:**
```typescript
// No parameters
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "data_aggregator": "ok",
    "llm": "ok",
    "cache": "ok"
  },
  "timestamp": "2025-10-28T12:00:00Z"
}
```

**TypeScript Types:**
```typescript
interface HealthResponse {
  status: 'healthy' | 'degraded' | 'down';
  version: string;
  services: {
    data_aggregator: 'ok' | 'error';
    llm: 'ok' | 'error';
    cache: 'ok' | 'error';
  };
  timestamp: string;
}
```

---

### 2. Bundesliga Standings

**Endpoint:** `GET /api/standings`
**Description:** Get current Bundesliga table with team form

**Request:**
```typescript
// Query Parameters:
// - season?: string (default: current season "2024/25")
```

**Response (200 OK):**
```json
{
  "data": {
    "season": "2024/25",
    "standings": [
      {
        "position": 1,
        "team": "Bayern München",
        "played": 34,
        "won": 25,
        "drawn": 7,
        "lost": 2,
        "goals_for": 99,
        "goals_against": 32,
        "goal_difference": 67,
        "points": 82,
        "form": {
          "last_5": "WWWWW",
          "points_last_5": 15
        }
      }
    ]
  },
  "timestamp": "2025-10-28T12:00:00Z",
  "cached": true,
  "cache_age_seconds": 21600
}
```

**TypeScript Types:**
```typescript
interface StandingsResponse {
  data: {
    season: string;
    standings: TeamStanding[];
  };
  timestamp: string;
  cached: boolean;
  cache_age_seconds: number;
}

interface TeamStanding {
  position: number;
  team: string;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
  form: {
    last_5: string; // e.g., "WWDLW"
    points_last_5: number;
  };
}
```

**Caching:** 6 hours (TheSportsDB data)

---

### 3. Top Scorers

**Endpoint:** `GET /api/players/top-scorers`
**Description:** Get top 20 Bundesliga scorers with stats

**Request:**
```typescript
// Query Parameters:
// - season?: string (default: current season "2024/25")
// - limit?: number (default: 20, max: 50)
```

**Response (200 OK):**
```json
{
  "data": {
    "season": "2024/25",
    "players": [
      {
        "name": "Harry Kane",
        "team": "Bayern München",
        "goals": 12,
        "assists": 3,
        "minutes_played": 673,
        "appearances": 10,
        "goals_per_90": 1.61
      }
    ]
  },
  "timestamp": "2025-10-28T12:00:00Z",
  "cached": true,
  "cache_age_seconds": 21600
}
```

**TypeScript Types:**
```typescript
interface TopScorersResponse {
  data: {
    season: string;
    players: PlayerStats[];
  };
  timestamp: string;
  cached: boolean;
  cache_age_seconds: number;
}

interface PlayerStats {
  name: string;
  team: string;
  goals: number;
  assists: number;
  minutes_played: number;
  appearances: number;
  goals_per_90: number;
}
```

**Caching:** 6 hours (API-Football data)

---

### 4. Fixtures

**Endpoint:** `GET /api/fixtures`
**Description:** Get upcoming Bundesliga matches with odds

**Request:**
```typescript
// Query Parameters:
// - days_ahead?: number (default: 7, max: 30)
// - team?: string (filter by team name)
```

**Response (200 OK):**
```json
{
  "data": {
    "fixtures": [
      {
        "id": "match_12345",
        "date": "2025-11-01T17:30:00Z",
        "home_team": "Bayern München",
        "away_team": "Bayer Leverkusen",
        "venue": "Allianz Arena",
        "odds": {
          "home_win": 1.15,
          "draw": 5.70,
          "away_win": 7.90
        }
      }
    ]
  },
  "timestamp": "2025-10-28T12:00:00Z",
  "cached": true,
  "cache_age_seconds": 86400
}
```

**TypeScript Types:**
```typescript
interface FixturesResponse {
  data: {
    fixtures: Fixture[];
  };
  timestamp: string;
  cached: boolean;
  cache_age_seconds: number;
}

interface Fixture {
  id: string;
  date: string; // ISO 8601
  home_team: string;
  away_team: string;
  venue: string;
  odds?: {
    home_win: number;
    draw: number;
    away_win: number;
  };
}
```

**Caching:** 24 hours (TheSportsDB + The Odds API)

---

### 5. Team Injuries

**Endpoint:** `GET /api/injuries/:team`
**Description:** Get injury/suspension data for a specific team

**Request:**
```typescript
// Path Parameters:
// - team: string (team name, e.g., "bayern-munchen")
```

**Response (200 OK):**
```json
{
  "data": {
    "team": "Bayern München",
    "injuries": [
      {
        "player": "Alphonso Davies",
        "injury": "Ruptured cruciate ligament",
        "status": "out",
        "expected_return": null
      },
      {
        "player": "Jamal Musiala",
        "injury": "Fracture of the fibula",
        "status": "out",
        "expected_return": "2025-12-15"
      },
      {
        "player": "Konrad Laimer",
        "injury": null,
        "status": "doubtful",
        "expected_return": "2025-11-05"
      }
    ]
  },
  "timestamp": "2025-10-28T12:00:00Z",
  "cached": true,
  "cache_age_seconds": 21600
}
```

**TypeScript Types:**
```typescript
interface InjuriesResponse {
  data: {
    team: string;
    injuries: Injury[];
  };
  timestamp: string;
  cached: boolean;
  cache_age_seconds: number;
}

interface Injury {
  player: string;
  injury: string | null;
  status: 'out' | 'doubtful' | 'fit';
  expected_return: string | null; // ISO 8601 date
}
```

**Caching:** 6 hours (API-Football data)

---

### 6. News Articles

**Endpoint:** `GET /api/news`
**Description:** Get recent Kicker articles with Bundesliga content filtering

**Request:**
```typescript
// Query Parameters:
// - limit?: number (default: 10, max: 50)
// - team?: string (filter by team)
// - search?: string (augment with Brave Search if <10 RSS results)
```

**Response (200 OK):**
```json
{
  "data": {
    "articles": [
      {
        "id": "article_123",
        "title": "Urbigs besondere Rückkehr nach Köln",
        "summary": "Bayern's goalkeeper Jonas Urbig returns to face Köln...",
        "url": "https://www.kicker.de/...",
        "published_at": "2025-10-28T10:00:00Z",
        "source": "Kicker RSS",
        "teams": ["Bayern München", "FC Köln"],
        "topics": ["goalkeepers", "bundesliga"]
      }
    ],
    "augmented_with_search": false
  },
  "timestamp": "2025-10-28T12:00:00Z",
  "cached": false
}
```

**TypeScript Types:**
```typescript
interface NewsResponse {
  data: {
    articles: Article[];
    augmented_with_search: boolean;
  };
  timestamp: string;
  cached: boolean;
}

interface Article {
  id: string;
  title: string;
  summary: string;
  url: string;
  published_at: string; // ISO 8601
  source: 'Kicker RSS' | 'Brave Search';
  teams: string[];
  topics: string[];
}
```

**Caching:**
- RSS: None (always fresh)
- Brave Search: 5 minutes (session cache)

---

### 7. AI Chat Query (STREAMING)

**Endpoint:** `POST /api/query`
**Description:** Send user query to LLM with Bundesliga data context (streaming response)

**Request:**
```typescript
interface QueryRequest {
  query: string;
  conversation_history?: ConversationTurn[];
  persona?: 'casual_fan' | 'expert_analyst' | 'betting_enthusiast' | 'fantasy_player';
  detail_level?: 'quick' | 'balanced' | 'detailed';
}

interface ConversationTurn {
  query: string;
  response: string;
  timestamp: string;
}
```

**Request Body:**
```json
{
  "query": "Who is the top scorer?",
  "conversation_history": [
    {
      "query": "Show me Bayern's form",
      "response": "Bayern has won their last 5 matches...",
      "timestamp": "2025-10-28T11:55:00Z"
    }
  ],
  "persona": "expert_analyst",
  "detail_level": "balanced"
}
```

**Response (200 OK - Server-Sent Events):**
```
Content-Type: text/event-stream
Cache-Control: no-store

data: Harry Kane is the top scorer with 12 goals this season

data:  (via API-Football)

data: . He's currently leading the Bundesliga scoring charts

data: .\n\n📰 Related from Kicker:\n

data:    • Kane's Record Start → https://kicker.de/article-123\n

data: \n💬 Want to see how Kane compares to other top scorers?

```

**Implementation Pattern (from Context7 docs):**
```typescript
// app/api/query/route.ts
import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  const { query, conversation_history, persona, detail_level } = await request.json();

  // Create async iterator for streaming
  async function* streamResponse() {
    const encoder = new TextEncoder();

    // Call Python backend (via child_process or HTTP)
    // For each chunk of LLM response:
    yield encoder.encode(`data: ${chunk}\n\n`);
  }

  // Convert iterator to ReadableStream
  const stream = new ReadableStream({
    async pull(controller) {
      const { value, done } = await iterator.next();
      if (done) {
        controller.close();
      } else {
        controller.enqueue(value);
      }
    },
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

**Frontend Consumption:**
```typescript
// Client component
'use client';
import { useState } from 'react';

export default function ChatInterface() {
  const [response, setResponse] = useState('');

  async function sendQuery(query: string) {
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
          setResponse(prev => prev + data);
        }
      }
    }
  }

  return (
    <div>
      <div>{response}</div>
      <button onClick={() => sendQuery('Who is top scorer?')}>Ask</button>
    </div>
  );
}
```

**TypeScript Types:**
```typescript
interface QueryRequest {
  query: string;
  conversation_history?: ConversationTurn[];
  persona?: Persona;
  detail_level?: DetailLevel;
}

type Persona = 'casual_fan' | 'expert_analyst' | 'betting_enthusiast' | 'fantasy_player';
type DetailLevel = 'quick' | 'balanced' | 'detailed';

interface ConversationTurn {
  query: string;
  response: string;
  timestamp: string;
}
```

**No Caching:** Real-time LLM responses

---

### 8. Personalized Feed Generation

**Endpoint:** `POST /api/feed`
**Description:** Generate personalized content feed based on user interests

**Request:**
```typescript
interface FeedRequest {
  topic: string; // e.g., "Bayern München", "transfers", "injuries"
  persona?: Persona;
  count?: number; // default: 10, max: 50
}
```

**Request Body:**
```json
{
  "topic": "Bayern München",
  "persona": "betting_enthusiast",
  "count": 10
}
```

**Response (200 OK):**
```json
{
  "data": {
    "topic": "Bayern München",
    "feed_items": [
      {
        "type": "news",
        "headline": "Urbig Returns to Face Köln",
        "summary": "Bayern's goalkeeper...",
        "url": "https://kicker.de/...",
        "timestamp": "2025-10-28T10:00:00Z",
        "relevance": 0.95,
        "persona_boost": 0.0,
        "content_category": "TEAM_NEWS"
      },
      {
        "type": "stat",
        "headline": "Kane's Season Stats",
        "summary": "12 goals, 3 assists in 10 appearances",
        "url": null,
        "timestamp": "2025-10-28T12:00:00Z",
        "relevance": 0.92,
        "persona_boost": 0.15,
        "content_category": "PLAYER_STATS"
      }
    ],
    "engagement_fallback_used": false
  },
  "timestamp": "2025-10-28T12:00:00Z"
}
```

**TypeScript Types:**
```typescript
interface FeedResponse {
  data: {
    topic: string;
    feed_items: FeedItem[];
    engagement_fallback_used: boolean;
  };
  timestamp: string;
}

interface FeedItem {
  type: 'news' | 'event' | 'stat';
  headline: string;
  summary: string;
  url: string | null;
  timestamp: string;
  relevance: number; // 0.0-1.0
  persona_boost: number; // -0.5 to +0.5
  content_category: string;
  is_fallback?: boolean;
}
```

**No Caching:** Generated on-demand

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Malformed request body or parameters |
| `NOT_FOUND` | 404 | Resource not found (e.g., invalid team) |
| `RATE_LIMIT` | 429 | Too many requests |
| `LLM_ERROR` | 503 | LLM service unavailable |
| `BACKEND_ERROR` | 500 | Python backend error |
| `CACHE_ERROR` | 500 | Cache read/write failure |

---

## Caching Strategy

### File-Based Cache (Current)
- **Location:** `cache/*.json`
- **TTL:**
  - Player stats: 6 hours
  - Team form: 6 hours
  - Betting odds: 24 hours
  - Injuries: 6 hours

### Session Cache (In-Memory)
- **Brave Search:** 5 minutes
- **Used for:** Query-specific article augmentation

### Future: Redis
When deploying to production:
```typescript
// Cache keys
`bundesliga:standings:${season}`     // 6h TTL
`bundesliga:scorers:${season}`       // 6h TTL
`bundesliga:fixtures:${date_range}`  // 24h TTL
`bundesliga:injuries:${team}`        // 6h TTL
`bundesliga:news`                    // No cache
```

---

## Rate Limiting

**Development:** None
**Production (Recommended):**
- `/api/query`: 60 requests/minute per IP
- `/api/feed`: 30 requests/minute per IP
- Other endpoints: 120 requests/minute per IP

---

## CORS Configuration

**Development:**
```typescript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: 'http://localhost:3000' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,POST,OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type' },
        ],
      },
    ];
  },
};
```

**Production:**
```typescript
// Restrict to production domain
{ key: 'Access-Control-Allow-Origin', value: 'https://fussball-gpt.vercel.app' }
```

---

## Testing Strategy

### API Route Tests
```typescript
// __tests__/api/query.test.ts
import { POST } from '@/app/api/query/route';

describe('/api/query', () => {
  it('should stream LLM response', async () => {
    const request = new Request('http://localhost:3000/api/query', {
      method: 'POST',
      body: JSON.stringify({ query: 'Who is top scorer?' }),
    });

    const response = await POST(request);
    expect(response.headers.get('Content-Type')).toBe('text/event-stream');
  });
});
```

### Integration Tests
Test full flow: Frontend → API Route → Python Backend → LLM

---

## Deployment Considerations

### Vercel Configuration
```json
// vercel.json
{
  "functions": {
    "app/api/**": {
      "memory": 1024,
      "maxDuration": 30
    }
  },
  "buildCommand": "npm run build && pip install -r requirements.txt"
}
```

### Environment Variables
```bash
# .env.local
ANTHROPIC_API_KEY=your_key_here
RAPIDAPI_KEY=your_key_here
ODDS_API_KEY=your_key_here
BRAVE_SEARCH_API_KEY=your_key_here

# Python backend path (for API routes)
PYTHON_BACKEND_PATH=/var/task/backend
```

---

## Next Steps

1. **Frontend Setup:**
   - Create Next.js project: `npx create-next-app@latest fussball-gpt-frontend --typescript --tailwind --app`
   - Install shadcn/ui: `npx shadcn@latest init`
   - Research AI chat components: Use shadcn research agent

2. **API Layer:**
   - Implement health check endpoint first
   - Test streaming with simple echo endpoint
   - Integrate Python backend incrementally

3. **UI Components:**
   - Chat interface (streaming text)
   - Stats dashboard (standings, scorers)
   - Feed view (personalized content)
   - Match cards (fixtures with odds)

4. **Testing:**
   - API route tests (Jest)
   - E2E tests (Playwright)
   - Performance testing (streaming latency)

---

## Questions to Resolve

1. **Python Execution:** Execute scripts via `child_process` or run FastAPI server?
2. **Authentication:** When to add user accounts? (Phase 2)
3. **Redis:** Deploy Redis instance or stick with file cache initially?
4. **WebSockets:** Use SSE (current) or upgrade to WebSockets for bi-directional chat?
5. **shadcn Components:** Which AI-specific components exist? (Need research)

---

**Document Status:** Draft for review
**Next Review:** After frontend worktree setup
