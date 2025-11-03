# Worktree Architecture for Parallel Agent Operations

## Overview

This system allows multiple agents to work on different features simultaneously using Git worktrees.

## Directory Structure

```
/Users/patrickmeehan/knowledge-base/projects/ksi_prototype_sdk/  (main repo)
├─ .claude/                    ← Orchestration config
├─ .worktrees/                 ← Agent workspaces (gitignored)
│   ├─ phm-60/                ← Feature branch: feature/phm-60
│   │   ├─ app/
│   │   ├─ components/
│   │   ├─ package.json
│   │   └─ [all repo files for this branch]
│   ├─ phm-61/                ← Feature branch: feature/phm-61
│   └─ phm-65/                ← Feature branch: feature/phm-65
├─ .worktree-registry.json    ← Tracks active worktrees (orchestrator managed)
└─ [main repo files]          ← Orchestrator works here
```

## Orchestrator Responsibilities

### 1. Worktree Creation

When launching dev-agent for a new feature:

```javascript
// Check if worktree exists
const worktreePath = `.worktrees/phm-${issueNumber}`;
const branchName = `feature/phm-${issueNumber}-${slug}`;

// Check worktree registry
const registry = await readWorktreeRegistry();

if (!registry[`phm-${issueNumber}`]) {
  // Create worktree
  await bash(`git worktree add ${worktreePath} -b ${branchName}`);

  // Install dependencies in worktree
  await bash(`cd ${worktreePath} && npm install`);

  // Register worktree
  await updateWorktreeRegistry({
    issue: `phm-${issueNumber}`,
    path: worktreePath,
    branch: branchName,
    port: assignPort(issueNumber),
    status: 'active',
    createdAt: new Date().toISOString()
  });
}
```

### 2. Port Management

Each worktree gets a unique dev server port:

```javascript
// Port allocation strategy
const BASE_PORT = 3002;

function assignPort(issueNumber) {
  const registry = readWorktreeRegistry();
  const usedPorts = Object.values(registry).map(w => w.port);

  // Extract issue number (e.g., PHM-60 → 60)
  const num = parseInt(issueNumber.replace('phm-', ''));

  // Try port 3000 + issue number first
  const preferredPort = 3000 + num;

  if (!usedPorts.includes(preferredPort)) {
    return preferredPort;
  }

  // Find next available port
  let port = BASE_PORT;
  while (usedPorts.includes(port)) {
    port++;
  }
  return port;
}
```

### 3. Agent Launch with Context

```javascript
// Launch dev-agent with worktree context
Task({
  subagent_type: "dev-agent",
  prompt: `
CRITICAL: You are working in an isolated worktree for this feature.

**Your working directory:** ${worktreePath}
**Your branch:** ${branchName}
**Your dev server port:** ${port}

All file operations must be relative to: ${worktreePath}

When starting dev server:
cd ${worktreePath} && npm run dev -- -p ${port}

When done, update Linear issue PHM-${issueNumber} and signal completion.
DO NOT modify files outside your worktree.
`
})
```

### 4. Cleanup After Merge

```javascript
// Phase 6: After PR merged
async function cleanupWorktree(issueNumber) {
  const registry = await readWorktreeRegistry();
  const worktree = registry[`phm-${issueNumber}`];

  if (worktree) {
    // Kill dev server if running
    await bash(`lsof -ti:${worktree.port} | xargs kill -9 || true`);

    // Remove worktree
    await bash(`git worktree remove ${worktree.path} --force`);

    // Delete branch
    await bash(`git branch -D ${worktree.branch}`);
    await bash(`git push origin --delete ${worktree.branch}`);

    // Update registry
    delete registry[`phm-${issueNumber}`];
    await writeWorktreeRegistry(registry);
  }
}
```

## Agent Behavior

### Dev-Agent Modifications

**Section 2: Pre-Implementation Verification**

