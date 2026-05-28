#!/usr/bin/env bash
# guard-main-branch.sh
# Blocks git push or commit directly to main or any protected branch.
# Exit 2 = block the tool call entirely (Claude Code hook convention).
# Exit 1 = warn but allow.
# Exit 0 = allow silently.

set -euo pipefail

# Read the command Claude is about to run from stdin (JSON input)
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''))" 2>/dev/null || echo "")

# Protected branches — extend this list as needed
PROTECTED_BRANCHES=("main" "master" "develop" "production")

# Only inspect git push and git commit commands
if echo "$COMMAND" | grep -qE "^git (push|commit)"; then
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

  for branch in "${PROTECTED_BRANCHES[@]}"; do
    if [ "$CURRENT_BRANCH" = "$branch" ]; then
      echo "🚫 BLOCKED: Direct $( echo "$COMMAND" | awk '{print $2}') to '$branch' is not allowed." >&2
      echo "   devflow always works on feature branches. Check your current branch." >&2
      echo "   Current branch: $CURRENT_BRANCH" >&2
      exit 2
    fi
  done

  # Also block explicit push to main: git push origin main
  if echo "$COMMAND" | grep -qE "push.*\b(main|master|develop|production)\b"; then
    echo "🚫 BLOCKED: Explicit push to protected branch detected." >&2
    echo "   Command: $COMMAND" >&2
    exit 2
  fi
fi

exit 0
