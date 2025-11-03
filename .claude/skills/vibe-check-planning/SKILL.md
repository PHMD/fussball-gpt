---
name: vibe-check-planning
description: |
  Validates technical approach BEFORE expensive research and agent delegation.
  Use PROACTIVELY when user requests new features or when planning complex
  implementations. Prevents wasted tokens on wrong approaches by validating
  direction early.
allowed-tools: mcp__vibe-check__vibe_check, mcp__vibe-check__vibe_learn, mcp__linear__linear_addIssueComment
---

# Vibe-Check Planning Skill

## Purpose
Validate technical approach BEFORE delegating to SPEC-AGENT for expensive doc research. This prevents wasted context on wrong directions.

## When Claude Uses This Skill

**Model-invoked automatically when:**
- User requests new feature implementation
- Planning complex architectural changes
- Uncertain about implementation approach
- Before delegating work to SPEC-AGENT

**Key insight:** Run vibe-check FIRST, then research. Not the other way around.

## Workflow

### 1. Extract Planning Context

When a feature request comes in, gather:

**Goal:** What does the user want to achieve?
- Clear, specific objective
- User's desired outcome

**Proposed Plan:** How will we solve it?
- High-level technical approach
- Key technologies/patterns to use
- Architecture sketch

**Uncertainties:** What are we unsure about?
- Known risks or unknowns
- Questions about approach
- Trade-offs to consider

**Task Context:** Current project state
- Relevant existing code/patterns
- Constraints (tech stack, timeline)
- Related features

### 2. Run Vibe-Check

```javascript
vibe_check({
  phase: "planning",
  goal: "Specific feature goal in 1-2 sentences",
  plan: "Proposed technical approach:\n- Key point 1\n- Key point 2\n- Key point 3",
  uncertainties: [
    "Specific concern or question",
    "Another uncertainty"
  ],
  taskContext: "Relevant context: Next.js 15 app, existing WebSocket chat, etc."
})
```

**Example:**
```javascript
vibe_check({
  phase: "planning",
  goal: "Add real-time score updates to chat interface without page refresh",
  plan: "Use Vercel AI SDK streamText with WebSocket for bi-directional communication. Client maintains persistent connection, server pushes score updates as they happen. Implement rate limiting to prevent abuse.",
  uncertainties: [
    "Should we use native WebSocket or library like socket.io?",
    "How to handle reconnection after network drops?",
    "What's the right rate limiting strategy?"
  ],
  taskContext: "Next.js 15 app with existing chat interface using Vercel AI SDK. Already have streaming response pattern for chat. Need to extend for real-time sports data."
})
```

### 3. Interpret Feedback

Vibe-check returns assessment with:
- ✓ Validated aspects of approach
- ⚠️ Concerns or warnings
- 💡 Suggestions for improvement
- ❌ Red flags to reconsider

**Response patterns:**

**All green (validated):**
```
✓ Approach is sound
✓ Technology choices appropriate
✓ Plan addresses key concerns
→ Proceed to SPEC-AGENT for detailed research
```

**Yellow flags (concerns):**
```
⚠️ Consider X instead of Y because...
⚠️ Missing consideration of Z
→ Address concerns, then proceed or re-check
```

**Red flags (reconsider):**
```
❌ Approach has fundamental flaw: ...
💡 Alternative: Consider different pattern...
→ Revise plan significantly, run vibe-check again
```

### 4. Document Decision

Update Linear issue with vibe-check results:

```javascript
linear_addIssueComment({
  issueId: "issue-id",
  body: `[PLANNING] Vibe-check Results

**Approach Validated:** ✓

**Key Points:**
- Native WebSocket approach confirmed appropriate
- Server-side rate limiting essential
- Exponential backoff recommended for reconnection

**Considerations:**
- Monitor connection pool size
- Consider fallback for browsers without WebSocket

**Decision:** Proceeding to SPEC-AGENT for detailed architecture and research.

---
_Vibe-check planning skill | ${new Date().toISOString()}_`
})
```

### 5. Decide Next Step

Based on vibe-check feedback:

**If validated (green):**
- Proceed to SPEC-AGENT
- Include vibe-check context in handoff
- SPEC-AGENT can now confidently research specific approaches

