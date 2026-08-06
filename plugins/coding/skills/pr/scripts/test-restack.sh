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

if [ "$#" -eq 4 ] && [ "$1" = git ] && [ "$2" = fetch ] &&
   [ "$3" = --remote ]; then
  printf 'fetch:%s\n' "$4" >>"$FAKE_LOG"
  if [ "$FETCH_FAIL" = true ]; then
    printf 'fetch failed\n' >&2
    exit 41
  fi
  exit 0
fi

# colocation detection: answer with the real HEAD of the surrounding repository
# so the script selects the jj path, and keep it out of the call log
if [ "$#" -eq 6 ] && [ "$1" = log ] && [ "$2" = -r ] && [ "$3" = @- ] &&
   [ "$4" = --no-graph ] && [ "$5" = -T ] && [ "$6" = commit_id ]; then
  cat "$DETECT_SHA_FILE"
  exit 0
fi

if [ "$#" -eq 6 ] && [ "$1" = log ] && [ "$2" = -r ] &&
   [ "$4" = --no-graph ] && [ "$5" = -T ] &&
   [ "$6" = 'commit_id ++ "\n"' ] &&
   [[ "$3" == *" & descendants("* ]]; then
  child=${3%% & descendants(*}
  parent=${3#* & descendants(}
  parent=${parent%)}
  [ "$child" = "$ANCESTRY_FAIL_SHA" ] && exit 43
  [ "$parent" = "$ANCESTRY_FAIL_PARENT_SHA" ] && exit 43
  printf '%s\n' "$child"
  exit 0
fi

if [ "$#" -eq 6 ] && [ "$1" = log ] && [ "$2" = -r ] &&
   [ "$4" = --no-graph ] && [ "$5" = -T ] &&
   [ "$6" = 'commit_id ++ "\n"' ]; then
  printf 'log:%s\n' "$3" >>"$FAKE_LOG"
  case "$3" in
    *@*) lookup "$3" "$REMOTE_SHAS" || exit 43 ;;
    *) lookup "$3" "$LOCAL_SHAS" || exit 43 ;;
  esac
  exit 0
fi

if [ "$#" -ge 6 ] && [ "$1" = git ] && [ "$2" = push ] &&
   [ "$3" = --remote ]; then
  printf 'push:%s' "$4" >>"$FAKE_LOG"
  shift 4
  while [ "$#" -gt 0 ]; do
    [ "$#" -ge 2 ] && [ "$1" = --bookmark ] || exit 97
    printf ':%s' "$2" >>"$FAKE_LOG"
    shift 2
  done
  printf '\n' >>"$FAKE_LOG"
  if [ "$PUSH_FAIL" = true ]; then
    printf 'push failed\n' >&2
    exit 42
  fi
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

if [ "$1" = pr ] && [ "$2" = list ] && [ "$3" = --head ] &&
   [ "$5" = --state ] && [ "$6" = all ]; then
  printf 'discover:%s\n' "$4" >>"$FAKE_LOG"
  if [ "$4" = "$GH_FAIL_BOOKMARK" ]; then
    printf 'discovery failed\n' >&2
    exit 44
  fi
  lookup "$4" "$PR_STATES" || exit 45
  exit 0
fi

if [ "$#" -eq 5 ] && [ "$1" = pr ] && [ "$2" = edit ] &&
   [ "$4" = --base ]; then
  printf 'edit:%s:%s\n' "$3" "$5" >>"$FAKE_LOG"
  if [ "$3" = "$EDIT_FAIL_BOOKMARK" ]; then
    printf 'edit failed\n' >&2
    exit 46
  fi
  exit 0
fi

printf 'unexpected-gh:%s\n' "$*" >>"$FAKE_LOG"
exit 98
EOF

cat >"$FAKE_BIN/git" <<'EOF'
#!/usr/bin/env bash
lookup() {
  while IFS='=' read -r key value; do
    if [ "$key" = "$1" ]; then printf '%s\n' "$value"; return 0; fi
  done <"$2"
  return 1
}

