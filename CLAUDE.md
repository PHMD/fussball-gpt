# CLAUDE.md - Feature Worktree (Dev Mode)

**Role**: Implementation and development
**Branch**: `feature/phm-prompt-optimization`
**Linear Issue**: PHM-216

## Project Management

**Issue Tracking**: Linear (required for feature work)
- Always include Linear ID (PHM-XX) in commits
- Update Linear issue status as work progresses

**Commit Format:**
```bash
git commit -m "type: description - PHM-216

- Bullet points
- What changed

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Communication Style

Be direct and factual. No validation phrases - just answer with technical diagnosis and optimization.

## Research Tools (Ref & Exa)

**IMPORTANT**: Always use these tools before implementing unfamiliar patterns or APIs.

### Ref MCP - Documentation Search

**What it does**: Searches official documentation for libraries, frameworks, and APIs.

**When to use:**
- Looking up API syntax or function signatures
- Finding official best practices
- Checking library version compatibility
- Understanding configuration options

**Tools:**
```
mcp__Ref__ref_search_documentation  - Search for docs
mcp__Ref__ref_read_url              - Read specific doc URL
```

**Examples:**
```
# Search for Claude prompt engineering docs
ref_search_documentation("Anthropic Claude system prompt best practices")

# Read a specific documentation page
ref_read_url("https://docs.anthropic.com/en/docs/...")
```

**Why we use it:**
- 50% token savings vs Context7
- Returns official, authoritative sources
- Better for API reference and configuration

---

### Exa MCP - Code Examples & Web Search

**What it does**: Searches GitHub repos and the web for real-world code examples.

**When to use:**
- Finding implementation examples
- Seeing how others solved similar problems
- Discovering patterns and approaches
- Getting context for unfamiliar codebases

**Tools:**
```
mcp__exa__get_code_context_exa  - Search code examples (PRIMARY)
mcp__exa__web_search_exa        - General web search
```

**Examples:**
```
# Find code examples for prompt engineering
get_code_context_exa("TypeScript XML structured prompt template LLM")

# Search for specific implementations
get_code_context_exa("Vercel AI SDK system prompt streaming")
```

**Why we use it:**
- Real code from real projects
- Shows practical implementations, not just theory
- Great for discovering patterns you didn't know existed

---

### Research Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                   BEFORE IMPLEMENTING                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Check Ref for official docs                              │
│     └─ "What does the API say?"                              │
│                                                              │
│  2. Check Exa for code examples                              │
│     └─ "How do others implement this?"                       │
│                                                              │
│  3. Combine learnings                                        │
│     └─ Official best practice + real-world pattern           │
│                                                              │
│  4. Implement with confidence                                │
│     └─ Cite sources in code comments if helpful              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Example for this task:**
```
# Before optimizing prompts:
1. ref_search_documentation("Anthropic Claude 4 prompt engineering")
2. get_code_context_exa("XML structured prompt template LLM system")
3. Apply learnings to lib/prompts.ts
```

## MCP Stack (Dev Mode)

**Current MCPs:**
- **Ref** - Documentation search (official docs)
- **Exa** - Code examples from GitHub
- **GitHub** - Commit and push
- **Semgrep** - Security scanning
- **Linear** - Issue tracking
- **browser-use** - Quick browser testing

**Not included** (keep context lean):
- Vercel (deployment is orchestrator's job)
- Playwright (use for QA phase only)

## Development Workflow

### 1. Start Work

```bash
# Ensure you're on the right branch
git status

# Read the Linear issue for full context
# PHM-216 has detailed implementation tasks
```

### 2. Research Phase

```bash
# Use Ref for official docs
ref_search_documentation("your topic")

# Use Exa for code examples
get_code_context_exa("your implementation pattern")
```

### 3. Implementation

- Make changes incrementally
- Run `npm run build` frequently
- Test with `npm test`

### 4. Commit & Push

```bash
git add .
git commit -m "feat: description - PHM-216"
git push origin feature/phm-prompt-optimization
```

### 5. Ready for Review

```bash
# Run security scan
semgrep scan --config auto .

# Create PR (or notify orchestrator)
gh pr create --base main --head feature/phm-prompt-optimization
```

## What NOT to Do

**Never:**
1. Merge directly to main (orchestrator's job)
2. Skip security scans
3. Implement without checking docs first
4. Ignore Linear issue requirements

**Always:**
1. Use Ref/Exa for research
2. Update Linear issue with progress
3. Run build and tests before committing
4. Keep commits atomic and well-described

## Escalation

**If blocked:**
1. Add comment to Linear issue
2. Ask user for clarification
3. Consider if task scope has changed

**If task grows:**
1. Update Linear issue description
2. Break into sub-issues if needed
3. Communicate scope change to user

## Token Budget

**Target**: ~6K tokens for this CLAUDE.md
**Why**: Include research tools documentation for effective development
