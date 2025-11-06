#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Usage message
if [ -z "$1" ]; then
    echo -e "${RED}Usage: ./scripts/merge-feature.sh <feature-branch-name>${NC}"
    echo "Example: ./scripts/merge-feature.sh feature/phm-119-query-classification"
    exit 1
fi

FEATURE_BRANCH=$1

echo -e "${GREEN}=== Safe Feature Merge Script ===${NC}"
echo ""

# 1. Verify we're on staging
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "staging" ]; then
    echo -e "${RED}ERROR: You must be on the 'staging' branch to run this script${NC}"
    echo "Current branch: $CURRENT_BRANCH"
    echo "Run: git checkout staging"
    exit 1
fi

# 2. Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}WARNING: You have uncommitted changes in staging${NC}"
    git status --short
    echo ""
    read -p "Commit these changes first? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Please commit your changes and run this script again."
        exit 1
    fi
fi

# 3. Fetch latest changes
echo -e "${GREEN}Fetching latest changes...${NC}"
git fetch origin

# 4. Check if feature branch exists
if ! git rev-parse --verify "$FEATURE_BRANCH" >/dev/null 2>&1; then
    echo -e "${RED}ERROR: Branch '$FEATURE_BRANCH' does not exist${NC}"
    exit 1
fi

# 5. Show what will be merged
echo ""
echo -e "${GREEN}Changes in $FEATURE_BRANCH that will be merged:${NC}"
git log --oneline staging..$FEATURE_BRANCH

# 6. Check for conflicts
echo ""
echo -e "${GREEN}Checking for potential conflicts...${NC}"
git merge --no-commit --no-ff "$FEATURE_BRANCH" 2>&1 | tee /tmp/merge-check.log || true

if grep -q "CONFLICT" /tmp/merge-check.log; then
    echo ""
    echo -e "${RED}⚠️  CONFLICTS DETECTED ⚠️${NC}"
    echo ""
    echo "Conflicting files:"
    git diff --name-only --diff-filter=U
    echo ""
    echo -e "${YELLOW}RECOMMENDED WORKFLOW:${NC}"
    echo "1. Abort this merge: git merge --abort"
    echo "2. Go to feature worktree: cd ../ksi_prototype-phm-XXX"
    echo "3. Merge staging into feature: git merge staging"
    echo "4. Resolve conflicts there"
    echo "5. Test the feature"
    echo "6. Come back and re-run this script"
    echo ""
    read -p "Do you want to abort and follow recommended workflow? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git merge --abort
        echo "Merge aborted. Follow steps above."
        exit 1
    else
        echo "Continuing with merge (you'll need to resolve conflicts manually)..."
    fi
else
    echo -e "${GREEN}✓ No conflicts detected${NC}"
fi

# 7. Show files that will change
echo ""
echo -e "${GREEN}Files modified in this merge:${NC}"
git diff --name-only staging $FEATURE_BRANCH | head -20

# 8. Show critical file changes
CRITICAL_FILES=("app/api/query/route.ts" "components/ui/shadcn-io/ai/response.tsx" "components/ui/shadcn-io/ai/response-with-citations.tsx")
echo ""
echo -e "${YELLOW}Checking critical files for changes:${NC}"
for file in "${CRITICAL_FILES[@]}"; do
    if git diff --quiet staging $FEATURE_BRANCH -- "$file" 2>/dev/null; then
        echo "  $file - No changes"
    else
        echo -e "  ${YELLOW}$file - MODIFIED${NC}"
    fi
done

# 9. Final confirmation
echo ""
read -p "Proceed with merge? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    git merge --abort 2>/dev/null || true
    echo "Merge cancelled."
    exit 1
fi

# 10. Complete the merge
if grep -q "CONFLICT" /tmp/merge-check.log; then
    echo ""
    echo -e "${YELLOW}Conflicts detected. Resolve them now.${NC}"
    echo "When done:"
    echo "  git add <resolved-files>"
    echo "  git commit"
else
    git commit -m "Merge $FEATURE_BRANCH into staging"
    echo ""
    echo -e "${GREEN}✓ Merge completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Test the merged changes"
    echo "  2. git push origin staging"
fi
