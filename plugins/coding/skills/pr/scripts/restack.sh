#!/usr/bin/env bash
set -euo pipefail

# publish an explicitly ordered pull request stack and repair each live base
# usage: restack.sh [--dry-run] --base <root-base> <bookmark>=<expected-git-sha>...
# stdout: a json summary with the selected vcs plus restacked, skipped_merged,
#         and errors arrays

dry_run=false
root_base=
bookmarks=()
expected_shas=()
states=()
restacked=()
skipped_merged=()
errors=()

# jj drives the stack wherever it is installed and initialized for this
# repository; a matching working-copy-parent commit id is the only proof the two
# share a backing store, so anything else is an ordinary git repository
detect_vcs() {
  command -v jj >/dev/null 2>&1 || return 1
  jj_head=$(jj log -r @- --no-graph -T 'commit_id' 2>/dev/null) || return 1
  git_head=$(git rev-parse HEAD 2>/dev/null) || return 1
  [ "$jj_head" = "$git_head" ]
}

if detect_vcs; then
  vcs=jj
else
  vcs=git
fi

vcs_fetch() {
  if [ "$vcs" = jj ]; then
    jj git fetch >/dev/null 2>&1
  else
    git fetch origin >/dev/null 2>&1
  fi
}

vcs_local_sha() {
  if [ "$vcs" = jj ]; then
    jj log -r "$1" --no-graph -T 'commit_id ++ "\n"' 2>/dev/null
  else
    git rev-parse --verify --quiet "refs/heads/$1"
  fi
}

# both pushes carry a lease, so a remote that advanced under a rewrite is
# rejected rather than overwritten
vcs_push() {
  if [ "$vcs" = jj ]; then
    jj git push --bookmark "$1" >/dev/null 2>&1
  else
    git push --force-with-lease origin \
      "refs/heads/$1:refs/heads/$1" >/dev/null 2>&1
  fi
}

vcs_remote_sha() {
  if [ "$vcs" = jj ]; then
    jj log -r "$1@origin" --no-graph -T 'commit_id ++ "\n"' 2>/dev/null
  else
    remote_ref=$(git ls-remote origin "refs/heads/$1" 2>/dev/null) || return 1
    [ -n "$remote_ref" ] || return 1
    printf '%s\n' "${remote_ref%%	*}"
  fi
}

vcs_base_sha() {
  git rev-parse --verify --quiet "refs/remotes/origin/$1" ||
    git rev-parse --verify --quiet "refs/heads/$1"
}

vcs_is_ancestor() {
  if [ "$vcs" = jj ]; then
    candidate=$(jj log -r "$2 & descendants($1)" --no-graph \
      -T 'commit_id ++ "\n"' 2>/dev/null) || return 1
    [ "$candidate" = "$2" ]
  else
    git merge-base --is-ancestor "$1" "$2"
  fi
}

json_array() {
  separator=
  printf '['
  for value in "$@"; do
    printf '%s"%s"' "$separator" "$value"
    separator=,
  done
  printf ']'
}

emit_json() {
  printf '{"vcs":"%s","restacked":' "$vcs"
  json_array ${restacked[@]+"${restacked[@]}"}
  printf ',"skipped_merged":'
  json_array ${skipped_merged[@]+"${skipped_merged[@]}"}
  printf ',"errors":'
  json_array ${errors[@]+"${errors[@]}"}
  printf '}\n'
}

fail_with() {
  status=$1
  error=$2
  errors[${#errors[@]}]=$error
  emit_json
  exit "$status"
}

valid_bookmark() {
  candidate=$1
  case "$candidate" in
    ''|-*|/*|*/|*//*|*..*|*.lock|*[!A-Za-z0-9._/-]*) return 1 ;;
  esac

  remainder=$candidate
  while :; do
    component=${remainder%%/*}
    case "$component" in
      ''|.*|*.) return 1 ;;
    esac
    [ "$remainder" = "$component" ] && break
    remainder=${remainder#*/}
  done
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) dry_run=true; shift ;;
    --base)
      [ "$#" -ge 2 ] || fail_with 2 missing-base
      root_base=$2
      shift 2
      ;;
    --*) fail_with 2 unknown-flag ;;
    *) break ;;
  esac
done

[ -n "$root_base" ] || fail_with 2 missing-base
valid_bookmark "$root_base" || fail_with 2 invalid-base
[ "$#" -gt 0 ] || fail_with 2 no-specs

