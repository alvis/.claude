#!/usr/bin/env bash
set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RESTACK_SH="$SCRIPT_DIR/restack.sh"
TMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/test-restack.XXXXXX") || exit 1
trap 'rm -rf "$TMP_ROOT"' EXIT HUP INT TERM

FAKE_BIN="$TMP_ROOT/bin"
FAKE_LOG="$TMP_ROOT/calls.log"
FAKE_BOOKMARKS="$TMP_ROOT/bookmarks"
mkdir -p "$FAKE_BIN"

cat >"$FAKE_BIN/jj" <<'EOF'
#!/usr/bin/env bash
case "$1 $2" in
  "git fetch") printf '%s\n' fetch >>"$FAKE_LOG" ;;
  "bookmark list") cat "$FAKE_BOOKMARKS" ;;
  "git push") printf 'push:%s\n' "$4" >>"$FAKE_LOG" ;;
  rebase\ *) printf 'rebase:%s\n' "$*" >>"$FAKE_LOG" ;;
  *) printf 'unexpected-jj:%s\n' "$*" >>"$FAKE_LOG"; exit 2 ;;
esac
EOF

cat >"$FAKE_BIN/gh" <<'EOF'
#!/usr/bin/env bash
case "$1 $2" in
  "pr view") printf '%s\n' OPEN ;;
  "pr edit")
    printf 'edit:%s\n' "$3" >>"$FAKE_LOG"
    [ "$3" = "$FAIL_EDIT_BOOKMARK" ] && exit 42
    ;;
  *) printf 'unexpected-gh:%s\n' "$*" >>"$FAKE_LOG"; exit 2 ;;
esac
EOF

cat >"$FAKE_BIN/jq" <<'EOF'
#!/usr/bin/env bash
case "$*" in
  "-R .")
    while IFS= read -r line; do
      printf '"%s"\n' "$line"
    done
    ;;
  "-s -c .")
    first=true
    printf '['
    while IFS= read -r line; do
      if [ "$first" = true ]; then first=false; else printf ','; fi
      printf '%s' "$line"
    done
    printf ']\n'
    ;;
  *) exit 2 ;;
esac
EOF

chmod +x "$FAKE_BIN/jj" "$FAKE_BIN/gh" "$FAKE_BIN/jq"
export PATH="$FAKE_BIN:$PATH" FAKE_LOG FAKE_BOOKMARKS

failures=0
fail() {
  failures=$((failures + 1))
  printf 'FAIL: %s\n' "$1" >&2
}

assert_call() {
  grep -F -x "$1" "$FAKE_LOG" >/dev/null 2>&1 || fail "missing call: $1"
}

PREFIX='feat[1].x'
FAIL_EDIT_BOOKMARK="$PREFIX/02-api"
export FAIL_EDIT_BOOKMARK
printf '%s\n' \
  "$PREFIX/01-core" \
  "$PREFIX/02-api" \
  'feat1ax/03-regex-only' \
  >"$FAKE_BOOKMARKS"
: >"$FAKE_LOG"

set +e
normal_output=$(/bin/bash "$RESTACK_SH" "$PREFIX" 2>&1)
normal_status=$?
set -e

[ "$normal_status" -ne 0 ] || fail 'PR-base edit failure must make restack nonzero'
assert_call "push:$PREFIX/01-core"
assert_call "push:$PREFIX/02-api"
if grep -F 'push:feat1ax/03-regex-only' "$FAKE_LOG" >/dev/null 2>&1; then
  fail 'regex-only prefix match was pushed'
fi
if grep -F 'rebase:' "$FAKE_LOG" >/dev/null 2>&1; then
  fail 'restack must not run jj rebase'
fi
case "$normal_output" in
  *'"pr-edit:feat[1].x/02-api"'*) ;;
  *) fail 'PR-base edit failure missing from JSON errors' ;;
esac

: >"$FAKE_LOG"
set +e
dry_output=$(/bin/bash "$RESTACK_SH" "$PREFIX" --dry-run 2>&1)
dry_status=$?
set -e

[ "$dry_status" -eq 0 ] || fail 'dry-run must succeed'
if [ -s "$FAKE_LOG" ]; then
  fail "dry-run invoked mutating fake commands: $(tr '\n' ' ' <"$FAKE_LOG")"
fi

if [ "$failures" -ne 0 ]; then
  printf 'normal status=%s output=%s\n' "$normal_status" "$normal_output" >&2
  printf 'dry-run status=%s output=%s\n' "$dry_status" "$dry_output" >&2
  exit 1
fi

printf 'PASS: literal prefix, push-only restack, PR edit errors, and dry-run\n'