```markdown
**CRITICAL: Check if working in worktree**

The orchestrator may launch you in an isolated worktree. Check your context:

```javascript
// You will receive working directory in your launch context
const workingDir = process.env.AGENT_WORKING_DIR || '.';
const devPort = process.env.AGENT_DEV_PORT || 3002;

// ALL file operations relative to working directory
await bash(`cd ${workingDir} && ...`);
```

**DO NOT create a new branch if working in worktree** - branch already created by orchestrator.

**When starting dev server:**
```bash
cd ${workingDir} && npm run dev -- -p ${devPort}
```

**When done:**
- All changes are in your worktree
- Commit to your branch
- Signal completion to orchestrator
- Orchestrator will create PR and merge
```

### QA-Agent Modifications

**Section 2: Pre-flight Check**

```markdown
**CRITICAL: Check working directory and port**

If launched in worktree:
- Working directory: ${workingDir}
- Dev server port: ${devPort}

**Pre-flight checks:**
```bash
# Check if server running on YOUR port
lsof -ti:${devPort} || echo "Server not running on port ${devPort}"

# If running, verify it responds
curl -s -o /dev/null -w "%{http_code}" http://localhost:${devPort}
```

**Browser tests:**
- Use `http://localhost:${devPort}` (not hardcoded 3002)
- All tests run in your worktree context
```

## Worktree Registry Format

`.worktree-registry.json`:

```json
{
  "phm-60": {
    "path": ".worktrees/phm-60",
    "branch": "feature/phm-60-news-feed",
    "port": 3060,
    "status": "active",
    "agent": "dev-agent",
    "createdAt": "2025-11-03T12:00:00Z",
    "lastActive": "2025-11-03T13:45:00Z"
  },
  "phm-61": {
    "path": ".worktrees/phm-61",
    "branch": "feature/phm-61-article-carousel",
    "port": 3061,
    "status": "testing",
    "agent": "qa-agent",
    "createdAt": "2025-11-03T11:30:00Z",
    "lastActive": "2025-11-03T14:00:00Z"
  }
}
```

## Parallel Workflow Example

```
Time: 12:00
├─ User: "Work on PHM-60 (news feed)"
├─ Orchestrator creates .worktrees/phm-60, port 3060
└─ Launches dev-agent in worktree

Time: 12:15
├─ User: "Also start PHM-61 (carousel)"
├─ Orchestrator creates .worktrees/phm-61, port 3061
└─ Launches spec-agent (no worktree needed yet)

Time: 12:30
├─ PHM-60 dev-agent: Code complete, server running on 3060
├─ Orchestrator: "Test PHM-60 at http://localhost:3060"
└─ PHM-61 spec-agent: Spec complete, ready for dev

Time: 12:45
├─ User: Testing PHM-60 at localhost:3060
├─ Orchestrator launches dev-agent for PHM-61 in .worktrees/phm-61
└─ PHM-61 dev server starts on port 3061

Time: 13:00
├─ User: Approved PHM-60, ready for QA
├─ Orchestrator launches qa-agent for PHM-60 (uses port 3060)
└─ PHM-61 dev-agent still working (port 3061)
```

**Result:** Three worktrees active simultaneously with no conflicts.

## Limitations & Constraints

### 1. Dev Server Ports

- Each worktree gets unique port (3000+issue_number)
- Max ~60 parallel features before port conflicts
- Kill unused servers to free ports

### 2. Disk Space

- Each worktree is ~200MB (node_modules per worktree)
- Cleanup merged features to free space
- Recommendation: Max 5 active worktrees

### 3. Context Awareness

- Agents must respect working directory parameter
- All bash commands must cd to worktree first
- File paths must be relative to worktree

### 4. Registry Synchronization

- Registry is file-based (potential race conditions)
- Use file locking for concurrent updates
- Orchestrator is single source of truth

## Error Handling

### Worktree Creation Fails

```javascript
try {
  await bash(`git worktree add ${worktreePath} -b ${branchName}`);
} catch (error) {
  if (error.includes('already exists')) {
    // Worktree exists, verify it's valid
    await bash(`git worktree list`);
    // Use existing worktree
  } else if (error.includes('branch already exists')) {
    // Branch exists, checkout in worktree
    await bash(`git worktree add ${worktreePath} ${branchName}`);
  } else {
    throw error;
  }
}
```

### Port Conflicts

```javascript
// Before starting dev server
const portInUse = await bash(`lsof -ti:${port}`);

