# Orchestration System Test Plan

This test validates the complete orchestration workflow in a fresh Claude Code instance.

## Prerequisites Checklist

Before starting the test, ensure:

- [x] Linear labels created (already done):
  - Agent labels: Agent:None, Agent:Spec, Agent:Dev, Agent:QA
  - Phase labels: Phase:Planning, Phase:Spec, Phase:Dev, Phase:QA
- [ ] Hooks configured in `~/.claude/settings.json`
- [ ] Claude Code restarted after hooks setup
- [ ] Linear MCP connected and working
- [ ] All MCPs loaded: Ref, Exasearch, GitHub, Semgrep, Playwright, vibe-check, Pieces

## Test Feature: Version Footer Component

**Goal:** Add a footer component displaying app version (from package.json) on all pages with bilingual support.

**Why this test:**
- Small scope (completable in one session)
- Tests all agents (spec → dev → qa)
- Requires research (Ref for Next.js patterns)
- Needs security scanning (XSS risk in version display)
- Bilingual testing (footer text in German/English)
- E2E testable (footer visible on page)

**Expected completion time:** 30-45 minutes

## Test Procedure

### Step 1: Start Fresh Session

```bash
# Open project in Claude Code
cd /path/to/ksi_prototype_sdk

# Start new chat session
# You should see SessionStart hook message:
# "🎯 Orchestrator ready | Sub-agents: spec, dev, qa | Skills: ..."
```

**✅ Success criteria:**
- Hook message appears on session start
- `/agents` shows spec-agent, dev-agent, qa-agent
- `/skills` shows linear-handoff, vibe-check-planning, pieces-context-logger

**❌ If fails:**
- Check `.claude/agents/` and `.claude/skills/` exist
- Verify hooks in `~/.claude/settings.json`
- Restart Claude Code

---

### Step 2: Submit Test Feature Request

**Exact prompt to use:**

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

**⏱️ What to watch for:**

**Immediate (< 30 seconds):**
1. **linear-handoff skill** should auto-invoke
   - Look for: "Creating Linear issue..."
   - Creates issue in Linear (check Linear UI)

2. **vibe-check-planning skill** should auto-invoke
   - Look for: "Running vibe-check with phase: planning"
   - Should validate the footer component approach
   - Should update Linear with: `[PLANNING] Vibe-check validated ✓`

**✅ Success criteria:**
- Linear issue created (e.g., PHM-124)
- Vibe-check ran and validated approach
- Linear issue has comment with vibe-check results
- Labels set: `Agent:None`, `Phase:Planning`

**❌ If skills don't auto-invoke:**
- Check `.claude/skills/*/SKILL.md` files exist
- Verify SKILL.md has proper YAML frontmatter
- Linear MCP may not be connected
- Try: "Use the linear-handoff skill to create an issue"

---

### Step 3: Review Planning & Launch SPEC-AGENT

**Orchestrator should:**
1. Explain that vibe-check validated the approach
2. Ask if you want to proceed to SPEC-AGENT
3. **linear-handoff skill** auto-invokes to create `[SPEC]` sub-issue

**Your response:**
```
Yes, proceed to SPEC-AGENT for technical specification.
```

**⏱️ What to watch for:**

1. **Sub-issue created in Linear:**
   - `PHM-124-1: [SPEC] Add version footer component`
   - Parent issue updated: `Agent: Spec`, `Phase: Spec`

2. **SPEC-AGENT launches** in background
   - Look for: "Launching spec-agent..."
   - SPEC-AGENT starts working

3. **SPEC-AGENT workflow:**
   - Reads Linear issue + vibe-check results
   - Uses **Ref MCP** to research:
     - Next.js layout patterns
     - shadcn/ui footer components
   - Uses **Exasearch** to find:
     - Production footer examples
     - Version display patterns
   - Writes comprehensive spec
   - Updates Linear sub-issue `PHM-124-1` with full spec

4. **SubagentStop hook fires:**
   - Look for: "✅ SPEC-AGENT complete. Review spec before launching DEV-AGENT..."

