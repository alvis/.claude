#!/usr/bin/env bash
# lifecycle-up.sh -- probe for a running Storybook on a port; spawn if absent.
#
# Contract:
#   lifecycle-up.sh --port <N> [--no-spawn] [--cwd <dir>] [--script <name>]
#
# Behavior:
#   1. Probe http://localhost:<N>/index.json with curl. If it returns 200,
#      report reuse and exit 0 (no spawn, no teardown later).
#   2. Otherwise, unless --no-spawn is set, discover the storybook script
#      name from <cwd>/package.json (or use --script) and run
#         npm run <script> -- --port <N> --ci --no-open
#      in the background. PID -> $RUN_DIR/sb.pid, logs -> $RUN_DIR/sb.log.
#   3. Poll http://localhost:<N>/index.json up to 90s (1s interval) for
#      readiness. On ready, emit {"spawned":true,"port":N} and exit 0.
#   4. With --no-spawn and no instance reachable, exit 1 with an error.
#
# Writes:
#   $RUN_DIR/sb.pid  (PID of the spawned Storybook, when applicable)
#   $RUN_DIR/sb.log  (combined stdout/stderr of the spawned Storybook)
#   ${TMPDIR:-/tmp}/storybook-audit/.current-run-id  (run id for siblings)
#
# Exit codes:
#   0  Ready (reused or spawned)
#   1  Not ready (--no-spawn with no instance, or spawn timed out)
#   2  Usage / dependency error
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: lifecycle-up.sh --port <N> [--no-spawn] [--cwd <dir>] [--script <name>]

Probe http://localhost:<N>/index.json. If unreachable and --no-spawn is not
set, spawn `npm run <script> -- --port <N> --ci --no-open` in the project at
<cwd> (defaults to $PWD), write its pid to $RUN_DIR/sb.pid, and poll for
readiness up to 90 seconds. Emits {"spawned":<bool>,"port":<N>} to stdout.
EOF
}

PORT=""
NO_SPAWN=0
CWD="$PWD"
SCRIPT_NAME=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)       PORT="${2:-}"; shift 2 ;;
    --no-spawn)   NO_SPAWN=1; shift ;;
    --cwd)        CWD="${2:-}"; shift 2 ;;
    --script)     SCRIPT_NAME="${2:-}"; shift 2 ;;
    -h|--help)    usage; exit 0 ;;
    *)
      printf 'lifecycle-up.sh: unknown flag: %s\n' "$1" >&2
      usage; exit 2 ;;
  esac
done

if [[ -z "$PORT" ]]; then
  printf 'lifecycle-up.sh: --port is required\n' >&2
  exit 2
fi

for tool in jq curl; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    printf 'lifecycle-up.sh: %s is required but not installed\n' "$tool" >&2
    exit 2
  fi
done

# Resolve $RUN_DIR. Reuse a current run id when present; otherwise mint one.
ROOT="${TMPDIR:-/tmp}/storybook-audit"
mkdir -p "$ROOT"
CURRENT_FILE="$ROOT/.current-run-id"
if [[ -s "$CURRENT_FILE" ]]; then
  RUN_ID="$(cat "$CURRENT_FILE")"
else
  RUN_ID="$(date +%Y%m%d-%H%M%S)-$$"
  printf '%s\n' "$RUN_ID" > "$CURRENT_FILE"
fi
RUN_DIR="$ROOT/$RUN_ID"
mkdir -p "$RUN_DIR"

URL="http://localhost:$PORT/index.json"

probe() {
  curl -fsS --max-time 2 "$URL" >/dev/null 2>&1
}

# Step 1: probe for an existing instance.
if probe; then
  jq -cn --argjson p "$PORT" '{spawned:false, port:$p}'
  exit 0
fi

if [[ "$NO_SPAWN" -eq 1 ]]; then
  printf 'lifecycle-up.sh: no Storybook reachable at %s and --no-spawn was set\n' "$URL" >&2
  exit 1
fi

# Step 2: resolve the script name from package.json if not provided.
if [[ -z "$SCRIPT_NAME" ]]; then
  PKG="$CWD/package.json"
  if [[ -f "$PKG" ]]; then
    SCRIPT_NAME="$(jq -r '((.scripts // {}) | keys[] | select(startswith("storybook"))) // empty' "$PKG" | head -n1 || true)"
  fi
  [[ -z "$SCRIPT_NAME" ]] && SCRIPT_NAME="storybook"
fi

# Step 3: spawn in the background and capture pid + logs.
(
  cd "$CWD"
  # `--` forwards remaining flags to the underlying storybook binary.
  nohup npm run "$SCRIPT_NAME" -- --port "$PORT" --ci --no-open \
    >"$RUN_DIR/sb.log" 2>&1 &
  printf '%s\n' "$!" > "$RUN_DIR/sb.pid"
)

# Step 4: poll readiness up to 90s.
DEADLINE=$(( $(date +%s) + 90 ))
while (( $(date +%s) < DEADLINE )); do
  if probe; then
    jq -cn --argjson p "$PORT" '{spawned:true, port:$p}'
    exit 0
  fi
  sleep 1
done

printf 'lifecycle-up.sh: Storybook did not become ready on %s within 90s\n' "$URL" >&2
printf 'lifecycle-up.sh: tail of %s/sb.log follows:\n' "$RUN_DIR" >&2
tail -n 40 "$RUN_DIR/sb.log" >&2 || true
exit 1
