#!/usr/bin/env bash
# Session start hook: emits the session-type header and the plugin environment
# block as one payload. Instruction files (CLAUDE.md, MAINAGENT.md) are emitted by
# their own `sed | jq` hooks in plugin.json, not from here, so every payload
# stays under the per-payload preview limit.
# Compatible with bash 3.2+

# Get script directory
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source shared context library (output_hook_context)
# shellcheck source=/dev/null
source "$SCRIPTS_DIR/context.sh"

# Get session type header based on the session source.
get_session_type_header() {
  local source="$1"
  local header=""

  case "$source" in
    startup)
      header="🚀 **New Session Started**"
      ;;
    resume)
      header="♻️  **Resuming Session**"
      ;;
    clear)
      header="🆕 **Fresh Start** (reloading full context)"
      ;;
    compact)
      header="🗜️  **Compact** (invoked from auto or manual compact)"
      ;;
  esac

  echo -n "$header"
}

# Emit the session header and the essential plugin environment block. Only
# essential registers this hook, so the environment block is emitted exactly
# once — no per-plugin flag gating is needed.
run_session_start_hook() {
  local input src
  input=$(cat)
  src=$(echo "$input" | jq -r '.source // "unknown"')

  local CONTEXT=""
  CONTEXT+=$(get_session_type_header "$src")
  if [[ -n "$CONTEXT" ]]; then
    CONTEXT+=$'\n\n'
  fi

  local plugin_root
  plugin_root="$(cd "$SCRIPTS_DIR/../.." && pwd)"
  if [[ -f "$plugin_root/scripts/context.sh" ]]; then
    # shellcheck source=/dev/null
    source "$plugin_root/scripts/context.sh"
    CONTEXT+=$(get_plugin_context)
  fi

  output_hook_context "SessionStart" "$CONTEXT"
}