**✅ Success criteria:**
- Sub-issue `PHM-124-1` exists in Linear
- SPEC-AGENT completed and added detailed comment to sub-issue
- Spec includes:
  - Files to create/modify
  - Component architecture
  - Testing requirements
  - Research links (Ref + Exasearch)
- Parent issue updated: `Agent: Spec`, `Phase: Spec`
- Hook message appeared

**❌ If SPEC-AGENT doesn't launch:**
- Check `.claude/agents/spec-agent.md` exists
- Verify YAML frontmatter is valid
- Try explicit: "Launch spec-agent to create technical spec"

**❌ If SPEC-AGENT can't access Linear:**
- Linear MCP not connected
- Check Linear API token in MCP config
- Verify team ID is correct

---

### Step 4: Review Spec & Launch DEV-AGENT

**Orchestrator should:**
1. Show summary of spec from SPEC-AGENT
2. Ask if you want to proceed to DEV-AGENT
3. **linear-handoff skill** auto-invokes to create `[DEV]` sub-issue

**Your response:**
```
Review looks good. Proceed to DEV-AGENT for implementation in verbose mode.
```

**⏱️ What to watch for:**

1. **Sub-issue created in Linear:**
   - `PHM-124-2: [DEV] Add version footer component`
   - Parent issue updated: `Agent: Dev`, `Phase: Dev`

2. **DEV-AGENT launches in VERBOSE MODE**
   - Look for: "Launching dev-agent in verbose mode..."
   - **Critical:** Code changes MUST be visible in main chat

3. **DEV-AGENT workflow:**
   - Creates branch: `feature/phm-124-version-footer`
   - Uses **Ref** to verify API patterns
   - Implements:
     - `components/Footer.tsx` (new)
     - `app/layout.tsx` (modified - add Footer)
     - Bilingual support (German/English text)
   - **You see the code** in main chat (verbose mode)
   - Uses **vibe-check** if complex logic
   - Updates Linear sub-issue `PHM-124-2`

4. **SubagentStop hook fires:**
   - Look for: "✅ DEV-AGENT complete. Code changes visible above..."

**✅ Success criteria:**
- Sub-issue `PHM-124-2` exists in Linear
- DEV-AGENT completed
- **Code is visible in main chat** (verbose mode working)
- Linear comment shows:
  - Branch name
  - Files created/modified
  - Implementation decisions
- Parent issue: `Agent: Dev`, `Phase: Dev`
- Hook message appeared

**❌ If code not visible (verbose mode failed):**
- DEV-AGENT may not have `model: sonnet` in frontmatter
- Check `.claude/agents/dev-agent.md`
- Look for actual file writes (Write/Edit tool calls)

**❌ If DEV-AGENT can't create branch:**
- GitHub MCP not connected
- Check GitHub PAT in MCP config
- Verify repo permissions

---

### Step 5: Review Code & Launch QA-AGENT

**Orchestrator should:**
1. Show summary of code changes
2. Ask if implementation looks correct
3. Ask if you want to proceed to QA-AGENT
4. **linear-handoff skill** auto-invokes to create `[QA]` sub-issue

**Your response:**
```
Code looks good. Proceed to QA-AGENT for security scan and testing.
```

**⏱️ What to watch for:**

1. **Sub-issue created in Linear:**
   - `PHM-124-3: [QA] Add version footer component`
   - Parent issue updated: `Agent: QA`, `Phase: QA`

2. **QA-AGENT launches**
   - Checkouts branch: `feature/phm-124-version-footer`

3. **QA-AGENT workflow:**
   - **Semgrep scan FIRST:**
     - Scans `components/Footer.tsx`
     - Scans `app/layout.tsx`
     - Should be clean (simple component)
   - **Playwright E2E tests:**
     - Writes: `tests/e2e/footer-version.spec.ts`
     - Tests German language: Footer visible with version
     - Tests English language: Footer visible with version
     - Runs tests → should pass
   - Uses **vibe-learn** to log patterns
   - Updates Linear sub-issue `PHM-124-3`

4. **SubagentStop hook fires:**
   - Look for: "✅ QA-AGENT complete. Review security scan and test results..."

