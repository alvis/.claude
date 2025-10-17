#!/usr/bin/env bash
# Reusable session start hook utilities for Claude Code plugins
# Compatible with bash 3.2+

# Get script directory
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source context library scripts
source "$SCRIPTS_DIR/constitution.sh"
source "$SCRIPTS_DIR/context.sh"

# Read session input from stdin and extract variables
# Parameters:
#   $1: "true" to export SESSION_ID, "false" to skip
# Sets global variables:
#   INPUT - The full JSON input
#   SOURCE - The session source (startup/resume/clear/compact/unknown)
#   SESSION_ID - Session identifier (if requested)
read_session_input() {
  local with_session_id="$1"

  INPUT=$(cat)
  SOURCE=$(echo "$INPUT" | jq -r '.source // "unknown"')

  if [[ "$with_session_id" == "true" ]]; then
    export SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
  fi
}

# Get session type header based on SOURCE
# Parameters:
#   $1: SOURCE value (startup/resume/clear/compact/unknown)
# Returns:
#   Formatted header string with emoji
get_session_type_header() {
  local source="$1"
  local header=""

  case "$source" in
    startup)
      header="🚀 **New Session Started**\n\n"
      ;;
    resume)
      header="♻️  **Resuming Session**\n\n"
      ;;
    clear)
      header="🆕 **Fresh Start** (reloading full context)\n\n"
      ;;
    compact)
      header="🗜️  **Compact** (invoked from auto or manual compact)\n\n"
      ;;
  esac

  echo -n "$header"
}

# Main session start hook orchestrator
# Parameters:
#   --plugin-dir: Path to plugin root directory (required for sourcing plugin context)
#   --with-session-id: Export SESSION_ID from input
#   --with-session-header: Add session type header to context
#   --constitution-paths: Space-separated list of paths for get_constitution_context
#
# Example usage:
#   run_session_start_hook --plugin-dir "$PLUGIN_ROOT" --with-session-id --constitution-paths "$PLUGIN_DIR"
#   run_session_start_hook --plugin-dir "$PLUGIN_ROOT" --with-session-header --constitution-paths "$HOME/.claude"
#   run_session_start_hook --plugin-dir "$PLUGIN_ROOT" --with-session-id --constitution-paths "$PROJECT_DIR/.claude" "$PLUGIN_DIR"
run_session_start_hook() {
  local plugin_dir=""
  local with_session_id=false
  local with_session_header=false
  local constitution_paths=()

  # Parse arguments
  while [[ $# -gt 0 ]]; do
    case $1 in
      --plugin-dir)
        plugin_dir="$2"
        shift 2
        ;;
      --with-session-id)
        with_session_id=true
        shift
        ;;
      --with-session-header)
        with_session_header=true
        shift
        ;;
      --constitution-paths)
        shift
        # Collect all remaining arguments as paths
        while [[ $# -gt 0 ]]; do
          constitution_paths+=("$1")
          shift
        done
        ;;
      *)
        shift
        ;;
    esac
  done

  # Read input from stdin
  read_session_input "$with_session_id"

  # Initialize context
  CONTEXT=""

  # Add session type header if requested
  if [[ "$with_session_header" == "true" ]]; then
    CONTEXT+=$(get_session_type_header "$SOURCE")
  fi

  # Source plugin context and add plugin-specific context
  if [[ -n "$plugin_dir" && -f "$plugin_dir/scripts/context.sh" ]]; then
    source "$plugin_dir/scripts/context.sh"
  fi
  CONTEXT+=$(get_plugin_context)

  # Add constitution context for each specified path
  for path in "${constitution_paths[@]}"; do
    CONTEXT+=$(get_constitution_context "$path")
  done

  # Output hook context as JSON
  output_hook_context "SessionStart" "$CONTEXT"
}
