#!/usr/bin/env bash
# Session context loader for Claude Code
# Compatible with bash 3.2+

set -euo pipefail

# Get script directory and plugin root
PLUGIN_ROOT="$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")"

# Source context library scripts
source "$PLUGIN_ROOT/../../scripts/session-start.sh"

# Determine project and plugin directories
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
PLUGIN_DIR="${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}"

# Run session start hook with two constitution paths
run_session_start_hook --plugin-dir "$PLUGIN_ROOT" --constitution-paths "$PROJECT_DIR/.claude" "$PLUGIN_DIR"
