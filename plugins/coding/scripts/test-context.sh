#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Runtime-resolved sibling; the focused test below exercises this source.
# shellcheck disable=SC1091
source "$SCRIPT_DIR/context.sh"

fixture="$(mktemp -d)"
trap 'rm -rf "$fixture"' EXIT

mkdir -p \
  "$fixture/.engineering/work/eng-42" \
  "$fixture/.engineering/work/eng-99" \
  "$fixture/docs/architecture/decisions" \
  "$fixture/docs/design" \
  "$fixture/docs/specs/payments" \
  "$fixture/.code-spec" \
  "$fixture/guide"

touch \
  "$fixture/README.md" \
  "$fixture/CONTEXT.md" \
  "$fixture/DESIGN.md" \
  "$fixture/PLAN.md" \
  "$fixture/NOTES.md" \
  "$fixture/.engineering/work/eng-42/working.md" \
  "$fixture/.engineering/work/eng-42/state.md" \
  "$fixture/.engineering/work/eng-42/decisions.md" \
  "$fixture/.engineering/work/eng-99/working.md" \
  "$fixture/.engineering/work/eng-99/state.md" \
  "$fixture/docs/index.md" \
  "$fixture/docs/architecture/overview.md" \
  "$fixture/docs/architecture/runtime-boundaries.md" \
  "$fixture/docs/architecture/decisions/0001-runtime.md" \
  "$fixture/docs/design/system.md" \
  "$fixture/docs/design/checkout-flow.md" \
  "$fixture/docs/specs/payments/index.md" \
  "$fixture/docs/specs/payments/error-contract.md" \
  "$fixture/.code-spec/legacy.md" \
  "$fixture/guide/overview.md"

# Hard-link variants simulate two spellings resolving to one filesystem object,
# as on case-insensitive APFS. On such a filesystem the second spelling already
# resolves, so no link is needed.
if [[ ! -e "$fixture/readme.md" ]]; then
  ln "$fixture/README.md" "$fixture/readme.md"
fi

export ENGINEERING_WORK_ID=eng-42
output="$(get_repo_root_documents_context "$fixture" "")"
unset ENGINEERING_WORK_ID

assert_contains() {
  case "$output" in
    *"$1"*) ;;
    *) printf 'missing expected path: %s\n' "$1" >&2; exit 1 ;;
  esac
}

assert_absent() {
  case "$output" in
    *"$1"*) printf 'unexpected legacy/detail path: %s\n' "$1" >&2; exit 1 ;;
    *) ;;
  esac
}

assert_before() {
  local first second positions first_line second_line
  first="$1"
  second="$2"
  positions="$(printf '%s\n' "$output" | grep -n -F -e "$first" -e "$second")"
  first_line="$(printf '%s\n' "$positions" | grep -F "$first" | cut -d: -f1)"
  second_line="$(printf '%s\n' "$positions" | grep -F "$second" | cut -d: -f1)"
  if [[ -z "$first_line" || -z "$second_line" || "$first_line" -ge "$second_line" ]]; then
    printf 'expected %s before %s\n' "$first" "$second" >&2
    exit 1
  fi
}

assert_contains '- README.md'
assert_contains '- .engineering/work/eng-42/working.md'
assert_contains '- .engineering/work/eng-42/state.md'
assert_absent '.engineering/work/eng-99/working.md'
assert_absent '.engineering/work/eng-99/state.md'
assert_contains '- docs/index.md'
assert_contains '- docs/architecture/overview.md'
assert_absent 'docs/architecture/runtime-boundaries.md'
assert_contains '- docs/design/system.md'
assert_absent 'docs/design/checkout-flow.md'
assert_contains '- docs/specs/payments/index.md'
assert_absent 'docs/specs/payments/error-contract.md'
assert_absent '.code-spec/legacy.md'
assert_contains '- guide/overview.md'

assert_absent 'CONTEXT.md'
assert_absent 'DESIGN.md'
assert_absent 'PLAN.md'
assert_absent 'NOTES.md'
assert_absent '.engineering/work/eng-42/decisions.md'
assert_absent 'docs/architecture/decisions/0001-runtime.md'

assert_before '.engineering/work/eng-42/working.md' '.engineering/work/eng-42/state.md'
assert_before '.engineering/work/eng-42/state.md' 'docs/index.md'

readme_count="$(printf '%s\n' "$output" | grep -Eio -- '- (README|readme)\.md' | wc -l | tr -d '[:space:]')"
if [[ "$readme_count" -ne 1 ]]; then
  printf 'expected one filesystem-distinct README path, got %s\n' "$readme_count" >&2
  exit 1
fi

ambiguous_output="$(get_repo_root_documents_context "$fixture" "")"
case "$ambiguous_output" in
  *'.engineering/work/'*)
    printf 'ambiguous work directories must not be injected without an active ID\n' >&2
    exit 1
    ;;
esac

marker_fixture="$fixture/marker-only"
mkdir -p "$marker_fixture/nested"
touch "$marker_fixture/.code-spec"
if [[ "$(find_project_root "$marker_fixture/nested")" != "$marker_fixture/nested" ]]; then
  printf '.code-spec must not act as a project marker\n' >&2
  exit 1
fi

printf 'context discovery tests passed\n'
