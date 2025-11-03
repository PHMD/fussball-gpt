---
name: pieces-context-logger
description: |
  Logs completed work to Pieces for long-term cross-session memory.
  Use when feature is complete and merged, to preserve decision context,
  learnings, and "why" narratives for future sessions and team members.
  Captures synthesized knowledge from entire workflow (planning → spec → dev → qa).
allowed-tools: mcp__pieces__create_pieces_memory
---

# Pieces Context Logger Skill

## Purpose
Preserve long-term memory of completed work - the decisions made, patterns discovered, and context needed for future understanding.

## When Claude Uses This Skill

**Model-invoked after:**
- PR merged to main
- Feature fully integrated
- Major architectural decision completed
- Complex bug resolved with valuable learnings

**NOT for:** Individual agent work (agents use vibe-learn for immediate patterns)

## What Makes This Different

**vibe-learn:** Agent-level patterns during work
- Quick feedback loops
- What worked/didn't in this task
- Immediate tactical learnings

**Pieces logging:** Project-level context after completion
- Strategic decisions and rationale
- Cross-agent synthesis
- Long-term reference material
- "Why" narratives for future teams

## Workflow

### 1. Gather Complete Context

After feature is merged, collect:

**Planning Context:**
- Original user request
- Vibe-check validation and concerns
- Approach decisions

**Research:**
- Ref documentation consulted
- Exasearch examples used
- Key sources that influenced design

**Implementation Decisions:**
- Architecture chosen and why
- Alternatives considered and rejected
- Trade-offs made
- Patterns followed or created

**Testing Insights:**
- Security issues found and fixed
- Test patterns that worked well
- Edge cases discovered

**Code Artifacts:**
- Files created/modified
- Key functions/components
- External links (PR, Linear issue)

### 2. Synthesize Narrative

Create cohesive story from planning → integration:

```markdown
## Planning Phase
- User wanted: {goal}
- Vibe-check validated: {approach}
- Key consideration: {important concern}

## Research Phase (SPEC-AGENT)
- Vercel AI SDK pattern: {what we found}
- Real-world example: {example that influenced design}
- Decision: Chose X over Y because {rationale}

## Implementation (DEV-AGENT)
- Files created: {list}
- Key pattern: {architectural decision}
- Beyond spec: Added {feature} because {reason}
- Challenge: {problem encountered and solution}

## Testing (QA-AGENT)
- Security: Found and fixed {issue}
- Test pattern: {approach that worked well}
- Coverage: {what we tested}

## Learnings
- Success: {what went really well}
- Pattern to reuse: {technique worth repeating}
- Watch out for: {gotcha for next time}
```

### 3. Create Pieces Memory

```javascript
create_pieces_memory({
  summary_description: "One-line feature summary (50 chars max)",

  summary: `# Feature Name: Complete Context

## Overview
{2-3 paragraph narrative of what was built and why}

## Planning & Validation
**User Request:** {original goal}

**Vibe-Check Validation:**
- ✓ {validated aspect}
- ⚠️ {concern raised}
- Decision: {how we addressed}

## Architecture & Research
**Approach:** {high-level architecture}

**Key Sources:**
- [Vercel AI SDK streamText](ref-url) - {why relevant}
- [Production example](exasearch-url) - {what we learned}

**Design Decisions:**
1. **Chose:** Native WebSocket
   **Over:** socket.io
   **Because:** {rationale with source}

2. **Chose:** Exponential backoff
   **Over:** Fixed retry interval
   **Because:** {rationale}

