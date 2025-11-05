---
trigger: auto
name: linear-handoff
description: Automatically create and update Linear issues with sub-issues, workflow states, and status updates
version: 2.0.0
---

# Linear Handoff Skill

**Purpose**: Seamlessly bridge between development phases by automatically managing Linear issues, sub-issues, Agent labels, workflow states, and phase transitions.

**v2.0 Changes:**
- ❌ Removed Phase labels (redundant with workflow states)
- ✅ Use Linear workflow states (Todo → In Progress → In Review → Done)
- ✅ Keep Agent labels for orchestration
- ✅ Keep phase comments for context

## When Invoked

**Automatically triggers when:**
- New feature work begins (create parent issue + spec sub-issue)
- Spec phase completes (create dev sub-issue)
- Dev phase completes (create QA sub-issue)
- QA phase completes (update parent issue to done)
- Phase transitions occur (update labels)

## What It Does

### 1. Create Parent Issue (Feature Start)

```typescript
// When user requests new feature
linear.create({
  title: "Feature X",
  description: `
    ## Requirements
    ${userRequirements}

    ## Workflow
    - [ ] Specification (SPEC-AGENT)
    - [ ] Development (DEV-AGENT)
    - [ ] Quality Assurance (QA-AGENT)
  `,
  labels: ["Agent:None"],
  stateId: workflowStates.Todo,  // Start in Todo state
  projectId: "PROJECT_ID"
})
```

### 2. Create Sub-Issues (Phase Transitions)

**Spec sub-issue:**
```typescript
linear.create({
  title: "Feature X - Specification",  // No bracket prefix
  description: "Research and specification for Feature X",
  parentId: "PHM-XX",
  labels: ["Agent:Spec"],
  stateId: workflowStates.InProgress
})
```

**Dev sub-issue:**
```typescript
linear.create({
  title: "Feature X - Implementation",  // No bracket prefix
  description: "Implementation of Feature X per spec",
  parentId: "PHM-XX",
  labels: ["Agent:Dev"],
  stateId: workflowStates.InProgress
})
```

**QA sub-issue:**
```typescript
linear.create({
  title: "Feature X - Testing",  // No bracket prefix
  description: "Testing and validation of Feature X",
  parentId: "PHM-XX",
  labels: ["Agent:QA"],
  stateId: workflowStates.InProgress
})
```

### 3. Update Parent Issue (Labels + Workflow State)

**Phase transitions:**
```typescript
// Spec starts
updateIssue(parentIssue, {
  removeLabels: ["Agent:None"],
  addLabels: ["Agent:Spec"],
  stateId: workflowStates.InProgress  // Move to In Progress
})

// Dev starts (spec complete)
updateIssue(parentIssue, {
  removeLabels: ["Agent:Spec"],
  addLabels: ["Agent:Dev"],
  stateId: workflowStates.InProgress  // Still In Progress
})

// QA starts (dev complete)
updateIssue(parentIssue, {
  removeLabels: ["Agent:Dev"],
  addLabels: ["Agent:QA"],
  stateId: workflowStates.InReview  // Move to In Review
})

// Complete (QA approves)
updateIssue(parentIssue, {
  removeLabels: ["Agent:QA"],
  addLabels: ["Agent:None"],
  stateId: workflowStates.Done  // Move to Done
})
```

### 4. Add Phase-Tagged Comments

**Format:**
```
[PLANNING] Validated approach with vibe-check
- Using WebSocket for real-time updates
- Fallback to polling for older browsers

[SPEC] Architecture designed
- Components: ScoreBoard, LiveFeed, ConnectionManager
- State: Zustand for real-time updates
- See sub-issue PHM-62-1 for details

[DEV] Implementation complete
- All components implemented per spec
- Semgrep scan clean
- See sub-issue PHM-62-2 for details

[QA] Testing complete
- Semgrep: Clean ✅
- Playwright: 2/2 passing ✅
- Manual testing: No issues ✅
- Approved for merge
```

## Requirements

**Linear Labels (must exist):**
- `Agent:None` (gray) - No agent assigned
- `Agent:Spec` (blue) - Spec agent working
- `Agent:Dev` (green) - Dev agent working
- `Agent:QA` (orange) - QA agent working

**Linear Workflow States (built-in):**
- `Todo` - Not started
- `In Progress` - Active work
- `In Review` - Ready for review
- `Done` - Complete
- `Canceled` - Won't do

**See**: `.claude/LINEAR_SETUP.md` for creating Agent labels

## Usage Examples

### Example 1: New Feature

```
User: "Add real-time score updates"

Skill invokes:
1. Creates parent issue: PHM-62 "Add real-time score updates"
   - Labels: Agent:None
   - State: Todo
2. Returns issue ID to orchestrator
3. Orchestrator runs vibe-check
4. Skill updates comment: [PLANNING] Validated approach
5. Orchestrator invokes SPEC-AGENT
6. Skill transitions:
   - Labels: Agent:None → Agent:Spec
   - State: Todo → In Progress
7. Skill creates sub-issue: PHM-62-1 "Real-time score updates - Specification"
   - Labels: Agent:Spec
   - State: In Progress
```

### Example 2: Phase Transition (Spec → Dev)

```
SPEC-AGENT completes:

Skill invokes:
1. Updates parent PHM-62:
   - Labels: Agent:Spec → Agent:Dev
   - State: In Progress (no change)
2. Adds comment: [SPEC] Architecture designed (links to PHM-62-1)
3. Creates sub-issue: PHM-62-2 "Real-time score updates - Implementation"
   - Labels: Agent:Dev
   - State: In Progress
4. Signals orchestrator: Ready for dev
```

### Example 3: Completion

```
QA-AGENT approves:

Skill invokes:
1. Updates parent PHM-62:
   - Labels: Agent:QA → Agent:None
   - State: In Review → Done
2. Adds comment: [QA] Testing complete, approved
3. Signals orchestrator: Ready for merge
```

## Error Handling

**If Linear API fails:**
- Log error
- Continue workflow (don't block development)
- User can update Linear manually

**If labels don't exist:**
- Warn user
- Provide setup instructions
- Create issue without labels

## Integration with Agents

**SPEC-AGENT:**
- Reads parent issue requirements
- Updates spec sub-issue
- Signals completion → Skill transitions labels

**DEV-AGENT:**
- Reads spec sub-issue
- Updates dev sub-issue
- Signals completion → Skill transitions labels

**QA-AGENT:**
- Reads dev sub-issue
- Updates QA sub-issue
- Signals completion → Skill marks done

## Configuration

**Project-specific:**
```typescript
// In each project's .claude/skills/linear-handoff/config.json
{
  "projectId": "LINEAR_PROJECT_ID",
  "teamId": "LINEAR_TEAM_ID",
  "labelPrefix": "Agent:",
  "workflowStates": {
    "Todo": "STATE_ID",         // Get from Linear team settings
    "InProgress": "STATE_ID",   // Get from Linear team settings
    "InReview": "STATE_ID",     // Get from Linear team settings
    "Done": "STATE_ID"          // Get from Linear team settings
  }
}
```

## Benefits

1. **Automatic tracking** - No manual Linear updates needed
2. **Clear history** - Phase-tagged comments show workflow
3. **Visual progress** - Labels show current phase
4. **Traceability** - Sub-issues link to agents' work
5. **Async coordination** - Agents know when to start/stop

## Token Cost

**Minimal**: ~200-500 tokens per invocation (Linear API calls are external, not in context)