if [ "${FAKE_REMOTE_LOOKUP:-false}" = true ] && [ "$#" -eq 4 ] &&
   [ "$1" = ls-remote ] && [ "$2" = -- ]; then
  bookmark=${4#refs/heads/}
  printf 'remote:%s:%s\n' "$3" "$bookmark" >>"$FAKE_LOG"
  sha=$(lookup "$bookmark@$3" "$REMOTE_SHAS") || exit 0
  printf '%s\trefs/heads/%s\n' "$sha" "$bookmark"
  exit 0
fi

exec /usr/bin/git "$@"
EOF

chmod +x "$FAKE_BIN/jj" "$FAKE_BIN/gh" "$FAKE_BIN/git"

# the jj cases run inside a real repository whose HEAD the fake jj echoes back,
# so colocation is detected exactly the way it is in the field
COLOCATED=$TMP_ROOT/colocated
DETECT_SHA_FILE=$TMP_ROOT/detect-sha
git init --quiet --initial-branch=main "$COLOCATED"
git -C "$COLOCATED" config user.email test@example.com
git -C "$COLOCATED" config user.name Test
: >"$COLOCATED/base"
git -C "$COLOCATED" add base
git -C "$COLOCATED" commit --quiet --no-gpg-sign -m base
git -C "$COLOCATED" rev-parse HEAD >"$DETECT_SHA_FILE"

export PATH="$FAKE_BIN:$PATH" FAKE_LOG LOCAL_SHAS REMOTE_SHAS PR_STATES \
  DETECT_SHA_FILE FAKE_REMOTE_LOOKUP=true

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
  PUSH_FAIL=false
  EDIT_FAIL_BOOKMARK=
  GH_FAIL_BOOKMARK=
  ANCESTRY_FAIL_SHA=
  ANCESTRY_FAIL_PARENT_SHA=
  base_args=(--remote upstream --base main)
  args=()
  expected_status=0
  expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":[]}'
  expected_log=
  expected_stderr=

  case "$name" in
    no-args)
      expected_status=2
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["no-specs"]}'
      ;;
    missing-remote)
      base_args=(--base main)
      args=(stack/01-a="$SHA_A")
      expected_status=2
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["missing-remote"]}'
      ;;
    dash-remote)
      base_args=(--remote -dash --base main)
      args=(stack/01-a="$SHA_A")
      FETCH_FAIL=true
      expected_status=1
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["fetch"]}'
      expected_log=fetch:-dash
      expected_stderr='fetch failed'
      ;;
    at-remote)
      base_args=(--remote foo@bar --base main)
      args=(stack/01-a="$SHA_A")
      FETCH_FAIL=true
      expected_status=1
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["fetch"]}'
      expected_log=fetch:foo@bar
      expected_stderr='fetch failed'
      ;;
    missing-base)
      base_args=(--remote upstream)
      args=(stack/01-a="$SHA_A")
      expected_status=2
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["missing-base"]}'
      ;;
    invalid-base)
      base_args=(--remote upstream --base bad..base)
      args=(stack/01-a="$SHA_A")
      expected_status=2
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["invalid-base"]}'
      ;;
    missing-base-ref)
      base_args=(--remote upstream --base absent)
      args=(stack/01-a="$SHA_A")
      expected_status=1
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["base-sha:absent"]}'
      expected_log=fetch:upstream
      ;;
    unknown-flag)
      args=(--bogus)
      expected_status=2
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["unknown-flag"]}'
      ;;
    malformed-spec)
      args=(stack/01-a)
      expected_status=2
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["invalid-spec"]}'
      ;;
    unsafe-bookmark)
      args=(bad..name="$SHA_A")
      expected_status=2
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["invalid-bookmark"]}'
      ;;
    nonhex-sha)
      args=(stack/01-a=not-hex)
      expected_status=2
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["invalid-sha"]}'
      ;;
    duplicate-bookmark)
      args=(stack/01-a="$SHA_A" stack/01-a="$SHA_A")
      expected_status=2
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["duplicate-bookmark"]}'
      ;;
    fetch-failure)
      args=(stack/01-a="$SHA_A")
      FETCH_FAIL=true
      expected_status=1
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["fetch"]}'
      expected_log=fetch:upstream
      expected_stderr='fetch failed'
      ;;
    local-mismatch)
      args=(stack/01-a="$SHA_A")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_B"
      expected_status=1
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["local-sha-mismatch:stack/01-a"]}'
      expected_log="fetch:upstream
log:stack/01-a"
      ;;
    nonlinear)
      args=(stack/01-a="$SHA_A")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$PR_STATES" stack/01-a OPEN
      ANCESTRY_FAIL_SHA=$SHA_A
      expected_status=1
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["nonlinear:stack/01-a"]}'
      expected_log="fetch:upstream
log:stack/01-a
discover:stack/01-a"
      ;;
    gh-failure)
      args=(stack/01-a="$SHA_A")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      GH_FAIL_BOOKMARK=stack/01-a
      expected_status=1
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["gh-discovery:stack/01-a"]}'
      expected_log="fetch:upstream
