---
trigger: auto
name: kb-research-handoff
description: Automatically organize knowledge base research work into epics and create worktrees
version: 1.0.0
---

# KB Research Handoff Skill

**Purpose**: Streamline knowledge base research workflow by organizing work into epics, creating Linear tickets, and setting up worktrees automatically.

**v1.0 Features:**
- ✅ Search for existing epics by topic
- ✅ Interactive epic selection or creation
- ✅ Create parent epic if needed
- ✅ Create child feature ticket
- ✅ Invoke worktree setup with ticket ID

## When Invoked

**Automatically triggers when:**
- User requests KB research work (e.g., "research vendor options", "investigate caching strategies")
- User mentions working on knowledge base epics
- User wants to organize research into structured workflow

**Keywords that trigger:**
- "research", "investigate", "analyze", "evaluate"
- "knowledge base", "KB", "documentation"
- "epic", "organize research", "structured research"

## What It Does

### 1. Search for Existing Epics

```typescript
// Search Linear for existing epics by topic
linear.searchIssues({
  query: "parent:null project:Kicker ${topic}",
  limit: 10
})

// Filter results:
// - No parent (parentId === null) = epic
// - Project = Kicker (or specified project)
// - Contains topic keywords
```

### 2. Interactive Epic Selection

**If epics found:**
```
Found 2 existing epics related to "${topic}":

1. PHM-100: RAG Optimization (14 children)
   - Status: In Progress
   - Updated: 2 days ago

2. PHM-50: Caching Strategy Research (5 children)
   - Status: Backlog
   - Updated: 1 week ago

Options:
[1] Add to PHM-100 (RAG Optimization)
[2] Add to PHM-50 (Caching Strategy Research)
[3] Create new epic
[4] Cancel

Your choice:
```

**If no epics found:**
```
No existing epics found for "${topic}".

Create new epic? [Y/n]
```

### 3. Create Parent Epic (If Needed)

```typescript
linear.createIssue({
  title: "${epic_title}",
  description: `
    ## Objective
    ${objective}

    ## Research Areas
    - ${area_1}
    - ${area_2}
    - ${area_3}

    ## Workflow
    Children will be created for each research area.
  `,
  projectId: "PROJECT_ID",
  labels: ["enhancement", "Agent:None"],
  stateId: workflowStates.Backlog,
  priority: 3  // Medium priority for research
})
```

### 4. Create Child Feature Ticket

```typescript
linear.createIssue({
  title: "${feature_title}",
  description: `
    ## Requirements
    ${user_requirements}

    ## Parent Epic
    Part of ${epic_title} (${epic_id})

    ## Workflow
    - [ ] Specification (SPEC-AGENT)
    - [ ] Development (DEV-AGENT)
    - [ ] Quality Assurance (QA-AGENT)
  `,
  parentId: "${epic_id}",
  projectId: "PROJECT_ID",
  labels: ["feature", "Agent:None"],
  stateId: workflowStates.Todo,
  priority: 3
})
```

### 5. Invoke Worktree Setup

```bash
# Call work-on.sh with the new ticket ID
work-on.sh ${ticket_id}

# This will:
# - Create worktree at ../worktrees/${ticket_id}/
# - Copy CLAUDE.md + agents + skills
# - Create .ticket.md placeholder
# - Open Warp tab with Claude Code
```

## Requirements

**Linear Configuration:**
- Project ID (e.g., Kicker project)
- Team ID
- Agent labels (Agent:None, Agent:Spec, Agent:Dev, Agent:QA)
- Workflow states (Todo, In Progress, In Review, Done)

**Category Labels:**
- `enhancement` - For epic creation
- `feature` - For child tickets

**See**: `.claude/LINEAR_SETUP.md` for label configuration

## Usage Examples

### Example 1: New Research Topic

```
User: "I need to research semantic caching strategies for our KB system"

Skill invokes:
1. Searches Linear for epics containing "semantic caching" or "caching strategies"
2. No matches found
3. Prompts: "Create new epic for Semantic Caching Research? [Y/n]"
4. User confirms: "y"
5. Creates epic: PHM-110 "Semantic Caching Research"
6. Creates child ticket: PHM-111 "Evaluate semantic caching strategies"
7. Calls: work-on.sh PHM-111
8. Opens Warp with worktree ready
```

