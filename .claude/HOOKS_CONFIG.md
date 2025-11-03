# Hooks Configuration for Orchestration System

This file documents the recommended hooks configuration for the orchestrated workflow system.

## Location

Hooks are configured in: `~/.claude/settings.json`

Use the `/hooks` slash command in Claude Code to configure, or manually edit the file.

## Recommended Configuration

```json
{
  "hooks": [
    {
      "event": "SessionStart",
      "command": "echo '🎯 Orchestrator ready | Sub-agents: spec, dev, qa | Skills: linear-handoff, vibe-check-planning, pieces-logger'"
    },
    {
      "event": "SubagentStop",
      "matcher": "spec-agent",
      "command": "echo '✅ SPEC-AGENT complete. Review spec before launching DEV-AGENT. Check Linear sub-issue for full research and architecture.'"
    },
    {
      "event": "SubagentStop",
      "matcher": "dev-agent",
      "command": "echo '✅ DEV-AGENT complete. Code changes visible above (verbose mode). Review implementation before QA. Check Linear sub-issue for details.'"
    },
    {
      "event": "SubagentStop",
      "matcher": "qa-agent",
      "command": "echo '✅ QA-AGENT complete. Review security scan and test results before integration. Check Linear sub-issue for full QA report.'"
    },
    {
      "event": "PostToolUse",
      "matcher": "mcp__linear__linear_createIssue",
      "command": "echo '📋 Linear issue created. Starting planning phase with vibe-check.'"
    },
    {
      "event": "Stop",
      "command": "echo '\n💡 Tip: Use /agents to view available sub-agents | Use /skills to see available skills'"
    }
  ]
}
```

## Hook Breakdown

### SessionStart Hook
**Purpose:** Display orchestrator capabilities at session start

**Event:** `SessionStart`
**Command:** Display welcome message with available agents and skills

**Why:** Reminds you of orchestration system capabilities each session

---

### SubagentStop Hooks (3 hooks)
**Purpose:** Notify when each agent completes and guide next steps

**Events:** `SubagentStop` with matchers for each agent
**Matchers:**
- `spec-agent` - SPEC-AGENT completed
- `dev-agent` - DEV-AGENT completed
- `qa-agent` - QA-AGENT completed

**Why:** Provides clear checkpoint after each agent finishes, reminds you to review before proceeding

---

### PostToolUse Hook (Linear)
**Purpose:** Confirm issue creation and next step

**Event:** `PostToolUse`
**Matcher:** `mcp__linear__linear_createIssue`
**Command:** Confirm issue created, note planning phase starting

**Why:** Explicit confirmation that workflow is starting properly

---

### Stop Hook
**Purpose:** Helpful reminders after each response

**Event:** `Stop`
**Command:** Show tips for discovering agents/skills

**Why:** Keeps orchestration features discoverable

## Optional Advanced Hooks

### Pre-Commit Quality Gates

```json
{
  "event": "PreToolUse",
  "matcher": "mcp__github__create_branch",
  "command": "git status --short | head -20"
}
```

Shows git status before creating branch (sanity check).

### Context Management Reminder

```json
{
  "event": "Notification",
  "command": "echo '⚠️ Claude is waiting for input. Review agent output before proceeding.'"
}
```

Explicit reminder when Claude needs your decision.

### Post-QA Success Checklist

```json
{
  "event": "SubagentStop",
  "matcher": "qa-agent",
  "command": "echo '📋 QA Complete Checklist:\n✓ Review security scan results\n✓ Verify all tests passing\n✓ Check test coverage\n✓ Review Linear sub-issue\n✓ Ready to create PR?'"
}
```

Shows checklist after QA completes.

## Hooks vs Skills vs Sub-agents

### When to Use Each