**If concerns (yellow):**
- Address specific concerns
- May need brief research (Ref quick check)
- Run vibe-check again with updated plan
- Then proceed to SPEC-AGENT

**If red flags (red):**
- Reconsider entire approach
- Discuss alternatives with user if needed
- Revise plan significantly
- Run vibe-check again before SPEC-AGENT

### 6. Log Pattern (Optional)

If vibe-check revealed valuable insight, log it:

```javascript
vibe_learn({
  type: "success",
  category: "Planning",
  mistake: "Vibe-check caught architectural flaw early: WebSocket won't work with serverless functions",
  solution: "Switched to Server-Sent Events (SSE) which is serverless-compatible"
})
```

## Integration with Workflow

### Typical Flow:

```
User: "Add real-time score updates"
  ↓
Orchestrator creates Linear issue
  ↓
vibe-check-planning skill AUTO-INVOKED
  ├─ Extracts: goal, plan, uncertainties
  ├─ Runs vibe_check(phase: "planning")
  ├─ Interprets feedback
  └─ Updates Linear with results
  ↓
If validated:
  ├─ linear-handoff skill creates [SPEC] sub-issue
  └─ Launch SPEC-AGENT with vibe-check context

If concerns:
  ├─ Address concerns
  └─ Re-run vibe-check or proceed with notes

If red flags:
  ├─ Revise approach
  └─ Discuss with user if needed
```

## Example Scenarios

### Scenario 1: Approach Validated

```
User: "Add export to PDF feature"

Orchestrator proposes:
- Use puppeteer to render page as PDF
- Server-side generation
- Store in Vercel Blob, return download link

vibe_check() returns:
✓ Puppeteer is good choice for PDF generation
✓ Server-side approach prevents client memory issues
⚠️ Consider PDF size limits on Vercel Blob
→ Validated, proceed with note about size limits

Update Linear: "[PLANNING] ✓ Approach validated. Watch PDF file sizes."
Proceed to SPEC-AGENT
```

### Scenario 2: Concern Raised

```
User: "Add user authentication"

Orchestrator proposes:
- Roll our own JWT auth
- Store passwords with bcrypt
- Session management in Redis

vibe_check() returns:
❌ Don't roll own auth - security risk
💡 Use NextAuth.js or Clerk for production
💡 Consider OAuth providers (Google, GitHub)
→ Red flag, revise approach

Update Linear: "[PLANNING] ⚠️ Vibe-check recommends NextAuth.js over custom auth"
Revise plan to use NextAuth.js
Re-run vibe_check()
Then proceed to SPEC-AGENT
```

### Scenario 3: Missing Consideration

```
User: "Add WebSocket chat"

Orchestrator proposes:
- Native WebSocket connection
- Server maintains connections
- Client-side reconnection logic

vibe_check() returns:
⚠️ Serverless functions (Vercel) don't support persistent WebSocket
💡 Consider: Vercel Edge Functions, separate WebSocket server, or SSE
→ Major technical constraint missed

Update Linear: "[PLANNING] ⚠️ WebSocket incompatible with serverless. Researching alternatives."
Revise to: Server-Sent Events (SSE) or Edge Functions
Re-run vibe_check()
Proceed to SPEC-AGENT with updated approach
```

## Important Notes

**Always run BEFORE research:**
- Don't waste Ref/Exasearch tokens on wrong approach
- Vibe-check is cheap, research is expensive
- Validate direction first, then gather details

**Be specific in uncertainties:**
- List actual technical questions
- Not vague "is this a good idea?"
- Specific: "Should we use X or Y for Z requirement?"

**Include enough context:**
- Current tech stack
- Existing patterns in codebase
- Constraints (serverless, budget, timeline)

**Don't skip on "simple" features:**
- Even simple features can have non-obvious issues
- Quick vibe-check prevents rework
- Takes < 30 seconds, saves hours

## Troubleshooting

**Vibe-check says "more context needed":**
- Add more task context
- Be more specific in plan
- Include relevant constraints

**Vibe-check too generic:**
- Make uncertainties more specific
- Provide concrete technical choices
- Include real alternatives you're considering

**Vibe-check conflicts with user request:**
- Present findings to user
- Explain trade-offs
- User makes final call
- Document decision in Linear
