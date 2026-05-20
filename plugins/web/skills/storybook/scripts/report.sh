#!/usr/bin/env bash
# report.sh — merge all per-story artifacts into report.md + report.json.
#
# Severity bucketing (locked by plan):
#   P0: render crash / 404 (smoke.json), a11y impact serious|critical,
#       interactions run status=failed.
#   P1: a11y impact moderate, smoke console error, grounding severity=high.
#   P2: a11y impact minor, grounding severity in {low,medium},
#       focus_visible_detected=false from states.json.
#
# Inputs (per story under $RUN_DIR/stories/<id>/):
#   - states.json   (capture-states.sh)
#   - panels.json   (scrape-panels.sh)
#   - grounding/*.json (one per state, emitted by ground.sh — caller drops here)
#
# Top-level: $RUN_DIR/smoke.json (smoke.sh — sibling skill).
#
# Usage:
#   report.sh --run-dir DIR
set -euo pipefail

RUN_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-dir) RUN_DIR="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$RUN_DIR" ]]; then
  marker="${TMPDIR:-/tmp}/storybook-audit/.current-run-id"
  if [[ -f "$marker" ]]; then
    run_id="$(cat "$marker")"
    RUN_DIR="${TMPDIR:-/tmp}/storybook-audit/${run_id}"
  else
    echo "report.sh: --run-dir required (no marker at $marker)" >&2
    exit 2
  fi
fi

if [[ ! -d "$RUN_DIR" ]]; then
  echo "report.sh: run dir does not exist: $RUN_DIR" >&2
  exit 2
fi

FINDINGS_JSON="$(mktemp)"
echo '[]' > "$FINDINGS_JSON"

append_finding() {
  # $1=severity $2=category $3=story $4=title $5=description $6=evidence
  local sev="$1" cat="$2" story="$3" title="$4" desc="$5" ev="$6"
  local current
  current="$(cat "$FINDINGS_JSON")"
  printf '%s' "$current" | jq -c \
    --arg sev "$sev" --arg cat "$cat" --arg story "$story" \
    --arg title "$title" --arg desc "$desc" --arg ev "$ev" \
    '. + [{severity:$sev, category:$cat, story:$story, title:$title, description:$desc, evidence:$ev}]' \
    > "$FINDINGS_JSON.tmp"
  mv "$FINDINGS_JSON.tmp" "$FINDINGS_JSON"
}

# ---------- smoke.json ----------
SMOKE="$RUN_DIR/smoke.json"
# track (story_id, kind) tuples already emitted for smoke-derived findings so
# crashes / not_found / sampled[].{ok,status,blank} don't triple-up on the same
# broken story.
SMOKE_SEEN="$(mktemp)"
: > "$SMOKE_SEEN"

smoke_seen() {
  # $1=kind $2=story_id ; returns 0 if already emitted, 1 if new.
  local key="$1|$2"
  if grep -Fxq "$key" "$SMOKE_SEEN" 2>/dev/null; then
    return 0
  fi
  printf '%s\n' "$key" >> "$SMOKE_SEEN"
  return 1
}