log:stack/01-a
discover:stack/01-a"
      expected_stderr='discovery failed'
      ;;
    multiple-open)
      args=(stack/01-a="$SHA_A")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$PR_STATES" stack/01-a AMBIGUOUS
      expected_status=1
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["multiple-open:stack/01-a"]}'
      expected_log="fetch:upstream
log:stack/01-a
discover:stack/01-a"
      ;;
    closed-head)
      args=(stack/01-a="$SHA_A")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$PR_STATES" stack/01-a CLOSED
      expected_status=1
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["closed-head:stack/01-a"]}'
      expected_log="fetch:upstream
log:stack/01-a
discover:stack/01-a"
      ;;
    none)
      args=(stack/01-a="$SHA_A")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$REMOTE_SHAS" stack/01-a@upstream "$SHA_A"
      add_ref "$PR_STATES" stack/01-a NONE
      expected_json='{"vcs":"jj","restacked":["stack/01-a"],"skipped_merged":[],"errors":[]}'
      expected_log="fetch:upstream
log:stack/01-a
discover:stack/01-a
push:upstream:stack/01-a
remote:upstream:stack/01-a"
      ;;
    merged)
      args=(stack/01-old="$SHA_A" stack/02-live="$SHA_B")
      add_ref "$LOCAL_SHAS" stack/01-old "$SHA_A"
      add_ref "$LOCAL_SHAS" stack/02-live "$SHA_B"
      add_ref "$REMOTE_SHAS" stack/02-live@upstream "$SHA_B"
      add_ref "$PR_STATES" stack/01-old MERGED
      add_ref "$PR_STATES" stack/02-live OPEN
      # The merged tip was rewritten by the forge; the live child now descends
      # the root base directly and must not be checked against that stale tip.
      ANCESTRY_FAIL_PARENT_SHA=$SHA_A
      expected_json='{"vcs":"jj","restacked":["stack/02-live"],"skipped_merged":["stack/01-old"],"errors":[]}'
      expected_log="fetch:upstream
log:stack/01-old
discover:stack/01-old
log:stack/02-live
discover:stack/02-live
push:upstream:stack/02-live
remote:upstream:stack/02-live
edit:stack/02-live:main"
      ;;
    success-chain)
      args=(stack/01-a="$SHA_A" stack/02-b="$SHA_B")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$LOCAL_SHAS" stack/02-b "$SHA_B"
      add_ref "$REMOTE_SHAS" stack/01-a@upstream "$SHA_A"
      add_ref "$REMOTE_SHAS" stack/02-b@upstream "$SHA_B"
      add_ref "$PR_STATES" stack/01-a OPEN
      add_ref "$PR_STATES" stack/02-b OPEN
      expected_json='{"vcs":"jj","restacked":["stack/01-a","stack/02-b"],"skipped_merged":[],"errors":[]}'
      expected_log="fetch:upstream
log:stack/01-a
discover:stack/01-a
log:stack/02-b
discover:stack/02-b
push:upstream:stack/01-a:stack/02-b
remote:upstream:stack/01-a
remote:upstream:stack/02-b
edit:stack/01-a:main
edit:stack/02-b:stack/01-a"
      ;;
    custom-base)
      base_args=(--remote upstream --base stack/00-root)
      git -C "$COLOCATED" branch --force stack/00-root HEAD
      args=(stack/01-a="$SHA_A")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$REMOTE_SHAS" stack/01-a@upstream "$SHA_A"
      add_ref "$PR_STATES" stack/01-a OPEN
      expected_json='{"vcs":"jj","restacked":["stack/01-a"],"skipped_merged":[],"errors":[]}'
      expected_log="fetch:upstream
log:stack/01-a
discover:stack/01-a
push:upstream:stack/01-a
remote:upstream:stack/01-a
edit:stack/01-a:stack/00-root"
      ;;
    push-failure)
      args=(stack/01-a="$SHA_A" stack/02-b="$SHA_B")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$LOCAL_SHAS" stack/02-b "$SHA_B"
      add_ref "$PR_STATES" stack/01-a OPEN
      add_ref "$PR_STATES" stack/02-b OPEN
      add_ref "$REMOTE_SHAS" stack/01-a@upstream "$SHA_A"
      PUSH_FAIL=true
      expected_status=1
      expected_json='{"vcs":"jj","restacked":["stack/01-a"],"skipped_merged":[],"errors":["push","remote-sha-mismatch:stack/02-b"]}'
      expected_log="fetch:upstream
