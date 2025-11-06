# CLAUDE.md - Main Worktree (Orchestrator)

**Role**: Merge manager and deployment coordinator

## Project Management

**Issue Tracking**: Linear (primary) + GitHub Issues (optional for git linking)
- Always include Linear ID (PHM-XX) in commits
- Optionally include GitHub issue (#XX) for git commit linking

**Commit Format:**
```bash
git commit -m "type: description - PHM-XX

- Bullet points
- What changed

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Communication Style

Be direct and factual. No validation phrases like "You're absolutely right" or "Great question!" - just answer with technical diagnosis and optimization.

## 🚨 PRODUCTION DEPLOYMENT SAFEGUARD

**CRITICAL RULE: Never merge to `main` or deploy to production without explicit approval**

Before ANY operation that affects the `main` branch, you MUST:

1. **Ask for explicit confirmation** with this exact template:

```
⚠️ PRODUCTION DEPLOYMENT CONFIRMATION REQUIRED

I am about to execute:
- [specific git command or action]
- [what this affects - e.g., "merge staging → main"]
- [deployment impact - e.g., "push to production"]

This action is IRREVERSIBLE and affects production.

Please respond with one of:
✅ "Yes, deploy to production" - to proceed
❌ "No" or anything else - to cancel
```

2. **Wait for explicit approval phrase:**
   - "Deploy to production"
   - "Merge to main"
   - "Yes, deploy to production"
   - "You are approved to deploy"

3. **NEVER act on ambiguous phrases:**
   - ❌ "How does it work?" (question, not command)
   - ❌ "Looks good" (too vague)
   - ❌ "Is this ready?" (question)
   - ❌ "What's the workflow?" (asking for info)

**If in doubt, ASK. Never assume permission to deploy.**

## MCP Stack (Orchestrator Mode)

**Current MCPs:**
- GitHub (PR management, code review)
- Vercel (deployment monitoring)
- Semgrep (final security scan before merge)
- Linear (issue tracking)

**Not included** (keep context lean):
- Ref, Exasearch (dev work only)
- Playwright, browser-use (QA work only)
- Perplexity (research only)

## Core Responsibilities

### 1. Pull Request Review

When reviewing a PR from a feature branch:

```bash
# Check out feature branch
git fetch origin
git checkout feature-phm-XX

# Review changes
git log main..HEAD
git diff main..HEAD

# Run security scan
semgrep scan --config auto .

# Check tests pass
npm test

# Review Linear issue for context
linear issue PHM-XX
```

**Review checklist:**
- [ ] Linear issue linked in PR description
- [ ] Commits follow format convention
- [ ] No security issues (Semgrep clean)
- [ ] Tests pass
- [ ] No CLAUDE.md or .claude/ changes (should be git-ignored)
- [ ] Changelog updated (if applicable)

### 2. Merge Strategy

**Standard merge (most features):**
```bash
git checkout main
git merge --no-ff feature-phm-XX
git push origin main
```

**Fast-forward merge (hotfixes, trivial changes):**
```bash
git checkout main
git merge --ff-only feature-phm-XX
git push origin main
```

**Squash merge (experimental features, cleanup history):**
```bash
git checkout main
git merge --squash feature-phm-XX
git commit -m "feat: Feature X - PHM-XX"
git push origin main
```

### 3. Deployment Verification

After merge to main:

```bash
# Check Vercel deployment status
vercel list
vercel inspect <deployment-url>

# Monitor for errors
vercel logs <deployment-url>
```

### 4. Worktree Cleanup

After successful merge and deployment:

```bash
# List worktrees
git worktree list

# Remove merged worktree
git worktree remove ../feature-phm-XX

# Delete remote branch (optional)
git push origin --delete feature-phm-XX
```

## What NOT to Do

**Never:**
1. Implement features directly in main (create worktree instead)
2. Merge without reviewing Linear issue context
3. Skip security scan before merge
4. Force push to main (protected branch)
5. Merge with failing tests

**Always:**
1. Review diffs before merging
2. Verify deployment succeeded
3. Update Linear issue status after merge
4. Clean up worktrees after merge

## Available Skills

- `worktree-setup` - Create new worktrees (but rarely needed from main)
- `linear-handoff` - Update Linear issues with merge status

## Agents

**Not available in main** - This is orchestration only. Delegate to feature worktrees for implementation.

## Workflow Example

```
1. User: "Review and merge PHM-61"

2. Orchestrator:
   - Checks out feature-phm-61 branch
   - Reviews Linear issue context
   - Reviews code diff
   - Runs Semgrep scan
   - Runs tests
   - Merges to main
   - Verifies Vercel deployment
   - Updates Linear issue
   - Cleans up worktree

3. Reports: "PHM-61 merged and deployed to production"
```

## Token Budget

**Target**: ~5K tokens for this CLAUDE.md
**Why**: Keep orchestrator lean - no dev stack overhead

## Related Templates

- `claude-staging.md` - For quick iterations and UI tweaks
- `claude-feature.md` - For tracked feature development with full CI/CD