**✅ Success criteria:**
- Sub-issue `PHM-124-3` exists in Linear
- QA-AGENT completed
- Semgrep scan ran (check for security issues)
- E2E tests written and passing
- Linear comment shows:
  - Security scan results
  - Test coverage (both languages)
  - Test file path
- Parent issue: `Agent: QA`, `Phase: QA`
- Hook message appeared

**❌ If Semgrep fails:**
- Semgrep not installed: `brew install semgrep`
- Check file paths are absolute
- Verify Semgrep MCP connected

**❌ If Playwright tests fail:**
- Dev server not running: `npm run dev`
- Check test patterns match existing tests
- Review test selectors

---

### Step 6: Integration & Completion

**Orchestrator should:**
1. Review all three sub-issues (spec, dev, qa)
2. Ask if you want to create PR
3. Create GitHub PR linking Linear issue
4. **pieces-context-logger skill** may auto-invoke (optional)
5. Close Linear issue

**Your response:**
```
All looks good. Create PR and complete the workflow.
```

**⏱️ What to watch for:**

1. **GitHub PR created:**
   - Title: "feat: Add version footer component - PHM-124"
   - Description includes sub-issue summaries
   - Links to Linear issue

2. **Pieces logging (if invoked):**
   - Synthesizes: planning → spec → dev → qa
   - Logs complete context for future reference

3. **Linear issue completed:**
   - Parent issue: `Agent: None`, `Phase: Done`
   - Status: Done
   - All sub-issues: Done

**✅ Success criteria:**
- GitHub PR exists
- PR description comprehensive
- Linear issue closed
- All sub-issues closed
- Context logged (if Pieces ran)

---

## Test Validation Checklist

After completing the workflow, verify:

### Linear Validation
- [ ] Parent issue exists (e.g., PHM-124)
- [ ] Three sub-issues exist:
  - [ ] `PHM-124-1: [SPEC]` (Done)
  - [ ] `PHM-124-2: [DEV]` (Done)
  - [ ] `PHM-124-3: [QA]` (Done)
- [ ] Parent issue has 4+ comments:
  - [ ] `[PLANNING]` comment with vibe-check
  - [ ] `[SPEC]` comment (handoff to dev)
  - [ ] `[DEV]` comment (handoff to qa)
  - [ ] `[QA]` comment (completion)
- [ ] Labels tracked correctly:
  - [ ] Agent:None → Agent:Spec → Agent:Dev → Agent:QA → Agent:None
  - [ ] Phase:Planning → Phase:Spec → Phase:Dev → Phase:QA → (removed at Done)

### Code Validation
- [ ] Branch exists: `feature/phm-124-version-footer`
- [ ] Files created:
  - [ ] `components/Footer.tsx`
  - [ ] `tests/e2e/footer-version.spec.ts`
- [ ] Files modified:
  - [ ] `app/layout.tsx` (footer added)
- [ ] Code is visible in chat (verbose mode worked)

### Quality Validation
- [ ] Semgrep scan ran on all changed files
- [ ] No critical/high security issues
- [ ] E2E tests written and passing
- [ ] Both German and English tested

### GitHub Validation
- [ ] PR created with proper title
- [ ] PR links to Linear issue
- [ ] PR description includes work summary
- [ ] Branch is ready for review

### Skills & Hooks Validation
- [ ] SessionStart hook fired (saw welcome message)
- [ ] linear-handoff skill invoked 4+ times
- [ ] vibe-check-planning skill invoked (planning phase)
- [ ] SubagentStop hooks fired 3 times (one per agent)
- [ ] pieces-context-logger skill may have invoked

---

## Common Issues & Solutions

### Skills Not Auto-Invoking

**Symptom:** Skills don't run automatically

**Diagnosis:**
```bash
# Check skills exist
ls -la .claude/skills/*/SKILL.md

# Verify YAML frontmatter
head -20 .claude/skills/linear-handoff/SKILL.md
```

**Fix:**
- Ensure SKILL.md has proper YAML frontmatter
- Restart Claude Code
- Try explicit: "Use the [skill-name] skill to..."

### Agents Not Launching

**Symptom:** Sub-agents don't start

**Diagnosis:**
```bash
# Check agents exist
ls -la .claude/agents/*.md

# Verify YAML frontmatter
head -20 .claude/agents/spec-agent.md

# Check available agents
# In Claude Code: /agents
```

