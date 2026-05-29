#!/usr/bin/env bash
# stamp-last-edited.sh — set `last_edited_time` in the YAML front matter of one
# or more .mdc files to the current UTC time.
#
# USAGE: stamp-last-edited.sh <file.mdc> [<file.mdc> ...]
# RUN ONLY after ALL edits to ALL listed .mdc files are complete and verified.
# Pass exactly the files whose content changed (skip read-only / untouched ones).
set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "usage: $(basename "$0") <file.mdc> [<file.mdc> ...]" >&2
  exit 2
fi

# One timestamp for the whole batch — real seconds, .000Z millis, UTC.
ts="$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"

status=0
for f in "$@"; do
  case "$f" in
    *.mdc) ;;
    *) echo "skip (not .mdc): $f" >&2; status=1; continue ;;
  esac
  if [ ! -f "$f" ]; then
    echo "skip (not found): $f" >&2; status=1; continue
  fi
  if [ "$(head -n1 "$f")" != "---" ]; then
    echo "skip (no front matter): $f" >&2; status=1; continue
  fi

  tmp="$(mktemp)"
  # Touch ONLY the first front-matter block. Replace key if present; else
  # insert immediately before the closing `---`.
  awk -v ts="$ts" '
    NR==1                                     { print; infm=1; next }
    infm && /^last_edited_time:[[:space:]]*/  { print "last_edited_time: " ts; hit=1; next }
    infm && /^---[[:space:]]*$/               { if (!hit) print "last_edited_time: " ts; infm=0; print; next }
                                              { print }
  ' "$f" > "$tmp"
  mv "$tmp" "$f"
  echo "stamped $f -> $ts"
done

exit "$status"