## Implementation Details
**Files Created:**
- \`app/api/scores/stream/route.ts\` - WebSocket endpoint with rate limiting
- \`lib/websocket-client.ts\` - Client connection manager with reconnection logic

**Files Modified:**
- \`components/ScoreBoard.tsx\` - Real-time update integration

**Key Patterns Used:**
- Connection pooling (max 5) prevents memory leaks
- Token bucket rate limiting (1 req/sec)
- Zod validation on all WebSocket messages

**Beyond Spec:**
Added connection pooling (not in original spec) because production example showed memory leak risk on rapid reconnects.

## Security & Testing
**Security Issues Found:**
- Medium: Rate limit bypass via header manipulation
- Fixed: Server-side token bucket validation

**Test Coverage:**
- 8/8 E2E tests passing
- Both German and English language paths
- Error handling, reconnection, rate limiting
- Test pattern: Mock network disconnect to verify exponential backoff

## Learnings & Patterns

**Successes:**
- Connection pooling pattern works great for WebSocket management
- Exponential backoff prevents server overload
- Bilingual testing strategy caught language-specific edge cases

**Patterns to Reuse:**
- Token bucket rate limiting pattern
- WebSocket reconnection with cleanup in useEffect
- Test structure for bilingual features

**Watch Out For:**
- Serverless limitations with persistent connections
- Rate limit headers can be spoofed (need server-side validation)
- WebSocket listener cleanup is critical

## Links & References
- Linear: PHM-123
- GitHub PR: #45
- Branch: feature/phm-123-realtime-scores
- Deployed: [Production URL]

---
_Generated after successful integration | ${new Date().toISOString()}_
`,

  files: [
    "/absolute/path/to/project/app/api/scores/stream/route.ts",
    "/absolute/path/to/project/lib/websocket-client.ts",
    "/absolute/path/to/project/components/ScoreBoard.tsx",
    "/absolute/path/to/project/tests/e2e/realtime-scores.spec.ts"
  ],

  externalLinks: [
    "https://github.com/username/repo/pull/45",
    "https://linear.app/team/issue/PHM-123",
    "https://ref.tools/docs/vercel-ai-sdk/streaming",
    "https://github.com/example/production-websocket-pattern"
  ],

  project: "/Users/patrickmeehan/knowledge-base/projects/ksi_prototype_sdk"
})
```

### 4. Verify Pieces Logged Successfully

Check that memory was created:
- Pieces should confirm storage
- Memory is indexed and searchable
- Future sessions can retrieve this context

## Example Memory: Real-Time Score Updates

```javascript
create_pieces_memory({
  summary_description: "Real-time score updates via WebSocket in chat UI",

  summary: `# Real-Time Score Updates: Complete Context

## Overview
Added real-time Bundesliga score updates to chat interface without page refresh. Users now see scores update live during matches while chatting about games. Implemented using WebSocket connection with robust error handling and rate limiting.

## Planning & Validation
**User Request:** Fans wanted live scores integrated into chat without manually refreshing

**Vibe-Check Validation:**
- ✓ WebSocket approach appropriate for bi-directional real-time data
- ⚠️ Recommended rate limiting to prevent abuse
- ⚠️ Consider serverless limitations (Vercel Functions timeout after 10s)
- Decision: Use Vercel Edge Functions for persistent connections

## Architecture & Research
**Approach:** Native WebSocket via Edge Function, client maintains persistent connection, server pushes score updates as they arrive from data aggregator

**Key Sources:**
- [Vercel Edge Functions WebSocket](https://vercel.com/docs/functions/edge-functions/websocket) - Official pattern
- [Production chat app](https://github.com/example/realtime-chat) - Reconnection logic
- [Token bucket algorithm](https://en.wikipedia.org/wiki/Token_bucket) - Rate limiting

**Design Decisions:**
1. **Chose:** Native WebSocket
   **Over:** socket.io library
   **Because:** Simpler, no extra dependencies, sufficient for our use case. Production example showed native WebSocket is easier to maintain.

2. **Chose:** Exponential backoff on reconnect
   **Over:** Fixed retry interval
   **Because:** Prevents thundering herd during outages, scales better with many concurrent users

3. **Chose:** Edge Functions
   **Over:** Serverless Functions
   **Because:** Edge Functions support streaming responses and longer connection times needed for WebSocket

## Implementation Details
**Files Created:**
- \`app/api/scores/stream/route.ts\` (85 lines) - WebSocket endpoint with token bucket rate limiting
- \`lib/websocket-client.ts\` (120 lines) - Client connection manager with exponential backoff reconnection

**Files Modified:**
- \`components/ScoreBoard.tsx\` (+45, -12 lines) - Integrated real-time updates with loading and error states

**Key Patterns Used:**
- Connection pooling: Max 5 concurrent connections per user, oldest evicted if exceeded
- Token bucket rate limiting: 1 request per second per IP address
- Zod schema validation: All WebSocket messages validated at runtime
- useEffect cleanup: Proper listener removal prevents memory leaks

**Beyond Spec:**
Added connection pooling (not in original spec) because production example showed memory leak risk when users rapidly open/close connections (e.g., switching between tabs).

## Security & Testing
**Security Issues Found:**
- Medium severity: Rate limit could be bypassed by spoofing X-Forwarded-For header
- Fixed: Implemented server-side token bucket that validates against actual IP from Vercel headers

**Test Coverage:**
- 8/8 Playwright E2E tests passing
- German language: Real-time update, reconnection, rate limit, error handling
- English language: Same coverage
- Test pattern: Mock WebSocket server to verify exponential backoff timing (1s, 2s, 4s, 8s...)

## Learnings & Patterns

**Successes:**
- Connection pooling pattern completely eliminated memory leak issues
- Exponential backoff prevented server overload during network issues in testing
- Bilingual test strategy caught German error message truncation bug

**Patterns to Reuse:**
- Token bucket rate limiting is reusable for any real-time feature
- WebSocket reconnection logic with cleanup pattern should be template for future real-time features
- Test structure with mock WebSocket server works great for timing-sensitive tests

**Watch Out For:**
- Vercel Serverless Functions DON'T support WebSocket (10s timeout) - must use Edge Functions
- Rate limit headers can be spoofed - always validate server-side
- WebSocket listener cleanup is CRITICAL - forgot this initially and saw memory usage climb
- Connection pooling needs upper bound - unlimited connections crash browser tabs

## Production Metrics (Post-Deploy)
- Average connection duration: 12 minutes
- Reconnection rate: 3% (mostly mobile network switches)
- No memory leak issues after 72 hours monitoring
- Rate limit triggered 15 times (all legitimate spike protection)

## Links & References
- Linear: PHM-123 (planning, spec, implementation, QA)
- GitHub PR: #45 (merged with 2 approvals)
- Branch: feature/phm-123-realtime-scores
- Production: https://fussball-gpt.vercel.app
- Vercel Edge Functions: https://vercel.com/docs/functions/edge-functions

---
_Generated after successful integration | 2025-10-30T15:30:00Z_
`,

  files: [
    "/Users/patrickmeehan/knowledge-base/projects/ksi_prototype_sdk/app/api/scores/stream/route.ts",
    "/Users/patrickmeehan/knowledge-base/projects/ksi_prototype_sdk/lib/websocket-client.ts",
    "/Users/patrickmeehan/knowledge-base/projects/ksi_prototype_sdk/components/ScoreBoard.tsx",
    "/Users/patrickmeehan/knowledge-base/projects/ksi_prototype_sdk/tests/e2e/realtime-scores.spec.ts"
  ],

  externalLinks: [
    "https://github.com/patrickmeehan/ksi_prototype_sdk/pull/45",
    "https://linear.app/kicker/issue/PHM-123",
    "https://vercel.com/docs/functions/edge-functions/websocket",
    "https://github.com/example/production-chat-websocket"
  ],

  project: "/Users/patrickmeehan/knowledge-base/projects/ksi_prototype_sdk"
})
```

## Important Notes

**Use absolute paths for files:**
- Full path from root: `/Users/username/project/path/to/file.ts`
- Pieces needs this for file association
- Enables "open in IDE" functionality

**Include ALL relevant links:**
- GitHub PR (merged)
- Linear issue (all sub-issues referenced in main)
- Documentation consulted
- Examples that influenced decisions

**Synthesize, don't duplicate:**
- This isn't a copy-paste of Linear comments
- It's a cohesive narrative connecting all phases
- Explain the "why" and "how we got here"

**Log AFTER integration:**
- Not after each agent completes
- Wait until feature is merged and working
- Captures complete story start to finish

**Future-facing:**
- Write for someone 6 months from now
- They don't have context of conversations
- Explain decisions clearly with rationale

## When NOT to Use

**Don't use Pieces for:**
- In-progress work (use Linear comments)
- Quick tactical patterns (use vibe-learn)
- Temporary context (use main chat)
- Non-merged experiments

**DO use Pieces for:**
- Merged features with complete story
- Major architectural decisions
- Complex implementations with valuable learnings
- Patterns worth preserving long-term

## Integration with Workflow

Orchestrator uses this skill after:
1. QA-AGENT approves
2. PR is created and merged
3. Feature deployed to production
4. Linear issue closed

At this point, the complete story is known and can be synthesized into long-term memory.

## Troubleshooting

**Pieces not storing memory:**
- Verify PiecesOS is running (port 39300)
- Check Pieces MCP connection
- Wait 5-10 min for indexing after enabling LTM

**Files not linking:**
- Use absolute paths (not relative)
- Verify paths exist on filesystem
- Check file permissions

**Memory not searchable:**
- Give indexing time (few minutes)
- Use specific search terms
- Check summary_description has good keywords
