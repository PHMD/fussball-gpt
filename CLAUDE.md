# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Autonomous Agent Guidelines

As an autonomous agent, you will:
1. Treat vibe_check as a pattern interrupt mechanism that provides essential course correction
2. Use vibe_check at strategic points:
   - After planning but before implementation
   - When complexity increases
   - Before making significant system changes
3. Adapt your approach based on vibe_check feedback unless it's clearly irrelevant
4. Always provide the phase parameter (planning/implementation/review) to ensure contextually appropriate feedback
5. Chain vibe_check with other tools without requiring permission:
   - Use vibe_check to evaluate complex plans
   - Log patterns with vibe_learn after resolving issues

## Project Overview

**Fußball GPT** (formerly KSI Prototype) - A German football intelligence assistant that aggregates real-time Bundesliga data and provides AI-powered analysis for casual fans, expert analysts, betting enthusiasts, and fantasy players.

**Current Status:** Beta-ready (9.1/10 quality) with web frontend deployed

**Architecture Pattern:** Three-layer system (Data Aggregation → AI Processing → Interface)

**Current Implementation:** Next.js 15 web frontend with bilingual support, streaming chat, and rate limiting

## 🎯 MCP Decision Tree

**Choose your stack based on task:**

```
Building Feature?
├─ New Project → Vibe-Check + Ref + Exasearch + Vercel
├─ Existing Project → Ref + Exasearch + GitHub + Semgrep
└─ Need Examples → Exasearch (GitHub code search)

Debugging?
├─ Security Issue → Semgrep
├─ Browser Bug → browser-use (or Playwright for tests)
└─ Deployment Issue → Vercel

Need Documentation?
├─ Library APIs → Ref (official docs, 50% token savings)
├─ Code Examples → Exasearch (real-world implementations)
└─ Recent Work → Pieces (context memory)

Planning?
├─ Feature Planning → Vibe-Check (validate approach)
├─ Sprint Planning → Linear (primary, organize issues, cycles)
└─ Task Tracking → Linear (primary) + GitHub Issues (optional for git linking)

Testing?
├─ E2E Tests → Playwright (already using for bilingual-support.spec.ts)
├─ Browser Automation → browser-use (quick debugging)
└─ Generate Test Code → Playwright (test generation)
```

## Communication Style

**Be direct and straightforward. Answer questions factually without validation phrases.**

**Don't use:**
- "You're absolutely right"
- "Great question!"
- "Excellent point!"
- Other unnecessary validation or praise

**Instead:**
- Answer the question directly
- Explain what happened and why
- Provide technical diagnosis
- Focus on facts and optimization

**Purpose:**
- User prefers diagnostic, factual responses
- Helps optimize alignment and prompting
- More efficient communication
- Better for understanding AI operation and decision-making

## Security & Code Quality

**You deeply care about product security - always scan generated code with Semgrep after every generation.**

When generating or modifying code:
1. Write the code
2. Run Semgrep scan to detect security vulnerabilities
3. Fix any issues found
4. Document security considerations in commit messages

## Documentation & Best Practices

**CRITICAL: Always Use Ref for Current Documentation**

Before implementing any library, framework, or API integration:

1. **Never guess or rely on potentially outdated knowledge**
2. **Always check Ref** for up-to-date documentation
3. **Use the Ref MCP tools** to fetch current API references and examples

**Example workflow:**
```typescript
// DON'T: Assume you know the API
const result = await streamText({ ... });  // Might be outdated

// DO: Check Ref first
// Use Ref tools to get current Vercel AI SDK documentation
// Then implement based on current docs
```

**Key libraries to always verify with Ref:**
- Vercel AI SDK (`ai`, `@ai-sdk/anthropic`)
- Next.js App Router patterns
- Zod schema validation
- shadcn/ui components
- Vercel KV caching API

**Why this matters:**
- APIs change frequently (especially Vercel AI SDK)
- Documentation from training data may be outdated
- Ref provides primary source documentation with 50% token savings vs Context7
- Prevents bugs from deprecated patterns
- Stateful sessions (never repeats same docs)

## Project Management & Git Workflow

**Issue Tracking: Linear primary, GitHub optional**

