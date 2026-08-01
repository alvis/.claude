#!/usr/bin/env bash
set -euo pipefail

: "${CLAUDE_PLUGIN_ROOT:?CLAUDE_PLUGIN_ROOT is required}"

exec "${CLAUDE_PLUGIN_ROOT}/scripts/pyrun.sh" \
  "${CLAUDE_PLUGIN_ROOT}/scripts/scan_potential_violations.py" "$@"