for spec in "$@"; do
  case "$spec" in
    -*) fail_with 2 unknown-flag ;;
    *=*) ;;
    *) fail_with 2 invalid-spec ;;
  esac

  bookmark=${spec%%=*}
  expected_sha=${spec#*=}
  [ -n "$bookmark" ] && [ -n "$expected_sha" ] || fail_with 2 invalid-spec
  valid_bookmark "$bookmark" || fail_with 2 invalid-bookmark
  [ "$bookmark" != "$root_base" ] || fail_with 2 invalid-base
  # Guarded expansion keeps an empty array valid under macOS Bash 3.2 + set -u.
  for existing in ${bookmarks[@]+"${bookmarks[@]}"}; do
    [ "$existing" != "$bookmark" ] || fail_with 2 duplicate-bookmark
  done
  case "$expected_sha" in
    *[!0-9A-Fa-f]*) fail_with 2 invalid-sha ;;
  esac

  bookmarks[${#bookmarks[@]}]=$bookmark
  expected_shas[${#expected_shas[@]}]=$expected_sha
done

# fetch and preflight every supplied bookmark before changing remote state
vcs_fetch || fail_with 1 fetch
if ! previous_sha=$(vcs_base_sha "$root_base"); then
  fail_with 1 "base-sha:$root_base"
fi

index=0
while [ "$index" -lt "${#bookmarks[@]}" ]; do
  bookmark=${bookmarks[$index]}
  expected_sha=${expected_shas[$index]}

  if ! local_sha=$(vcs_local_sha "$bookmark"); then
    fail_with 1 "local-sha-mismatch:$bookmark"
  fi
  [ "$local_sha" = "$expected_sha" ] || fail_with 1 "local-sha-mismatch:$bookmark"

  if ! state=$(gh pr list --head "$bookmark" --state all --limit 100 \
    --json state,headRefOid --jq "
      [.[] | select(.state == \"OPEN\")] as \$open |
      if (\$open | length) > 1 then \"AMBIGUOUS\"
      elif (\$open | length) == 1 then \"OPEN\"
      elif any(.[]; .state == \"MERGED\" and .headRefOid == \"$expected_sha\")
        then \"MERGED\"
      elif any(.[]; .state == \"CLOSED\" and .headRefOid == \"$expected_sha\")
        then \"CLOSED\"
      else \"NONE\" end" 2>/dev/null); then
    fail_with 1 "gh-discovery:$bookmark"
  fi
  case "$state" in
    NONE|OPEN|MERGED) ;;
    AMBIGUOUS) fail_with 1 "multiple-open:$bookmark" ;;
    CLOSED) fail_with 1 "closed-head:$bookmark" ;;
    *) fail_with 1 "gh-discovery:$bookmark" ;;
  esac
  states[${#states[@]}]=$state

  # Squash- or rebase-merged heads need not remain in destination ancestry.
  # Never make that stale tip the required parent of the next live head.
  if [ "$state" != MERGED ]; then
    vcs_is_ancestor "$previous_sha" "$expected_sha" ||
      fail_with 1 "nonlinear:$bookmark"
    previous_sha=$expected_sha
  fi
  index=$((index + 1))
done

# merged pull requests never become the base of a remaining live item
previous_base=$root_base
index=0
while [ "$index" -lt "${#bookmarks[@]}" ]; do
  bookmark=${bookmarks[$index]}
  expected_sha=${expected_shas[$index]}
  state=${states[$index]}

  if [ "$state" = MERGED ]; then
    skipped_merged[${#skipped_merged[@]}]=$bookmark
    index=$((index + 1))
    continue
  fi

  if [ "$dry_run" = true ]; then
    index=$((index + 1))
    continue
  fi

  vcs_push "$bookmark" || fail_with 1 "push:$bookmark"
  if ! remote_sha=$(vcs_remote_sha "$bookmark"); then
    fail_with 1 "remote-sha-mismatch:$bookmark"
  fi
  [ "$remote_sha" = "$expected_sha" ] || fail_with 1 "remote-sha-mismatch:$bookmark"
  restacked[${#restacked[@]}]=$bookmark

  if [ "$state" = OPEN ]; then
    gh pr edit "$bookmark" --base "$previous_base" >/dev/null 2>&1 || \
      fail_with 1 "pr-edit:$bookmark"
  fi

  previous_base=$bookmark
  index=$((index + 1))
done

emit_json
