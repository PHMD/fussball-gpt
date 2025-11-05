#!/usr/bin/env bash

# work-on.sh
# Automated Linear-to-worktree workflow
# Fetches ticket from Linear, creates worktree, opens in Warp
# Part of the Agentic Worktree Development System

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
TEMPLATES_DIR="$HOME/knowledge-base/templates/agentic-worktree"
DEFAULT_TYPE="feature"

# Usage information
usage() {
    cat << EOF
Usage: $(basename "$0") TICKET_ID [OPTIONS]

Fetch ticket from Linear, create worktree, and open in Warp.

ARGUMENTS:
    TICKET_ID               Linear ticket ID (e.g., PHM-81)

OPTIONS:
    -t, --type TYPE         Worktree type: feature|staging (default: feature)
    -f, --from BRANCH       Branch to create from (default: auto-detect from git)
    --no-warp               Skip opening Warp tab
    -h, --help              Show this help message

EXAMPLES:
    # Work on PHM-81
    $(basename "$0") PHM-81

    # Work on PHM-81, create from specific branch
    $(basename "$0") PHM-81 -f develop

    # Work on PHM-81, skip Warp opening
    $(basename "$0") PHM-81 --no-warp

PREREQUISITES:
    - Linear MCP must be configured
    - Must run from within a git repository
    - Warp terminal (optional, use --no-warp to skip)

EOF
    exit 1
}

# Parse command line arguments
TICKET_ID=""
WORKTREE_TYPE="$DEFAULT_TYPE"
FROM_BRANCH=""  # Will be detected from git config
OPEN_WARP=true

if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Missing ticket ID${NC}"
    usage
fi

TICKET_ID="$1"
shift

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            WORKTREE_TYPE="$2"
            shift 2
            ;;
        -f|--from)
            FROM_BRANCH="$2"
            shift 2
            ;;
        --no-warp)
            OPEN_WARP=false
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            usage
            ;;
    esac
done

# Validate ticket ID format
if [[ ! "$TICKET_ID" =~ ^PHM-[0-9]+$ ]]; then
    echo -e "${RED}Error: Invalid ticket ID format '$TICKET_ID'${NC}"
    echo "Expected format: PHM-XX (e.g., PHM-81)"
    exit 1
fi

# Validate worktree type
if [[ ! "$WORKTREE_TYPE" =~ ^(feature|staging)$ ]]; then
    echo -e "${RED}Error: Invalid worktree type '$WORKTREE_TYPE'${NC}"
    echo "Must be one of: feature, staging"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

PROJECT_PATH=$(git rev-parse --show-toplevel)
PROJECT_NAME=$(basename "$PROJECT_PATH")

# Detect default branch if not specified
if [ -z "$FROM_BRANCH" ]; then
    # Try to detect default branch from remote
    FROM_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')

    # Fallback to current branch if detection fails
    if [ -z "$FROM_BRANCH" ]; then
        FROM_BRANCH=$(git rev-parse --abbrev-ref HEAD)
        echo -e "${YELLOW}⚠ Could not detect default branch, using current: $FROM_BRANCH${NC}"
    fi
fi

echo -e "${BLUE}=== Work-On Automation ===${NC}"
echo ""
echo "Ticket ID:     $TICKET_ID"
echo "Project:       $PROJECT_NAME"
echo "Type:          $WORKTREE_TYPE"
echo "From branch:   $FROM_BRANCH"
echo ""

# Step 1: Fetch ticket from Linear using Claude Code's Linear MCP
echo -e "${BLUE}Step 1: Fetching ticket from Linear...${NC}"

# Create a temporary Python script to call Linear MCP via Claude Code
TEMP_SCRIPT=$(mktemp)
cat > "$TEMP_SCRIPT" << 'PYTHON_EOF'
#!/usr/bin/env python3
import sys
import json
import subprocess

ticket_id = sys.argv[1]

# Use Claude Code CLI to call Linear MCP
# Note: This assumes Claude Code is installed and Linear MCP is configured
try:
    # Call linear_getIssueById via Claude Code
    result = subprocess.run(
        ['claude', 'mcp', 'call', 'linear', 'linear_getIssueById',
         '--id', ticket_id],
        capture_output=True,
        text=True,
        check=True
    )

    # Parse the result
    ticket_data = json.loads(result.stdout)
    print(json.dumps(ticket_data, indent=2))

