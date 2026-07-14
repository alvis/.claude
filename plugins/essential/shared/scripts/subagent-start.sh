#!/usr/bin/env bash
# Reusable subagent start hook utilities for Claude Code plugins.
# Mirrors session-start but omits session-specific context (no session-type
# header, no session id) — a subagent only needs the shared project and
# constitution context. In addition, any constitution path carrying a
# SUBAGENT.md gets it embedded as subagent-specific instructions.
# Compatible with bash 3.2+

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPTS_DIR/constitution.sh"
source "$SCRIPTS_DIR/context.sh"

# Main subagent start hook orchestrator
# Parameters:
#   --plugin-dir: Path to plugin root directory (for plugin context)
#   --constitution-paths: Space-separated list of paths for get_constitution_context
#
# Example usage:
#   run_subagent_start_hook --plugin-dir "$PLUGIN_ROOT" --constitution-paths "$PLUGIN_DIR"
run_subagent_start_hook() {
  local plugin_dir=""
  local with_plugin_context=false
  local constitution_paths=()

  # Parse arguments
  while [[ $# -gt 0 ]]; do
    case $1 in
      --plugin-dir)
        plugin_dir="$2"
        shift 2
        ;;
      --with-plugin-context)
        with_plugin_context=true
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

  # No session-specific header/id for subagents.
  local CONTEXT=""

  # Source plugin context and add plugin-specific context, but only when the
  # caller explicitly requests it via --with-plugin-context. Only essential's
  # own hook passes the flag, so the environment block is emitted once instead
  # of being duplicated across every plugin's hook. Calling get_plugin_context
  # only after a successful source also avoids the latent "command not found"
  # crash when a plugin ships no scripts/context.sh.
  if [[ "$with_plugin_context" == "true" && -n "$plugin_dir" && -f "$plugin_dir/scripts/context.sh" ]]; then
    source "$plugin_dir/scripts/context.sh"
    CONTEXT+=$(get_plugin_context)
  fi

  # Add constitution context for each specified path
  local path
  for path in "${constitution_paths[@]}"; do
    CONTEXT+=$(get_constitution_context "$path")
  done

  # Embed subagent-specific instructions (SUBAGENT.md) for each path,
  # resolving the {{PLUGIN_DIR}} placeholder to the absolute plugin path so
  # embedded file references work from any project repo.
  local abs_path
  for path in "${constitution_paths[@]}"; do
    if [[ -f "$path/SUBAGENT.md" ]]; then
      abs_path="$(cd "$path" && pwd)"
      CONTEXT+="# As a team player\n\n"
      CONTEXT+="$(sed "s|{{PLUGIN_DIR}}|$abs_path|g" "$path/SUBAGENT.md")\n\n"
    fi
  done

  # Output hook context as JSON
  output_hook_context "SubagentStart" "$CONTEXT"
}
