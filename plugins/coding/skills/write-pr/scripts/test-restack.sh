#!/usr/bin/env bash
set -u

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
RESTACK_SH="$SCRIPT_DIR/restack.sh"
TMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/test-restack.XXXXXX") || exit 1
trap 'rm -rf "$TMP_ROOT"' EXIT HUP INT TERM

FAKE_BIN="$TMP_ROOT/bin"
FAKE_LOG="$TMP_ROOT/calls.log"
LOCAL_SHAS="$TMP_ROOT/local-shas"
REMOTE_SHAS="$TMP_ROOT/remote-shas"
PR_STATES="$TMP_ROOT/pr-states"
mkdir -p "$FAKE_BIN"

cat >"$FAKE_BIN/jj" <<'EOF'
#!/usr/bin/env bash
lookup() {
  while IFS='=' read -r key value; do
    if [ "$key" = "$1" ]; then printf '%s\n' "$value"; return 0; fi
  done <"$2"
  return 1
}

if [ "$#" -eq 2 ] && [ "$1" = git ] && [ "$2" = fetch ]; then
  printf '%s\n' fetch >>"$FAKE_LOG"
  [ "$FETCH_FAIL" = true ] && exit 41
  exit 0
fi

if [ "$#" -eq 6 ] && [ "$1" = log ] && [ "$2" = -r ] &&
   [ "$4" = --no-graph ] && [ "$5" = -T ] &&
   [ "$6" = 'commit_id ++ "\n"' ]; then
  printf 'log:%s\n' "$3" >>"$FAKE_LOG"
  case "$3" in
    *@origin) lookup "$3" "$REMOTE_SHAS" || exit 43 ;;
    *) lookup "$3" "$LOCAL_SHAS" || exit 43 ;;
  esac
  exit 0
fi

if [ "$#" -eq 4 ] && [ "$1" = git ] && [ "$2" = push ] &&
   [ "$3" = --bookmark ]; then
  printf 'push:%s\n' "$4" >>"$FAKE_LOG"
  [ "$4" = "$PUSH_FAIL_BOOKMARK" ] && exit 42
  exit 0
fi

printf 'unexpected-jj:%s\n' "$*" >>"$FAKE_LOG"
exit 97
EOF

cat >"$FAKE_BIN/gh" <<'EOF'
#!/usr/bin/env bash
lookup() {
  while IFS='=' read -r key value; do
    if [ "$key" = "$1" ]; then printf '%s\n' "$value"; return 0; fi
  done <"$2"
  return 1
}

if [ "$#" -eq 10 ] && [ "$1" = pr ] && [ "$2" = list ] &&
   [ "$3" = --head ] && [ "$5" = --state ] && [ "$6" = all ] &&
   [ "$7" = --json ] && [ "$8" = state ] && [ "$9" = --jq ] &&
   [ "${10}" = '.[0].state // "NONE"' ]; then
  printf 'discover:%s\n' "$4" >>"$FAKE_LOG"
  [ "$4" = "$GH_FAIL_BOOKMARK" ] && exit 44
  lookup "$4" "$PR_STATES" || exit 45
  exit 0
fi

if [ "$#" -eq 5 ] && [ "$1" = pr ] && [ "$2" = edit ] &&
   [ "$4" = --base ]; then
  printf 'edit:%s:%s\n' "$3" "$5" >>"$FAKE_LOG"
  [ "$3" = "$EDIT_FAIL_BOOKMARK" ] && exit 46
  exit 0
fi

printf 'unexpected-gh:%s\n' "$*" >>"$FAKE_LOG"
exit 98
EOF

chmod +x "$FAKE_BIN/jj" "$FAKE_BIN/gh"
export PATH="$FAKE_BIN:$PATH" FAKE_LOG LOCAL_SHAS REMOTE_SHAS PR_STATES

SHA_A=1111111111111111111111111111111111111111
SHA_B=2222222222222222222222222222222222222222
SHA_C=3333333333333333333333333333333333333333
failures=0

fail() {
  failures=$((failures + 1))
  printf 'FAIL [%s]: %s\n' "$1" "$2" >&2
}

