# Linear Labels Setup (v2.0)

This guide documents the Linear labels and workflow states used for the orchestration system.

## Overview

**v2.0 Changes:**
- ❌ Removed Phase labels (redundant with workflow states)
- ✅ Use Linear workflow states (Todo → In Progress → In Review → Done)
- ✅ Keep Agent labels for orchestration
- ✅ Keep phase comments for context

The orchestration system uses:

1. **Agent labels** - Which agent is currently working (Agent:None, Agent:Spec, Agent:Dev, Agent:QA)
2. **Linear workflow states** - Current phase tracked via built-in states (Todo, In Progress, In Review, Done)

**Why labels?**
- Linear doesn't support traditional custom fields via API
- Labels provide the same functionality with better API support
- Fully supported by Linear MCP tools (`linear_addIssueLabel`, `linear_removeIssueLabel`)

## Created Labels

All labels have been created for team PHM (`57dfac47-8b23-4841-a760-e8f1d144c10d`).

### Agent Labels (Purple theme - AI/automation)

| Label | Color | ID | Description |
|-------|-------|----|----|
| `Agent:None` | #E9D5FF | `15e72e00-0f69-4eaf-9ede-3859766f1b7e` | Default state - no agent active |
| `Agent:Spec` | #A78BFA | `6a997911-b2a8-427a-af03-f3407edc8398` | SPEC-AGENT researching and writing specification |
| `Agent:Dev` | #8B5CF6 | `1ec5953b-a316-4091-ae9c-4a4814bc32e3` | DEV-AGENT implementing code changes |
| `Agent:QA` | #7C3AED | `240e6885-52dd-495c-b9ed-00092ac4cb7f` | QA-AGENT running security scans and tests |

### ~~Phase Labels~~ (DEPRECATED in v2.0)

**Phase labels have been removed** - use Linear workflow states instead:

| Workflow State | Old Phase Label | When Used |
|----------------|-----------------|-----------|
| Todo | Phase:Planning | Issue created, awaiting start |
| In Progress | Phase:Spec, Phase:Dev | Spec or dev work in progress |
| In Review | Phase:QA | QA-AGENT testing and validation |
| Done | (no label) | Work complete, PR merged |

## Workflow (v2.0)

### Agent Label + Workflow State Transitions

| Transition | Agent Label | Workflow State | Actions |
|------------|-------------|----------------|---------|
| **Creation → Planning** | `Agent:None` | Todo | Create issue with Agent:None label |
| **Planning → Spec** | `Agent:Spec` | In Progress | Remove: `Agent:None`<br>Add: `Agent:Spec`<br>State: Todo → In Progress |
| **Spec → Dev** | `Agent:Dev` | In Progress | Remove: `Agent:Spec`<br>Add: `Agent:Dev`<br>State: stays In Progress |
| **Dev → QA** | `Agent:QA` | In Review | Remove: `Agent:Dev`<br>Add: `Agent:QA`<br>State: In Progress → In Review |
| **QA → Done** | `Agent:None` | Done | Remove: `Agent:QA`<br>Add: `Agent:None`<br>State: In Review → Done |

### How linear-handoff Skill Uses Labels (v2.0)

The `linear-handoff` skill automatically manages Agent labels and workflow states during transitions.

**Example: Planning → Spec**
```javascript
// Remove old Agent label
linear_removeIssueLabel({
  id: "PHM-123",
  labelId: "15e72e00-0f69-4eaf-9ede-3859766f1b7e" // Agent:None
})

// Add new Agent label
linear_addIssueLabel({
  id: "PHM-123",
  labelId: "6a997911-b2a8-427a-af03-f3407edc8398" // Agent:Spec
})

// Update workflow state
linear_updateIssue({
  id: "PHM-123",
  stateId: "in-progress-state-id"  // Todo → In Progress
})
```

## Usage in Workflow

### Agent Labels by Phase (v2.0)

