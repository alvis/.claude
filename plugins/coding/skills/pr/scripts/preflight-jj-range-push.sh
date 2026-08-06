#!/usr/bin/env bash
set -euo pipefail

# prove an ordered bookmark range selects exactly those bookmarks and no tags,
# then publish the inclusive range in one jj command
# usage: preflight-jj-range-push.sh --remote <name> <bookmark>...

remote=
bookmarks=()

fail() {
  echo "refusing revision-range push: $1" >&2
  exit 1
}

valid_bookmark() {
  git check-ref-format "refs/heads/$1" >/dev/null 2>&1
}

resolve_endpoint() {
  position=$1
  bookmark=$2
  escaped=${bookmark//\\/\\\\}
  escaped=${escaped//\"/\\\"}
  revset='bookmarks(exact:"'"$escaped"'")'

  if ! commit=$(jj --at-operation "$operation_id" log -r "$revset" --no-graph \
    -T 'commit_id ++ "\n"'); then
    fail "$position endpoint lookup failed"
  fi
  case "$commit" in
    '') fail "empty $position endpoint" ;;
    *$'\n'*) fail "ambiguous $position endpoint" ;;
  esac
  printf '%s\n' "$commit"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --remote)
      [ "$#" -ge 2 ] || fail 'missing remote'
      remote=$2
      shift 2
      ;;
    --)
      shift
      break
      ;;
    --*) fail 'unknown option' ;;
    *) break ;;
  esac
done

[ -n "$remote" ] || fail 'missing remote'
[ "$#" -gt 0 ] || fail 'no bookmarks'

for bookmark in "$@"; do
  valid_bookmark "$bookmark" || fail "invalid bookmark: $bookmark"
  for existing in ${bookmarks[@]+"${bookmarks[@]}"}; do
    [ "$existing" != "$bookmark" ] || fail "duplicate bookmark: $bookmark"
  done
  bookmarks[${#bookmarks[@]}]=$bookmark
done

first_bookmark=${bookmarks[0]}
last_bookmark=
for bookmark in "${bookmarks[@]}"; do
  last_bookmark=$bookmark
done

if ! operation_id=$(jj op log -n1 --no-graph -T 'self.id()'); then
  fail 'operation lookup failed'
fi
first_commit=$(resolve_endpoint first "$first_bookmark")
last_commit=$(resolve_endpoint last "$last_bookmark")
if ! first_in_range=$(jj --at-operation "$operation_id" log \
  -r "$first_commit & ::$last_commit" --no-graph \
  -T 'commit_id ++ "\n"'); then
  fail 'boundary ancestry lookup failed'
fi
[ "$first_in_range" = "$first_commit" ] ||
  fail 'boundaries are not linear'

push_revset="${first_commit}::${last_commit}"
expected_bookmarks=$(printf '%s\n' "${bookmarks[@]}" | LC_ALL=C sort -u)
if ! unsorted_bookmarks=$(jj --at-operation "$operation_id" bookmark list \
  -r "$push_revset" -T 'name ++ "\n"'); then
  fail 'bookmark lookup failed'
fi
actual_bookmarks=$(printf '%s\n' "$unsorted_bookmarks" | LC_ALL=C sort -u)
[ "$actual_bookmarks" = "$expected_bookmarks" ] ||
  fail 'unexpected bookmarks'

if ! range_tags=$(jj --at-operation "$operation_id" tag list \
  -r "$push_revset" -T 'name ++ "\n"'); then
  fail 'tag lookup failed'
fi
[ -z "$range_tags" ] || fail 'selected tags'

jj --at-operation "$operation_id" git push --remote "$remote" \
  --revision "$push_revset"
printf 'PUSH_REVSET=%s\n' "$push_revset"