**Fix:**
- Verify YAML frontmatter is valid
- Check `name:` matches filename (spec-agent)
- Restart Claude Code

### Linear Integration Failing

**Symptom:** Can't create issues or sub-issues

**Diagnosis:**
- Check Linear MCP in `/mcps` output
- Verify API token in MCP config
- Test: "Get Linear issue by ID: [any-issue-id]"

**Fix:**
- Reconnect Linear MCP
- Verify team ID in config
- Check API permissions

### Hooks Not Firing

**Symptom:** No hook messages appear

**Diagnosis:**
```bash
# Check hooks config
cat ~/.claude/settings.json | jq '.hooks'

# Verify JSON syntax
cat ~/.claude/settings.json | jq '.'
```

**Fix:**
- Verify hooks in `~/.claude/settings.json`
- Check JSON syntax is valid
- Restart Claude Code

### Verbose Mode Not Working

**Symptom:** Can't see DEV-AGENT code changes

**Diagnosis:**
- Check `.claude/agents/dev-agent.md`
- Look for `model: sonnet` in frontmatter

**Fix:**
- Add `model: sonnet` to dev-agent.md
- Ensure agent uses Write/Edit tools (not just describes)

---

## Success Metrics

**Full success:** All checkboxes ✅ in validation checklist

**Partial success:** Workflow completed but some automation missing
- May need to manually trigger skills
- May need to explicitly launch agents
- Core functionality works

**Failure:** Workflow doesn't complete
- Check prerequisites again
- Review common issues
- See troubleshooting sections

---

## After Test Completion

### If Successful

You now have a working orchestration system!

**Next steps:**
1. Keep the footer component (or merge the PR)
2. Use orchestration for real features
3. Customize agents/skills for your workflow
4. Add more hooks as needed

### If Partially Successful

Identify what worked vs. what didn't:

**Worked:**
- Note which skills/agents functioned
- Document which MCPs are reliable

**Didn't work:**
- Fix configuration issues
- Re-test specific components
- May need to trigger manually

### If Failed

Debug systematically:

1. **Prerequisites:** Verify Linear fields, hooks, MCPs
2. **Skills:** Test each skill individually
3. **Agents:** Launch each agent manually
4. **Hooks:** Check console for errors
5. **MCPs:** Test each MCP separately

---

## Test Report Template

After completing the test, document results:

```markdown
# Orchestration System Test Report

**Date:** [YYYY-MM-DD]
**Tester:** [Your name]
**Claude Code Version:** [version]

## Test Summary
- [ ] Full success
- [ ] Partial success
- [ ] Failed

## What Worked
- Skills auto-invoked: [list which ones]
- Sub-agents launched: [list which ones]
- Hooks fired: [list which ones]
- Linear integration: [working/not working]
- Code visibility (verbose): [working/not working]

## What Didn't Work
[List any issues encountered]

## Time to Complete
- Expected: 30-45 minutes
- Actual: [XX] minutes

## Recommendations
[Any suggestions for improving the system]

## Notes
[Any additional observations]
```

---

## Quick Reference: Expected Messages

**Session Start:**
```
🎯 Orchestrator ready | Sub-agents: spec, dev, qa | Skills: linear-handoff, vibe-check-planning, pieces-logger
```

**After Linear Issue Created:**
```
📋 Linear issue PHM-XXX created. Starting planning phase with vibe-check.
```

**After SPEC-AGENT:**
```
✅ SPEC-AGENT complete. Review spec before launching DEV-AGENT. Check Linear sub-issue for full research and architecture.
```

**After DEV-AGENT:**
```
✅ DEV-AGENT complete. Code changes visible above (verbose mode). Review implementation before QA. Check Linear sub-issue for details.
```

**After QA-AGENT:**
```
✅ QA-AGENT complete. Review security scan and test results before integration. Check Linear sub-issue for full QA report.
```

**Session End:**
```
💡 Tip: Use /agents to view available sub-agents | Use /skills to see available skills
```

---

**Ready to test? Follow the procedure above step-by-step and check off each validation item as you go!**