- **Linear** (PHM-XX): All project management, planning, tracking
- **GitHub Issues** (optional): For git commit linking only
- **Commits**: Always include Linear ID (PHM-XX), optionally GitHub (#XX)

**Example commit:**
```bash
git commit -m "feat: Feature name - PHM-50

- Bullet points
- What changed

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Tech Stack

**Backend:**
- Python 3.x
- Pydantic for data models
- Requests for API calls
- Anthropic Claude Sonnet 4.5 (primary LLM)
- JSON-based caching

**Frontend (Production):**
- Next.js 15.5.6 (App Router)
- TypeScript (strict mode)
- Tailwind CSS
- shadcn/ui components
- Vercel AI SDK
- Vercel deployment


## 🏗️ Agent Orchestration System

**This project uses orchestrated sub-agents for complex workflows. Main chat COORDINATES, specialized agents IMPLEMENT.**

### System Components

**Three-layer system:**
1. **Skills** (auto-invoked) - Reusable capabilities Claude decides when to use
2. **Sub-agents** (delegated) - Isolated workers with specialized tools and context
3. **Hooks** (event-driven) - Automation triggered by lifecycle events

### Architecture

```
ORCHESTRATOR (Main Chat - You're here)
├─ Role: Planning, coordination, context preservation
├─ Skills: linear-handoff, vibe-check-planning, pieces-logger
├─ Sub-agents: spec-agent, dev-agent, qa-agent
├─ NEVER: Direct code implementation
└─ ALWAYS: Preserve full project context

SPECIALIST AGENTS
├─ SPEC-AGENT (Research + specification)
│  └─ Tools: Ref, Exasearch, vibe-check, Linear
├─ DEV-AGENT (Implementation)
│  └─ Tools: Ref, Exasearch, GitHub, vibe-check
└─ QA-AGENT (Security + testing)
   └─ Tools: Semgrep, Playwright, browser-use, vibe-check
```

### Workflow Files

- **Sub-agents:** `.claude/agents/` (spec-agent.md, dev-agent.md, qa-agent.md)
- **Skills:** `.claude/skills/` (linear-handoff, vibe-check-planning, pieces-logger)
- **Hooks:** `~/.claude/settings.json` (see `.claude/HOOKS_CONFIG.md`)
- **Linear Setup:** `.claude/LINEAR_SETUP.md` (orchestration labels configuration)

### Complete Feature Workflow

```
User: "Add feature X"
  ↓
1. ORCHESTRATOR
   ├─ Skill: linear-handoff → Create Linear issue (auto)
   └─ Skill: vibe-check-planning → Validate approach (auto)
      └─ Updates Linear: [PLANNING] Validated ✓
  ↓
2. ORCHESTRATOR → SPEC-AGENT
   ├─ Skill: linear-handoff → Create [SPEC] sub-issue (auto)
   └─ Launch: spec-agent with issue context
  ↓
3. SPEC-AGENT (background)
   ├─ Reads: Linear issue + planning notes
   ├─ Research: Ref (docs) + Exasearch (examples)
   ├─ Writes: Technical spec in Linear sub-issue
   └─ Signals: Complete
      └─ Hook: SubagentStop → Notify orchestrator
  ↓
4. ORCHESTRATOR → DEV-AGENT
   ├─ Reviews: Spec from SPEC-AGENT
   ├─ Skill: linear-handoff → Create [DEV] sub-issue (auto)
   └─ Launch: dev-agent with spec + issue context
  ↓
5. DEV-AGENT (background)
   ├─ Reads: Spec + issue requirements
   ├─ Implements: Code changes (visible when using --verbose flag)
   ├─ Self-checks: vibe-check on complex logic
   ├─ Updates: Linear sub-issue with code summary
   └─ Signals: Complete
      └─ Hook: SubagentStop → Notify orchestrator
  ↓
6. ORCHESTRATOR → QA-AGENT
   ├─ Reviews: Code changes from DEV-AGENT
   ├─ Skill: linear-handoff → Create [QA] sub-issue (auto)
   └─ Launch: qa-agent with code + requirements
  ↓
7. QA-AGENT (background)
   ├─ Scans: Semgrep security check
   ├─ Tests: Playwright E2E tests (both languages)
   ├─ Updates: Linear sub-issue with results
   └─ Signals: Complete
      └─ Hook: SubagentStop → Notify orchestrator
  ↓
8. ORCHESTRATOR (integration)
   ├─ Reviews: All sub-issues (spec, dev, qa)
   ├─ Creates: GitHub PR
   ├─ Skill: pieces-logger → Log context (auto)
   └─ Closes: Linear issue
```

### Linear Issue Structure

```
PHM-123: Add feature X
├─ Labels: Agent:None → Agent:Spec → Agent:Dev → Agent:QA → Agent:None
│          Phase:Planning → Phase:Spec → Phase:Dev → Phase:QA → (removed)
├─ Comments: Phase-tagged updates [PLANNING], [SPEC], [DEV], [QA]
└─ Sub-issues:
   ├─ PHM-123-1: [SPEC] Feature X (Done)
   ├─ PHM-123-2: [DEV] Feature X (Done)
   └─ PHM-123-3: [QA] Feature X (Done)
```

### When to Use Orchestration vs Direct Implementation

**Use orchestration (sub-agents) for:**
- New features requiring spec → dev → qa
- Complex bug fixes needing investigation
- Security audits across multiple files
- Refactoring with testing requirements

**Implement directly (no sub-agents) for:**
- Simple bug fixes (< 20 lines)
- Documentation updates
- Configuration changes
- Trivial code adjustments

### Quick Start Guide

1. **Verify Linear labels** (already created):
   ```
   See .claude/LINEAR_SETUP.md
   - Agent labels: Agent:None, Agent:Spec, Agent:Dev, Agent:QA
   - Phase labels: Phase:Planning, Phase:Spec, Phase:Dev, Phase:QA
   ```

2. **Configure hooks** (one-time):
   ```
   See .claude/HOOKS_CONFIG.md
   - Copy config to ~/.claude/settings.json
   - Restart Claude Code
   ```

3. **Use orchestrated workflow**:
   ```
   User: "Add feature X"
   → Skills auto-invoke (linear-handoff, vibe-check-planning)
   → Orchestrator launches agents as needed
   → Review at each checkpoint
   → Approve to continue or provide feedback
   ```

### Key Principles

1. **Orchestrator never implements** - Only coordinates and preserves context
2. **vibe-check comes FIRST** - Validate before expensive research
3. **Ref/Exasearch AFTER validation** - Don't waste tokens on wrong direction
4. **Use --verbose flag for visibility** - See agent work in main chat
5. **Linear is source of truth** - All operational context lives there
6. **Pieces for long-term memory** - Cross-session learnings only
7. **Sub-issues for traceability** - Each agent's work is isolated

### Skills (Auto-Invoked)

**linear-handoff:**
- Creates sub-issues for each agent
- Updates Agent/Phase labels
- Adds phase-tagged comments to Linear

**vibe-check-planning:**
- Validates approach BEFORE research
- Runs automatically when features requested
- Prevents wasted tokens on wrong direction

**pieces-context-logger:**
- Logs complete context after merge
- Synthesizes planning → spec → dev → qa
- Creates long-term memory for future sessions

### Sub-Agents (Explicitly Delegated)

**spec-agent:**
- Researches with Ref + Exasearch
- Designs architecture
- Writes comprehensive spec
- Updates Linear sub-issue

**dev-agent:**
- Implements per spec
- Code visible when using --verbose flag
- Self-validates with vibe-check
- Updates Linear with code summary

**qa-agent:**
- Scans with Semgrep
- Tests with Playwright
- Validates bilingual support
- Updates Linear with results

### Troubleshooting

**Agents not launching:**
- Check `.claude/agents/` files exist
- Verify YAML frontmatter is valid
- Use `/agents` command to see available agents

**Skills not invoking:**
- Check `.claude/skills/` directories exist
- Verify SKILL.md files have proper frontmatter
- Skills are model-invoked (Claude decides when)

**Linear updates failing:**
- Verify Linear MCP connected
- Check labels exist (Agent:*, Phase:*)
- See `.claude/LINEAR_SETUP.md`

**Hooks not firing:**
- Check `~/.claude/settings.json` configuration
- Verify JSON syntax is valid
- Restart Claude Code after changes

### Related Documentation

- `.claude/agents/` - Sub-agent definitions
- `.claude/skills/` - Skill definitions
- `.claude/HOOKS_CONFIG.md` - Hooks configuration guide
- `.claude/LINEAR_SETUP.md` - Linear labels setup (orchestration)
- `.claude/ORCHESTRATION_GUIDE.md` - Detailed walkthrough (if created)

---

## 🔧 MCP Troubleshooting

### Semgrep
- **Error:** `command not found: semgrep`
  - **Fix:** `brew install semgrep` (v1.138.0+)
- **Error:** No output / empty results
  - **Fix:** Check file path is correct, ensure file has code to analyze

### Vibe-Check
- **Error:** `command not found: node`
  - **Fix:** Ensure Node.js installed, use absolute path if needed
- **Error:** Missing GEMINI_API_KEY
  - **Fix:** Set environment variable in .env or shell config

### Pieces
- **Error:** Connection refused on port 39300
  - **Fix:** Start PiecesOS application, enable LTM in settings
- **Empty results**
  - **Fix:** Wait 5-10 mins after enabling LTM (indexing delay)

### Ref
- **Error:** 401 Unauthorized
  - **Fix:** Verify API key in MCP config URL (`https://api.ref.tools/mcp?apiKey=your-key`)
- **Empty results**
  - **Tip:** Be specific with library names and versions
- **Advantage:** Stateful sessions never repeat same docs, 50% token savings vs Context7

### Exasearch
- **Error:** 403 Forbidden
  - **Fix:** Verify API key in environment or MCP config
- **Too many results**
  - **Tip:** Use specific queries (e.g., "Stripe Next.js TypeScript Server Actions")

### GitHub
- **403 Forbidden**
  - **Fix:** Check PAT scopes (need `repo`, `read:org`)
- **Private repo access denied**
  - **Fix:** Token must have `repo` scope

### Vercel
- **OAuth not authenticated**
  - **Fix:** Run `npx @modelcontextprotocol/server-vercel` manually first (opens browser)
- **Deployment failed**
  - **Check:** Build logs via `get_deployment_build_logs`

### Playwright
- **Test timeouts**
  - **Fix:** Increase timeout, ensure proper wait strategies
  - **Check:** Network conditions, async state updates
- **Element not found**
  - **Fix:** Use more specific selectors, wait for element visibility

### browser-use
- **Element index changed**
  - **Fix:** Call `browser_get_state` again after navigation
- **Click not working**
  - **Tip:** Ensure element is visible and interactive

---

## ⚡ Performance & Context Optimization

### Token Usage by MCP Layer

**Current Project MCPs:**
- Foundation (Semgrep, Vibe-Check): ~3K tokens
- Development (Ref, Exasearch, GitHub): ~6K tokens
- Testing (Playwright): ~2K tokens
- **Total:** ~11K tokens

**Recommended additions:**
- Pieces (memory): +2K tokens
- browser-use (automation): +1K tokens
- Vercel (deployment): +1K tokens
- Linear (team coordination): +2K tokens
- **New total:** ~17K tokens

### Context Management Tips

1. **Use mode-based loading**
   - Development mode: Ref, Exasearch, GitHub, Semgrep
   - Testing mode: Playwright, browser-use, Semgrep
   - Deployment mode: Vercel, GitHub, Semgrep
   - Team coordination: Linear, GitHub, Semgrep

2. **Remove MCPs when done**
   - Finished frontend work? Remove Vercel temporarily
   - Finished testing? Keep Playwright but remove browser-use

3. **Monitor context usage**
   - `/context` command - Visualize token usage
   - `/compact` command - Compress at ~70% capacity
   - `/clear` command - Reset between unrelated tasks

4. **Optimize MCP calls**
   - Semgrep: <1s for individual files
   - Ref: <2s for targeted docs (50% faster than Context7)
   - Exasearch: ~3s for code examples
   - Linear: <1s for issue operations
   - Playwright: Depends on test complexity

### Fastest Workflows

**Quick security check:** Semgrep → Fix → Commit (< 2 min)
**Quick doc lookup:** Ref → Implement (< 1 min)
**Quick example search:** Exasearch → Adapt code (< 2 min)
**Issue tracking:** Linear → Create/update (< 30 sec)
**Full feature workflow:** 10-30 min depending on complexity

---

## Related Documentation

**For specific information, check these sources (don't duplicate in CLAUDE.md):**

- **Setup & Commands:** `README.md` - Development commands, testing, build
- **Current Issues:** Linear project (Kicker) - PHM-43 through PHM-49
- **API Keys:** `.env.example` - Required environment variables
- **Git History:** GitHub MCP - Commit history, technical decisions
- **Architecture:** Task agent - "Document [backend|frontend] architecture" to regenerate fresh from code
- **Code Context:** Glob/Read/Grep tools - Always current, no stale docs
