# SDK Refactor Agent Prompt

**Copy-paste this into Claude Code when opening this worktree:**

---

I'm refactoring the **Fußball GPT** backend from Python to TypeScript using Vercel AI SDK.

**Current location:** `/Users/patrickmeehan/knowledge-base/projects/ksi_prototype_sdk`
**Branch:** `sdk-refactor`
**Purpose:** Experimental - evaluate Vercel AI SDK approach vs. Python backend

---

## Mission

Port the entire Python backend (1,625 lines) to TypeScript + Vercel AI SDK while maintaining the same functionality and quality.

**Why:** Simpler deployment, better DX, TypeScript end-to-end, built-in streaming with `useChat()` hook.

---

## What Exists (Python Backend to Port)

**In parent directory:** `/Users/patrickmeehan/knowledge-base/projects/ksi_prototype`

### Backend Files to Port

| File | Lines | What It Does | Port To |
|------|-------|--------------|---------|
| `data_aggregator.py` | 1,100 | Fetches from 5 sports APIs, caching | `lib/data-aggregator.ts` |
| `models.py` | 150 | Pydantic data models | `lib/models.ts` (Zod) |
| `cli.py` | 200 | LLM integration (Anthropic) | `app/api/query/route.ts` (Vercel AI SDK) |
| `user_config.py` | 175 | User preferences (personas, detail levels) | `lib/user-config.ts` |
| **Total** | **1,625** | | |

### Sports APIs Integrated (Must Port All)

1. **TheSportsDB** (FREE)
   - Standings
   - Fixtures
   - Results
   - Team form
   - H2H records

2. **API-Football** (Pro $19/mo)
   - Player stats (top scorers)
   - Injury data

3. **The Odds API** (FREE 500 req/mo)
   - Betting odds

4. **Kicker RSS** (FREE)
   - News articles

5. **Brave Search** (used for article augmentation if <10 RSS results)

### Caching Strategy (Must Port)

**Current (file-based):**
```python
# cache/player_stats.json (6-hour TTL)
# cache/team_form.json (6-hour TTL)
# cache/injuries.json (6-hour TTL)
# cache/betting_odds.json (24-hour TTL)
```

**New (Vercel KV or Redis):**
```typescript
// Need to implement same TTL strategy
await kv.set('bundesliga:player_stats', data, { ex: 21600 }); // 6 hours
await kv.set('bundesliga:betting_odds', data, { ex: 86400 }); // 24 hours
```

---

## Getting Started (Do These in Order)

### 1. Read SDK_REFACTOR_PLAN.md
```bash
cat SDK_REFACTOR_PLAN.md
```

This has:
- Why this worktree exists
- 3-week timeline
- Success metrics
- Decision criteria (Python vs SDK)

### 2. Read Parent Directory Docs
```bash
cat ../ksi_prototype/API_SPEC.md
cat ../ksi_prototype/FRONTEND_HANDOFF.md
cat ../ksi_prototype/VALIDATION_REPORT.md
cat ../ksi_prototype/FRONTEND_COMPARISON.md
```

These define the functional requirements and API contract.

### 3. Study Python Backend
```bash
# Read current implementation
cat ../ksi_prototype/data_aggregator.py  # 1,100 lines to port
cat ../ksi_prototype/models.py           # Data schemas
cat ../ksi_prototype/cli.py              # LLM integration
cat ../ksi_prototype/user_config.py      # User preferences
```

---

## Week 1: Core Backend Refactor

### Task 1: Project Setup

**Initialize Next.js + TypeScript:**
```bash
npx create-next-app@latest . --typescript --tailwind --app

# Install Vercel AI SDK
npm install ai @ai-sdk/anthropic

# Install utilities
npm install zod  # For data validation (replaces Pydantic)
npm install @vercel/kv  # For caching
npm install rss-parser  # For Kicker RSS
```