except subprocess.CalledProcessError as e:
    print(f"Error fetching ticket: {e.stderr}", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Error parsing ticket data: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_EOF

chmod +x "$TEMP_SCRIPT"

# Note: The above approach uses Claude CLI, which may not exist yet.
# For MVP, we'll use a simpler approach - create a placeholder .ticket.md
# and instruct the user to fill it via Claude Code chat.

echo -e "${YELLOW}⚠ Note: Linear MCP integration requires Claude Code${NC}"
echo -e "${YELLOW}Creating worktree with placeholder ticket context...${NC}"
echo -e "${YELLOW}Use Claude Code chat to fetch and populate ticket details${NC}"
echo ""

# Clean up temp script
rm -f "$TEMP_SCRIPT"

# For now, create a basic structure
TICKET_TITLE="Work on $TICKET_ID"
BRANCH_NAME=$(echo "$TICKET_ID" | tr '[:upper:]' '[:lower:]')

# Step 2: Determine worktree path (sibling to project)
WORKTREE_PARENT=$(dirname "$PROJECT_PATH")
WORKTREE_NAME="$PROJECT_NAME-$BRANCH_NAME"
WORKTREE_PATH="$WORKTREE_PARENT/$WORKTREE_NAME"

echo "Worktree will be created at: $WORKTREE_PATH"
echo ""

# Check if worktree already exists
if [ -d "$WORKTREE_PATH" ]; then
    echo -e "${YELLOW}⚠ Worktree already exists at $WORKTREE_PATH${NC}"
    read -p "Continue and use existing worktree? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
    EXISTING_WORKTREE=true
else
    EXISTING_WORKTREE=false
fi

# Step 3: Create worktree if needed
if [ "$EXISTING_WORKTREE" = false ]; then
    echo -e "${BLUE}Step 2: Creating git worktree...${NC}"

    # Check if branch already exists
    if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
        echo -e "${YELLOW}⚠ Branch $BRANCH_NAME already exists${NC}"
        read -p "Continue and use existing branch? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborted."
            exit 0
        fi

        # Create worktree from existing branch
        mkdir -p "$(dirname "$WORKTREE_PATH")"
        git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"
    else
        # Create new branch and worktree
        mkdir -p "$(dirname "$WORKTREE_PATH")"
        git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" "$FROM_BRANCH"
    fi

    echo -e "${GREEN}✓ Worktree created${NC}"

    # Step 4: Copy CLAUDE.md template
    echo -e "${BLUE}Step 3: Copying CLAUDE.md template...${NC}"
    case $WORKTREE_TYPE in
        staging)
            cp "$TEMPLATES_DIR/claude-staging.md" "$WORKTREE_PATH/CLAUDE.md"
            CONTEXT_STRING="Staging Worktree - Rapid Prototyping"
            ;;
        feature)
            cp "$TEMPLATES_DIR/claude-feature.md" "$WORKTREE_PATH/CLAUDE.md"
            CONTEXT_STRING="Feature $TICKET_ID"
            ;;
    esac
    echo -e "${GREEN}✓ CLAUDE.md copied ($WORKTREE_TYPE)${NC}"

    # Step 5: Copy agents and skills
    echo -e "${BLUE}Step 4: Copying agents and skills...${NC}"
    mkdir -p "$WORKTREE_PATH/.claude"
    cp -r "$TEMPLATES_DIR/agents" "$WORKTREE_PATH/.claude/"
    cp -r "$TEMPLATES_DIR/skills" "$WORKTREE_PATH/.claude/"
    echo -e "${GREEN}✓ Agents and skills copied${NC}"
else
    echo -e "${YELLOW}Using existing worktree${NC}"
fi

# Step 6: Create .ticket.md placeholder
echo -e "${BLUE}Step 5: Creating .ticket.md...${NC}"
cat > "$WORKTREE_PATH/.ticket.md" << EOF
# $TICKET_ID

**Status:** Loading...

## Quick Actions

\`\`\`bash
# Fetch ticket details via Claude Code
# In Claude Code chat, run:
# "Fetch ticket $TICKET_ID from Linear and update this file"
\`\`\`

## Ticket Context

<!-- Will be populated by Claude Code -->

---

*This file is auto-generated by work-on.sh*
*Use Claude Code to fetch complete ticket context from Linear*
EOF

echo -e "${GREEN}✓ .ticket.md created (use Claude Code to populate)${NC}"

# Step 8: Open in Warp if requested
if [ "$OPEN_WARP" = true ]; then
    echo -e "${BLUE}Step 7: Opening in Warp...${NC}"

    # Check if Warp is installed
    if [ ! -d "/Applications/Warp.app" ]; then
        echo -e "${YELLOW}⚠ Warp not found, skipping Warp tab opening${NC}"
    else
        # Use osascript to open new Warp tab and run commands
        osascript << APPLESCRIPT
tell application "Warp"
    activate
end tell

tell application "System Events"
    tell process "Warp"
        keystroke "t" using {command down}
        delay 1
        keystroke "cd \"$WORKTREE_PATH\""
        delay 0.3
        keystroke return
        delay 1
        keystroke "claude --dangerously-skip-permissions $CONTEXT_STRING"
        delay 0.3
        keystroke return
    end tell
end tell
APPLESCRIPT

        echo -e "${GREEN}✓ Warp tab opened${NC}"
    fi
else
    echo -e "${YELLOW}Skipping Warp tab opening${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}=== Setup Complete ===${NC}"
echo ""
echo "Ticket ID:    $TICKET_ID"
echo "Worktree:     $WORKTREE_PATH"
echo "Branch:       $BRANCH_NAME"
echo ""
echo "Next steps:"
echo "  1. Wait for Warp tab to open with Claude Code"
echo "  2. Ask Claude to fetch ticket $TICKET_ID and update .ticket.md"
echo "  3. Start working!"
echo ""
echo -e "${YELLOW}Manual alternative:${NC}"
echo "  cd $WORKTREE_PATH"
echo "  claude code"
echo ""
