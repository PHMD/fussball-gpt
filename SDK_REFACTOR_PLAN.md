# SDK Refactor Plan

**Branch:** `sdk-refactor`
**Worktree:** `/Users/patrickmeehan/knowledge-base/projects/ksi_prototype_sdk`
**Goal:** Experiment with Vercel AI SDK approach in parallel with Python backend

---

## Why This Worktree Exists

This is an **experimental branch** to evaluate Vercel AI SDK + TypeScript-only architecture against the existing Python backend.

**Strategy:** Build both, compare side-by-side, make data-driven decision.

---

## What Changes in This Branch

### 1. Backend Refactor (2-3 weeks)

**Remove (Python):**
- `data_aggregator.py` (1,100 lines)
- `models.py` (150 lines)
- `cli.py` (200 lines)
- `user_config.py` (175 lines)
- `requirements.txt`
- All Python tests

**Add (TypeScript):**
- `lib/data-aggregator.ts` - Sports API integration
- `lib/models.ts` - Type definitions (Zod schemas)
- `lib/llm-client.ts` - Anthropic integration via Vercel AI SDK
- `lib/user-config.ts` - User preferences
- `lib/cache.ts` - Caching layer (Vercel KV or Redis)

### 2. Frontend Integration (Days)

**Next.js API Routes:**
```typescript
// app/api/query/route.ts (10 lines vs 100)
import { anthropic } from '@ai-sdk/anthropic';
import { streamText } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();
  const result = streamText({
    model: anthropic('claude-3-5-sonnet-20241022'),
    messages,
  });
  return result.toDataStreamResponse();
}
```

**Frontend Components:**
```typescript
// app/page.tsx (3 lines vs 100)
import { useChat } from 'ai/react';

const { messages, input, handleSubmit } = useChat();
```

---

## Parallel Development Strategy

### Week 1: Backend Refactor
**Tasks:**
1. Set up TypeScript project structure
2. Port data aggregation (TheSportsDB, API-Football, etc.)
3. Implement caching layer (Vercel KV)
4. Port Pydantic models → Zod schemas

**Validation:**
- Test each API integration independently
- Verify caching works (6-24 hour TTLs)
- Compare response times vs Python

### Week 2: LLM Integration
**Tasks:**
1. Integrate Vercel AI SDK
2. Port system prompt logic
3. Implement streaming
4. Port user config (personas, detail levels)

**Validation:**
- Test streaming with real queries
- Compare response quality vs Python backend
- Verify persona behavior matches

### Week 3: Frontend + Testing
**Tasks:**
1. Build Next.js frontend with `useChat()` hook
2. Integrate shadcn AI components
3. End-to-end testing
4. Performance comparison

**Validation:**
- Compare frontend code complexity (SDK vs Python)
- Test deployment to Vercel
- Measure cold start times

---

## Success Metrics

### Technical Comparison

| Metric | Python Backend (master) | SDK Refactor (sdk-refactor) |
|--------|------------------------|----------------------------|
| **Frontend Code** | ~200 lines (custom streaming) | ~20 lines (`useChat()`) |
| **Backend Code** | 1,625 lines Python | ~800 lines TypeScript (estimate) |
| **Deployment Complexity** | Python + Node.js runtime | Node.js only |
| **Cold Start Time** | ~2-3s (Python spawn) | ~500ms (Edge runtime) |
| **Developer Experience** | 2 languages, separate testing | 1 language, unified |
| **Type Safety** | Python runtime errors | TypeScript compile-time |
| **Caching** | File-based (proven) | Vercel KV (new, untested) |
| **Time to Ship** | Already done (9.1/10 quality) | 2-3 weeks + testing |

### Decision Criteria

**Choose Python Backend if:**
- Time to market is critical (ship in 2 weeks)
- Python backend quality is proven (9.1/10)
- Team comfortable debugging Python
- Don't want to risk new bugs

**Choose SDK Refactor if:**
- Simpler deployment is top priority
- Team prefers TypeScript-only
- Want to learn Vercel AI SDK
- Willing to invest 2-3 weeks

---

## Frontend Agent Handoff Differences

### Python Backend (ksi_prototype_frontend worktree)

**Complexity:** High

**What frontend agent builds:**
1. **Custom streaming API route** (~100 lines)
   - Spawn Python subprocess
   - Handle stdout/stderr streams
   - Parse SSE events
   - Error handling and cleanup

2. **Custom useChat hook** (~100 lines)
   - Message state management
   - Manual streaming handling
   - Loading states
   - Error handling

3. **shadcn AI components** (same in both)

**Total complexity:** ~200 lines of streaming infrastructure

---

### SDK Refactor (this worktree)

**Complexity:** Low

**What frontend agent builds:**
1. **Simple API route** (~10 lines)
   - Import Vercel AI SDK
   - Call `streamText()`
   - Return response

2. **Use built-in hook** (~3 lines)
   - Import `useChat()`
   - Destructure state
   - Done

3. **shadcn AI components** (same in both)

**Total complexity:** ~15 lines total

---

## Migration Path (If SDK Wins)

If SDK refactor proves better, migration path:

1. **Deploy SDK version** to new Vercel project
2. **A/B test** both versions (10% traffic to SDK)
3. **Compare metrics:**
   - Response times
   - Error rates
   - User satisfaction
   - Bug reports

4. **Gradual migration:**
   - 10% → 25% → 50% → 100%
   - Keep Python backend as fallback

5. **Sunset Python:**
   - After 2 weeks of 100% SDK traffic
   - Archive Python backend to branch

---

## Current Status

**Phase:** Setup complete
**Next Steps:**
1. Port `data_aggregator.py` → `lib/data-aggregator.ts`
2. Set up Vercel KV for caching
3. Test sports API integrations

**Timeline:** 2-3 weeks to completion

---

## How to Work on This Branch

```bash
# Navigate to SDK worktree
cd /Users/patrickmeehan/knowledge-base/projects/ksi_prototype_sdk

# Install dependencies
npm install
npm install ai @ai-sdk/anthropic

# Start development
npm run dev

# Compare with Python backend
cd ../ksi_prototype
python test_data_aggregator.py  # Test Python version
cd ../ksi_prototype_sdk
npm test  # Test TypeScript version
```

---

## Questions to Answer During Experiment

1. **Is TypeScript data aggregation as reliable as Python?**
   - Do API clients work as well?
   - Is error handling as robust?

2. **Is Vercel KV caching as effective as file-based?**
   - Same hit rates?
   - Same TTL behavior?

3. **Is frontend development truly simpler with SDK?**
   - How much code savings in practice?
   - Fewer bugs?

4. **What's the actual deployment difference?**
   - Build times?
   - Cold start performance?
   - Error rates?

5. **What's the real development velocity impact?**
   - Faster to add features with SDK?
   - Easier debugging?

---

## Exit Criteria

**After 3 weeks, we should know:**
- Which approach is faster to develop
- Which approach is more reliable
- Which approach frontend developers prefer
- Which approach deploys better to Vercel

**Then make the call:** Keep Python or migrate to SDK

---

**Status:** Experimental - Not Production Ready
**Decision Date:** TBD (after 3-week evaluation)