**Project structure:**
```
src/
├── app/
│   └── api/
│       ├── query/route.ts          # LLM endpoint (replaces cli.py)
│       ├── standings/route.ts
│       ├── players/route.ts
│       └── ...
├── lib/
│   ├── data-aggregator.ts          # Port from data_aggregator.py
│   ├── models.ts                   # Port from models.py (Pydantic → Zod)
│   ├── user-config.ts              # Port from user_config.py
│   ├── cache.ts                    # Vercel KV wrapper
│   └── api-clients/
│       ├── thesportsdb.ts
│       ├── api-football.ts
│       ├── odds-api.ts
│       ├── kicker-rss.ts
│       └── brave-search.ts
└── types/
    └── index.ts
```

### Task 2: Port Data Models (Pydantic → Zod)

**Python (current):**
```python
from pydantic import BaseModel

class PlayerStats(BaseModel):
    name: str
    team: str
    goals: int
    assists: int
    minutes_played: int
```

**TypeScript (port to):**
```typescript
import { z } from 'zod';

export const PlayerStatsSchema = z.object({
  name: z.string(),
  team: z.string(),
  goals: z.number(),
  assists: z.number(),
  minutes_played: z.number(),
});

export type PlayerStats = z.infer<typeof PlayerStatsSchema>;
```

**Files to create:**
- `lib/models.ts` - All Zod schemas

### Task 3: Port API Clients

**For each API, create a TypeScript client:**

**Example - TheSportsDB:**
```typescript
// lib/api-clients/thesportsdb.ts
export async function fetchBundesligaStandings() {
  const response = await fetch(
    'https://www.thesportsdb.com/api/v1/json/3/lookuptable.php?l=4331&s=2024-2025'
  );

  const data = await response.json();

  // Validate with Zod
  return StandingsSchema.parse(data);
}
```

**Files to create:**
- `lib/api-clients/thesportsdb.ts`
- `lib/api-clients/api-football.ts`
- `lib/api-clients/odds-api.ts`
- `lib/api-clients/kicker-rss.ts`
- `lib/api-clients/brave-search.ts`

### Task 4: Port Caching Layer

**Python (file-based):**
```python
def fetch_player_stats_cached(self):
    cache_file = "cache/player_stats.json"
    if cache_valid(cache_file, 21600):  # 6 hours
        return load_from_cache(cache_file)
    data = fetch_player_stats()
    save_to_cache(cache_file, data)
    return data
```

**TypeScript (Vercel KV):**
```typescript
// lib/cache.ts
import { kv } from '@vercel/kv';

export async function fetchPlayerStatsCached() {
  const cached = await kv.get('bundesliga:player_stats:2024');
  if (cached) return cached;

  const data = await fetchPlayerStats();
  await kv.set('bundesliga:player_stats:2024', data, { ex: 21600 }); // 6 hours
  return data;
}
```

**File to create:**
- `lib/cache.ts` - Caching wrapper with same TTLs

### Task 5: Port Data Aggregator

**This is the big one - 1,100 lines.**

**Python structure:**
```python
class DataAggregator:
    def fetch_bundesliga_standings(self):
        # ...

    def fetch_player_stats_cached(self):
        # ...

    def fetch_injuries_cached(self):
        # ...

    def aggregate_all(self):
        # Combines all data sources
        return AggregatedData(...)
```

**TypeScript structure:**
```typescript
// lib/data-aggregator.ts
export async function fetchBundesligaStandings() {
  // ...
}

export async function fetchPlayerStatsCached() {
  // ...
}

export async function fetchInjuriesCached() {
  // ...
}

export async function aggregateAllData() {
  const [standings, players, fixtures, injuries, news] = await Promise.all([
    fetchBundesligaStandings(),
    fetchPlayerStatsCached(),
    fetchFixturesCached(),
    fetchInjuriesCached(),
    fetchNewsCached(),
  ]);

  return { standings, players, fixtures, injuries, news };
}
```

**File to create:**
- `lib/data-aggregator.ts` - Main orchestration

