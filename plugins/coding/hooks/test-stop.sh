#!/usr/bin/env bash

set -euo pipefail

HOOK_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TRANSCRIPT=$(mktemp)
trap 'rm -f "$TRANSCRIPT"' EXIT

cat >"$TRANSCRIPT" <<'JSONL'
{"type":"user","message":{"content":"Update the implementation"}}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Edit","input":{"file_path":"src/example.ts"}}]}}
JSONL

OUTPUT=$(jq -nc --arg transcript_path "$TRANSCRIPT" \
  '{transcript_path:$transcript_path,stop_hook_active:false}' \
  | "$HOOK_DIR/stop.sh")
REASON=$(jq -r '.reason // ""' <<<"$OUTPUT")

[[ $(jq -r '.decision // ""' <<<"$OUTPUT") == "block" ]]
grep -Fq 'choose a suitable agent from the available agent types' <<<"$REASON"
grep -Fq "invoke the \`coding:lint\` skill with the Skill tool" <<<"$REASON"
grep -Fq "Never pass \`coding:lint\` as the Agent/Task \`subagent_type\`" <<<"$REASON"

cat >"$TRANSCRIPT" <<'JSONL'
{"type":"user","message":{"content":"Implement the following plan:\n# Hook routing"}}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Edit","input":{"file_path":"src/example.ts"}}]}}
JSONL

PLAN_OUTPUT=$(jq -nc --arg transcript_path "$TRANSCRIPT" \
  '{transcript_path:$transcript_path,stop_hook_active:false}' \
  | "$HOOK_DIR/stop.sh")
PLAN_REASON=$(jq -r '.reason // ""' <<<"$PLAN_OUTPUT")

grep -Fq "tell it to invoke the \`review-code\` or \`requesting-code-review\` skill with the Skill tool" <<<"$PLAN_REASON"
grep -Fq "Never use either skill name as the Agent/Task \`subagent_type\`" <<<"$PLAN_REASON"

echo "stop hook lint dispatch contract: PASS"
