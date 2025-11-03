---
name: linear-handoff
description: |
  Manages agent transitions in Linear workflow. Use when transitioning
  between workflow phases to update issue fields and create sub-issues.
  Automatically invoked when orchestrator needs to hand off work to
  the next agent (planning → spec → dev → qa → done).
allowed-tools: mcp__linear__linear_createIssue, mcp__linear__linear_updateIssue, mcp__linear__linear_addIssueComment
---

# Linear Handoff Skill

## Purpose
Automate Linear issue management during agent transitions in the orchestrated workflow.

## CRITICAL: Sub-Issue Creation Pattern

**ONLY the orchestrator uses this skill to create sub-issues.**

**NEVER create new top-level tickets for [SPEC], [DEV], or [QA] work.**

**Always create as sub-issues under the parent:**
```javascript
// CORRECT - Sub-issue under parent
linear_createIssue({
  title: "[SPEC] Feature name",
  parentId: "PHM-123",  // ← REQUIRED for sub-issues
  projectId: parent.project?.id,
  teamId: "57dfac47-8b23-4841-a760-e8f1d144c10d"
})

// WRONG - Top-level ticket (duplicate)
linear_createIssue({
  title: "[SPEC] Feature name",
  // Missing parentId creates NEW top-level ticket!
  projectId: "kicker-project-id",
  teamId: "57dfac47-8b23-4841-a760-e8f1d144c10d"
})
```

**Agents do NOT have access to linear_createIssue and cannot create tickets.**

## Project Assignment Rules

**ALWAYS assign issues to the Kicker project when working in this repository.**

### Project Details
- **Project Name:** Kicker
- **Project ID:** `2e7ebce4-bf1c-43e6-8eec-062a52e2cf8a`
- **Team:** PHMD

### Parent Issue Creation

When creating a parent issue (the main feature ticket), ALWAYS include the project:

```javascript
// CORRECT - Parent issue with Kicker project
const parentIssue = await linear_createIssue({
  title: "Feature name",
  description: "Feature description...",
  teamId: "57dfac47-8b23-4841-a760-e8f1d144c10d",
  projectId: "2e7ebce4-bf1c-43e6-8eec-062a52e2cf8a", // ← Kicker project (REQUIRED)
  stateId: "fe1a9f10-44f1-47dd-8f7f-dfb1cc62d07c" // Backlog
})

// WRONG - Missing project assignment
const parentIssue = await linear_createIssue({
  title: "Feature name",
  description: "Feature description...",
  teamId: "57dfac47-8b23-4841-a760-e8f1d144c10d"
  // ❌ Missing projectId - issue won't be tracked in Kicker project
})
```

### Sub-Issue Creation

When creating sub-issues ([SPEC], [DEV], [QA]), the linear-handoff skill MUST:

1. Get parent issue first to read project assignment
2. Create sub-issue with parentId AND projectId
3. Inherit project from parent

```javascript
// Step 1: Get parent issue
const parent = await linear_getIssueById("parent-issue-id");

// Step 2: Create sub-issue with BOTH parentId and projectId
const specIssue = await linear_createIssue({
  title: "[SPEC] Feature name",
  parentId: "parent-issue-id",           // ← Makes it a sub-issue
  projectId: parent.project?.id,         // ← Inherits Kicker project
  cycleId: parent.cycle?.id,             // ← Inherits cycle (if set)
  teamId: "57dfac47-8b23-4841-a760-e8f1d144c10d",
  description: "Spec details..."
})
```

### Verification Checklist

After creating issues, verify:
- ✅ Parent issue has projectId: `"2e7ebce4-bf1c-43e6-8eec-062a52e2cf8a"`
- ✅ Sub-issues have parentId set (creates hierarchy)
- ✅ Sub-issues have projectId matching parent
- ✅ All issues appear in Kicker project in Linear UI

### Why This Matters

**Without project assignment:**
- Issues are "orphaned" and don't appear in Kicker project view
- Can't track project progress
- Issues are harder to find and organize
- Sprint planning becomes difficult

