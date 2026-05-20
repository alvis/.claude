#!/usr/bin/env bash
set -euo pipefail

# restack.sh -- rebase every unmerged bookmark in the current stack onto its
#               (now-up-to-date) parent in the stack, re-push (force-with-lease
#               via jj), and reparent the open PR.
#
# Bookmarks in the stack are ordered by lexicographic sort of the `NN-<scope>`
# suffix (per GIT-PR-STACK-01). For bookmark #1 the parent is main@origin; for
# bookmark #N the parent is bookmark #N-1.
#
# Usage:   restack.sh <branch-prefix> [--dry-run]
# Stdout:  JSON summary { restacked, skipped_merged, errors }
# Exit:    0 = all ok or all skipped; non-zero only on hard failure of the loop

PREFIX="${1:-}"
[ -z "$PREFIX" ] && { echo "usage: restack.sh <branch-prefix> [--dry-run]" >&2; exit 2; }
DRY="${2:-}"

restacked=()
skipped=()
errors=()

run() {
  if [ "$DRY" = "--dry-run" ]; then
    printf '[dry] %s\n' "$*" >&2
  else
    "$@"
  fi
}

# Refresh remote tracking before deciding what to rebase
run jj git fetch >/dev/null 2>&1 || true

# Enumerate `<prefix>/*` bookmarks that are NOT ancestors of main@origin
# (i.e., not yet merged into main as of this fetch). Sort lexicographically so
# `01-foo` < `02-bar` < `10-baz` -- matches the intended stack order.
mapfile -t bookmarks < <(
  jj bookmark list -r "all() ~ ::main@origin" --templater 'name ++ "\n"' 2>/dev/null \
    | grep "^${PREFIX}/" \
    | sort
)

prev_base="main"
for bm in "${bookmarks[@]}"; do
  [ -z "$bm" ] && continue
  state="$(gh pr view "$bm" --json state -q .state 2>/dev/null || echo "NONE")"
  if [ "$state" = "MERGED" ]; then
    skipped+=("$bm")
    # A merged bookmark advances the base for the next unmerged PR
    prev_base="$bm"
    continue
  fi
  if ! run jj rebase -b "$bm" -d "$prev_base@origin" 2>&1; then
    errors+=("rebase:$bm")
    prev_base="$bm"
    continue
  fi
  if ! run jj git push --bookmark "$bm" 2>&1; then
    errors+=("push:$bm")
    prev_base="$bm"
    continue
  fi
  if [ "$state" != "NONE" ]; then
    # PR is open -- reparent to the current base (prev bookmark or main)
    run gh pr edit "$bm" --base "$prev_base" >/dev/null 2>&1 || true
  fi
  restacked+=("$bm")
  prev_base="$bm"
done

# Emit JSON summary. Build each array with `jq -R . | jq -s .` only when it has
# entries; otherwise emit an empty array literal so the output is well-formed.
to_json_array() {
  if [ "$#" -eq 0 ]; then
    printf '[]'
  else
    printf '%s\n' "$@" | jq -R . | jq -s -c .
  fi
}

if command -v jq >/dev/null 2>&1; then
  printf '{"restacked":%s,"skipped_merged":%s,"errors":%s}\n' \
    "$(to_json_array "${restacked[@]+"${restacked[@]}"}")" \
    "$(to_json_array "${skipped[@]+"${skipped[@]}"}")" \
    "$(to_json_array "${errors[@]+"${errors[@]}"}")"
else
  echo "jq not on PATH -- cannot emit JSON summary" >&2
  exit 2
fi

[ "${#errors[@]}" -eq 0 ] || exit 1
