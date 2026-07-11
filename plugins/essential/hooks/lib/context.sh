#!/usr/bin/env bash
# Common utilities for Claude Code hooks and context management

# Output hook context as JSON
# Parameters:
#   $1: Hook event name (e.g., "SessionStart", "UserPromptSubmit")
#   $2: Context string to include in additionalContext
#
# Outputs JSON structure with escaped context
output_hook_context() {
  local event_name="$1"
  local context="$2"

  # Escape context for JSON using jq
  local escaped_context
  escaped_context=$(printf '%s' "$context" | jq -Rs .)

  # Output JSON structure
  cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "$event_name",
    "additionalContext": $escaped_context
  }
}
EOF

  exit 0
}
