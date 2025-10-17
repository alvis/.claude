#!/usr/bin/env bash
# Session context loader for Claude Code
# Compatible with bash 3.2+

set -euo pipefail

# Get script directory and plugin root
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(dirname "$HOOK_DIR")"

# Source context library scripts
source "$HOOK_DIR/../../../scripts/context.sh"
source "$HOOK_DIR/../../../scripts/constitution.sh"
source "$HOOK_DIR/../../../scripts/session-start.sh"

# Run session start hook with session header
run_session_start_hook --plugin-dir "$PLUGIN_ROOT" --with-session-header --constitution-paths "$HOME/.claude"
