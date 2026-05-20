#!/usr/bin/env bash
set -euo pipefail

# post-rewrite-hook.sh -- PostToolUse hook
# Auto-verifies integrity after any successful history-rewriting op (git or jj).
# Input:  JSON on stdin { tool_name, tool_input: { command }, tool_output, exit_code }
# Output: stderr = verify results (always shown to agent)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

INPUT="$(cat)"

extract_command() {
  local input="$1"
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null
  else
    printf '%s' "$input" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1
  fi
}

extract_exit_code() {
  local input="$1"
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$input" | jq -r '.tool_output.exit_code // .exit_code // empty' 2>/dev/null
  else
    printf '%s' "$input" | sed -n 's/.*"exit_code"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p' | head -1
  fi
}

COMMAND="$(extract_command "$INPUT")"
EXIT_CODE="$(extract_exit_code "$INPUT")"

# Trigger on any history-rewriting op (git or jj)
case "$COMMAND" in
  git\ rebase*) ;;
  jj\ rebase*|jj\ split*|jj\ edit*|jj\ squash*|jj\ absorb*|jj\ abandon*) ;;
  *) exit 0 ;;
esac

# Only on successful op
if [ "${EXIT_CODE:-1}" != "0" ]; then
  exit 0
fi

# Need a checkpoint to compare against
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
CKPT_BASE="$(checkpoint_dir "$REPO_ROOT")"
CKPT_FILE="${CKPT_BASE}/.checkpoint"

if [ ! -f "$CKPT_FILE" ]; then
  printf 'No checkpoint found, skipping integrity verify\n' >&2
  exit 0
fi

VERIFY_OUTPUT=""
# VERIFY_EXIT captured for diagnostic visibility; verdict is parsed from VERIFY_OUTPUT
# shellcheck disable=SC2034
VERIFY_EXIT=0
# shellcheck disable=SC2034
VERIFY_OUTPUT="$(bash "$SCRIPT_DIR/verify.sh" 2>&1)" || VERIFY_EXIT=$?

{
  printf '── Integrity Check ──────────────────────\n'

  GIT_MATCH="$(printf '%s' "$VERIFY_OUTPUT" | grep '^GIT_TREE_MATCH=' | cut -d= -f2)"
  CONTENT_MATCH="$(printf '%s' "$VERIFY_OUTPUT" | grep '^CONTENT_MATCH=' | cut -d= -f2)"

  printf 'GIT_TREE:  %s  (baseline vs HEAD)\n' "${GIT_MATCH:-UNKNOWN}"
  printf 'CONTENT:   %s  (filesystem check)\n' "${CONTENT_MATCH:-UNKNOWN}"

  if [ "${GIT_MATCH:-}" = "FAIL" ] || [ "${CONTENT_MATCH:-}" = "FAIL" ]; then
    printf '%s\n' "$VERIFY_OUTPUT" | grep -v '^GIT_TREE_MATCH=' | grep -v '^CONTENT_MATCH=' | \
      grep -v '^POST_GIT_TREE_SHA=' | grep -v '^POST_CONTENT_HASH=' | \
      grep -v '^$' || true
  fi

  printf '─────────────────────────────────────────\n'
} >&2

# Always exit 0 -- informational only, never block
exit 0
