#!/usr/bin/env bash
# lifecycle-down.sh -- SIGTERM the Storybook spawned by lifecycle-up.sh.
#
# Contract:
#   lifecycle-down.sh
#
# Reads:
#   $RUN_DIR/sb.pid   (when present)
#
# Behavior:
#   Read the pid file from the current run dir (resolved via the run-id
#   pointer at ${TMPDIR:-/tmp}/storybook-audit/.current-run-id) and send
#   SIGTERM. Missing pid file, dead process, or absent run-id are all
#   non-fatal -- this script always exits 0 so it is safe in cleanup chains.
set -euo pipefail

ROOT="${TMPDIR:-/tmp}/storybook-audit"
CURRENT_FILE="$ROOT/.current-run-id"

if [[ ! -s "$CURRENT_FILE" ]]; then
  exit 0
fi

RUN_ID="$(cat "$CURRENT_FILE")"
RUN_DIR="$ROOT/$RUN_ID"
PID_FILE="$RUN_DIR/sb.pid"

if [[ ! -s "$PID_FILE" ]]; then
  exit 0
fi

PID="$(cat "$PID_FILE")"
if [[ -z "$PID" ]] || ! [[ "$PID" =~ ^[0-9]+$ ]]; then
  exit 0
fi

# Ignore failures: the process may already be gone, or we may not own it.
kill -TERM "$PID" 2>/dev/null || true

# Best-effort: give it a moment, then SIGKILL if still alive.
for _ in 1 2 3 4 5; do
  if ! kill -0 "$PID" 2>/dev/null; then
    rm -f "$PID_FILE"
    exit 0
  fi
  sleep 1
done

kill -KILL "$PID" 2>/dev/null || true
rm -f "$PID_FILE"
exit 0