if (portInUse) {
  // Port occupied, try next port
  port = assignPort(issueNumber, usedPorts);
  await updateWorktreeRegistry({ port });
}
```

### Orphaned Worktrees

```javascript
// Cleanup command (run periodically)
async function cleanupOrphanedWorktrees() {
  const gitWorktrees = await bash(`git worktree list --porcelain`);
  const registry = await readWorktreeRegistry();

  // Find worktrees not in registry
  const orphans = parseWorktrees(gitWorktrees).filter(
    w => !Object.values(registry).some(r => r.path === w.path)
  );

  // Remove orphans
  for (const orphan of orphans) {
    await bash(`git worktree remove ${orphan.path} --force`);
  }
}
```

## Migration Path

### Phase 1: Setup Infrastructure

1. Add `.worktrees/` to `.gitignore`
2. Create worktree registry management functions
3. Update linear-handoff skill with worktree creation logic

### Phase 2: Update Agents

1. Modify dev-agent.md to check for worktree context
2. Modify qa-agent.md to use dynamic ports
3. Test with single worktree first

### Phase 3: Enable Parallel Operations

1. Test two parallel features
2. Monitor registry for conflicts
3. Verify cleanup after merge

### Phase 4: Production Ready

1. Add monitoring dashboard (active worktrees, ports, disk usage)
2. Add automatic cleanup on stale worktrees (>7 days inactive)
3. Document user-facing workflow

## Commands Reference

```bash
# List all worktrees
git worktree list

# Create worktree
git worktree add .worktrees/phm-60 -b feature/phm-60

# Remove worktree
git worktree remove .worktrees/phm-60

# Prune deleted worktrees from git's records
git worktree prune

# Check what's using a port
lsof -ti:3060

# Kill process on port
lsof -ti:3060 | xargs kill -9
```

## Future Enhancements

### 1. Worktree Pooling

Pre-create worktrees to speed up agent launches:

```javascript
// Maintain pool of 3 ready worktrees
const pool = ['worktree-1', 'worktree-2', 'worktree-3'];

// When agent needs worktree, assign from pool
// When agent done, reset worktree and return to pool
```

### 2. Resource Limits

```javascript
const MAX_WORKTREES = 5;
const MAX_DISK_USAGE_GB = 5;

async function canCreateWorktree() {
  const activeCount = Object.keys(registry).length;
  const diskUsage = await calculateWorktreeDiskUsage();

  return activeCount < MAX_WORKTREES && diskUsage < MAX_DISK_USAGE_GB;
}
```

### 3. Worktree Monitoring Dashboard

```javascript
// Real-time view of active worktrees
{
  "phm-60": {
    "status": "🟢 Dev server running (port 3060)",
    "branch": "feature/phm-60-news-feed",
    "age": "2 hours",
    "diskUsage": "180 MB"
  }
}
```

## Troubleshooting

**Problem:** Agent created files in wrong directory
- **Check:** Did orchestrator pass working directory in launch context?
- **Fix:** Add AGENT_WORKING_DIR to agent launch parameters

**Problem:** Port already in use
- **Check:** `lsof -ti:3060`
- **Fix:** Kill process or assign new port

**Problem:** Worktree won't remove ("contains modified or untracked files")
- **Check:** `cd .worktrees/phm-60 && git status`
- **Fix:** `git worktree remove .worktrees/phm-60 --force`

**Problem:** Registry out of sync with actual worktrees
- **Fix:** Run `cleanupOrphanedWorktrees()` function