add_ref() {
  printf '%s=%s\n' "$2" "$3" >>"$1"
}

run_case() {
  name=$1
  : >"$FAKE_LOG"
  : >"$LOCAL_SHAS"
  : >"$REMOTE_SHAS"
  : >"$PR_STATES"
  FETCH_FAIL=false
  PUSH_FAIL_BOOKMARK=
  EDIT_FAIL_BOOKMARK=
  GH_FAIL_BOOKMARK=
  args=()
  expected_status=0
  expected_json='{"restacked":[],"skipped_merged":[],"errors":[]}'
  expected_log=

  case "$name" in
    no-args)
      expected_status=2
      expected_json='{"restacked":[],"skipped_merged":[],"errors":["no-specs"]}'
      ;;
    unknown-flag)
      args=(--bogus)
      expected_status=2
      expected_json='{"restacked":[],"skipped_merged":[],"errors":["unknown-flag"]}'
      ;;
    malformed-spec)
      args=(stack/01-a)
      expected_status=2
      expected_json='{"restacked":[],"skipped_merged":[],"errors":["invalid-spec"]}'
      ;;
    unsafe-bookmark)
      args=(bad..name="$SHA_A")
      expected_status=2
      expected_json='{"restacked":[],"skipped_merged":[],"errors":["invalid-bookmark"]}'
      ;;
    nonhex-sha)
      args=(stack/01-a=not-hex)
      expected_status=2
      expected_json='{"restacked":[],"skipped_merged":[],"errors":["invalid-sha"]}'
      ;;
    fetch-failure)
      args=(stack/01-a="$SHA_A")
      FETCH_FAIL=true
      expected_status=1
      expected_json='{"restacked":[],"skipped_merged":[],"errors":["fetch"]}'
      expected_log=fetch
      ;;
    local-mismatch)
      args=(stack/01-a="$SHA_A")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_B"
      expected_status=1
      expected_json='{"restacked":[],"skipped_merged":[],"errors":["local-sha-mismatch:stack/01-a"]}'
      expected_log="fetch
log:stack/01-a"
      ;;
    gh-failure)
      args=(stack/01-a="$SHA_A")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      GH_FAIL_BOOKMARK=stack/01-a
      expected_status=1
      expected_json='{"restacked":[],"skipped_merged":[],"errors":["gh-discovery:stack/01-a"]}'
      expected_log="fetch
log:stack/01-a
discover:stack/01-a"
      ;;
    none)
      args=(stack/01-a="$SHA_A")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$REMOTE_SHAS" stack/01-a@origin "$SHA_A"
      add_ref "$PR_STATES" stack/01-a NONE
      expected_json='{"restacked":["stack/01-a"],"skipped_merged":[],"errors":[]}'
      expected_log="fetch
log:stack/01-a
discover:stack/01-a
push:stack/01-a
log:stack/01-a@origin"
      ;;
    merged)
      args=(stack/01-old="$SHA_A" stack/02-live="$SHA_B")
      add_ref "$LOCAL_SHAS" stack/01-old "$SHA_A"
      add_ref "$LOCAL_SHAS" stack/02-live "$SHA_B"
      add_ref "$REMOTE_SHAS" stack/02-live@origin "$SHA_B"
      add_ref "$PR_STATES" stack/01-old MERGED
      add_ref "$PR_STATES" stack/02-live OPEN
      expected_json='{"restacked":["stack/02-live"],"skipped_merged":["stack/01-old"],"errors":[]}'
      expected_log="fetch
log:stack/01-old
discover:stack/01-old
log:stack/02-live
discover:stack/02-live
push:stack/02-live
log:stack/02-live@origin
edit:stack/02-live:main"
      ;;
    success-chain)
      args=(stack/01-a="$SHA_A" stack/02-b="$SHA_B")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$LOCAL_SHAS" stack/02-b "$SHA_B"
      add_ref "$REMOTE_SHAS" stack/01-a@origin "$SHA_A"
      add_ref "$REMOTE_SHAS" stack/02-b@origin "$SHA_B"
      add_ref "$PR_STATES" stack/01-a OPEN
      add_ref "$PR_STATES" stack/02-b OPEN
      expected_json='{"restacked":["stack/01-a","stack/02-b"],"skipped_merged":[],"errors":[]}'
      expected_log="fetch