| Phase | Agent Label | Workflow State | Description |
|-------|-------------|----------------|-------------|
| **Planning** | `Agent:None` | Todo | Orchestrator validating with vibe-check |
| **Spec** | `Agent:Spec` | In Progress | SPEC-AGENT researching and designing |
| **Dev** | `Agent:Dev` | In Progress | DEV-AGENT implementing code |
| **QA** | `Agent:QA` | In Review | QA-AGENT testing and scanning |
| **Done** | `Agent:None` | Done | Orchestrator created PR and merged |

## Filtering and Views (v2.0)

### Create Filtered Views

**View: In Development**
```
Filter: has label "Agent:Dev" AND status "In Progress"
Shows: All issues currently being implemented
```

**View: Needs QA**
```
Filter: has label "Agent:QA" AND status "In Review"
Shows: All issues ready for testing
```

**View: Orchestrator Review**
```
Filter: has label "Agent:None" AND status NOT "Done" AND status NOT "Todo"
Shows: Issues waiting for orchestrator review between phases
```

**View: Current Sprint by Workflow**
```
Group by: Workflow State
Filter: Current cycle
Shows: Sprint progress through workflow (Todo/In Progress/In Review/Done)
```

### Saved Filters

Create saved filters for common queries:
- Agent: `Agent:Spec` + State: In Progress - All specs in progress
- Agent: `Agent:Dev` + State: In Progress - All development in progress
- Agent: `Agent:QA` + State: In Review - All in QA
- Label: `Agent:None` AND Status: NOT Done AND NOT Todo - Needs orchestrator review

## Sub-Issue Naming Convention

The system uses prefixed sub-issue names (same as with custom fields):

**Parent Issue:**
```
PHM-123: Add real-time score updates
Labels: Agent:Dev, Phase:Dev
```

**Sub-Issues:**
```
PHM-123-1: [SPEC] Add real-time score updates
PHM-123-2: [DEV] Add real-time score updates
PHM-123-3: [QA] Add real-time score updates
```

**Benefits:**
- Clear visual hierarchy
- Searchable by prefix (`[SPEC]`, `[DEV]`, `[QA]`)
- Chronological order maintained
- Easy to see workflow stage

## Visual Example (v2.0)

### Issue Lifecycle with Agent Labels + Workflow States

```
Creation:
┌─────────────────────────────────┐
│ PHM-123: Feature name           │
│ Label: Agent:None               │
│ State: Todo                     │
└─────────────────────────────────┘

After vibe-check (orchestrator → SPEC-AGENT):
┌─────────────────────────────────┐
│ PHM-123: Feature name           │
│ Label: Agent:Spec ← changed     │
│ State: In Progress ← changed    │
│ └─ PHM-123-1: [SPEC] Feature    │
└─────────────────────────────────┘

After spec complete (SPEC-AGENT → DEV-AGENT):
┌─────────────────────────────────┐
│ PHM-123: Feature name           │
│ Label: Agent:Dev ← changed      │
│ State: In Progress (unchanged)  │
│ ├─ PHM-123-1: [SPEC] (Done)     │
│ └─ PHM-123-2: [DEV] Feature     │
└─────────────────────────────────┘

After implementation (DEV-AGENT → QA-AGENT):
┌─────────────────────────────────┐
│ PHM-123: Feature name           │
│ Label: Agent:QA ← changed       │
│ State: In Review ← changed      │
│ ├─ PHM-123-1: [SPEC] (Done)     │
│ ├─ PHM-123-2: [DEV] (Done)      │
│ └─ PHM-123-3: [QA] Feature      │
└─────────────────────────────────┘

After QA (QA-AGENT → orchestrator integration):
┌─────────────────────────────────┐
│ PHM-123: Feature name           │
│ Label: Agent:None ← changed     │
│ State: Done ← changed           │
│ ├─ PHM-123-1: [SPEC] (Done)     │
│ ├─ PHM-123-2: [DEV] (Done)      │
│ └─ PHM-123-3: [QA] (Done)       │
└─────────────────────────────────┘
```

## Troubleshooting

### Labels Not Showing

**Issue:** Labels don't appear on issues

