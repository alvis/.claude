#!/usr/bin/env bash
# smoke.sh -- exploratory pass against a live Storybook root frame.
#
# Contract:
#   smoke.sh --cdp <PORT> --url <URL>
#
# Reads:
#   the live Chrome instance at CDP port <PORT> (shared with chrome-devtools MCP)
#
# Writes:
#   $RUN_DIR/smoke.json
#     {
#       "url": "<URL>",
#       "console_errors": [ { "story": "<storyId|"">", "message": "<text>" } ],
#       "sidebar_present": <bool>,
#       "index_reachable": <bool>,
#       "story_count": <int>,
#       "sampled": [
#         { "id": "<storyId>", "status": <http|"blank"|"ok">, "ok": <bool>, "blank": <bool> }
#       ],
#       "crashes":   [ "<storyId>", ... ],
#       "not_found": [ "<storyId>", ... ]
#     }
#
# Exit codes:
#   0  Always (smoke is exploratory; structural problems surface in JSON)
#   2  Usage / dependency error
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: smoke.sh --cdp <PORT> --url <URL>

Attach agent-browser to the running Chrome on <PORT>, navigate to <URL>,
install a console error listener, then probe the manager UI for a populated
sidebar and randomly sample up to three stories from /index.json to confirm
each renders without HTTP 404 or a blank iframe. Result is written to
$RUN_DIR/smoke.json.
EOF
}

CDP=""
URL=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --cdp) CDP="${2:-}"; shift 2 ;;
    --url) URL="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *)
      printf 'smoke.sh: unknown flag: %s\n' "$1" >&2
      usage; exit 2 ;;
  esac
done

if [[ -z "$CDP" || -z "$URL" ]]; then
  printf 'smoke.sh: --cdp and --url are required\n' >&2
  exit 2
fi

for tool in jq curl agent-browser; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    printf 'smoke.sh: %s is required but not installed\n' "$tool" >&2
    exit 2
  fi
done

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

OUT="$RUN_DIR/smoke.json"

# 1. Attach to the live Chrome session.
agent-browser --cdp "$CDP" open "$URL" >/dev/null 2>&1 || true

# 2. Install a console.error listener BEFORE further navigation so that any
#    render-time error is captured. Idempotent: only installs once per page.
INSTALL_EXPR='(() => {
  if (window.__sbAuditConsoleInstalled) return true;
  window.__sbAuditErrors = window.__sbAuditErrors || [];
  window.__sbCurrentStory = window.__sbCurrentStory || "";
  const origError = console.error.bind(console);
  console.error = (...args) => {
    try {
      const message = args.map(a => {
        try { return typeof a === "string" ? a : JSON.stringify(a); }
        catch (e) { return String(a); }
      }).join(" ");
      window.__sbAuditErrors.push({ story: window.__sbCurrentStory || "", message });
    } catch (_) { /* ignore */ }
    return origError(...args);
  };
  window.addEventListener("error", (e) => {
    window.__sbAuditErrors.push({
      story: window.__sbCurrentStory || "",
      message: String(e.message || e.error || "window error")
    });
  });
  window.addEventListener("unhandledrejection", (e) => {
    window.__sbAuditErrors.push({
      story: window.__sbCurrentStory || "",
      message: "unhandled rejection: " + String(e.reason)
    });
  });
  window.__getConsoleErrors__ = () => (window.__sbAuditErrors || []).slice();
  window.__sbAuditConsoleInstalled = true;
  return true;
})()'
agent-browser --cdp "$CDP" eval "$INSTALL_EXPR" >/dev/null 2>&1 || true

# 3. Sidebar presence -- Storybook 7+ marks story rows with data-nodetype/story
#    and data-item-id. Either selector is sufficient evidence.
SIDEBAR_RAW="$(agent-browser --cdp "$CDP" eval \
  '!!document.querySelector(\"[data-nodetype=\\\"story\\\"], [data-item-id]\")' \
  2>/dev/null || printf 'false')"
case "$SIDEBAR_RAW" in
  *true*)  SIDEBAR_PRESENT=true ;;
  *)       SIDEBAR_PRESENT=false ;;
esac

# 4. Hit /index.json -- this is what every downstream phase relies on.
INDEX_JSON="$RUN_DIR/.smoke-index.json"
INDEX_REACHABLE=false
STORY_COUNT=0
if curl -fsS --max-time 5 "$URL/index.json" -o "$INDEX_JSON" 2>/dev/null; then
  INDEX_REACHABLE=true
  STORY_COUNT="$(jq '[(.entries // .stories // {}) | to_entries[] | select(.value.type == "story" or (.value.type // "") == "")] | length' "$INDEX_JSON" 2>/dev/null || echo 0)"