if [[ -f "$SMOKE" ]]; then
  # top-level smoke gates → P0
  # NOTE: jq's `//` treats `false` as null-equivalent, so `.index_reachable // true`
  # collapses an explicit `false` to `true`. Use an explicit equality test instead.
  index_reachable="$(jq -r 'if .index_reachable == false then "false" else "true" end' "$SMOKE" 2>/dev/null || echo true)"
  if [[ "$index_reachable" == "false" ]]; then
    append_finding "P0" "smoke-index" "" \
      "Storybook index.json unreachable" \
      "smoke.sh reported index_reachable=false; the Storybook index endpoint could not be loaded." \
      "$SMOKE"
  fi

  sidebar_present="$(jq -r 'if .sidebar_present == false then "false" else "true" end' "$SMOKE" 2>/dev/null || echo true)"
  if [[ "$sidebar_present" == "false" ]]; then
    append_finding "P0" "smoke-sidebar" "" \
      "Storybook sidebar failed to render" \
      "smoke.sh reported sidebar_present=false; the Storybook UI sidebar did not render in the host page." \
      "$SMOKE"
  fi

  # render crashes / 404s → P0 (dedupe by story id within smoke-crash kind)
  while IFS= read -r row; do
    [[ -z "$row" ]] && continue
    story="$(printf '%s' "$row" | jq -r 'if type=="string" then . else (.story // .id // "") end')"
    msg="$(printf '%s' "$row" | jq -r 'if type=="string" then . else (.message // .description // "") end')"
    if smoke_seen "smoke-crash" "$story"; then continue; fi
    append_finding "P0" "smoke-crash" "$story" "Render crash or story 404" "$msg" "$SMOKE"
  done < <(jq -c '(.crashes // []) + (.not_found // []) | .[]?' "$SMOKE" 2>/dev/null || true)

  # sampled[] failures → P0 (dedupe by story id within smoke-crash kind so a
  # story that also appears in crashes/not_found doesn't fire twice).
  while IFS= read -r row; do
    [[ -z "$row" ]] && continue
    story="$(printf '%s' "$row" | jq -r '.id // ""')"
    status="$(printf '%s' "$row" | jq -r '.status // ""')"
    # explicit equality tests — `.ok // true` would mistakenly normalize ok=false to true.
    okv="$(printf '%s' "$row" | jq -r 'if .ok == false then "false" else "true" end')"
    blank="$(printf '%s' "$row" | jq -r 'if .blank == true then "true" else "false" end')"

    # only consider rows that actually signal failure
    if [[ "$okv" != "false" && "$status" != "404" && "$blank" != "true" ]]; then
      continue
    fi
    if smoke_seen "smoke-crash" "$story"; then continue; fi

    reason=""
    [[ "$status" == "404" ]] && reason="status=404"
    if [[ "$okv" == "false" ]]; then
      reason="${reason:+$reason; }ok=false (status=$status)"
    fi
    [[ "$blank" == "true" ]] && reason="${reason:+$reason; }blank render"
    append_finding "P0" "smoke-crash" "$story" "Render crash or story 404" "$reason" "$SMOKE"
  done < <(jq -c '(.sampled // []) | .[]?' "$SMOKE" 2>/dev/null || true)

  # console errors → P1
  while IFS= read -r row; do
    [[ -z "$row" ]] && continue
    story="$(printf '%s' "$row" | jq -r '.story // ""')"
    msg="$(printf '%s' "$row" | jq -r '.message // ""')"
    append_finding "P1" "console-error" "$story" "Console error during render" "$msg" "$SMOKE"
  done < <(jq -c '(.console_errors // []) | .[]?' "$SMOKE" 2>/dev/null || true)
fi
rm -f "$SMOKE_SEEN"

