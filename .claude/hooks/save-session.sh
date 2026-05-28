#!/usr/bin/env bash
# save-session.sh
# Saves current devflow session state on Stop so an interrupted
# session can be resumed. Writes .devflow-state.json at repo root.

set -euo pipefail

STATE_FILE=".devflow-state.json"

# Collect state
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
WORKTREES=$(git worktree list --porcelain 2>/dev/null | grep "^worktree " | awk '{print $2}' | tail -n +2 | tr '\n' ',' | sed 's/,$//')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")

# Try to detect active ticket from branch name
TICKET=$(echo "$CURRENT_BRANCH" | grep -oE '[A-Z]+-[0-9]+' | head -1 || echo "")

python3 - <<EOF
import json, os

state = {
    "saved_at": "$TIMESTAMP",
    "current_branch": "$CURRENT_BRANCH",
    "active_ticket": "$TICKET",
    "worktrees": [w for w in "$WORKTREES".split(",") if w],
    "repo_root": "$REPO_ROOT",
    "resume_hint": f"Run /devflow $TICKET to resume" if "$TICKET" else "No active devflow ticket detected"
}

with open("$STATE_FILE", "w") as f:
    json.dump(state, f, indent=2)

print(f"💾 Session state saved to $STATE_FILE")
if "$TICKET":
    print(f"   Active ticket: $TICKET — resume with /devflow $TICKET")
EOF

exit 0