**With proper project assignment:**
- All work appears in Kicker project dashboard
- Easy to see feature progress (parent + sub-issues)
- Clean organization and filtering
- Proper sprint/cycle tracking

### Common Mistakes to Avoid

❌ **Creating parent without project:**
```javascript
linear_createIssue({ title: "Feature", teamId: "..." })
// Missing projectId!
```

❌ **Creating sub-issue without inheriting project:**
```javascript
linear_createIssue({
  title: "[SPEC] Feature",
  parentId: "...",
  teamId: "..."
})
// Missing projectId!
```

❌ **Hardcoding project instead of inheriting:**
```javascript
// BAD - What if parent is in different project?
linear_createIssue({
  title: "[SPEC] Feature",
  parentId: "...",
  projectId: "hardcoded-id" // ❌ Should read from parent
})
```

✅ **Correct pattern:**
```javascript
// Get parent first
const parent = await linear_getIssueById(parentId);

// Create with inherited project
const subIssue = await linear_createIssue({
  title: "[SPEC] Feature",
  parentId: parentId,
  projectId: parent.project?.id,  // ✓ Inherited
  cycleId: parent.cycle?.id,      // ✓ Inherited
  teamId: "57dfac47-8b23-4841-a760-e8f1d144c10d"
})
```

### Troubleshooting

**Issue not appearing in Kicker project:**
1. Check project field in API response - is it null?
2. If null, update with: `linear_updateIssue({ id: "...", projectId: "2e7ebce4-bf1c-43e6-8eec-062a52e2cf8a" })`
3. Verify in Linear UI

**Sub-issue not showing under parent:**
1. Check parent field in API response - is it null?
2. Verify parentId was set during creation
3. If broken, recreate sub-issue or update parent field

## When Claude Uses This Skill

This skill is **model-invoked** - Claude decides when to use it based on workflow context:

- After vibe-check validation (orchestrator → SPEC-AGENT)
- After spec completion (SPEC-AGENT → DEV-AGENT)
- After implementation (DEV-AGENT completes → Checkpoint 1)
- After Checkpoint 1 approval (orchestrator → QA-AGENT)
- After QA approval (QA-AGENT completes → Checkpoint 2)
- After Checkpoint 2 approval (orchestrator merges → Done)

## Workflow Phases

### 1. Planning → Spec

**Trigger:** Orchestrator has validated approach with vibe-check

**Actions:**
- Create sub-issue with title: `[SPEC] {feature name}`
- Update parent labels: Remove `Agent:None`, add `Agent:Spec`, change to `Phase:Spec`
- Update parent status: Backlog → Todo
- Add comment to parent: `[PLANNING] Vibe-check validated. Creating spec sub-issue for SPEC-AGENT.`

**Linear API calls:**
```javascript
// Get parent issue details (for project inheritance)
const parent = await linear_getIssueById("parent-issue-id");

// Create spec sub-issue
const specIssue = await linear_createIssue({
  title: "[SPEC] Feature name",
  parentId: "parent-issue-id",
  description: "Planning context:\n\n{vibe-check results}\n\nRequirements:\n{from parent issue}",
  teamId: "57dfac47-8b23-4841-a760-e8f1d144c10d",
  projectId: parent.project?.id, // Inherit parent's project
  cycleId: parent.cycle?.id // Inherit parent's cycle
})

// Update status to Todo
linear_updateIssue({
  id: "parent-issue-id",
  stateId: "91f7c12d-0131-4a8f-883f-20ea5a095720" // Todo
})

// Remove old Agent label (Agent:None)
linear_removeIssueLabel({
  id: "parent-issue-id",
  labelId: "15e72e00-0f69-4eaf-9ede-3859766f1b7e" // Agent:None
})

// Remove old Phase label (Phase:Planning)
linear_removeIssueLabel({
  id: "parent-issue-id",
  labelId: "c429859c-1147-4b5b-894b-73106c9cb1b7" // Phase:Planning
})

// Add new Agent label (Agent:Spec)
linear_addIssueLabel({
  id: "parent-issue-id",
  labelId: "6a997911-b2a8-427a-af03-f3407edc8398" // Agent:Spec
})

// Add new Phase label (Phase:Spec)
linear_addIssueLabel({
  id: "parent-issue-id",
  labelId: "14e817b3-01d2-49d9-b7af-33177e099602" // Phase:Spec
})

// Add transition comment
linear_addIssueComment({
  issueId: "parent-issue-id",
  body: "[PLANNING] Approach validated by vibe-check. Passing to SPEC-AGENT for research and architecture design."
})
```