# ---------- per-story walk ----------
shopt -s nullglob
for story_dir in "$RUN_DIR"/stories/*/; do
  story_id="$(basename "$story_dir")"
  states_file="$story_dir/states.json"
  panels_file="$story_dir/panels.json"

  # focus-visible missing → P2
  if [[ -f "$states_file" ]]; then
    fvd="$(jq -r '."focus-visible".focus_visible_detected // true' "$states_file")"
    if [[ "$fvd" == "false" ]]; then
      append_finding "P2" "focus-visible" "$story_id" \
        "Missing :focus-visible indicator" \
        "Primary interactive element did not match :focus-visible after synthetic focus." \
        "$states_file"
    fi
  fi

  # a11y violations
  if [[ -f "$panels_file" ]]; then
    while IFS= read -r v; do
      [[ -z "$v" ]] && continue
      impact="$(printf '%s' "$v" | jq -r '.impact // "minor"')"
      vid="$(printf '%s' "$v" | jq -r '.id // ""')"
      vdesc="$(printf '%s' "$v" | jq -r '.description // ""')"
      case "$impact" in
        serious|critical) sev="P0" ;;
        moderate)         sev="P1" ;;
        *)                sev="P2" ;;
      esac
      append_finding "$sev" "a11y" "$story_id" "a11y: $vid ($impact)" "$vdesc" "$panels_file"
    done < <(jq -c '.a11y.violations // [] | .[]?' "$panels_file" 2>/dev/null || true)

    # interactions failures → P0
    while IFS= read -r r; do
      [[ -z "$r" ]] && continue
      status="$(printf '%s' "$r" | jq -r '.status // ""')"
      if [[ "$status" == "failed" ]]; then
        name="$(printf '%s' "$r" | jq -r '.name // "<unnamed>"')"
        exc="$(printf '%s' "$r" | jq -r '.exception // ""')"
        append_finding "P0" "interaction" "$story_id" "Interaction failed: $name" "$exc" "$panels_file"
      fi
    done < <(jq -c '.interactions.runs // [] | .[]?' "$panels_file" 2>/dev/null || true)
  fi

  # grounding findings
  if [[ -d "$story_dir/grounding" ]]; then
    for gfile in "$story_dir/grounding"/*.json; do
      [[ -f "$gfile" ]] || continue
      state="$(jq -r '.state // ""' "$gfile")"
      while IFS= read -r issue; do
        [[ -z "$issue" ]] && continue
        gsev="$(printf '%s' "$issue" | jq -r '.severity // "medium"')"
        gdesc="$(printf '%s' "$issue" | jq -r '.description // ""')"
        case "$gsev" in
          high)         sev="P1" ;;
          medium|low)   sev="P2" ;;
          *)            sev="P2" ;;
        esac
        # locate evidence PNG for this state.
        ev_png="$story_dir/${state}.png"
        [[ -f "$ev_png" ]] || ev_png="$gfile"
        append_finding "$sev" "grounding-$state" "$story_id" \
          "Visual grounding ($state): $gsev" "$gdesc" "$ev_png"
      done < <(jq -c '.issues // [] | .[]?' "$gfile" 2>/dev/null || true)
    done
  fi
done
shopt -u nullglob

# ---------- counts ----------
P0_COUNT="$(jq '[.[] | select(.severity=="P0")] | length' "$FINDINGS_JSON")"
P1_COUNT="$(jq '[.[] | select(.severity=="P1")] | length' "$FINDINGS_JSON")"
P2_COUNT="$(jq '[.[] | select(.severity=="P2")] | length' "$FINDINGS_JSON")"
TOTAL="$(jq 'length' "$FINDINGS_JSON")"

# ---------- report.json ----------
jq -n \
  --arg run_dir "$RUN_DIR" \
  --argjson p0 "$P0_COUNT" --argjson p1 "$P1_COUNT" --argjson p2 "$P2_COUNT" \
  --argjson total "$TOTAL" \
  --slurpfile findings "$FINDINGS_JSON" \
  '{ run_dir: $run_dir, counts: {P0:$p0,P1:$p1,P2:$p2,total:$total}, findings: $findings[0] }' \
  > "$RUN_DIR/report.json"

# ---------- report.md ----------
{
  echo "# Storybook Audit Report"
  echo ""
  echo "Run directory: \`$RUN_DIR\`"
  echo ""
  echo "## Summary"
  echo ""
  echo "- P0 (blockers): $P0_COUNT"
  echo "- P1 (high):     $P1_COUNT"
  echo "- P2 (medium):   $P2_COUNT"
  echo "- Total:         $TOTAL"
  echo ""
  for sev in P0 P1 P2; do
    echo "## $sev"
    echo ""
    rows="$(jq -r --arg sev "$sev" \
      '[.[] | select(.severity==$sev)] | .[] | "- **\(.story)** — \(.title)\n  - \(.description)\n  - evidence: `\(.evidence)`"' \
      "$FINDINGS_JSON")"
    if [[ -z "$rows" ]]; then
      echo "_(none)_"
    else
      echo "$rows"
    fi
    echo ""
  done
} > "$RUN_DIR/report.md"

# ---------- stdout summary ----------
echo "Storybook audit complete."
echo "Run dir: $RUN_DIR"
echo "Counts:  P0=$P0_COUNT  P1=$P1_COUNT  P2=$P2_COUNT  total=$TOTAL"
echo ""
echo "Top 10 findings:"
jq -r '.[:10] | .[] | "  [\(.severity)] \(.story) — \(.title)"' "$FINDINGS_JSON"

rm -f "$FINDINGS_JSON"
