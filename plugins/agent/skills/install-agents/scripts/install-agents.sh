#!/usr/bin/env bash
# Install the bundled specialist agent roster into ~/.claude/agents.
# Idempotent: overwrites the managed same-named files, leaves other agents alone.
# Compatible with bash 3.2+

set -euo pipefail

SKILL_DIRECTORY="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE_DIRECTORY="$SKILL_DIRECTORY/references/agents"
DESTINATION_DIRECTORY="$HOME/.claude/agents"

# preflight: the bundled roster must exist and hold at least one .md
if [[ ! -d "$SOURCE_DIRECTORY" ]]; then
    echo "error: bundled roster not found at $SOURCE_DIRECTORY" >&2
    exit 1
fi
shopt -s nullglob
sources=("$SOURCE_DIRECTORY"/*.md)
shopt -u nullglob
if [[ ${#sources[@]} -eq 0 ]]; then
    echo "error: no agent definitions found in $SOURCE_DIRECTORY" >&2
    exit 1
fi

# install (copy, not symlink — survives plugin relocation/reinstall)
mkdir -p "$DESTINATION_DIRECTORY"
count=0
for source in "${sources[@]}"; do
    cp "$source" "$DESTINATION_DIRECTORY/"
    echo "installed: $DESTINATION_DIRECTORY/$(basename "$source")"
    count=$((count + 1))
done

echo "done — installed $count agent(s) into $DESTINATION_DIRECTORY"