| Feature | Purpose | Triggered By | Example |
|---------|---------|--------------|---------|
| **Skills** | Reusable capabilities | Claude decides (auto) | vibe-check-planning, linear-handoff |
| **Sub-agents** | Isolated specialized work | Orchestrator delegates | spec-agent, dev-agent, qa-agent |
| **Hooks** | Automation & notifications | Lifecycle events | Display message after agent stops |

### How They Work Together

```
User: "Add feature X"
  ↓
Hook: SessionStart → Display capabilities
  ↓
Skill: linear-handoff → Create issue (auto-invoked by Claude)
  ↓
Hook: PostToolUse (linear_createIssue) → Confirm creation
  ↓
Skill: vibe-check-planning → Validate approach (auto-invoked)
  ↓
Skill: linear-handoff → Create spec sub-issue (auto-invoked)
  ↓
Orchestrator: Launch spec-agent (explicit delegation)
  ↓
SPEC-AGENT works in background
  ↓
Hook: SubagentStop (spec-agent) → Notify completion, remind to review
  ↓
[Continue through dev and qa agents with similar flow]
```

## Testing Your Hooks

After configuring, test each hook:

1. **SessionStart:**
   ```
   Restart Claude Code
   → Should see welcome message with agents/skills
   ```

2. **SubagentStop:**
   ```
   Launch a sub-agent manually
   → Should see completion message after agent finishes
   ```

3. **PostToolUse (Linear):**
   ```
   Create Linear issue via MCP
   → Should see confirmation message
   ```

4. **Stop:**
   ```
   Any Claude response
   → Should see tip message
   ```

## Customization

### Adjust Verbosity

**Less verbose:**
- Remove Stop hook (no tip on every response)
- Simplify SubagentStop messages to just "✅ [AGENT] complete"

**More verbose:**
- Add git status hook before commits
- Add checklist hooks after each phase
- Add time tracking hooks

### Team-Specific Hooks

**Add deployment notifications:**
```json
{
  "event": "PostToolUse",
  "matcher": "mcp__github__create_pull_request",
  "command": "echo '📢 PR created. Notify team in Slack? Linear issue updated.'"
}
```

**Add compliance reminders:**
```json
{
  "event": "SubagentStop",
  "matcher": "qa-agent",
  "command": "echo '⚠️ Reminder: Update compliance docs if feature affects PII handling'"
}
```

## Troubleshooting

### Hooks Not Firing

**Check:**
- Hooks configured in `~/.claude/settings.json`
- JSON syntax is valid (use JSON validator)
- Event names match exactly (case-sensitive)
- Matchers are correct (check tool names)

**Debug:**
```bash
# View current hooks config
cat ~/.claude/settings.json | jq '.hooks'

# Validate JSON
cat ~/.claude/settings.json | jq '.'
```

### Wrong Matcher

**Issue:** Hook triggers for wrong tool

**Fix:** Use exact tool name from MCP
```json
// Wrong
"matcher": "createIssue"

// Correct
"matcher": "mcp__linear__linear_createIssue"
```

### Hook Command Fails

**Issue:** Command in hook returns error

**Fix:** Test command in terminal first
```bash
# Test your command
echo "test message"

# Then add to hook
"command": "echo 'test message'"
```

## Best Practices

1. **Keep hooks simple:** Just echo messages or simple git commands
2. **Don't block workflow:** Hooks should inform, not require input
3. **Use for notifications:** Not for heavy logic (use skills/agents)
4. **Test after changes:** Restart Claude Code and verify hooks fire
5. **Document custom hooks:** Add comments in settings.json

## Next Steps

1. Copy recommended configuration to `~/.claude/settings.json`
2. Restart Claude Code
3. Test by creating a Linear issue
4. Verify hooks fire at expected times
5. Customize based on your workflow preferences

## Related Files

- `.claude/agents/` - Sub-agent definitions
- `.claude/skills/` - Skill definitions
- `.claude/LINEAR_SETUP.md` - Linear custom fields setup
- `CLAUDE.md` - Full orchestration documentation