fi

# 5. Sample up to three story ids and visit each iframe.
SAMPLED_JSON="[]"
if [[ "$INDEX_REACHABLE" == "true" && "$STORY_COUNT" -gt 0 ]]; then
  IDS="$(jq -r '
    [(.entries // .stories // {}) | to_entries[]
      | select(.value.type == "story" or (.value.type // "") == "")
      | .key] as $all
    | ($all | length) as $n
    | [range(0; (if $n < 3 then $n else 3 end))]
    | map($all[. * ($n) / 3 | floor])
    | unique
    | .[]
  ' "$INDEX_JSON" 2>/dev/null || true)"

  SAMPLES=()
  while IFS= read -r ID; do
    [[ -z "$ID" ]] && continue
    IFRAME_URL="$URL/iframe.html?viewMode=story&id=$ID"
    HTTP_CODE="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$IFRAME_URL" 2>/dev/null || echo 000)"
    STATUS="ok"
    OK=true
    BLANK=false
    if [[ "$HTTP_CODE" == "404" ]]; then
      STATUS="404"
      OK=false
    elif [[ "$HTTP_CODE" != "200" ]]; then
      STATUS="$HTTP_CODE"
      OK=false
    else
      # Tag console errors with the story id BEFORE navigating, so the
      # listener attributes any render-time error to this story.
      agent-browser --cdp "$CDP" eval \
        "window.__sbCurrentStory = $(printf '%s' "$ID" | jq -Rs '.')" \
        >/dev/null 2>&1 || true
      # Navigate the live tab to the iframe and check the body has content.
      agent-browser --cdp "$CDP" open "$IFRAME_URL" >/dev/null 2>&1 || true
      BODY_LEN_RAW="$(agent-browser --cdp "$CDP" eval \
        '(document.body ? document.body.innerText.length : 0)' \
        2>/dev/null || echo 0)"
      BODY_LEN="$(printf '%s' "$BODY_LEN_RAW" | tr -cd '0-9')"
      [[ -z "$BODY_LEN" ]] && BODY_LEN=0
      if [[ "$BODY_LEN" -lt 1 ]]; then
        STATUS="blank"
        OK=false
        BLANK=true
      fi
    fi
    SAMPLES+=("$(jq -cn --arg id "$ID" --arg s "$STATUS" --argjson ok "$OK" --argjson blank "$BLANK" \
      '{id:$id, status:$s, ok:$ok, blank:$blank}')")
  done <<< "$IDS"

  if (( ${#SAMPLES[@]} > 0 )); then
    SAMPLED_JSON="$(printf '%s\n' "${SAMPLES[@]}" | jq -cs '.')"
  fi
fi

# 6. Drain console errors collected during navigation.
ERRORS_RAW="$(agent-browser --cdp "$CDP" eval \
  'JSON.stringify(window.__getConsoleErrors__ ? window.__getConsoleErrors__() : [])' \
  2>/dev/null || echo '"[]"')"
# Strip outer quoting that some agent-browser response shapes apply.
ERRORS_JSON="$(printf '%s' "$ERRORS_RAW" | jq -r 'if type == "string" then . else tostring end' 2>/dev/null || echo '[]')"
echo "$ERRORS_JSON" | jq -e 'type == "array"' >/dev/null 2>&1 || ERRORS_JSON='[]'

jq -n \
  --arg url "$URL" \
  --argjson errors "$ERRORS_JSON" \
  --argjson sidebar "$SIDEBAR_PRESENT" \
  --argjson reachable "$INDEX_REACHABLE" \
  --argjson count "$STORY_COUNT" \
  --argjson sampled "$SAMPLED_JSON" \
  '{
    url:$url,
    console_errors: (
      $errors
      | map(
          if type == "object" then
            { story: ((.story // "") | tostring), message: ((.message // "") | tostring) }
          else
            { story: "", message: (. | tostring) }
          end
        )
    ),
    sidebar_present:$sidebar,
    index_reachable:$reachable,
    story_count:$count,
    sampled:$sampled,
    crashes:   ($sampled | map(select((.blank // false) == true or (.ok == false and .status != "404")) | .id)),
    not_found: ($sampled | map(select(.status == "404") | .id))
  }' > "$OUT"

rm -f "$INDEX_JSON"
printf '%s\n' "$OUT"
exit 0