---

## Week 2: LLM Integration with Vercel AI SDK

### Task 6: Build Streaming API Route

**Python (current):**
```python
# cli.py
llm = LLMClient(provider="anthropic")
response = llm.stream_query(query, aggregated_data)
```

**TypeScript (Vercel AI SDK):**
```typescript
// app/api/query/route.ts
import { anthropic } from '@ai-sdk/anthropic';
import { streamText } from 'ai';
import { aggregateAllData } from '@/lib/data-aggregator';

export const maxDuration = 60;

export async function POST(req: Request) {
  const { messages } = await req.json();

  // Fetch current sports data
  const sportsData = await aggregateAllData();

  // Build system prompt with data context
  const systemMessage = {
    role: 'system',
    content: `You are Fußball GPT, a German football intelligence assistant.

Current Bundesliga Data (2024/25 season):
${JSON.stringify(sportsData, null, 2)}

Provide accurate, context-aware responses using this data. Include source citations.`
  };

  const result = streamText({
    model: anthropic('claude-3-5-sonnet-20241022'),
    messages: [systemMessage, ...messages],
  });

  return result.toDataStreamResponse();
}
```

**That's it - 15 lines vs. Python's complex streaming logic.**

### Task 7: Port User Config

**Python:**
```python
# user_config.py
class UserProfile(BaseModel):
    language: Language
    detail_level: DetailLevel
    persona: Optional[str] = None

def get_system_prompt_modifier(profile: UserProfile) -> str:
    # Returns custom prompt based on preferences
```

**TypeScript:**
```typescript
// lib/user-config.ts
export const UserProfileSchema = z.object({
  language: z.enum(['de', 'en']),
  detail_level: z.enum(['quick', 'balanced', 'detailed']),
  persona: z.enum(['casual_fan', 'expert_analyst', 'betting_enthusiast', 'fantasy_player']).optional(),
});

export function getSystemPromptModifier(profile: UserProfile): string {
  // Returns custom prompt based on preferences
}
```

### Task 8: Integrate User Preferences into API Route

```typescript
// app/api/query/route.ts
export async function POST(req: Request) {
  const { messages, persona, detail_level } = await req.json();

  const sportsData = await aggregateAllData();
  const promptModifier = getSystemPromptModifier({ persona, detail_level });

  const systemMessage = {
    role: 'system',
    content: `${promptModifier}\n\nCurrent data: ${JSON.stringify(sportsData)}`
  };

  // ... rest of streaming
}
```

---

## Week 3: Frontend + Testing

### Task 9: Build Simple Frontend to Test

**Super simple with Vercel AI SDK:**

```typescript
// app/page.tsx
'use client';
import { useChat } from 'ai/react';
import { Message, Response, Conversation, PromptInput } from '@/components/ai';

export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: '/api/query',
  });

  return (
    <div className="flex flex-col h-screen">
      <Conversation>
        {messages.map((message) => (
          <Message key={message.id} from={message.role}>
            <Response>{message.content}</Response>
          </Message>
        ))}
      </Conversation>
      <PromptInput
        value={input}
        onChange={handleInputChange}
        onSubmit={handleSubmit}
        placeholder="Ask about Bundesliga..."
      />
    </div>
  );
}
```

**That's it - 20 lines for complete chat UI.**

Copy shadcn AI components from https://www.shadcn.io/ai.

### Task 10: Testing & Comparison

**Test checklist:**
- [ ] All 5 APIs work (TheSportsDB, API-Football, Odds, Kicker, Brave)
- [ ] Caching works with same TTLs (6-24 hours)
- [ ] Streaming works end-to-end
- [ ] User preferences (personas, detail levels) work
- [ ] Response quality matches Python backend
- [ ] Performance acceptable (cold starts, latency)

**Compare against Python:**
```bash
# Python backend (for comparison)
cd ../ksi_prototype
python data_aggregator.py

# TypeScript backend (your new version)
cd ../ksi_prototype_sdk
npm run dev
```

