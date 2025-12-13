#!/usr/bin/env bash
# Session context loader for Claude Code
# Compatible with bash 3.2+

set -euo pipefail

# Source context library scripts
source "$CLAUDE_PLUGIN_ROOT/shared/scripts/session-start.sh"

# Run session start hook with session header
run_session_start_hook --plugin-dir "$CLAUDE_PLUGIN_ROOT" --with-session-header --constitution-paths "$HOME/.claude" "$CLAUDE_PLUGIN_ROOT"
