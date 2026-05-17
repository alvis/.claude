#!/usr/bin/env bash
# Stop hook: on the first stop attempt of a turn, force a lint loop whenever
# the assistant edited any code (Edit/Write/MultiEdit/NotebookEdit) since the
# last user message; when a plan execution is also in flight, additionally
# enrich the block reason with a plan-review directive so both ride in one
# block — pure-conversation stops (no edit-class tool calls this turn) and the
# second invocation (stop_hook_active=true) pass through unchanged.
#
# decision is communicated via stdout JSON per Stop hook spec; exit code
# is always 0 so tooling failures never trap the user in a stop loop.

set -euo pipefail

# fail-open if jq is unavailable — never block stop on tooling issues
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

# loop guard: second invocation passes through
if [[ "$STOP_HOOK_ACTIVE" == "true" ]]; then
  echo '{}'
  exit 0
fi

# without a readable transcript we cannot decide whether code was edited;
# fail open rather than spuriously blocking chat-only stops
if [[ -z "$TRANSCRIPT_PATH" || ! -f "$TRANSCRIPT_PATH" ]]; then
  echo '{}'
  exit 0
fi

# collect file paths touched by edit-class tool calls (Edit/Write/MultiEdit/
# NotebookEdit) after the last real user prompt — mirrors the jq filter used by
# list-touched-files.sh by convention so the two stay in lock-step.
# NOTE: tool_result responses are wrapped in type=="user" entries — exclude those
# so the boundary is the actual human input, not internal tool plumbing
TOUCHED_FILES=$(jq -rs '
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
  | map(select(.type == "assistant"))
  | map(.message.content // [] | .[]?
        | select(.type == "tool_use"
                 and (.name | IN("Edit","Write","MultiEdit","NotebookEdit"))))
  | map(.input.file_path // .input.notebook_path // empty)
  | unique_by(.) | .[]
' "$TRANSCRIPT_PATH" 2>/dev/null || true)

# source-code extensions /coding:lint can meaningfully enforce — anchored at
# end-of-path; matched case-insensitively so .TS / .PY etc. also fire
CODE_EXT_RE='\.(ts|tsx|js|jsx|mjs|cjs|cts|mts|py|pyi|go|rs|rb|java|kt|kts|swift|c|cc|cpp|cxx|h|hpp|cs|php|scala|sh|bash|zsh|ipynb|sql|graphql|proto|vue|svelte|astro)$'

CODE_EDITED=false
if [[ -n "$TOUCHED_FILES" ]]; then
  shopt -s nocasematch
  while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    if [[ "$path" =~ $CODE_EXT_RE ]]; then
      CODE_EDITED=true
      break
    fi
  done <<< "$TOUCHED_FILES"
  shopt -u nocasematch
fi

if [[ "$CODE_EDITED" != "true" ]]; then
  echo '{}'
  exit 0
fi

BASE_REASON="Before stopping: code was edited in this turn. Dispatch a subagent to run \`/coding:lint\` on the touched code files (derive the list from \`git status\` and the assistant's recent Edit/Write tool calls). Apply lint only to source-code files — \`.ts/.tsx/.js/.jsx/.mjs/.cjs/.py/.go/.rs/.rb/.java/.kt/.swift/.c/.cpp/.h/.hpp/.cs/.php/.sh/.bash/.ipynb/.sql/.graphql/.proto/.vue/.svelte/.astro\` and similar — and skip any text-content files like \`.md/.mdx/.mdc/.txt/.rst/.json/.jsonc/.yaml/.yml/.toml/.html/.svg/.csv\` that were also touched in this turn, since \`/coding:lint\` has no rules for them. Only allow the stop to proceed once the lint loop reports zero standard violations."

PLAN_REASON=""

# best-effort plan-execution enrichment: last user message containing the sentinel
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