log:stack/01-a
discover:stack/01-a
log:stack/02-b
discover:stack/02-b
push:upstream:stack/01-a:stack/02-b
remote:upstream:stack/01-a
remote:upstream:stack/02-b"
      expected_stderr='push failed'
      ;;
    edit-failure)
      args=(stack/01-a="$SHA_A" stack/02-b="$SHA_B")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$LOCAL_SHAS" stack/02-b "$SHA_B"
      add_ref "$REMOTE_SHAS" stack/01-a@upstream "$SHA_A"
      add_ref "$REMOTE_SHAS" stack/02-b@upstream "$SHA_B"
      add_ref "$PR_STATES" stack/01-a OPEN
      add_ref "$PR_STATES" stack/02-b OPEN
      EDIT_FAIL_BOOKMARK=stack/01-a
      expected_status=1
      expected_json='{"vcs":"jj","restacked":["stack/01-a","stack/02-b"],"skipped_merged":[],"errors":["pr-edit:stack/01-a"]}'
      expected_log="fetch:upstream
log:stack/01-a
discover:stack/01-a
log:stack/02-b
discover:stack/02-b
push:upstream:stack/01-a:stack/02-b
remote:upstream:stack/01-a
remote:upstream:stack/02-b
edit:stack/01-a:main"
      expected_stderr='edit failed'
      ;;
    remote-mismatch)
      args=(stack/01-a="$SHA_A")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$REMOTE_SHAS" stack/01-a@upstream "$SHA_C"
      add_ref "$PR_STATES" stack/01-a OPEN
      expected_status=1
      expected_json='{"vcs":"jj","restacked":[],"skipped_merged":[],"errors":["remote-sha-mismatch:stack/01-a"]}'
      expected_log="fetch:upstream
log:stack/01-a
discover:stack/01-a
push:upstream:stack/01-a
remote:upstream:stack/01-a"
      ;;
    dry-run)
      args=(--dry-run stack/01-a="$SHA_A" stack/02-b="$SHA_B")
      add_ref "$LOCAL_SHAS" stack/01-a "$SHA_A"
      add_ref "$LOCAL_SHAS" stack/02-b "$SHA_B"
      add_ref "$PR_STATES" stack/01-a OPEN
      add_ref "$PR_STATES" stack/02-b NONE
      expected_log="fetch:upstream
log:stack/01-a
discover:stack/01-a
log:stack/02-b
discover:stack/02-b"
      ;;
  esac

  export FETCH_FAIL PUSH_FAIL EDIT_FAIL_BOOKMARK GH_FAIL_BOOKMARK \
    ANCESTRY_FAIL_SHA ANCESTRY_FAIL_PARENT_SHA
  set +e
  output=$(cd "$COLOCATED" &&
    /bin/bash "$RESTACK_SH" "${base_args[@]}" \
      ${args[@]+"${args[@]}"} 2>"$TMP_ROOT/stderr")
  status=$?
  set -e
  actual_log=$(cat "$FAKE_LOG")
  actual_stderr=$(cat "$TMP_ROOT/stderr")

  [ "$status" -eq "$expected_status" ] || fail "$name" "status $status, expected $expected_status"
  [ "$output" = "$expected_json" ] || fail "$name" "JSON $output, expected $expected_json"
  [ "$actual_log" = "$expected_log" ] || fail "$name" "log [$actual_log], expected [$expected_log]"
  [ "$actual_stderr" = "$expected_stderr" ] || fail "$name" \
    "stderr [$actual_stderr], expected [$expected_stderr]"
}

for test_case in \
  no-args missing-remote dash-remote at-remote missing-base invalid-base \
  missing-base-ref unknown-flag malformed-spec \
  unsafe-bookmark nonhex-sha duplicate-bookmark fetch-failure local-mismatch \
  nonlinear gh-failure multiple-open closed-head none merged success-chain \
  custom-base push-failure edit-failure remote-mismatch dry-run
do
  run_case "$test_case"
done

# the git cases exercise real git against a real bare origin, because the point
# is that the git commands themselves work, not that a stub was called
GIT_BIN=$TMP_ROOT/git-bin
ORIGIN=$TMP_ROOT/origin.git
PLAIN=$TMP_ROOT/plain
NONCOLOCATED_SHA_FILE=$TMP_ROOT/noncolocated-sha
mkdir -p "$GIT_BIN"
cp "$FAKE_BIN/gh" "$GIT_BIN/gh"
printf '%s\n' "$SHA_C" >"$NONCOLOCATED_SHA_FILE"

