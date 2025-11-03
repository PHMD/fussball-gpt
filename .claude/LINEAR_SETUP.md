# Linear Labels Setup

This guide documents the Linear labels used for the orchestration system.

## Overview

The orchestration system uses **labels** (not custom fields) to track workflow state:

1. **Agent labels** - Which agent is currently working (Agent:None, Agent:Spec, Agent:Dev, Agent:QA)
2. **Phase labels** - Current phase of the workflow (Phase:Planning, Phase:Spec, Phase:Dev, Phase:QA)

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

### Phase Labels (Blue theme - process/workflow)

| Label | Color | ID | Description |
|-------|-------|----|----|
| `Phase:Planning` | #BFDBFE | `c429859c-1147-4b5b-894b-73106c9cb1b7` | Planning and validation phase |
| `Phase:Spec` | #60A5FA | `14e817b3-01d2-49d9-b7af-33177e099602` | Technical specification phase |
| `Phase:Dev` | #3B82F6 | `d2d3ee45-30be-431d-80a6-64163f692c65` | Code implementation phase |
| `Phase:QA` | #2563EB | `aba3a1b0-762d-4133-8aea-33f03c01f7ce` | Quality assurance and testing phase |

## Label Workflow

### Label Transitions by Phase

| Transition | Actions |
|------------|---------|
| **Creation → Planning** | Add: `Agent:None`, `Phase:Planning` |
| **Planning → Spec** | Remove: `Agent:None`, `Phase:Planning`<br>Add: `Agent:Spec`, `Phase:Spec` |
| **Spec → Dev** | Remove: `Agent:Spec`, `Phase:Spec`<br>Add: `Agent:Dev`, `Phase:Dev` |
| **Dev → QA** | Remove: `Agent:Dev`, `Phase:Dev`<br>Add: `Agent:QA`, `Phase:QA` |
| **QA → Done** | Remove: `Agent:QA`, `Phase:QA`<br>Add: `Agent:None`<br>(No Phase label - use Linear Status: Done) |

### How linear-handoff Skill Uses Labels

The `linear-handoff` skill automatically manages labels during transitions.

**Example: Planning → Spec**
```javascript
// Remove old labels
linear_removeIssueLabel({
  id: "PHM-123",
  labelId: "15e72e00-0f69-4eaf-9ede-3859766f1b7e" // Agent:None
})
linear_removeIssueLabel({
  id: "PHM-123",
  labelId: "c429859c-1147-4b5b-894b-73106c9cb1b7" // Phase:Planning
})

// Add new labels
linear_addIssueLabel({
  id: "PHM-123",
  labelId: "6a997911-b2a8-427a-af03-f3407edc8398" // Agent:Spec
})
linear_addIssueLabel({
  id: "PHM-123",
  labelId: "14e817b3-01d2-49d9-b7af-33177e099602" // Phase:Spec
})
```

## Usage in Workflow

### Label Values by Phase

| Phase | Agent Label | Phase Label | Linear Status | Description |
|-------|-------------|-------------|---------------|-------------|
| **Planning** | `Agent:None` | `Phase:Planning` | Backlog/In Progress | Orchestrator validating with vibe-check |
| **Spec** | `Agent:Spec` | `Phase:Spec` | In Progress | SPEC-AGENT researching and designing |
| **Dev** | `Agent:Dev` | `Phase:Dev` | In Progress | DEV-AGENT implementing code |
| **QA** | `Agent:QA` | `Phase:QA` | In Review | QA-AGENT testing and scanning |
| **Done** | `Agent:None` | (no phase label) | Done | Orchestrator created PR and merged |

## Filtering and Views

### Create Filtered Views

**View: In Development**
```
Filter: has label "Agent:Dev" AND has label "Phase:Dev"
Shows: All issues currently being implemented
```

**View: Needs QA**
```
Filter: has label "Agent:QA" AND has label "Phase:QA"
Shows: All issues ready for testing
```

**View: Orchestrator Review**
```
Filter: has label "Agent:None" AND NOT has label "Phase:Planning"
Shows: Issues waiting for orchestrator review between phases
```

**View: Current Sprint by Phase**
```
Group by: Labels (filter to Phase:* labels)
Filter: Current cycle
Shows: Sprint progress through workflow phases
```

### Saved Filters

Create saved filters for common queries:
- Label: `Phase:Spec` - All specs in progress
- Label: `Phase:Dev` - All development in progress
- Label: `Phase:QA` - All in QA
- Label: `Agent:None` AND Status: NOT Done - Needs orchestrator review

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

## Visual Example

### Issue Lifecycle with Labels

```
Creation:
┌─────────────────────────────────┐
│ PHM-123: Feature name           │
│ Labels: Agent:None              │
│         Phase:Planning          │
│ Status: In Progress             │
└─────────────────────────────────┘

After vibe-check (orchestrator → SPEC-AGENT):
┌─────────────────────────────────┐
│ PHM-123: Feature name           │
│ Labels: Agent:Spec ← changed    │
│         Phase:Spec ← changed    │
│ Status: In Progress             │
│ └─ PHM-123-1: [SPEC] Feature    │
└─────────────────────────────────┘

After spec complete (SPEC-AGENT → DEV-AGENT):
┌─────────────────────────────────┐
│ PHM-123: Feature name           │
│ Labels: Agent:Dev ← changed     │
│         Phase:Dev ← changed     │
│ Status: In Progress             │
│ ├─ PHM-123-1: [SPEC] (Done)     │
│ └─ PHM-123-2: [DEV] Feature     │
└─────────────────────────────────┘

After implementation (DEV-AGENT → QA-AGENT):
┌─────────────────────────────────┐
│ PHM-123: Feature name           │
│ Labels: Agent:QA ← changed      │
│         Phase:QA ← changed      │
│ Status: In Review               │
│ ├─ PHM-123-1: [SPEC] (Done)     │
│ ├─ PHM-123-2: [DEV] (Done)      │
│ └─ PHM-123-3: [QA] Feature      │
└─────────────────────────────────┘

After QA (QA-AGENT → orchestrator integration):
┌─────────────────────────────────┐
│ PHM-123: Feature name           │
│ Labels: Agent:None ← changed    │
│         (no Phase label)        │
│ Status: Done ← changed          │
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

## Best Practices

1. **Always set defaults:** New issues start with `Agent:None`, `Phase:Planning`
2. **One Agent label at a time:** Remove old before adding new
3. **One Phase label at a time:** Remove old before adding new
4. **Let skills manage labels:** Don't manually change during workflow
5. **Manual updates okay at transitions:** If reviewing between agents
6. **Document deviations:** Comment why if manually changing labels

## Summary

**What was created:**
- ✅ 4 Agent labels (None, Spec, Dev, QA) - Purple theme
- ✅ 4 Phase labels (Planning, Spec, Dev, QA) - Blue theme
- ✅ All labels created with team scope

**What they enable:**
- Automatic workflow tracking
- Clear handoff points
- Filterable views by phase
- Progress visibility
- Orchestration automation

**Advantages over custom fields:**
- Fully supported by Linear API
- Work with Linear MCP tools
- Visual in issue list (colored badges)
- Can have multiple labels if needed

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
