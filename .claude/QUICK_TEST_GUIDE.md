# Quick Test Guide: Orchestration System

**Time:** 30-45 minutes | **Difficulty:** Intermediate

## Before You Start

✅ Setup checklist:
- [x] Linear labels: `Agent:*`, `Phase:*` (already created)
- [ ] Hooks in `~/.claude/settings.json`
- [ ] Claude Code restarted
- [ ] All MCPs loaded (Linear, Ref, Exasearch, GitHub, Semgrep, Playwright, vibe-check, Pieces)

## The Test: Version Footer Component

**What:** Add footer with app version (from package.json) on all pages, bilingual support

**Why:** Tests entire workflow (spec → dev → qa) with all skills and agents

## Test Flow (6 Steps)

### 1. Start Fresh Session
**Do:** Open project, new chat
**Watch for:** `🎯 Orchestrator ready | Sub-agents: spec, dev, qa...`

### 2. Submit Feature Request
**Paste exactly:**
```
Add a footer component that displays the app version from package.json.
The footer should:
- Appear on all pages at the bottom
- Show "Version X.X.X" in German as "Version X.X.X"
- Show "Version X.X.X" in English as "Version X.X.X"
- Use shadcn/ui styling to match existing design
- Be a reusable component

This is a test of the orchestration system. Use the full workflow with sub-agents.
```

**Watch for:**
- ✅ linear-handoff skill creates issue (PHM-XXX)
- ✅ vibe-check-planning skill validates approach
- ✅ Linear updated with `[PLANNING]` comment

### 3. SPEC-AGENT Phase
**Do:** Approve proceeding to SPEC-AGENT
**Watch for:**
- ✅ Sub-issue created: `PHM-XXX-1: [SPEC]`
- ✅ SPEC-AGENT researches (Ref + Exasearch)
- ✅ Spec posted to Linear sub-issue
- ✅ Hook: `✅ SPEC-AGENT complete. Review spec...`

### 4. DEV-AGENT Phase (Verbose)
**Do:** Approve proceeding to DEV-AGENT
**Watch for:**
- ✅ Sub-issue created: `PHM-XXX-2: [DEV]`
- ✅ **Code visible in chat** (verbose mode)
- ✅ Files created: `components/Footer.tsx`, modified: `app/layout.tsx`
- ✅ Branch created: `feature/phm-XXX-*`
- ✅ Hook: `✅ DEV-AGENT complete. Code changes visible...`

### 5. QA-AGENT Phase
**Do:** Approve proceeding to QA-AGENT
**Watch for:**
- ✅ Sub-issue created: `PHM-XXX-3: [QA]`
- ✅ Semgrep scan runs
- ✅ E2E tests written: `tests/e2e/footer-version.spec.ts`
- ✅ Tests pass (both languages)
- ✅ Hook: `✅ QA-AGENT complete. Review security...`

### 6. Integration
**Do:** Approve creating PR
**Watch for:**
- ✅ GitHub PR created
- ✅ Linear issue closed (`Phase: Done`)
- ✅ All sub-issues closed
- ✅ (Optional) Pieces logs context

## Validation (Quick Check)

In Linear, you should have:
```
PHM-XXX: Add version footer component
├─ Agent: None (was: Spec → Dev → QA)
├─ Phase: Done (was: Planning → Spec → Dev → QA)
├─ 4+ comments with [PLANNING], [SPEC], [DEV], [QA] tags
└─ Sub-issues:
   ├─ PHM-XXX-1: [SPEC] (Done)
   ├─ PHM-XXX-2: [DEV] (Done)
   └─ PHM-XXX-3: [QA] (Done)
```

## Common Issues

| Issue | Quick Fix |
|-------|-----------|
| Skills don't auto-invoke | Check `.claude/skills/*/SKILL.md` exist, restart Claude Code |
| Agents don't launch | Check `.claude/agents/*.md` exist, use `/agents` command |
| Can't see code (verbose) | Verify `model: sonnet` in dev-agent.md |
| Linear errors | Check Linear MCP connected, verify labels exist |
| Hooks not firing | Check `~/.claude/settings.json`, restart Claude Code |

## Success = All Green ✅

If you get through all 6 steps with ✅ checks, your orchestration system works perfectly!

## Need Help?

See detailed troubleshooting: `.claude/ORCHESTRATION_TEST.md`

---

**Ready? Open a fresh Claude Code session and paste the test prompt above!**
