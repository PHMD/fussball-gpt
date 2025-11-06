# CLAUDE.md - Staging Worktree (Vibe Zone)

**Role**: Rapid prototyping and UI/UX iteration

## Project Management

**Issue Tracking**: Optional - use Linear for bigger changes, skip for minor tweaks

**Commit Format** (flexible):
```bash
# For tracked work
git commit -m "feat: Feature name - PHM-XX"

# For quick iterations (no Linear tracking)
git commit -m "tweak: Make button bigger"
git commit -m "polish: Smooth sidebar animation"
```

## Communication Style

Be direct and factual. No validation phrases - just answer with technical diagnosis and optimization.

## 🚨 PRODUCTION DEPLOYMENT SAFEGUARD

**CRITICAL: Never merge staging → main without explicit user approval**

Before merging to main, you MUST ask:

```
⚠️ PRODUCTION DEPLOYMENT CONFIRMATION REQUIRED

Ready to merge staging → main (production deployment).
This is IRREVERSIBLE.

Please respond:
✅ "Yes, deploy to production" - to proceed
❌ "No" - to cancel
```

**Approved phrases only:**
- "Deploy to production"
- "Merge to main"
- "Yes, deploy to production"

**Never act on:**
- ❌ "How does it work?" (question)
- ❌ "Looks good" (vague)
- ❌ "Is this ready?" (question)

**If unclear, ASK. Never assume.**

## MCP Stack (Dev Mode)

**Current MCPs:**
- Ref (documentation - 50% token savings vs Context7)
- Exasearch (code examples from GitHub)
- GitHub (commit and push)
- Semgrep (security scanning)
- Vercel (preview deployments)
- browser-use (quick browser testing)

**Optional MCPs** (add as needed):
- Playwright (if writing tests)
- Linear (if work grows beyond quick tweaks)

## Core Philosophy

**This is your creative space:**
- Fast iterations without overhead
- Experiment freely
- UI/UX polish
- Quick fixes and tweaks
- No mandatory Linear tracking

**When to escalate to feature worktree:**
- Change grows beyond "quick tweak"
- Needs proper testing
- Requires spec or architectural decision
- Should be tracked in Linear

## Typical Workflows

### 1. Quick UI Tweak

```
User: "Make the button 20% bigger and add hover animation"

Agent:
- Updates CSS directly
- Tests in browser-use
- Commits with descriptive message
- No Linear ticket needed
```

### 2. Exploratory Prototyping

```
User: "Try a card-based layout for the news feed"

Agent:
- Checks Ref for component patterns
- Searches Exasearch for examples
- Implements prototype
- Commits as "experiment: Card layout"
```

### 3. Escalation to Feature

```
User: "This prototype is great, let's track it properly"

Agent:
- Creates Linear issue
- Invokes worktree-setup skill
- Creates feature worktree
- Commits current work to staging
- Reports: "Feature worktree created for PHM-XX"
```

## Available Skills

- `vibe-check-planning` - Quick validation before implementation
- `worktree-setup` - Escalate to feature worktree if needed
- `pieces-logger` - Log learnings (optional)

## Agents

**Available** (but lightweight invocation):
- `dev-agent` - For implementation help
- `qa-agent` - For quick testing (optional)

**Not available**:
- `spec-agent` - Not needed for quick iterations

## Merge to Main

**Frequent merges encouraged:**

```bash
# Merge staging changes to main frequently
git checkout main
git merge staging
git push origin main
```

**Or create PR for review:**

```bash
git push origin staging
gh pr create --base main --head staging
```

## What NOT to Do

**Avoid:**
1. Large architectural changes (use feature worktree)
2. Breaking changes without testing
3. Skipping security scans on new code
4. Letting staging diverge too far from main

**Encouraged:**
1. Rapid iteration
2. UI/UX experimentation
3. Quick bug fixes
4. Visual polish

## Escalation Decision Tree

```
Is this change:
├─ < 50 lines, UI/UX only? → Stay in staging
├─ Needs testing? → Consider feature worktree
├─ Architectural change? → Feature worktree required
└─ Grew beyond "quick tweak"? → Escalate to feature
```

## Token Budget

**Target**: ~8K tokens for this CLAUDE.md
**Why**: Lean dev stack, no CI/CD overhead

## Security Note

**Always scan before merging to main:**
```bash
semgrep scan --config auto .
```

Even quick tweaks can introduce vulnerabilities.

## Related Templates

- `claude-main.md` - For merging your staging work
- `claude-feature.md` - For escalating to tracked feature work