**Metrics to measure:**
- Response times
- Cache hit rates
- Error rates
- Code maintainability
- Development velocity

---

## Environment Variables

```bash
# .env.local
ANTHROPIC_API_KEY=your_key_here
RAPIDAPI_KEY=your_key_here        # API-Football
ODDS_API_KEY=your_key_here        # The Odds API
BRAVE_SEARCH_API_KEY=your_key_here
KV_URL=your_vercel_kv_url         # Vercel KV for caching
KV_REST_API_URL=your_vercel_kv_rest_url
KV_REST_API_TOKEN=your_vercel_kv_token
KV_REST_API_READ_ONLY_TOKEN=your_vercel_kv_readonly_token
```

---

## Key Decisions

### Caching: Vercel KV vs. File-Based

**Python (file-based):**
- Simple, works locally
- No external dependencies
- Persistent across deploys (if using persistent storage)

**TypeScript (Vercel KV):**
- Cloud-native
- Better for serverless
- Requires Vercel account
- More setup

**Alternative:** Could use file-based in TypeScript too, but Vercel KV is more production-ready.

### API Clients: axios vs. fetch

**Recommendation:** Use native `fetch` (built into Node.js 18+)
- No dependencies
- Standard API
- Async/await support

```typescript
// Don't need axios
const response = await fetch(url);
const data = await response.json();
```

---

## Success Criteria

**Week 1:**
- [ ] All API clients ported and tested
- [ ] Caching layer working
- [ ] Data aggregation matches Python output

**Week 2:**
- [ ] Vercel AI SDK streaming working
- [ ] User config ported
- [ ] System prompts match Python behavior

**Week 3:**
- [ ] Frontend working with `useChat()` hook
- [ ] End-to-end testing complete
- [ ] Performance comparison done

**Final Decision:**
- [ ] Compare Python vs SDK side-by-side
- [ ] Measure: code complexity, deployment ease, performance
- [ ] Choose winner based on data

---

## Resources

**Parent Directory (Python reference):**
- `/Users/patrickmeehan/knowledge-base/projects/ksi_prototype`
- `data_aggregator.py` - Reference implementation
- `models.py` - Data schemas
- `cli.py` - LLM integration
- `user_config.py` - User preferences

**Documentation:**
- `SDK_REFACTOR_PLAN.md` - This refactor plan
- `../ksi_prototype/API_SPEC.md` - API contract
- `../ksi_prototype/FRONTEND_COMPARISON.md` - Shows SDK simplicity
- `../ksi_prototype/VALIDATION_REPORT.md` - Tech validation

**Vercel AI SDK:**
- https://sdk.vercel.ai/docs - Official docs
- https://sdk.vercel.ai/docs/ai-sdk-core/streaming - Streaming guide

**shadcn AI Components:**
- https://www.shadcn.io/ai - Copy-paste components

---

## Timeline

**Week 1:** API clients + caching + data aggregation
**Week 2:** LLM integration + user config
**Week 3:** Frontend + testing + comparison

**Total:** 2-3 weeks to production-ready TypeScript version

---

## Exit Criteria

After 3 weeks, we should know:
- Is TypeScript as reliable as Python?
- Is Vercel KV caching as effective?
- Is frontend simpler with `useChat()` hook?
- Is deployment easier?

**Then decide:** Keep Python or migrate to SDK.

---

**Ready to start?**

```bash
# 1. Initialize Next.js
npx create-next-app@latest . --typescript --tailwind --app

# 2. Install dependencies
npm install ai @ai-sdk/anthropic @vercel/kv zod rss-parser

# 3. Study Python backend
cat ../ksi_prototype/data_aggregator.py

# 4. Start porting!
mkdir -p src/lib/api-clients
touch src/lib/models.ts
touch src/lib/data-aggregator.ts
```

Good luck! 🚀

**Remember:** This is an experiment. Python backend is your safety net.
