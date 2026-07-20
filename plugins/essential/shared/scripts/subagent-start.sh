#!/usr/bin/env bash
# Subagent start hook: emits the plugin environment block as one payload. It
# omits the session-type header (subagents have no session source). Instruction
# files (CLAUDE.md, SUBAGENT.md) are emitted by their own `sed | jq` hooks in
# plugin.json, not from here, so every payload stays under the per-payload
# preview limit.
# Compatible with bash 3.2+

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source shared context library (output_hook_context)
# shellcheck source=/dev/null
source "$SCRIPTS_DIR/context.sh"

# Emit the essential plugin environment block. Only essential registers this
# hook, so the environment block is emitted exactly once.
run_subagent_start_hook() {
  local CONTEXT=""

  local plugin_root
  plugin_root="$(cd "$SCRIPTS_DIR/../.." && pwd)"
  if [[ -f "$plugin_root/scripts/context.sh" ]]; then
    # shellcheck source=/dev/null
    source "$plugin_root/scripts/context.sh"
    CONTEXT+=$(get_plugin_context)
  fi

  output_hook_context "SubagentStart" "$CONTEXT"
}
