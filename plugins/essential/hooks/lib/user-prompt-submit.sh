#!/usr/bin/env bash
# UserPromptSubmit hook for token usage tracking
# Monitors cumulative token consumption and alerts every 25k tokens
# Compatible with bash 3.2+

set -euo pipefail

# Get plugin root from first argument
PLUGIN_ROOT="$1"

# Get script directory
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source shared utility scripts
source "$SCRIPTS_DIR/context.sh"
source "$SCRIPTS_DIR/reminder.sh"

# Optionally source plugin-specific reminder context if it exists
if [[ -f "$PLUGIN_ROOT/scripts/context.sh" ]]; then
  source "$PLUGIN_ROOT/scripts/context.sh"
fi

# Read JSON from stdin
INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // ""')

# Check token usage and get base reminder context
CONTEXT=$(check_and_remind_token_usage "$SESSION_ID" "$TRANSCRIPT_PATH")

# If boundaries were crossed AND plugin has custom reminder context function, add it
if [[ -n "$CONTEXT" ]] && type get_plugin_context &>/dev/null; then
  CONTEXT+=$(get_plugin_context)
fi

# Output hook context as JSON
output_hook_context "UserPromptSubmit" "$CONTEXT"
