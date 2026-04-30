#!/usr/bin/env bash
# brew.sh — install or update Homebrew on macOS.
#
# Contract:
#   - macOS: install via official script if missing; `brew update` if present.
#   - Linux / Windows: skip with a note (Homebrew is mac-only here by design).
#   - Honors DRY_RUN=1 (echo planned cmd) and FORCE=1 (reinstall even if present).
#   - Exits 0 on success; non-zero with stderr message on failure.
#
# Self-contained: no shared shell library.

set -euo pipefail

DRY_RUN="${DRY_RUN:-0}"
FORCE="${FORCE:-0}"

run_cmd() {
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "+ $*" >&2
  else
    eval "$@"
  fi
}

uname_s="$(uname -s)"

case "$uname_s" in
  Darwin)
    if command -v brew >/dev/null 2>&1 && [[ "$FORCE" != "1" ]]; then
      run_cmd "brew update"
    else
      # Official Homebrew install script (NONINTERACTIVE for unattended runs).
      run_cmd "NONINTERACTIVE=1 /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    fi
    ;;
  Linux | MINGW* | MSYS* | CYGWIN*)
    echo "brew.sh: skip — Homebrew is macOS-only in this registry (uname -s: $uname_s)" >&2
    exit 0
    ;;
  *)
    echo "brew.sh: unrecognized OS (uname -s: $uname_s)" >&2
    exit 1
    ;;
esac