reset_plain() {
  rm -rf "$ORIGIN" "$PLAIN"
  git init --quiet --bare --initial-branch=main "$ORIGIN"
  git init --quiet --initial-branch=main "$PLAIN"
  git -C "$PLAIN" config user.email test@example.com
  git -C "$PLAIN" config user.name Test
  : >"$PLAIN/base"
  git -C "$PLAIN" add base
  git -C "$PLAIN" commit --quiet --no-gpg-sign -m base
  git -C "$PLAIN" remote add origin "$ORIGIN"
  git -C "$PLAIN" push --quiet origin main
  git -C "$PLAIN" checkout --quiet -b stack/01-a
  : >"$PLAIN/one"
  git -C "$PLAIN" add one
  git -C "$PLAIN" commit --quiet --no-gpg-sign -m one
  HEAD_A=$(git -C "$PLAIN" rev-parse HEAD)
}

run_git_case() {
  name=$1
  reset_plain
  : >"$FAKE_LOG"
  : >"$PR_STATES"
  GH_FAIL_BOOKMARK=
  EDIT_FAIL_BOOKMARK=
  base_args=(--remote origin --base main)
  args=()
  expected_status=0
  expected_remote=
  command_path="$GIT_BIN:/usr/bin:/bin"
  detection_file=$DETECT_SHA_FILE

  case "$name" in
    git-publish)
      args=(stack/01-a="$HEAD_A")
      add_ref "$PR_STATES" stack/01-a NONE
      expected_json='{"vcs":"git","restacked":["stack/01-a"],"skipped_merged":[],"errors":[]}'
      expected_remote=$HEAD_A
      ;;
    git-reparent)
      args=(stack/01-a="$HEAD_A")
      add_ref "$PR_STATES" stack/01-a OPEN
      expected_json='{"vcs":"git","restacked":["stack/01-a"],"skipped_merged":[],"errors":[]}'
      expected_remote=$HEAD_A
      ;;
    git-noncolocated-jj)
      args=(stack/01-a="$HEAD_A")
      add_ref "$PR_STATES" stack/01-a NONE
      expected_json='{"vcs":"git","restacked":["stack/01-a"],"skipped_merged":[],"errors":[]}'
      expected_remote=$HEAD_A
      command_path="$FAKE_BIN:/usr/bin:/bin"
      detection_file=$NONCOLOCATED_SHA_FILE
      ;;
    git-local-mismatch)
      args=(stack/01-a="$SHA_A")
      expected_status=1
      expected_json='{"vcs":"git","restacked":[],"skipped_merged":[],"errors":["local-sha-mismatch:stack/01-a"]}'
      ;;
    git-unknown-branch)
      args=(stack/09-missing="$HEAD_A")
      expected_status=1
      expected_json='{"vcs":"git","restacked":[],"skipped_merged":[],"errors":["local-sha-mismatch:stack/09-missing"]}'
      ;;
    git-dry-run)
      args=(--dry-run stack/01-a="$HEAD_A")
      add_ref "$PR_STATES" stack/01-a OPEN
      expected_json='{"vcs":"git","restacked":[],"skipped_merged":[],"errors":[]}'
      ;;
  esac

  export GH_FAIL_BOOKMARK EDIT_FAIL_BOOKMARK
  set +e
  output=$(cd "$PLAIN" && FAKE_REMOTE_LOOKUP=false \
    DETECT_SHA_FILE="$detection_file" PATH="$command_path" \
    /bin/bash "$RESTACK_SH" "${base_args[@]}" \
      ${args[@]+"${args[@]}"} 2>"$TMP_ROOT/stderr")
  status=$?
  set -e
  actual_remote=$(git -C "$ORIGIN" rev-parse --verify --quiet \
    refs/heads/stack/01-a || true)

  [ "$status" -eq "$expected_status" ] || fail "$name" "status $status, expected $expected_status"
  [ "$output" = "$expected_json" ] || fail "$name" "JSON $output, expected $expected_json"
  [ "$actual_remote" = "$expected_remote" ] || fail "$name" "remote [$actual_remote], expected [$expected_remote]"
}

for test_case in \
  git-publish git-reparent git-noncolocated-jj git-local-mismatch \
  git-unknown-branch git-dry-run
do
  run_git_case "$test_case"
done

if [ "$failures" -ne 0 ]; then exit 1; fi
printf 'PASS: 26 jj and 6 git fail-closed ordered stack sync cases\n'
