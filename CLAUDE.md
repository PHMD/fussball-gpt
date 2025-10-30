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
├─ Sprint Planning → Linear (organize issues, cycles) or GitHub Issues (solo)
└─ Task Tracking → GitHub Issues (current workflow)

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

**GitHub Issues and Regular Commits**

To maintain better traceability and project management:

1. **Create or update GitHub issues** as we work on tasks
   - Document what you're working on
   - Link commits to issues with keywords (e.g., "Fixes #123", "Closes #45")
   - Track progress and decisions

2. **Commit regularly** for better git history
   - Commit after completing logical units of work
   - Use descriptive commit messages following project conventions
   - Include issue references in commit messages
   - Push frequently to keep remote in sync

3. **Issue workflow:**
   - Start work → Create/update issue with task details
   - During work → Reference issue in commits
   - Complete work → Close issue with final commit
   - Document decisions and blockers in issue comments

**Example commit message:**
```bash
git commit -m "feat: Add suggestion component - Fixes #42

- Created interactive suggestion buttons
- Integrated with chat interface
- Added German-language prompts

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


## 🎯 Vibe-Coding Workflows

### New Feature Development (Full Stack)

```
1. GitHub → Create issue with feature description
2. Vibe-Check → Validate technical approach
   - Use phase="planning"
   - Include: goal, plan, uncertainties
   - Adapt based on feedback
3. Ref → Get official library docs for implementation
   - Vercel AI SDK patterns
   - Next.js App Router best practices
   - shadcn/ui component APIs
4. Exasearch → Find real-world code examples
   - "Next.js streaming chat with Vercel AI SDK"
   - "shadcn/ui chat components TypeScript"
5. Code → Implement with type safety
   - Follow existing patterns in codebase
   - Use Pydantic models for data validation
   - Implement caching where appropriate
6. Semgrep → Security scan
   - Run on ALL changed files
   - Fix vulnerabilities before commit
7. Playwright → Write E2E tests
   - Test user flows end-to-end
   - Cover both German and English paths
   - Validate accessibility
8. GitHub → Create branch, commit with issue reference
   - Branch: feature/issue-number-description
   - Commit: "feat: Description - Fixes #N"
   - Push frequently
9. Vibe-Learn → Document patterns/mistakes
   - Log what worked/didn't work
   - Track preference decisions
10. GitHub → Create PR, link issue, request review
11. Pieces → Store decisions and context (optional)
```

### Bug Fix Workflow

```
1. GitHub → Triage bug, create/update issue
   - Document reproduction steps
   - Include error logs
   - Assign priority label
2. Pieces → Retrieve context (if using)
   - When was feature last working?
   - What changed since then?
3. browser-use → Quick debugging (if browser-related)
   - Inspect elements
   - Test interactions
   - Validate error states
4. Ref → Check API documentation
   - Verify correct API usage
   - Check for breaking changes
5. Fix → Update code
   - Minimal changeset
   - Add defensive checks
6. Semgrep → Verify no new vulnerabilities
7. Playwright → Add regression test
   - Prevent bug from reoccurring
   - Cover edge cases
8. GitHub → Create PR with "Fixes #N"
   - Link to original issue
   - Document root cause
   - Include test coverage
9. Vibe-Learn → Log mistake pattern
   - What caused the bug?
   - How to prevent similar bugs?
```

### Security Audit Workflow

```
1. Semgrep → Run comprehensive scan
   - All Python files (data_aggregator.py, models.py, etc.)
   - All TypeScript files (lib/, app/, components/)
   - Focus on: auth, data validation, API calls
2. Review findings → Categorize by severity
   - Critical: Fix immediately
   - High: Fix before deploy
   - Medium/Low: Schedule for fix
3. Ref → Research secure patterns
   - OWASP best practices
   - Framework-specific security guides
4. Fix → Implement secure alternatives
5. Semgrep → Re-scan to verify fixes
6. GitHub → Create PR with security fixes
   - Use "security:" prefix in commit
   - Reference CVE/CWE numbers
7. Vibe-Learn → Document security patterns
```

### Test Writing Workflow (E2E)

```
1. Playwright → Generate test code from user interactions
   - Use browser_generate_playwright_test
   - Document expected behavior
2. Implement tests → Follow existing patterns
   - See tests/e2e/bilingual-support.spec.ts
   - Use proper wait strategies
   - Handle async state updates
3. Run tests → Validate all scenarios
   - Both language paths (German/English)
   - All detail levels (Quick/Balanced/Detailed)
   - Error states and edge cases
4. browser-use → Quick validation (if needed)
   - Debug flaky tests
   - Verify selector stability
5. GitHub → Commit test suite
   - "test: Add E2E coverage for feature X"
6. Pieces → Document test coverage decisions (optional)
```

### Frontend Component Development

```
1. GitHub → Create issue for component
2. Vibe-Check → Validate component approach
   - Does this need to be a new component?
   - Can we use existing shadcn/ui component?
   - Accessibility considerations?
3. Ref → Research shadcn/ui patterns
   - Find similar components
   - Check accessibility patterns
   - Review TypeScript patterns
4. Exasearch → Find real-world examples
   - "shadcn chat interface streaming"
   - "Next.js 14 server components with streaming"
5. Code → Implement component
   - TypeScript strict mode
   - Tailwind for styling
   - Accessibility (ARIA labels, keyboard nav)
6. Playwright → Write component tests
   - User interaction flows
   - Responsive behavior
   - Accessibility checks
7. Semgrep → Security scan (XSS, injection)
8. GitHub → PR with component + tests
```

### Code Audit Workflow (Current Task)

```
1. Vibe-Check → Validate audit approach
   - What are audit goals?
   - Which files to prioritize?
   - Security vs. quality vs. performance?
2. Semgrep → Security scan across codebase
   - Python backend files
   - TypeScript frontend files
   - Configuration files
3. Review architecture → Assess patterns
   - Data flow correctness
   - Error handling completeness
   - Caching strategy effectiveness
   - Type safety coverage
4. Ref + Exasearch → Verify against best practices
   - Vercel AI SDK patterns
   - Next.js App Router patterns
   - Pydantic validation patterns
   - Real-world production examples
5. Document findings → Create issues
   - Security vulnerabilities (immediate)
   - Technical debt (scheduled)
   - Optimization opportunities (backlog)
6. Vibe-Learn → Log audit insights
7. GitHub → Create issues for follow-up work
```

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