### Example 2: Add to Existing Epic

```
User: "I want to add vector store comparison to the RAG work"

Skill invokes:
1. Searches Linear for "RAG" epics
2. Finds PHM-100: RAG Optimization (14 children)
3. Prompts: "Add to existing epic PHM-100? [Y/n]"
4. User confirms: "y"
5. Creates child ticket: PHM-112 "Compare vector store options"
   - parentId: "PHM-100"
6. Calls: work-on.sh PHM-112
7. Opens Warp with worktree ready
```

### Example 3: Multiple Epics Match

```
User: "Research authentication patterns for KB access"

Skill invokes:
1. Searches Linear for "authentication" epics
2. Finds:
   - PHM-90: Authentication System (8 children)
   - PHM-95: Security Audit (12 children)
3. Prompts: "Which epic? [1] PHM-90, [2] PHM-95, [3] New, [4] Cancel"
4. User selects: "1"
5. Creates child ticket: PHM-113 "KB authentication patterns"
   - parentId: "PHM-90"
6. Calls: work-on.sh PHM-113
7. Opens Warp with worktree ready
```

## Epic Naming Convention

**Format:** `${Topic} ${Type}`

**Examples:**
- "RAG Optimization" (epic for optimizing RAG system)
- "Caching Strategy Research" (epic for caching investigations)
- "Security Audit Phase 2" (epic for security work)

**Child ticket format:** `${Action} ${Specific_Topic}`

**Examples:**
- "Evaluate semantic caching strategies" (child of Caching epic)
- "Compare vector store options" (child of RAG epic)
- "Implement session-based auth" (child of Authentication epic)

## Error Handling

**If Linear API fails:**
- Log error
- Provide manual instructions
- Don't block workflow

**If no project specified:**
- Use default project (Kicker)
- Warn user

**If epic creation fails:**
- Create standalone ticket without parent
- Log warning
- Continue with worktree setup

**If worktree setup fails:**
- Provide manual worktree creation instructions
- Linear ticket still created for tracking

## Integration with Worktree System

**Dependencies:**
- `work-on.sh` script (must exist in templates/agentic-worktree/scripts/)
- Linear MCP (must be configured)
- Git repository (must be valid repo)

**Workflow:**
```
User request
  ↓
kb-research-handoff skill
  ├─ Search epics
  ├─ Interactive selection
  ├─ Create epic (if needed)
  ├─ Create child ticket
  └─ Call work-on.sh
      ↓
work-on.sh
  ├─ Create worktree
  ├─ Copy templates
  ├─ Create .ticket.md
  └─ Open Warp + Claude Code
```

## Configuration

**Project-specific config:**
```json
{
  "projectId": "LINEAR_PROJECT_ID",
  "teamId": "LINEAR_TEAM_ID",
  "defaultPriority": 3,
  "workflowStates": {
    "Backlog": "STATE_ID",
    "Todo": "STATE_ID",
    "InProgress": "STATE_ID",
    "InReview": "STATE_ID",
    "Done": "STATE_ID"
  },
  "labels": {
    "enhancement": "LABEL_ID",
    "feature": "LABEL_ID",
    "Agent:None": "LABEL_ID"
  }
}
```

## Benefits

1. **Organized research** - All related work grouped under epics
2. **Automatic progress tracking** - Epic shows aggregate child status
3. **No manual setup** - Worktree created automatically
4. **Context preserved** - Linear ticket linked to worktree
5. **Consistent workflow** - Same process for all KB research

## Token Cost

**Minimal**: ~500-1000 tokens per invocation
- Linear API calls: External (not in context)
- User prompts: ~200 tokens
- Skill logic: ~300 tokens
- Error handling: ~100 tokens

## Related Skills

- `linear-handoff` - Updates Linear during agent workflow
- `vibe-check-planning` - Validates research approach
- `pieces-context-logger` - Logs research findings after completion

---

*Part of the Agentic Worktree Development System*
*Version 1.0.0 - Epic Support*
