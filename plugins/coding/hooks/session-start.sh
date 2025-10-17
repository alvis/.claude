#!/usr/bin/env bash
# Session context loader for Claude Code
# Compatible with bash 3.2+

set -euo pipefail

# Source context library scripts
source "$CLAUDE_PLUGIN_ROOT/../../scripts/session-start.sh"

# Run session start hook with two constitution paths
run_session_start_hook --plugin-dir "$CLAUDE_PLUGIN_ROOT" --constitution-paths "$CLAUDE_PLUGIN_ROOT/.claude" "$CLAUDE_PLUGIN_ROOT"