### 2. Spec → Dev

**Trigger:** SPEC-AGENT has completed technical specification

**Actions:**
- Create sub-issue with title: `[DEV] {feature name}`
- Update parent labels: Remove `Agent:Spec`, add `Agent:Dev`, change to `Phase:Dev`
- Update parent status: Todo → In Progress
- Link to spec sub-issue in description
- Add comment to parent

**Linear API calls:**
```javascript
// Get parent issue details (for project inheritance)
const parent = await linear_getIssueById("parent-issue-id");

// Create dev sub-issue
const devIssue = await linear_createIssue({
  title: "[DEV] Feature name",
  parentId: "parent-issue-id",
  description: "Implement feature per spec in PHM-XXX-1.\n\nKey files to modify:\n{from spec}\n\nSee full spec in sub-issue PHM-XXX-1.",
  teamId: "57dfac47-8b23-4841-a760-e8f1d144c10d",
  projectId: parent.project?.id, // Inherit parent's project
  cycleId: parent.cycle?.id // Inherit parent's cycle
})

// Update status to In Progress
linear_updateIssue({
  id: "parent-issue-id",
  stateId: "3d26f665-923b-4497-b9ce-1a8195a3e5c7" // In Progress
})

// Remove old Agent label (Agent:Spec)
linear_removeIssueLabel({
  id: "parent-issue-id",
  labelId: "6a997911-b2a8-427a-af03-f3407edc8398" // Agent:Spec
})

// Remove old Phase label (Phase:Spec)
linear_removeIssueLabel({
  id: "parent-issue-id",
  labelId: "14e817b3-01d2-49d9-b7af-33177e099602" // Phase:Spec
})

// Add new Agent label (Agent:Dev)
linear_addIssueLabel({
  id: "parent-issue-id",
  labelId: "1ec5953b-a316-4091-ae9c-4a4814bc32e3" // Agent:Dev
})

// Add new Phase label (Phase:Dev)
linear_addIssueLabel({
  id: "parent-issue-id",
  labelId: "d2d3ee45-30be-431d-80a6-64163f692c65" // Phase:Dev
})

// Add transition comment
linear_addIssueComment({
  issueId: "parent-issue-id",
  body: "[SPEC] Architecture complete. Spec available in PHM-XXX-1. Passing to DEV-AGENT for implementation."
})
```

### 3. Dev Complete (Checkpoint 1)

**Trigger:** DEV-AGENT has completed implementation

**Actions:**
- Update parent status: In Progress → In Review (marks Checkpoint 1 - user reviews frontend)
- Update parent labels: Remove `Agent:Dev`, keep `Phase:Dev` until QA launches
- Add comment to parent indicating Checkpoint 1
- Note: QA sub-issue created later when user approves and says "Ready for QA"

**Linear API calls:**
```javascript
// Update status to In Review (Checkpoint 1 - user reviews)
linear_updateIssue({
  id: "parent-issue-id",
  stateId: "b095092b-dcb4-4456-9a0d-e35158850305" // In Review
})

// Remove Agent:Dev label (orchestrator takes over for Checkpoint 1)
linear_removeIssueLabel({
  id: "parent-issue-id",
  labelId: "1ec5953b-a316-4091-ae9c-4a4814bc32e3" // Agent:Dev
})

// Add Agent:None label
linear_addIssueLabel({
  id: "parent-issue-id",
  labelId: "15e72e00-0f69-4eaf-9ede-3859766f1b7e" // Agent:None
})

// Note: Keep Phase:Dev label until QA launches

// Add Checkpoint 1 comment
linear_addIssueComment({
  issueId: "parent-issue-id",
  body: "[DEV] Implementation complete on branch feature/phm-XXX-description. Ready for Checkpoint 1 review. Test at http://localhost:3002"
})
```