log:stack/01-a
discover:stack/01-a
log:stack/02-b
discover:stack/02-b
push:stack/01-a
log:stack/01-a@origin
edit:stack/01-a:main
push:stack/02-b
log:stack/02-b@origin
edit:stack/02-b:stack/01-a"
      ;;
    push-failure)
      args=(stack/01-a="$SHA_A" stack/02-b="$SHA_B")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$LOCAL_SHAS" stack/02-b "$SHA_B"
      add_ref "$PR_STATES" stack/01-a OPEN
      add_ref "$PR_STATES" stack/02-b OPEN
      PUSH_FAIL_BOOKMARK=stack/01-a
      expected_status=1
      expected_json='{"restacked":[],"skipped_merged":[],"errors":["push:stack/01-a"]}'
      expected_log="fetch
log:stack/01-a
discover:stack/01-a
log:stack/02-b
discover:stack/02-b
push:stack/01-a"
      ;;
    edit-failure)
      args=(stack/01-a="$SHA_A" stack/02-b="$SHA_B")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$LOCAL_SHAS" stack/02-b "$SHA_B"
      add_ref "$REMOTE_SHAS" stack/01-a@origin "$SHA_A"
      add_ref "$PR_STATES" stack/01-a OPEN
      add_ref "$PR_STATES" stack/02-b OPEN
      EDIT_FAIL_BOOKMARK=stack/01-a
      expected_status=1
      expected_json='{"restacked":[],"skipped_merged":[],"errors":["pr-edit:stack/01-a"]}'
      expected_log="fetch
log:stack/01-a
discover:stack/01-a
log:stack/02-b
discover:stack/02-b
push:stack/01-a
log:stack/01-a@origin
edit:stack/01-a:main"
      ;;
    remote-mismatch)
      args=(stack/01-a="$SHA_A")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$REMOTE_SHAS" stack/01-a@origin "$SHA_C"
      add_ref "$PR_STATES" stack/01-a OPEN
      expected_status=1
      expected_json='{"restacked":[],"skipped_merged":[],"errors":["remote-sha-mismatch:stack/01-a"]}'
      expected_log="fetch
log:stack/01-a
discover:stack/01-a
push:stack/01-a
log:stack/01-a@origin"
      ;;
    dry-run)
      args=(--dry-run stack/01-a="$SHA_A" stack/02-b="$SHA_B")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$LOCAL_SHAS" stack/02-b "$SHA_B"
      add_ref "$PR_STATES" stack/01-a OPEN
      add_ref "$PR_STATES" stack/02-b NONE
      expected_log="fetch
log:stack/01-a
discover:stack/01-a
log:stack/02-b
discover:stack/02-b"
      ;;
  esac

  export FETCH_FAIL PUSH_FAIL_BOOKMARK EDIT_FAIL_BOOKMARK GH_FAIL_BOOKMARK
  set +e
  output=$(/bin/bash "$RESTACK_SH" ${args[@]+"${args[@]}"} 2>"$TMP_ROOT/stderr")
  status=$?
  set -e
  actual_log=$(cat "$FAKE_LOG")

  [ "$status" -eq "$expected_status" ] || fail "$name" "status $status, expected $expected_status"
  [ "$output" = "$expected_json" ] || fail "$name" "JSON $output, expected $expected_json"
  [ "$actual_log" = "$expected_log" ] || fail "$name" "log [$actual_log], expected [$expected_log]"
}

for test_case in \
  no-args unknown-flag malformed-spec unsafe-bookmark nonhex-sha fetch-failure \
  local-mismatch gh-failure none merged success-chain push-failure edit-failure \
  remote-mismatch dry-run
do
  run_case "$test_case"
done

if [ "$failures" -ne 0 ]; then exit 1; fi
printf 'PASS: 15 fail-closed ordered stack sync cases\n'
