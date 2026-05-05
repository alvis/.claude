#!/usr/bin/env bash
# Stop hook: on the first stop attempt of a turn, force a lint loop whenever
# the assistant edited any code (Edit/Write/MultiEdit/NotebookEdit) since the
# last user message. When a plan execution is also in flight, additionally
# enrich the block reason with a plan-review directive so both ride in one
# block. Pure-conversation stops (no edit-class tool calls this turn) and the
# second invocation (stop_hook_active=true) pass through unchanged.
#
# Decision is communicated via stdout JSON per Stop hook spec; exit code
# is always 0 so tooling failures never trap the user in a stop loop.

set -euo pipefail

# Fail-open if jq is unavailable — never block stop on tooling issues.
if ! command -v jq >/dev/null 2>&1; then
  echo '{}'
  exit 0
fi

INPUT=""
read -r INPUT || true

if [[ -z "$INPUT" ]]; then
  echo '{}'
  exit 0
fi

STOP_HOOK_ACTIVE=$(printf '%s' "$INPUT" | jq -r '.stop_hook_active // false')
TRANSCRIPT_PATH=$(printf '%s' "$INPUT" | jq -r '.transcript_path // ""')

# Loop guard: second invocation passes through.
if [[ "$STOP_HOOK_ACTIVE" == "true" ]]; then
  echo '{}'
  exit 0
fi

# Without a readable transcript we cannot decide whether code was edited;
# fail open rather than spuriously blocking chat-only stops.
if [[ -z "$TRANSCRIPT_PATH" || ! -f "$TRANSCRIPT_PATH" ]]; then
  echo '{}'
  exit 0
fi

# Did the assistant call any edit-class tool after the last real user prompt?
# Note: tool_result responses are wrapped in type=="user" entries — exclude those
# so the boundary is the actual human input, not internal tool plumbing.
CODE_EDITED=$(jq -rs '
  . as $all
  | ($all
     | map(
         .type == "user"
         and (
           (.message.content | type) == "string"
           or ((.message.content // []) | type == "array"
               and (all(.[]?; .type != "tool_result")))
         )
       )
     | reverse | index(true)) as $r
  | (if $r == null then 0 else ($all | length) - $r end) as $start
  | $all[$start:]
  | any(.[];
      .type == "assistant"
      and ((.message.content // []) | type == "array")
      and ((.message.content // []) | any(.type == "tool_use" and (.name | IN("Edit","Write","MultiEdit","NotebookEdit"))))
    )
' "$TRANSCRIPT_PATH" 2>/dev/null || echo "false")

if [[ "$CODE_EDITED" != "true" ]]; then
  echo '{}'
  exit 0
fi

BASE_REASON="Before stopping: code was edited in this turn. Dispatch a subagent to run \`/coding:lint\` on the touched files (derive the list from \`git status\` and the assistant's recent Edit/Write tool calls). Only allow the stop to proceed once the lint loop reports zero standard violations."

PLAN_REASON=""

# Best-effort plan-execution enrichment: last user message containing the sentinel.
PLAN_PROMPT=$(jq -rs '
  [.[]
   | select(.type=="user")
   | (.message.content | tostring) as $c
   | select($c | contains("Implement the following plan:"))
   | $c
  ] | last // ""
' "$TRANSCRIPT_PATH" 2>/dev/null || true)

if [[ -n "$PLAN_PROMPT" ]]; then
  FINGERPRINT=$(printf '%s\n' "$PLAN_PROMPT" | grep -m1 '^# ' || true)
  if [[ -z "$FINGERPRINT" ]]; then
    FINGERPRINT=$(printf '%s\n' "$PLAN_PROMPT" | grep -m1 -v '^[[:space:]]*$' || true)
  fi

  PLAN_FILE="unknown"
  PLANS_DIR="${HOME:-/tmp}/.claude/plans"
  if [[ -n "$FINGERPRINT" ]]; then
    MATCH=$(grep -lF "$FINGERPRINT" "${PLANS_DIR}/"*.md 2>/dev/null | head -n 1 || true)
    if [[ -n "$MATCH" ]]; then
      PLAN_FILE="$MATCH"
    fi
  fi

  PLAN_REASON=" Additionally, plan execution detected (plan: ${PLAN_FILE}). Dispatch an independent review subagent (e.g. coding:review-code or superpowers:requesting-code-review) to verify EVERY task in the plan was actually delivered — open the plan file, walk each task, confirm code/tests/docs match. Report unmet tasks before exiting."
fi

REASON="${BASE_REASON}${PLAN_REASON}"

jq -nc --arg reason "$REASON" '{decision:"block", reason:$reason}'
exit 0