### 4. Launch QA (After Checkpoint 1 Approval)

**Trigger:** User has approved at Checkpoint 1, ready for QA

**Actions:**
- Create sub-issue with title: `[QA] {feature name}`
- Update parent labels: Remove `Phase:Dev`, add `Agent:QA`, change to `Phase:QA`
- Status stays In Review
- Include branch name in description
- Add comment to parent

**Linear API calls:**
```javascript
// Get parent issue details (for project inheritance)
const parent = await linear_getIssueById("parent-issue-id");

// Create QA sub-issue
const qaIssue = await linear_createIssue({
  title: "[QA] Feature name",
  parentId: "parent-issue-id",
  description: "Test implementation on branch: feature/phm-XXX-description\n\nTest requirements from spec (PHM-XXX-1):\n{testing requirements}\n\nCode changes (PHM-XXX-2):\n{files modified}",
  teamId: "57dfac47-8b23-4841-a760-e8f1d144c10d",
  projectId: parent.project?.id, // Inherit parent's project
  cycleId: parent.cycle?.id // Inherit parent's cycle
})

// Status stays "In Review" (no update needed)

// Remove old Agent label (Agent:None from Checkpoint 1)
linear_removeIssueLabel({
  id: "parent-issue-id",
  labelId: "15e72e00-0f69-4eaf-9ede-3859766f1b7e" // Agent:None
})

// Remove old Phase label (Phase:Dev)
linear_removeIssueLabel({
  id: "parent-issue-id",
  labelId: "d2d3ee45-30be-431d-80a6-64163f692c65" // Phase:Dev
})

// Add new Agent label (Agent:QA)
linear_addIssueLabel({
  id: "parent-issue-id",
  labelId: "240e6885-52dd-495c-b9ed-00092ac4cb7f" // Agent:QA
})

// Add new Phase label (Phase:QA)
linear_addIssueLabel({
  id: "parent-issue-id",
  labelId: "aba3a1b0-762d-4133-8aea-33f03c01f7ce" // Phase:QA
})

// Add transition comment
linear_addIssueComment({
  issueId: "parent-issue-id",
  body: "[QA] Checkpoint 1 approved. Passing to QA-AGENT for security scan and E2E testing."
})
```

### 5. QA Complete (Checkpoint 2)

**Trigger:** QA-AGENT has approved (tests passing, security clean)

**Actions:**
- Update parent labels: Remove `Agent:QA` and `Phase:QA`, add `Agent:None`
- Status stays In Review (already set at Checkpoint 1)
- Add completion comment to parent indicating Checkpoint 2

**Linear API calls:**
```javascript
// Status stays "In Review" (no update needed - already set at Checkpoint 1)

// Remove old Agent label (Agent:QA)
linear_removeIssueLabel({
  id: "parent-issue-id",
  labelId: "240e6885-52dd-495c-b9ed-00092ac4cb7f" // Agent:QA
})

// Remove old Phase label (Phase:QA)
linear_removeIssueLabel({
  id: "parent-issue-id",
  labelId: "aba3a1b0-762d-4133-8aea-33f03c01f7ce" // Phase:QA
})

// Add Agent:None label to indicate no active agent
linear_addIssueLabel({
  id: "parent-issue-id",
  labelId: "15e72e00-0f69-4eaf-9ede-3859766f1b7e" // Agent:None
})

// Add Checkpoint 2 comment
linear_addIssueComment({
  issueId: "parent-issue-id",
  body: "[QA] Security scan clean, all tests passing. Ready for Checkpoint 2 review and integration."
})
```

### 6. Merge Complete (In Review → Done)

**Trigger:** Orchestrator has merged PR, ready to close parent

