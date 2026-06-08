#!/usr/bin/env bash
# pyrun.sh — resolve the newest available Python >= 3.13 and exec a script through it.
#
# Resolution:
#   - Scan candidate interpreter names python3.20 .. python3.13 (descending),
#     plus bare python3.
#   - For each one found on PATH, parse X.Y from `--version` and keep the
#     highest whose version is >= 3.13.0.
#   - bare python3 is accepted only if its own version is >= 3.13.
#
# Auto-heal:
#   - If no >= 3.13 interpreter is found, run the bundled installer
#     (../skills/sync-tool/scripts/installers/python.sh, resolved relative to
#     this script's own location so it works regardless of cwd), then re-resolve.
#   - If still none after the install attempt, print a clear error to stderr and
#     exit non-zero, pointing the user at /coding:sync-tool.
#
# Usage:
#   plugins/coding/scripts/pyrun.sh <script.py> <files…> --category all --before 5 --after 10
#
# All arguments are passed through verbatim: the first arg is the .py script,
# the rest are its arguments.
#
# Self-contained: no shared shell library.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER="$SCRIPT_DIR/../skills/sync-tool/scripts/installers/python.sh"

MIN_MAJOR=3
MIN_MINOR=13

# Compute a comparable integer (major*100 + minor) from a `python --version`
# string, e.g. "Python 3.14.5" -> 314. Prints nothing if it cannot be parsed.
version_key() {
  local raw="$1" ver major minor
  # Extract the first "X.Y" token from the version output.
  ver="$(printf '%s\n' "$raw" | grep -oE '[0-9]+\.[0-9]+' | head -n1)"
  [[ -n "$ver" ]] || return 1
  major="${ver%%.*}"
  minor="${ver#*.}"
  [[ "$major" =~ ^[0-9]+$ && "$minor" =~ ^[0-9]+$ ]] || return 1
  printf '%s\n' "$(( major * 100 + minor ))"
}

MIN_KEY="$(( MIN_MAJOR * 100 + MIN_MINOR ))"

# Resolve the newest interpreter >= 3.13. On success, sets PY and returns 0.
resolve_python() {
  PY=""
  local best_key=0
  local candidates name path raw key
  candidates=(
    python3.20 python3.19 python3.18 python3.17 python3.16
    python3.15 python3.14 python3.13
    python3
  )
  for name in "${candidates[@]}"; do
    path="$(command -v "$name" 2>/dev/null)" || continue
    [[ -n "$path" ]] || continue
    raw="$("$path" --version 2>&1)" || continue
    key="$(version_key "$raw")" || continue
    if (( key >= MIN_KEY && key > best_key )); then
      best_key="$key"
      PY="$path"
    fi
  done
  [[ -n "$PY" ]]
}

if resolve_python; then
  exec "$PY" "$@"
fi

# No suitable interpreter — attempt to auto-heal via the bundled installer.
echo "pyrun.sh: no Python >= ${MIN_MAJOR}.${MIN_MINOR} found; attempting install via ${INSTALLER}" >&2
if [[ -f "$INSTALLER" ]]; then
  bash "$INSTALLER" >&2 || echo "pyrun.sh: installer exited non-zero" >&2
else
  echo "pyrun.sh: installer not found at ${INSTALLER}" >&2
fi

if resolve_python; then
  exec "$PY" "$@"
fi

echo "pyrun.sh: error — no Python >= ${MIN_MAJOR}.${MIN_MINOR} interpreter available and the install attempt did not produce one." >&2
echo "pyrun.sh: run /coding:sync-tool to install a supported Python interpreter, then retry." >&2
exit 1
