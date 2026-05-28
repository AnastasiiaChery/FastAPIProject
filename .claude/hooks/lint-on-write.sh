#!/usr/bin/env bash
# lint-on-write.sh
# Runs ruff check --fix and ruff format on any .py file after it is
# written or edited. Keeps code style consistent without manual steps.
# Runs silently on success — only prints on error.

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path', d.get('path','')))" 2>/dev/null || echo "")

# Only run on Python files
if [[ "$FILE_PATH" != *.py ]]; then
  exit 0
fi

# Check ruff is available
if ! command -v ruff &>/dev/null && ! command -v uvx &>/dev/null; then
  exit 0  # silently skip if ruff not installed
fi

RUFF_CMD="ruff"
if ! command -v ruff &>/dev/null; then
  RUFF_CMD="uvx ruff"
fi

# Run lint fix + format, suppress output on success
if ! $RUFF_CMD check --fix "$FILE_PATH" --silent 2>/dev/null; then
  echo "⚠️  ruff found issues in $FILE_PATH that could not be auto-fixed." >&2
  $RUFF_CMD check "$FILE_PATH" >&2
fi

$RUFF_CMD format "$FILE_PATH" --silent 2>/dev/null || true

exit 0