**Actions:**
- Verify all sub-issues are Done (auto-close validation)
- Update parent status: In Review → Done
- Add final comment

**Linear API calls:**
```javascript
// Get parent issue with sub-issues
const parent = await linear_getIssueById("parent-issue-id");

// Verify all sub-issues are Done before closing parent
const allSubsDone = parent.children?.nodes?.every(
  child => child.state.name === "Done"
);

if (!allSubsDone) {
  // Log warning if trying to close with incomplete sub-issues
  console.warn("Some sub-issues not Done yet. Check before closing parent.");
}

// Update status to Done
linear_updateIssue({
  id: "parent-issue-id",
  stateId: "9d9410ce-fece-4f2b-98db-04307019b309" // Done
})

// Add merge comment
linear_addIssueComment({
  issueId: "parent-issue-id",
  body: "✅ PR merged to main. Feature complete. All sub-issues done."
})
```

## Usage Examples

### Orchestrator Launching SPEC-AGENT

After running vibe-check and validating the approach, the orchestrator would think:

"I need to hand off to SPEC-AGENT. The linear-handoff skill should create the spec sub-issue and update the parent issue fields."

Claude will automatically invoke this skill to:
1. Create `[SPEC]` sub-issue
2. Update parent status to Todo
3. Update labels: `Agent:Spec`, `Phase:Spec`
4. Add handoff comment

Then launch SPEC-AGENT with context pointing to the new sub-issue.

### DEV-AGENT Completing Work (Checkpoint 1)

When DEV-AGENT finishes implementation, it signals completion. The orchestrator then:

"DEV-AGENT is done. This is Checkpoint 1 - user needs to review the frontend."

Claude invokes this skill to:
1. Update parent status to In Review
2. Update labels: Remove `Agent:Dev`, add `Agent:None`
3. Add Checkpoint 1 comment with test URL

Then orchestrator notifies user: "Code complete on port 3002. Please test manually."

### After Checkpoint 1 Approval

When user approves at Checkpoint 1 and says "Ready for QA", the orchestrator:

"User approved Checkpoint 1. Time to launch QA-AGENT."

Claude invokes this skill to:
1. Create `[QA]` sub-issue
2. Update labels: Remove `Phase:Dev`, add `Agent:QA`, `Phase:QA`
3. Add handoff comment

Then launch QA-AGENT with test requirements.

## Important Notes

**When to create sub-issues:**
DO create sub-issues for:
- Each orchestrated phase (SPEC, DEV, QA)
- Example: PHM-57 creates PHM-58 [SPEC], PHM-59 [DEV], PHM-60 [QA]

DON'T create sub-issues for:
- Checkpoint 1 iterations (user testing and quick fixes)
- CSS tweaks, spacing, colors, small bugs during active testing
- Orchestrator making direct edits based on user feedback
- These happen directly on parent issue, no new sub-issues

**Automated project/cycle inheritance:**
When creating sub-issues, this skill automatically:
- Reads parent issue to get project and cycle
- Assigns sub-issue to same project as parent
- Assigns sub-issue to same cycle as parent (if set)
- No manual cleanup needed after orchestrated workflow

**Agent responsibility for sub-issue status:**
Each agent manages their sub-issue status lifecycle:

**When starting work:**
- SPEC-AGENT: Marks PHM-XXX-1 as "In Progress" when beginning research
- DEV-AGENT: Marks PHM-XXX-2 as "In Progress" when starting implementation
- QA-AGENT: Marks PHM-XXX-3 as "In Progress" when beginning tests

**When completing work:**
- SPEC-AGENT: Marks PHM-XXX-1 as "Done" after posting spec
- DEV-AGENT: Marks PHM-XXX-2 as "Done" after implementation
- QA-AGENT: Marks PHM-XXX-3 as "Done" after tests pass

**Status = "In Review" is reserved for USER review only**

**Parent auto-close validation:**
When merging (Phase 6), this skill:
- Verifies all sub-issues are in "Done" state
- Only then closes parent issue to "Done"
- Warns if trying to close with incomplete sub-issues