**Solutions:**
- Refresh Linear web app
- Check labels exist (see label IDs above)
- Verify team ID is correct (`57dfac47-8b23-4841-a760-e8f1d144c10d`)

### linear-handoff Skill Can't Update Labels

**Issue:** Skill tries to update but labels don't change

**Solutions:**
1. **Verify label IDs:**
   - Check `.claude/skills/linear-handoff/SKILL.md` for correct IDs
   - IDs are hardcoded in the skill

2. **Check Linear API access:**
   - MCP connected: `/mcps` in Claude Code
   - Has write permissions
   - Team ID is correct

3. **Verify tools available:**
   ```javascript
   // Should have these tools
   linear_addIssueLabel
   linear_removeIssueLabel
   ```

### Wrong Labels on Issue

**Issue:** Issue has incorrect Agent or Phase label

**Solutions:**
- Manually remove incorrect label in Linear UI
- Add correct label in Linear UI
- Or use Linear MCP tools to fix:
  ```javascript
  linear_removeIssueLabel({ id: "PHM-123", labelId: "wrong-id" })
  linear_addIssueLabel({ id: "PHM-123", labelId: "correct-id" })
  ```

## Migration from Existing Issues

If you have existing issues without these labels:

### Bulk Update

1. **Filter all issues:** Select your team
2. **Multi-select issues:** Cmd/Ctrl + click
3. **Bulk edit labels:** Right-click → Add labels
4. **Add default labels:**
   - `Agent:None`
   - `Phase:Planning` (or current actual phase)

### Script for Large Migrations

```javascript
// Get all issues in team
const issues = await linear.team("57dfac47-8b23-4841-a760-e8f1d144c10d").issues();

// Update each with default labels
for (const issue of issues.nodes) {
  // Add Agent:None if no Agent label
  await linear.addIssueLabel({
    id: issue.id,
    labelId: "15e72e00-0f69-4eaf-9ede-3859766f1b7e" // Agent:None
  });

  // Add Phase:Planning if no Phase label
  await linear.addIssueLabel({
    id: issue.id,
    labelId: "c429859c-1147-4b5b-894b-73106c9cb1b7" // Phase:Planning
  });
}
```

## Best Practices (v2.0)

1. **Always set defaults:** New issues start with `Agent:None`, state: Todo
2. **One Agent label at a time:** Remove old before adding new
3. **Use workflow states:** Let Linear's built-in states track phase (no Phase labels)
4. **Let skills manage labels:** Don't manually change during workflow
5. **Manual updates okay at transitions:** If reviewing between agents
6. **Document deviations:** Comment why if manually changing labels
7. **Workflow state changes:** Use linear_updateIssue to change states (Todo/In Progress/In Review/Done)

## Summary (v2.0)

**What was created:**
- ✅ 4 Agent labels (None, Spec, Dev, QA) - Purple theme
- ❌ Phase labels removed (use Linear workflow states instead)
- ✅ All labels created with team scope

**What they enable:**
- Automatic workflow tracking via Agent labels + workflow states
- Clear handoff points between agents
- Filterable views by Agent and workflow state
- Progress visibility without redundant Phase labels
- Orchestration automation

**v2.0 Advantages:**
- Reduced label clutter (4 labels instead of 8)
- Native workflow states more intuitive than Phase labels
- Fully supported by Linear API
- Work with Linear MCP tools (linear_updateIssue for state changes)
- Visual in issue list (colored badges for Agent labels)

**Next steps:**
- ✅ Labels created
- ✅ Skills updated with label IDs
- ✅ Hooks configured
- Ready to test orchestration system!

## Related Files

- `.claude/skills/linear-handoff/SKILL.md` - Uses these labels (updated with IDs)
- `.claude/agents/` - Agents work with these sub-issues
- `CLAUDE.md` - Full orchestration documentation
- `.claude/HOOKS_CONFIG.md` - Hooks that respond to workflow events
- `.claude/ORCHESTRATION_TEST.md` - Test the complete system
