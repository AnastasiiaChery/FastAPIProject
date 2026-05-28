#!/usr/bin/env bash
# guard-env-read.sh
# Blocks Claude from reading .env files to prevent secret exposure.
# This hook runs before the Read tool executes.

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null || echo "")

# Get basename of the file
BASENAME=$(basename "$FILE_PATH" 2>/dev/null || echo "")

# Block any file starting with .env
if [[ "$BASENAME" == .env* ]]; then
  echo "🚫 BLOCKED: Reading .env files is not allowed." >&2
  echo "   File: $FILE_PATH" >&2
  echo "   .env files contain secrets and should never be read by Claude." >&2
  echo "   If you need configuration values, ask the user to provide them directly." >&2
  echo "   See CLAUDE.md security rules for more information." >&2
  exit 2
fi

exit 0