#!/usr/bin/env bash
# SubagentStart drops raw stdout, so wrap the instructions in the
# hookSpecificOutput JSON envelope for the context to reach the subagent
set -euo pipefail

jq -Rs '{hookSpecificOutput: {hookEventName: "SubagentStart", additionalContext: .}}' \
  "${CLAUDE_PLUGIN_ROOT}/hooks/lean-code/instructions.md"