**Parallel workflows supported:**
System handles multiple features simultaneously:
- PHM-57 (Feature A) in QA while PHM-61 (Feature B) in Spec
- Independent features don't block each other
- Each parent issue tracks its own sub-issues independently
- Example: QA-AGENT on one feature, SPEC-AGENT on another

**Phase-tagged comments:**
All comments added by this skill use phase tags:
- `[PLANNING]` - During initial validation
- `[SPEC]` - Specification phase
- `[DEV]` - Development phase
- `[QA]` - Quality assurance phase

**Labels required:**
This skill uses Linear labels for orchestration tracking:
- **Agent labels:** Agent:None, Agent:Spec, Agent:Dev, Agent:QA
- **Phase labels:** Phase:Planning, Phase:Spec, Phase:Dev, Phase:QA

**Label IDs (already created):**
- Agent:None: `15e72e00-0f69-4eaf-9ede-3859766f1b7e`
- Agent:Spec: `6a997911-b2a8-427a-af03-f3407edc8398`
- Agent:Dev: `1ec5953b-a316-4091-ae9c-4a4814bc32e3`
- Agent:QA: `240e6885-52dd-495c-b9ed-00092ac4cb7f`
- Phase:Planning: `c429859c-1147-4b5b-894b-73106c9cb1b7`
- Phase:Spec: `14e817b3-01d2-49d9-b7af-33177e099602`
- Phase:Dev: `d2d3ee45-30be-431d-80a6-64163f692c65`
- Phase:QA: `aba3a1b0-762d-4133-8aea-33f03c01f7ce`

**Workflow State IDs:**
- Backlog: `fe1a9f10-44f1-47dd-8f7f-dfb1cc62d07c`
- Todo: `91f7c12d-0131-4a8f-883f-20ea5a095720`
- In Progress: `3d26f665-923b-4497-b9ce-1a8195a3e5c7`
- In Review: `b095092b-dcb4-4456-9a0d-e35158850305`
- Done: `9d9410ce-fece-4f2b-98db-04307019b309`

See setup guide: `.claude/LINEAR_SETUP.md`

**Sub-issue naming:**
All sub-issues use consistent naming:
- `[SPEC] Feature name` - Created in Phase 1
- `[DEV] Feature name` - Created in Phase 2
- `[QA] Feature name` - Created in Phase 4 (after Checkpoint 1)

This makes filtering and searching easy in Linear UI.

**Workflow state flow:**

**Parent issue:**
- Backlog → Todo (Phase 1: Launch spec)
- Todo → In Progress (Phase 2: Launch dev)
- In Progress → In Review (Phase 3: Dev complete, Checkpoint 1 - **USER reviews**)
- In Review (Phase 4: Launch QA after approval)
- In Review (Phase 5: QA complete, Checkpoint 2 - **USER reviews**)
- In Review → Done (Phase 6: Merge after approval)

**Sub-issues:**
- Created (initial state: Todo or Backlog)
- Agent starts work → In Progress (agent marks when starting)
- Agent completes → Done (agent marks when finishing)
- **NOTE:** "In Review" status is for USER review only, not for agent work

**Team ID:**
Replace `"team-id"` with actual team ID from Linear (e.g., from PHM issues).

## Integration with Agents

**Agents don't call this skill directly.** The orchestrator (main chat) uses it to manage transitions. Agents focus on their work (spec writing, coding, testing) and signal completion. The orchestrator handles all Linear administrative tasks via this skill.

## Troubleshooting

**If sub-issues aren't created:**
- Verify Linear MCP is connected
- Check team ID is correct
- Ensure parent issue exists

**If labels don't update:**
- Verify label IDs are correct
- Check labels exist in Linear (should already be created)
- Ensure using correct tool: `linear_addIssueLabel` and `linear_removeIssueLabel`
- See `.claude/LINEAR_SETUP.md` for label details

**If comments don't appear:**
- Verify issue ID is correct
- Check Linear API permissions
- Ensure comment body is valid markdown
