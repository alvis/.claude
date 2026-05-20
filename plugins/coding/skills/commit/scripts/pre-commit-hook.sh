#!/usr/bin/env bash
set -euo pipefail

# pre-commit-hook.sh -- PreToolUse hook
# Backs up the working tree before any commit-ish or history-rewriting op (git or jj).
# Input:  JSON on stdin { tool_name, tool_input: { command } }
# Output: JSON on stdout (permissionDecision: "allow" + additionalContext)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

# Read JSON from stdin
INPUT="$(cat)"

extract_command() {
  local input="$1"
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null
  else
    printf '%s' "$input" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1
  fi
}

COMMAND="$(extract_command "$INPUT")"

# Trigger on git commit/rebase OR any jj history-rewriting op
case "$COMMAND" in
  git\ commit*|git\ rebase*) ;;
  jj\ rebase*|jj\ split*|jj\ edit*|jj\ squash*|jj\ absorb*|jj\ abandon*|jj\ new*|jj\ describe*) ;;
  *) exit 0 ;;
esac

# Run backup -- capture output, don't block on failure
BACKUP_OUTPUT=""
if BACKUP_OUTPUT="$(bash "$SCRIPT_DIR/backup.sh" 2>&1)"; then
  GIT_TREE_SHA="$(printf '%s' "$BACKUP_OUTPUT" | grep '^GIT_TREE_SHA=' | cut -d= -f2)"
  CONTENT_HASH="$(printf '%s' "$BACKUP_OUTPUT" | grep '^CONTENT_HASH=' | cut -d= -f2)"
  BACKUP_PATH="$(printf '%s' "$BACKUP_OUTPUT" | grep '^BACKUP_PATH=' | cut -d= -f2)"

  cat <<EOF
{
  "hookSpecificOutput": {
    "permissionDecision": "allow",
    "additionalContext": "Auto-backup: GIT_TREE_SHA=$GIT_TREE_SHA CONTENT_HASH=$CONTENT_HASH BACKUP_PATH=$BACKUP_PATH"
  }
}
EOF
else
  printf 'Warning: backup.sh failed (exit %s), proceeding anyway\n' "$?" >&2
  printf 'Backup output: %s\n' "$BACKUP_OUTPUT" >&2
  exit 0
fi
