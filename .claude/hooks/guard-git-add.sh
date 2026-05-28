#!/usr/bin/env bash
# guard-git-add.sh
# Blocks "git add ." and "git add -A" to prevent accidental staging
# of secrets, unrelated files, or generated artifacts.
# Forces explicit file listing — a devflow convention enforced at runtime.

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''))" 2>/dev/null || echo "")

if echo "$COMMAND" | grep -qE "^git add\s+(\.|--all|-A)(\s|$)"; then
  echo "🚫 BLOCKED: 'git add .' and 'git add -A' are not allowed in devflow." >&2
  echo "   Always list files explicitly: git add path/to/file.py path/to/other.py" >&2
  echo "   This prevents accidental staging of .env files, secrets, or unrelated changes." >&2
  exit 2
fi

# Extract file arguments (everything after "git add") and check for sensitive patterns.
# Matches: .env* | *.pem | *secret* | *credentials* | *.key (case-insensitive)
ARGS=$(echo "$COMMAND" | sed 's/^git add[[:space:]]*//')
MATCHED=$(echo "$ARGS" | tr ' ' '\n' | grep -iE '(^\.env(\.|$|.+$)|\.pem$|secret|credentials|\.key$)' | head -1 || true)
if [ -n "$MATCHED" ]; then
  echo "🚫 BLOCKED: Sensitive file detected in 'git add': '$MATCHED'" >&2
  echo "   Files matching .env*, *.pem, *secret*, *credentials*, *.key must not be staged." >&2
  exit 2
fi

exit 0