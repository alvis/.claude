#!/usr/bin/env bash
# detect.sh -- detect a Storybook installation in a project's package.json.
#
# Contract:
#   detect.sh --cwd <dir>
#
# Reads:
#   <dir>/package.json
#
# Writes (stdout, single line JSON):
#   {"detected": <bool>, "script": <string|null>, "port": 6006}
#
# Exit codes:
#   0  Storybook detected
#   1  Storybook not detected (or package.json missing)
#   2  Usage / dependency error
#
# Detection rule:
#   Storybook is present iff ANY of:
#     - (devDependencies|dependencies)['storybook'] exists
#     - any (devDependencies|dependencies) key matches '@storybook/*'
#     - any scripts.* key starts with 'storybook'
#   When a scripts.storybook* entry exists, the first such key is returned
#   as `script`. Otherwise, when only the dependency signal fires, `script`
#   defaults to "storybook" so the model can invoke `npm run storybook`.
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: detect.sh --cwd <directory>

Detect whether the project at <directory> declares Storybook. Prints a single
JSON object describing the detection to stdout.

Exit 0 when detected, 1 when not detected, 2 on usage errors.
EOF
}

CWD=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --cwd)
      CWD="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'detect.sh: unknown flag: %s\n' "$1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$CWD" ]]; then
  printf 'detect.sh: --cwd is required\n' >&2
  usage
  exit 2
fi

if ! command -v jq >/dev/null 2>&1; then
  printf 'detect.sh: jq is required but not installed\n' >&2
  exit 2
fi

PKG="$CWD/package.json"
if [[ ! -f "$PKG" ]]; then
  printf '{"detected":false,"script":null,"port":6006}\n'
  exit 1
fi

# Single jq pass: returns "detected|script" where script is "" if none.
RESULT="$(
  jq -r '
    def dep_has_storybook:
      ((.devDependencies // {}) + (.dependencies // {})) as $deps
      | ($deps | has("storybook"))
        or ([$deps | keys[] | select(startswith("@storybook/"))] | length > 0);

    def script_name:
      ((.scripts // {}) | keys[] | select(startswith("storybook"))) // empty;

    . as $pkg
    | (dep_has_storybook) as $dep
    | ([script_name] | first // "") as $sn
    | if ($dep or ($sn != "")) then
        ((if $sn == "" then "storybook" else $sn end)) as $effective
        | "true|\($effective)"
      else
        "false|"
      end
  ' "$PKG"
)"

DETECTED="${RESULT%%|*}"
SCRIPT="${RESULT#*|}"

if [[ "$DETECTED" == "true" ]]; then
  jq -cn --arg s "$SCRIPT" '{detected:true, script:$s, port:6006}'
  exit 0
fi

printf '{"detected":false,"script":null,"port":6006}\n'
exit 1
